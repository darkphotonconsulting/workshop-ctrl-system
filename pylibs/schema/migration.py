import os
import sys
import json
from copy import copy

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])

sys.path.append(libs)

from pymongo import (
    MongoClient, )
from pymongo.database import Database
from pymongo.collection import Collection
from pylibs.schema.default_schemas import DefaultSchemas, SchemaFactory

from pylibs.constants.constants import FILE_MAP, MONGO_STRUCTURE
from backend.config import BaseConfig

# applicable schema choices


class SchemaMigrationEngine():
    DEFAULT_MONGO_STRUCTURE = MONGO_STRUCTURE
    SUPPORTED_SCHEMAS = list(
        sorted(list(set(list(FILE_MAP.keys())) - set(['extension']))))

    def __initialize_mongo_connection(mongo_host: str, mongo_port: int,
                                      admin_user: str, admin_password: str):
        config = BaseConfig(mongo_host=mongo_host,
                            mongo_port=mongo_port,
                            mongo_username=admin_user,
                            mongo_password=admin_password)
        return MongoClient(config.mongo_connect_string)

    def __list_databases(client: MongoClient, key: str = None) -> list:
        dbs = [db['name'] for db in client.list_databases()]
        if key is None:
            return dbs
        else:
            return [db.get(key, None) for db in dbs]

    def __list_collections(client: MongoClient,
                           database_name: str,
                           key: str = None) -> list:
        db = client[database_name]
        collections = [
            collection['name'] for collection in db.list_collections()
        ]
        if key is None:
            return collections
        else:
            return [collection.get(key, None) for collection in collections]

    def __database_exists(client: MongoClient, database_name: str) -> bool:
        dbs = [db for db in client.list_databases()]
        if database_name in [db['name'] for db in dbs]:
            return True
        else:
            return False

    def __collection_exists(client: MongoClient, database_name: str,
                            collection_name: str) -> bool:
        db = client[database_name]
        collections = [
            collection['name'] for collection in db.list_collections()
        ]
        if collection_name in collections:
            return True
        else:
            return False

    def __drop_database(client: MongoClient, database_name: str) -> bool:
        dbs = [db['name'] for db in client.list_databases()]
        if database_name in [db['name'] for db in dbs]:
            client[database_name].drop()
        if database_name not in [db['name'] for db in client.list_databases()]:
            return True
        else:
            return False

    def __drop_collection(client: MongoClient, database_name: str,
                          collection_name: str) -> bool:
        db = client[database_name]
        collections = [
            collection['name'] for collection in db.list_collections()
        ]
        if collection_name in collections:
            db[collection_name].drop()
            if collection_name not in [
                    collection['name'] for collection in db.list_collection()
            ]:
                return True
            else:
                return False
        else:
            return False

    def __create_database(client: MongoClient, database_name: str) -> bool:
        dbs = [db['name'] for db in client.list_databases()]
        if database_name not in dbs:
            db = client[database_name]  # creates database
        else:
            return False

        if database_name in [db['name'] for db in client.list_databases()]:
            return True
        else:
            return False

    def __get_database(client: MongoClient, database_name: str) -> Database:
        return client[database_name]

    def __create_collection(client: MongoClient, database_name: str,
                            collection_name: str, schema: dict) -> bool:
        db = client[database_name]
        if collection_name not in [
                collection['name'] for collection in db.list_collections()
        ]:
            db.create_collection(name=collection_name, validator=schema)
        else:
            return False

        # collection creation mishap
        if collection_name in [
                collection['name'] for collection in db.list_collections()
        ]:
            return True
        else:
            return False

    ## schema functions
    def __get_schema_template(schema_template_name: str = None) -> dict:
        """Returns schema from default schemas templates
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
            schema_template = {
                "system": defaults.system,
                "gpios": defaults.gpios,
                "relays": defaults.relays
            }
        else:
            # TODO: find a better way to do this, setter and getter functions?
            schema_template = DefaultSchemas().__getattribute__(
                schema_template_name)
        return schema_template

    def __compile_schema_template(schema_template: dict = None) -> dict:
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

    def __init__(self, mongo_host: str, mongo_port: int, admin_user: str,
                 admin_password: str) -> None:
        self.client = self.__class__.__initialize_mongo_connection(
            mongo_host=mongo_host,
            mongo_port=mongo_port,
            admin_user=admin_user,
            admin_password=admin_password)
        self.server_info = self.client.server_info()
        self.server_version = self.server_info['version']
        #initialize parameters on self, will be updated
        self.schema_template = {}
        self.schema = {}
        self.database = ""

    def list_databases(self, key=None):
        dbs = [db for db in self.client.list_databases()]
        if key is None:
            return dbs
        else:
            return [db.get(key, None) for db in dbs]

    def create_database(self, database_name: str = None, drop: bool = False) -> bool:
        client = self.client
        # check if database exists
        if self.__class__.__database_exists(client, database_name):
            # drop flag was passed
            if drop:
                self.__class__.__drop_database(client, database_name)
                self.__class__.__create_database(client, database_name)
                if self.__class__.__database_exists(client, database_name):
                    return True
                else:
                    return False
            else:
                return False
        else:
            print('branch..')
            self.__class__.__create_database(client, database_name)

    def delete_database(self, database_name: str = None) -> bool:
        client = self.client
        if self.__class__.__database_exists(client, database_name):
            self.__class__.__drop_database(client, database_name)
            if database_name not in self.__class__.__list_databases(client):
                return True
            else:
                return False

    def get_database(self, database_name: str = None) -> Database:
        client = self.client
        if self.__class__.__database_exists(client, database_name):
            #print(f"{type(client)} {client} {database_name} {type(database_name)}")
            return self.__class__.__get_database(client, database_name)
        else:
            return False 
            
    def check_database(self, database_name: str = None) -> bool:
        client = self.client 
        if self.__class__.__database_exists(client, database_name):
            return True
        else:
            return False

    def create_collection(
        self,
        database_name: str = None,
        collection_name: str = None,
        drop: bool = False,
    ) -> bool:
        client = self.client
        db = self.client[database_name]
        c = self.DEFAULT_MONGO_STRUCTURE.get(collection_name, None)

        if c is not None:  # get the schema template to compile
            schema_template = self.__class__.__get_schema_template()
            schema = self.__class__.__compile_schema_template(schema_template)
        else:  # if no such template exists, fail
            return False

        if self.__class__.__collection_exists(client, database_name,
                                              collection_name):
            if drop:  # collection exists .. now drop and recreate it
                self.__class__.__drop_collection(client, database_name,
                                                 collection_name)
                self.__class__.__create_collection(client, database_name,
                                                   collection_name, schema)
            else:  # collection exists and not instructed to drop it
                return False
        if self.__class__.__collection_exists(client, database_name,
                                              collection_name, schema):
            return True
        else:
            return False

    def get_schema(self,
                   database_name: str = None,
                   collection_name: str = None,
                   pretty_print: bool = False) -> dict:
        if database_name is None:
            database_name = 'static'
            
        c = self.DEFAULT_MONGO_STRUCTURE.get(collection_name, None)
        if c is not None:  # get the schema template to compile
            schema_template = self.__class__.__get_schema_template()
            schema = self.__class__.__compile_schema_template(schema_template)
            if pretty_print:
                print(json.dumps(schema, indent=2))
            return schema
        else:  # if no such template exists, fail
            return None