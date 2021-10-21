import sys
import os
import json
from logging import Logger

from sqlalchemy import schema

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])
sys.path.append(libs)
from typing import (Union, Optional)
from pylibs.config.configuration import (ConfigLoader, Configuration)

from pylibs.coders.encode import SchemaTemplateEncoder
from pylibs.database.engines import SchemaMigrationEngine
from pylibs.database.schemas import SchemaFactory
from pylibs.logging.loginator import Loginator
from argparse import (ArgumentParser, _ArgumentGroup, ArgumentTypeError,
                      Namespace)
from pylibs.device.raspberry_pi import PiInfo
from pylibs.device.generic_relay import RelayInfo

NoneType = type(None)
logger = Loginator(logger=Logger('migrate')).logger
parser: ArgumentParser = ArgumentParser(prog='Schema Migration Tool')
connection_args: _ArgumentGroup = parser.add_argument_group('connection')
global_args: _ArgumentGroup = parser.add_argument_group('global')
database_args: _ArgumentGroup = parser.add_argument_group('databases')
collection_args: _ArgumentGroup = parser.add_argument_group('collections')
action_args: _ArgumentGroup = parser.add_argument_group('actions')
misc_args: _ArgumentGroup = parser.add_argument_group('misc')

connection_args.add_argument(
    '--configuration-file',
    type=str,
    required=False,
    action='store',
    help=f"""The path to a JSON formatted configuration file""")

global_args.add_argument('--validate-connection',
                         action='store_true',
                         required=False,
                         help=f"Verify the MongoDB connection is valid")

global_args.add_argument(
    '--list-operation-key',
    type=str,
    action='store',
    required=False,
    default=None,
    help=
    f"Only return list of values for `--list-operation-key [keyName]` when listing databases or collections"
)

global_args.add_argument(
    '--default-schema-template-name',
    type=str,
    action='store',
    default=None,
    required=False,
    help='Use the named default schema (ex: system, gpios, relays, etc.)')

global_args.add_argument(
    '--debug',
    action='store_true',
    required=False,
    help='Print additional debugging messages to the console')

global_args.add_argument(
    '--output-file',
    type=str,
    action='store',
    default=None,
    required=False,
    help='Output filename for exports --write-default-schema-template, etc.')

database_args.add_argument(
    '--list-databases',
    action='store_true',
    required=False,
    help='List databases visible to the configured MongoDB client')

database_args.add_argument(
    '--create-database',
    action='store_true',
    required=False,
    help=
    'Create a database with the `--database-name <database_name>` argument as name value'
)

database_args.add_argument(
    '--drop-database',
    action='store_true',
    required=False,
    help=
    'Drop a database with the `--database-name <database_name>` argument as name value'
)

database_args.add_argument('--database-name',
                           type=str,
                           action='store',
                           required=False,
                           default=None,
                           help='Selects target Database for CRUD operations')

collection_args.add_argument(
    '--list-collections',
    action='store_true',
    required=False,
    help='List collections in database visible to MongoDB client')

collection_args.add_argument('--list-items',
                             action='store_true',
                             required=False,
                             help='List items in a collection')

collection_args.add_argument(
    '--create-collection',
    action='store_true',
    required=False,
    help=
    'Create a collection within `--database-name <database_name>` with the `--collection-name <collection_name>` argument as name value'
)

collection_args.add_argument(
    '--drop-collection',
    action='store_true',
    required=False,
    help=
    'Drop a collection within `--database-name <database_name>` with the `--collection-name <collection_name>` argument as name'
)

collection_args.add_argument(
    '--wipe-items',
    action='store_true',
    required=False,
    help=
    'Allow dropping collections which contain items/data, used with `--drop-collection`'
)

collection_args.add_argument(
    '--create-if-not-exist',
    action='store_true',
    required=False,
    help=
    'Create a database for a collection if it does not exist, used with `--create-collection`'
)

collection_args.add_argument(
    '--use-default-schema-template',
    action='store_true',
    required=False,
    help=
    'Use a default schema when creating collections, uses the schema named in --default-template-name'
)

collection_args.add_argument(
    '--collection-name',
    type=str,
    action='store',
    required=False,
    default=None,
    help='Collection name to target during CRUD operations')

collection_args.add_argument('--seed-collection',
                             action='store_true',
                             required=False,
                             help='Insert data to a collection')

collection_args.add_argument(
    '--seed-data',
    type=str,
    action='store',
    required=False,
    help=
    'Path to a file containing the seed data JSON file in an appropriate format if applicable'
)

misc_args.add_argument(
    '--print-default-template',
    action='store_true',
    required=False,
    help=
    'Prints the default schema requested by `--default-schema-template-name <schemaName>`'
)

misc_args.add_argument(
    '--write-default-template',
    action='store_true',
    required=False,
    help=
    'Write the default schema requested by `--default-schema-template-name <schemaName>` to a file defined by --output-file <path/to/outputfile.json>'
)

misc_args.add_argument('--write-seed-data',
                       action='store_true',
                       required=False,
                       help=f"""
    Generate and write seed data for `system`, `gpios`, and `relays`. Must also provide --seed-data with one of [system, gpios, relays] and --output-file <file.json or path/to/file.json>. \U0001F4D3 -- relays is not auto-generated, this file must be created by a human to describe their relay board
    """)


def get_engine(args: Namespace) -> Union[SchemaMigrationEngine, bool]:
    if args.configuration_file is not None:

        loader: ConfigLoader = ConfigLoader(from_file=True,
                                            config=args.configuration_file)
        loader.add_attributes()
        config: Configuration = Configuration(**loader.database)
        return SchemaMigrationEngine(config=config)
    else:
        return False


def validate_connection(args: Namespace):
    engine = get_engine(args)
    if engine.validate_connection():
        logger.info("Connection is valid")
        return True
    else:
        logger.error("Connection is not valid")
        return False


def write_seed_data(args: Namespace):
    relay = RelayInfo()
    raspi = PiInfo()
    if args.seed_data in ['system', 'gpios', 'relays']:
        if args.seed_data == 'system':
            data = raspi.system
        elif args.seed_data == 'gpios':
            data = raspi.gpios
        elif args.seed_data == 'relays':
            data = relay.data
        else:
            data = {}
    else:
        logger.warning(
            f"the argument --seed-data is {args.seed_data} but must be one of ..."
        )
        return False
    output_file = args.output_file
    if output_file is not None:
        if '/' in output_file:
            if os.path.exists(os.path.dirname(output_file)):
                with open(output_file, 'w') as file:
                    file.write(json.dumps(data, indent=2))
        else:
            output_file = os.path.join('data', args.output_file)
            with open(output_file, 'w') as file:
                file.write(json.dumps(data, indent=2))

        if os.path.exists(output_file):
            logger.info(f"successfully created file")
            return True
        else:
            logger.warning(f"failed to create file")
            return False
    else:
        logger.warning(f"you must set --output-file with a value")
        return False


def print_default_template(args: Namespace) -> None:
    engine = get_engine(args)
    if args.default_schema_template_name is None:
        print(
            json.dumps(
                engine.get_default_schema_template(
                    schema_template_name=args.default_schema_template_name,
                    pretty_print=False),
                cls=SchemaTemplateEncoder,
                indent=2,
            ))
    else:
        print(
            json.dumps(
                engine.get_default_schema_template(
                    schema_template_name=args.default_schema_template_name,
                    pretty_print=False),
                cls=SchemaTemplateEncoder,
                indent=2,
            ))


def write_default_template(args: Namespace) -> None:
    engine = get_engine(args)
    # add --output-file argument
    if args.default_schema_template_name is not None:
        if args.output_file is not None:
            output_file = args.output_file
            if '/' in output_file:  # argument is a path to a file
                parent_dir = os.path.dirname(output_file)
                if os.path.exists(parent_dir):  # parent exists, write file
                    with open(output_file, 'w') as file:
                        file.write(
                            json.dumps(
                                engine.get_default_schema_template(
                                    schema_template_name=args.
                                    default_schema_template_name,
                                    pretty_print=False),
                                cls=SchemaTemplateEncoder,
                                indent=2,
                            ))
            else:  # argument is a file name only
                output_file = os.path.join('schemas', output_file)
                with open(output_file, 'w') as file:
                    file.write(
                        json.dumps(
                            engine.get_default_schema_template(
                                schema_template_name=args.
                                default_schema_template_name,
                                pretty_print=False),
                            cls=SchemaTemplateEncoder,
                            indent=2,
                        ))
                    if os.path.exists(output_file):
                        logger.info("succesfully wrote file")
                    else:
                        logger.warning("unable to write file")


def list_databases(args: Namespace) -> Union[list, bool]:
    engine = get_engine(args)
    if engine.validate_connection():
        #print('here')
        print(engine.list_databases(key=args.list_operation_key))
    else:
        return False


def list_collections(args: Namespace) -> Union[list, bool]:
    engine = get_engine(args)
    if engine.validate_connection():
        if args.database_name is not None:
            print(
                engine.list_collections(database_name=args.database_name,
                                        key=args.list_operation_key))
        else:
            logger.warning(
                f"please set the database name using --database-name <dbName>")
            return False

    else:
        logger.error(f"invalid connection")
        return False


def list_items(args: Namespace) -> Union[NoneType, bool]:
    engine = get_engine(args)
    if args.list_items and args.database_name is not None and args.collection_name is not None:
        print(
            engine.list_items(
                database_name=args.database_name,
                collection_name=args.collection_name,
            ))
    else:
        return False


def create_database(args: Namespace) -> bool:
    engine = get_engine(args)
    if args.create_database and args.database_name is not None:
        return engine.create_database(database_name=args.database_name)
    else:
        logger.warning(
            "In order to use create database, please provide the --database-name <dbName> argument"
        )
        return False


def drop_database(args: Namespace) -> bool:
    engine = get_engine(args)
    if args.database_name is not None:
        return engine.drop_database(database_name=args.database_name)
    else:
        logger.warning(
            f"please set the --database-name <dbname> in order to use --drop-database"
        )


def create_collection(args: Namespace) -> bool:
    engine = get_engine(args)
    if args.create_collection and args.database_name is not None and args.collection_name is not None:
        print('here')
        if args.use_default_schema_template:
            template = engine.get_default_schema_template(
                schema_template_name=args.default_schema_template_name)
            schema = engine.compile_schema_template(schema_template=template)
            return engine.create_collection(
                database_name=args.database_name,
                collection_name=args.collection_name,
                use_schema=args.use_default_schema_template,
                schema=schema,
                create_if_not_exist=args.create_if_not_exist,
                debug=args.debug)
        else:
            return engine.create_collection(
                database_name=args.database_name,
                collection_name=args.collection_name,
                use_schema=None,
                schema=None,
                create_if_not_exist=args.create_if_not_exist,
                debug=args.debug)
    else:
        logger.warning(
            f"please set --database-name <dbName> --collection-name <collectionName> in order to use --create-collection"
        )


def drop_collection(args: Namespace) -> bool:
    engine = get_engine(args)
    if args.drop_collection and args.database_name is not None and args.collection_name is not None:
        print('here')
        return engine.drop_collection(
            database_name=args.database_name,
            collection_name=args.collection_name,
            wipe_items=args.wipe_items,
        )


def insert(args: Namespace) -> bool:
    engine = get_engine(args)
    if args.seed_collection and args.seed_data is not None:
        if os.path.exists(args.seed_data):
            with open(args.seed_data, 'r') as file:
                data = json.load(file)
                if isinstance(data, dict):
                    engine.insert_item(database_name=args.database_name,
                                       collection_name=args.collection_name,
                                       data=data)
                    return True
                elif isinstance(data, list):
                    engine.insert_items(database_name=args.database_name,
                                        collection_name=args.collection_name,
                                        data=data)
                    return True
    else:
        return False
        #engine.


def main(args: Namespace):

    # generate and write seed data
    if args.write_seed_data:
        write_seed_data(args)

    if args.configuration_file is not None:  # these functions requires a configuration file

        # validate conn
        if args.validate_connection:
            validate_connection(args)

        # print schema default templates
        if args.print_default_template:
            if args.default_schema_template_name is not None:
                print_default_template(args)
            else:
                engine = get_engine(args)
                print(
                    json.dumps(
                        engine.DEFAULT_SCHEMAS,
                        indent=2,
                        cls=SchemaTemplateEncoder,
                    ))

        # write default schema templates
        if args.write_default_template:
            if args.default_schema_template_name is not None and args.output_file is not None:
                write_default_template(args)

        # list dbs
        if args.list_databases:
            list_databases(args)

        # ceate db
        if args.create_database:
            create_database(args)

        # drop db
        if args.drop_database:
            drop_database(args)

        # list cols
        if args.list_collections:
            list_collections(args)

        # list col items
        if args.list_items:
            list_items(args)

        # create col
        if args.create_collection:
            create_collection(args)

        # drop col
        if args.drop_collection:
            drop_collection(args)

        # seed col
        if args.seed_collection:
            insert(args)

    # else:
    #     logger.warning(f"Please provide the --configuration-file <path/to/config.json> argument to use this action")
    #     parser.print_help()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)