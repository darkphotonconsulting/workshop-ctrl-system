import logging
import json
from json import JSONEncoder
import uuid

from pymongo import collection
#from pymongo import database, collec
from pylibs.schema.migration import SchemaMigrationEngine
from pylibs.logging.loginator import Loginator
from argparse import ArgumentParser, Namespace

logger = logging.getLogger('Main')
loginator = Loginator(
    logger=logger
)
logger = loginator.logger

parser = ArgumentParser(prog='HeadUnit Schema Migration Tool')

stop_codes= {
    'SUCCESS': 0,
    'ARGUMENTS': 1,
    'EXECUTION_ERROR': -1,

}


class MigrationEncoder(json.JSONEncoder):
    """
    """
    def default(self, object):
        if isinstance(object, uuid.UUID):
            return str(object)

        return JSONEncoder.default(self, object)



conn_args = parser.add_argument_group(
    'connection'
)
action_args = parser.add_argument_group(
    'actions'
)
conn_args.add_argument('--mongo-host',
    type=str,
    required=False,
    action='store',
    help='MongoDB host IP or FQDN',
    default="mongo.darkphotonworks-labs.io"
)
conn_args.add_argument('--mongo-port',
    type=int,
    required=False,
    action='store',
    help='MongoDB Port',
    default=27017
)
conn_args.add_argument('--mongo-username',
    type=str,
    required=True,
    action='store',
    help='MongoDB Administrative Username'
)
conn_args.add_argument('--mongo-password',
    type=str,
    required=True,
    action='store',
    help='MongoDB Administrative Password'
)


action_args.add_argument('--drop-existing',
    action='store_true',
    required=False,
    help='Performs drops on Databases and Collections before recreating them'
)
action_args.add_argument('--debug',
    action='store_true',
    required=False,
    help=
    'Debugging messages enabled on supporting operations'
)

action_args.add_argument('--use-default-schemas',
    action='store_true',
    required=False,
    help='Collections will be created using the default schema items [system, gpios, relays], the --collection-name MUST be system, gpios, or relays'
)


action_args.add_argument('--database-name',
    action='store',
    required=False,
    default='',
    help='The MongoDB Database to perform CRUD operations on, use with Database level CRUD operations'
)
action_args.add_argument('--collection-name',
    action='store',
    required=False,
    default='',
    help='The MongoDB Collection to perform CRUD operations on, use with Collection level CRUD operations'
)
action_args.add_argument('--list-databases',
    action='store_true',
    required=False,
    help='Lists MongoDB Database objects'
)
action_args.add_argument('--list-collections',
    action='store_true',
    required=False,
    help='Lists MongoDB Collection objects'
)
action_args.add_argument('--list-items',
    action='store_true',
    required=False,
    help='Lists items in a MongoDB Collection'
)
action_args.add_argument('--list-key',
    action='store',
    required=False,
    default=None,
    help='Use to return just the requested keys value when using [--list-databases or --list-collections]'
)
action_args.add_argument('--create-database',
    action='store_true',
    required=False,
    help='Creates a MongoDB Database'
)
action_args.add_argument('--drop-database',
    action='store_true',
    required=False,
    default='',
    help='Drop a MongoDB Database'
)
action_args.add_argument('--create-collection',
    action='store_true',
    required=False,
    help='Creates a MongoDB Database'
)
action_args.add_argument('--drop-collection',
    action='store_true',
    required=False,
    default='',
    help='Drop a MongoDB Collection'
)


# idempotent functions for migrating default or user defined and dynamic schemas to mongodb
def get_engine(a: Namespace):
    return SchemaMigrationEngine(
        mongo_host=a.mongo_host,
        mongo_port=a.mongo_port,
        admin_user=a.mongo_username,
        admin_password=a.mongo_password
    )

def list_databases(a: Namespace):
    engine = get_engine(a)
    databases = engine.list_databases(key=a.list_key)
    if isinstance(databases, list):
        print(json.dumps(databases, indent=2, cls=MigrationEncoder))
    elif isinstance(databases, str):
        logger.warning(databases)
    else:
        logger.warning("unsupported data type returned from a list operation")
        exit(stop_codes['EXECUTION_ERROR'])
    exit(stop_codes['SUCCESS'])


def list_collections(a: Namespace):
    engine = get_engine(a)
    if a.database_name == '':
        logger.warning(
            f"please set the [--database-name] with a valid value to use --list-collections"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])
    else:
        collections = engine.list_collections(database_name=a.database_name,
                                              key=a.list_key)
        if isinstance(collections, list):
            print(json.dumps(collections, indent=2, cls=MigrationEncoder))
        elif isinstance(collections, str):
            logger.warning(collections)
        else:
            logger.warning(
                f"unsupported data type returned by collection list operation")
            exit(stop_codes['EXECUTION_ERROR'])
        exit(stop_codes['SUCCESS'])

def list_items(a: Namespace):
    engine = get_engine(a)
    if a.database_name == '':
        logger.warning(
            f"please set the [--database-name] with a valid value to use --create-collection"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])

    if a.collection_name == '':
        logger.warning(
            f"please set the [--collection-name] with a valid value to use --create-collection"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])
    
    print()


def create_database(a: Namespace):
    engine = get_engine(a)
    if a.database_name == '':
        logger.warning("please set the [--database-name] value")
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])
    else:
        engine.create_database(a.database_name, drop=a.drop_existing)
    exit(stop_codes['SUCCESS'])

def create_collection(a: Namespace):
    engine = get_engine(a)
    if a.database_name == '':
        logger.warning(
            f"please set the [--database-name] with a valid value to use --create-collection"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])

    if a.collection_name == '':
        logger.warning(
            f"please set the [--collection-name] with a valid value to use --create-collection"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])

    if a.use_default_schemas:
        if a.collection_name not in ['system', 'relays', 'gpios']:
            logger.warning(
                f"if using [--load-default-schemas] the [--collection-name] argument value MUST be one of 'system', 'relays' or 'gpios'"
            )
            exit(stop_codes['ARGUMENTS'])
    if engine.create_collection(
        database_name=a.database_name,
        collection_name=a.collection_name,
        custom_schema=None,
        use_schema=a.use_default_schemas,
        drop=a.drop_existing,
        debug=a.debug
    ):
        exit(stop_codes['SUCCESS'])
    else:
        exit(stop_codes['EXECUTION_ERROR'])


def drop_database(a: Namespace):
    engine = get_engine(a)
    if a.database_name == '':
        logger.warning('please set the [--database-name] value')
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])
    else:
        engine.drop_database(args.database_name)
    exit(stop_codes['SUCCESS'])


def drop_collection(a: Namespace):
    engine = get_engine(a)
    if a.database_name == '':
        logger.warning(
            f"please set the [--database-name] with a valid value to use --create-collection"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])

    if a.collection_name == '':
        logger.warning(
            f"please set the [--collection-name] with a valid value to use --create-collection"
        )
        parser.print_help()
        exit(stop_codes['ARGUMENTS'])

    if engine.drop_collection(
        database_name=a.database_name,
        collection_name=a.collection_name
    ):
        exit(stop_codes['SUCCESS'])
    else:
        exit(stop_codes['EXECUTION_ERROR'])


def main(a: Namespace):
    if a.list_databases:
        list_databases(a)

    if a.list_collections:
        list_collections(a)

    if a.create_database:
        create_database(a)

    if a.drop_database:
        drop_database(a)

    if a.create_collection:
        create_collection(a)

    if a.drop_collection:
        drop_collection(a)


# run as a script called from the shell
if __name__ == '__main__':
    args = parser.parse_args()
    main(args)