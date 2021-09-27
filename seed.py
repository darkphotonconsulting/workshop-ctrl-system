#!/usr/bin/python3
"""Multi-purpose data utility for populating the headunit backends system data easily 

- Uses RPi.GPIO & BeautifulSoup to gather and produce a robust map of raspberry pi & GPIO attributes in JSON format
- write outputs to file (--write-file)
- write outputs to backend (--write-db)

[arguments]
------------
--schema-template - determines which schema to read or write
--data-out-dir - determines where files are saved when --write-file is enabled
--write-file - enables writing the selected compiled template to --data-out-dir
--read-file - read already created compiled template from --data-out-dir (?)
--write-db - write selected compiled schema to database
--read-db - read the selected compiled template from database

"""
import os
import platform
import sys
import json
from copy import copy
#import argparse
from argparse import ArgumentError, ArgumentParser, Namespace
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid

from collections import OrderedDict
from config.settings import Config
from pylibs.pi import PiInfo, PiInfoEncoder
from pylibs.relay import RelayInfo
from pylibs.schema.default_schemas import DefaultSchemas, SchemaFactory

# mappings for writing files

DATABASE_COLLECTION_MAPPING = {
    'static': {
        'system': 'static-system',
        'gpios': 'static-gpios',
        'relays': 'static-relays',
        'all': [
            'static-system',
            'static-gpios'
        ]
    },
    'dynamic': {

    }
}
FILE_MAPPING = {
    'extension': 'json',
    'all': 'raspberrypi',
    'system': 'system',
    'gpios': 'gpios',
    'relays': 'user-relays'
}

# applicable schema choices
SCHEMA_CHOICES = list(sorted(list(
    set(list(FILE_MAPPING.keys())) -
    set(['extension'])
)))
# configure arg parser
argparser = ArgumentParser(
    prog="The handy dandy headunit CRUD Tool",
    description="""One stop shop for generating pi info data,
    seeding that data to mongo, and reading data in mongo collections. Generates JSON inputs for Mongo backend(s). 
    Insert JSON inputs into appropriate Mongo Collections (system, gpios). Compiles schemas defined in pylib.schema.schemas 
    to be used as validators in MongoDB. Lists records in MongoDB system collections/databases.
    JSON object describes the running raspberry pi"""
)

# argparser groups
general_args = argparser.add_argument_group('general args')
mongo_args = argparser.add_argument_group('mongoDB connections')
mongo_crud_args = argparser.add_argument_group('mongoDB crud')
template_args = argparser.add_argument_group('schemas')
info_args = argparser.add_argument_group('system')

# args
mongo_args.add_argument('--mongodb-host',
    action='store',
    type=str,
    required=False,
    default=Config.mongodb_host,
    help="MongoDB host"
)
mongo_args.add_argument('--mongodb-port',
    action='store',
    type=int,
    required=False,
    default=Config.mongodb_port,
    help="MongoDB Port"
)

mongo_crud_args.add_argument('--mongodb-db',
    action='store',
    required=False,
    default=None,
    help="Validate a Mongo DB exits"
)

mongo_crud_args.add_argument('--mongodb-create-static-db',
    action='store_true',
    required=False,
    help="Create a Mongo database with attached validator schema for --collection-name"
)


mongo_crud_args.add_argument('--mongodb-dbs',
    action='store_true',
    required=False,
    default=False,
    help="List Mongo DB Databases"
)

mongo_crud_args.add_argument('--mongodb-drop',
    action='store_true',
    required=False,
    default=False,
    help="Drop databases and collections that exist before recreating them (development feature)"
)

general_args.add_argument('--data-out-dir',
    action='store',
    type=str,
    required=False,
    default='data',
    help="Data out directory"
)

general_args.add_argument('--collection-name',
    action='store',
    type=str,
    required=False,
    default=None,
    choices=SCHEMA_CHOICES,
    help=
    f"Name of the collection out of {SCHEMA_CHOICES}, determines which schema, file, and/or database collection to work with"
)

general_args.add_argument('--collection-names',
    action='store_true',
    required=False,
    help=
    f"Print names of the supported collections"
)

info_args.add_argument('--print-info',
    action='store_true',
    required=False,
    default=False,
    help="Print the raspberry pi info object as JSON"
)

template_args.add_argument('--print-schema',
    action='store_true',
    required=False,
    default=False,
    help="print the compiled schema object as JSON"
)

info_args.add_argument('--write-info',
    action='store_true',
    required=False,
    default=False,
    help=
    "Write raspberry pi info object as JSON to file in [--data_out_dir], defaults to './data'"
)

template_args.add_argument('--write-schema',
    action='store_true',
    required=False,
    default=False,
    help=
    "write the schema object as JSON to file in [--data_out_dir], defaults to './data'"
)
mongo_crud_args.add_argument('--mongo-write-schema',
    action='store_true',
    required=False,
    default=False,
    help="Compiles schema, attaches to collection, inserts "
)
argparser.add_argument('--debug',
    action='store_true',
    required=False,
    default=False
)

## schema functions

def get_schema_template(schema_template_name: str = None) -> dict:
    """Returns schema from default schemas

    Args:
        schema_template_name ([str]): The name of the schema template 

    Returns:
        [dict]: Python dictionary representation of mongo schema template
    """
    schema = {}
    if schema_template_name is None:
        schema_template_name = 'all'
    if schema_template_name == 'all':
        defaults = DefaultSchemas()
        schema = {
            "system": defaults.system,
            "gpios": defaults.gpios
        }
    else:
        # TODO: find a better way to do this, setter and getter functions?
        schema = DefaultSchemas().__getattribute__(schema_template_name)
    return schema

def compile_schema_template(schema_template: dict = None) -> dict:
    """Compiles a Mongo DB compliant validator schema from the user selected schema template object, 
    This is used when creating the initial database resources in MongoDB and defines the data types of the attributes within each collection

    Args:
        schema_template dict: The dict reprsentation of the mongo schema template

    Returns:
        dict: compiled validator schema python object
    """
    factory = SchemaFactory()
    validator = copy(factory.validator)
    schema = factory.generate_schema(schema_template)
    validator['$jsonSchema']['properties'] = schema
    return validator

# pi info functions
def get_pi_info() -> PiInfo:
    """Analyzes the running pi and returns a rich data object
        - Scans running pi for system and gpio data
        - Scrapes pinout.xyz for enrichiment data
    
    Returns:
        PiInfo: An instance of a PiInfo object
    """
    return PiInfo()

# mongo db functions
def mongo_connection(args: Namespace) -> MongoClient:
    """

    Args:
        args (Namespace): 

    Returns:
        MongoClient: a MongoClient object
    """

    return MongoClient(
        f"mongodb://{args.mongodb_host}:{args.mongodb_port}")

def mongo_databases(client: MongoClient) -> list:
    """List the databases in mongodb

    Args:
        client (MongoClient): a pymongo client object

    Returns:
        list: list of databases (empty if none, which probably won't happen)
    """
    return client.database_names()

def mongo_database_created(client: MongoClient, db: str) -> bool:
    """Verify if a database has already been created

    Args:
        client (MongoClient): a pymongo client object
        db (str): a database name to check exists

    Returns:
        bool: returns True if database exists, False if not
    """
    return True if db in mongo_databases(client) else False

def _create_collection(args: Namespace, client: MongoClient, db_name: str, collection_name: str) -> Collection:
    """Create a mongodb collection, attaches validator schema, uses connection names defined in DATABASE_COLLECTION_MAPPING

    Args:
        client (MongoClient): [description]
        db_name (str): [description]
        collection_name (str): [description]

    Returns:
        Collection: [description]
    """
    db = client[db_name]
    schema_template = get_schema_template(collection_name)
    collection_name = DATABASE_COLLECTION_MAPPING[db_name][collection_name]
    schema = compile_schema_template(schema_template)
    if collection_name not in db.collection_names():
        print(f"creating collection: {collection_name}")
        collection = db.create_collection(name=collection_name, validator=schema)
    else:
        if args.mongodb_drop:
            print(f"dropping collection {collection_name} in database {db_name}")
            db.drop_collection(collection_name)
            print(f"recreating collection {collection_name} in {db_name}" )
            collection = db.create_collection(name=collection_name,
                                              validator=schema)
        else:
            print(f"re-using existing collection: {collection_name}")
            collection = db[collection_name]
    return collection


def mongo_create_static_database(args: Namespace, client: MongoClient) -> None:
    """[summary]

    Args:
        client (MongoClient): [description]
        collection_name (str): [description]
    """
    pi_info = get_pi_info()
    server_info = client.server_info()
    #the database does not exist
    if 'static' not in mongo_databases(client):
        db = client['static']
        if args.collection_name != 'all':
            if args.collection_name in ['system', 'gpios']:
                pidict = pi_info.__getattribute__(args.collection_name)
                collection = _create_collection(args, client, 'static', args.collection_name)
                collection.insert(pidict)
            elif args.collection_name in ['relays']:
                relay_info = RelayInfo()
                relaydict = relay_info.data
                collection = _create_collection(args, client, 'static', args.collection_name)
                collection.insert(relaydict)
        else:
            for collection in ['system', 'gpios', 'relays']:
                if collection in ['system', 'gpios']:
                    pidict = pi_info.__getattribute__(collection)
                    collection = _create_collection(args, client, 'static', collection)
                    collection.insert(pidict)
                elif collection in ['relays']:
                    relay_info = RelayInfo()
                    relaydict = relay_info.data
                    collection = _create_collection(args, client, 'static',
                                                    collection)
                    collection.insert(relaydict)

    else:
        if args.mongodb_drop:
            print("db exists, dropping and recreating database")
            client.drop_database('static')
            db = client['static']
        else:
            print("adding or updating specified collections")
        if args.collection_name != 'all':
            if args.collection_name in ['system', 'gpios']:
                pidict = pi_info.__getattribute__(args.collection_name)
                collection = _create_collection(args, client, 'static',
                                                args.collection_name)
                collection.insert(pidict)
            elif args.collection_name in ['relays']:
                relay_info = RelayInfo()
                relaydict = relay_info.data
                collection = _create_collection(args, client, 'static', args.collection_name)
                collection.insert(relaydict)
        else:
            for collection in ['system', 'gpios', 'relays']:
                if collection in ['system', 'gpios']:
                    pidict = pi_info.__getattribute__(collection)
                    collection = _create_collection(args, client, 'static', collection)
                    collection.insert(pidict)
                elif collection in ['relays']:
                    relay_info = RelayInfo()
                    relaydict = relay_info.data
                    collection = _create_collection(args, client, 'static',
                                                    collection)
                    collection.insert(relaydict)



def write_schema(args: Namespace, data) -> None:
    """Write compiled schema to JSON file

    Args:
        args ([argparse.ArgumentParser]): the args object
        data ([dict]): compiled schema object
    """
    #print(type(data))
    file_name = FILE_MAPPING[args.collection_name]
    with open(f"{args.data_out_dir}/schema-{file_name}.{FILE_MAPPING['extension']}", 'w') as file:
        print(
            f"writing compiled schema: {args.data_out_dir}/schema-{file_name}.{FILE_MAPPING['extension']}"
        )
        #json.dump(data, file)
        file.write(data)

def write_info(args: Namespace, data):
    """Write pi info to JSON file
    
    Args:
        args ([argparse.ArgumentParser]): the args object
        data ([dict]): dict format of PiInfo object
    """
    file_name = FILE_MAPPING[args.collection_name]
    with open(f"{args.data_out_dir}/{file_name}.{FILE_MAPPING['extension']}", 'w') as file:
        print(
            f"writing pi info: {args.data_out_dir}/{file_name}.{FILE_MAPPING['extension']}"
        )
        file.write(data)

def get_json(data):
    """Get JSON version of dictionary

    Args:
        data dict: some dictionary

    Returns:
        str: This should return a proper JSON string... not an object
    """
    return json.dumps(data, indent=2, sort_keys=True)

def pretty_print(data):
    """Prints a JSON string prettily

    Args:
        data ([dict]): pretty print dict as JSON
    """
    print(get_json(data))

def main(args):
    """Main thread for seed.py

    Args:
        args ([ArgumentParser]): pass in ArgumentParser.parse_args()
    """
    print(args) if args.debug else None

    schema_template = get_schema_template(args.collection_name)
    schema = compile_schema_template(schema_template)
    #only get pi_info if we need it.
    if args.write_info or args.print_info:
        pi_info = get_pi_info()
        relay_info = RelayInfo()
    # print data
    if args.print_info:
        if args.collection_name == 'all':
            pretty_print(pi_info.__dict__)
        else:
            pretty_print(pi_info.__getattribute__(args.collection_name))
    if args.print_schema:
        pretty_print(schema)
    # write files
    if args.write_schema:
        print(get_json(schema)) if args.debug else None
        write_schema(args, get_json(schema))
    if args.write_info:
        if args.collection_name != 'all' and args.collection_name in ['system', 'gpios']:
            print(
                get_json(pi_info.__dict__) if args.collection_name ==
                'all' else get_json(pi_info.__dict__[args.collection_name])) if args.debug else None
            write_info(
                args,
                get_json(pi_info.__dict__) if args.collection_name == 'all' else get_json(pi_info.__dict__[args.collection_name])
            )
        elif args.collection_name != 'all' and args.collection_name in ['relays']:
            print(get_json(relay_info.data)) if args.debug else None
            write_info(
                args,
                get_json(relay_info.data)
            )

    if args.mongodb_dbs or args.mongodb_db is not None:
        mongo = mongo_connection(args)

    if args.mongodb_dbs:
        databases = mongo_databases(mongo)
        print(f"{databases}")

    if args.mongodb_db is not None:
        print("True") if mongo_database_created(mongo, args.mongodb_db) else print("False")

    if args.mongodb_create_static_db:
        mongo = mongo_connection(args)
        print("database exists") if mongo_database_created(mongo, 'static') else print("database does not exist") if args.debug else None
        ret = mongo_create_static_database(args, mongo)
        if ret:
            print("created db")

# run as a script called from the shell
if __name__ == '__main__':
    if platform.uname().node == 'raspberrypi' and platform.machine() in ['armv7l']:
        args = argparser.parse_args()
        main(args)
    else:
        print("Please run this script on a supported system!")
        exit()
