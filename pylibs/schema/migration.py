import os
import sys
import json
import logging
from copy import copy

from pymongo import collection

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])

sys.path.append(libs)

from pymongo import (
    MongoClient, )
from pymongo.database import Database
from pymongo.collection import Collection
from pylibs.schema.default_schemas import StaticSchemas, SchemaFactory

from pylibs.constants.constants import FILE_MAP, MONGO_STRUCTURE
from backend.config import BaseConfig

from pylibs.logging.loginator import Loginator





class SchemaMigrationEngine():
    # setup the loginator alligator =)
    logger = logging.getLogger('SchemaMigrationEngine')
    loginator = Loginator(
        logger=logger
    )
    logger = loginator.logger
    DEFAULT_FILE_MAP = FILE_MAP
    DEFAULT_MONGO_STRUCTURE = MONGO_STRUCTURE
    SUPPORTED_STATIC_SCHEMAS = list(
        sorted(list(set(list(FILE_MAP.keys())) - set(['extension']))))
    SUPPORTED_DYNAMIC_SCHEMAS = []

    @classmethod
    def __initialize_mongo_connection(cls,
        mongo_host: str,
        mongo_port: int,
        admin_user: str,
        admin_password: str
    ) -> MongoClient:
        config = BaseConfig(mongo_host=mongo_host,
                            mongo_port=mongo_port,
                            mongo_username=admin_user,
                            mongo_password=admin_password)
        return MongoClient(config.mongo_connect_string)


    @classmethod
    def __list_databases(cls,
        client: MongoClient,
        key: str = None
    ) -> list:
        dbs = [db for db in client.list_databases()]
        if key is None:
            return dbs
        else:
            dbs = [db.get(key, None) for db in dbs]
            if None in dbs:
                return f"the key [{key}] does not exist in a pymongo db object, valid keys are: ['name', 'sizeOnDisk', 'empty']"
            else:
                return dbs


    @classmethod
    def __list_collections(cls,
        client: MongoClient,
        database_name: str,
        key: str = None
    ) -> list:
        db = client[database_name]
        collections = [
            collection for collection in db.list_collections()
        ]
        if key is None:
            return collections
        else:
            collections = [collection.get(key, None) for collection in collections]
            if None in collections:
                return f"the key [{key}] does not exist in a pymongo collection object"
            else:
                return collections

    @classmethod
    def __list_items(cls,
        client: MongoClient,
        database_name: str = None,
        collection_name: str = None,
    ) -> list:
        if cls.__database_exists(client=client,
                                            database_name=database_name):
            if cls.__collection_exists(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name):
                db = cls.__get_database(client=client,
                                                   database_name=database_name)
                collection = db.get_collection(name=collection_name)
                items = [i for i in collection.find({})]
                return items


    @classmethod
    def __database_exists(cls,
        client: MongoClient,
        database_name: str
    ) -> bool:
        dbs = [db for db in client.list_databases()]
        if database_name in [db['name'] for db in dbs]:
            cls.logger.info(f"database [{database_name}] exists")
            return True
        else:
            cls.logger.info(f"no database [{database_name}] exists")
            return False


    @classmethod
    def __collection_exists(cls, client: MongoClient, database_name: str,
                            collection_name: str) -> bool:
        db = client[database_name]
        collections = [
            collection['name'] for collection in db.list_collections()
        ]
        if collection_name in collections:
            cls.logger.info(f"The collection [{collection_name}] exists in database [{database_name}]")
            return True
        else:
            cls.logger.info(f"The collection [{collection_name}] does not exist in database [{database_name}]")
            return False


    # database methods


    @classmethod
    def __get_database(cls,
        client: MongoClient,
        database_name: str
    ) -> Database:
        if cls.__database_exists(
            client=client,
            database_name=database_name,
        ): #database exists
            cls.logger.info(f"getting database [{database_name}]")
            return client[database_name]
        else: #database does not exist
            cls.logger.error(f"can't get database [{database_name}] because it does not exist")
            return False

    @classmethod
    def __get_collection(cls,
        client: MongoClient,
        database_name: str = None,
        collection_name: str = None,                   
    ) -> Collection:
        if cls.__database_exists(
            client=client,
            database_name=database_name,
            collection_name=collection_name
        ): #database exists
            db = cls.__get_database(
                client=client,
                database_name=database_name
            )
            if cls.__collection_exists(
                client=client, 
                database_name=database_name, 
                collection_name=collection_name
            ): #collection exists
                return db.get_collection(name=collection_name)
            else: # collection does not exist
                cls.logger.error(
                    f"can't get collection [{collection_name}] in database [{database_name}], the collection does not exist"
                )
                return False
        else: # database does not exist
            cls.logger.error(
                f"can't get collection [{collection_name}] in database [{database_name}], the database does not exist"
            )
            return False

    @classmethod
    def __create_database(cls,
        client: MongoClient,
        database_name: str
    ) -> bool:
        dbs = [db['name'] for db in client.list_databases()]
        if database_name not in dbs:
            cls.logger.info(f"creating the requested database [{database_name}]")
            db = client[database_name]
            # creates a placeholder collection to ensure the db is saved in Mongo
            db.create_collection(
                name='__pymongo__',
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "properties": {
                            "foo": {
                                "bsonType": "string"
                            }
                        }
                    }
                }
            )
        else:
            cls.logger.warning(f"the database [{database_name}] already exists")
            return False
        # naïve verification the DB was created
        if database_name in [db['name'] for db in client.list_databases()]:
            cls.logger.info(f"the database [{database_name}] was successfully created")
            return True
        else:
            cls.logger.error(f"the database [{database_name}] was not successfully created")
            return False

    @classmethod
    def __drop_database(cls,
        client: MongoClient,
        database_name: str
    ) -> bool:
        dbs = [db for db in client.list_databases()]
        if database_name in [db['name'] for db in dbs]:
            cls.logger.info(f"dropping database [{database_name}]")
            #db = client[database_name]
            client.drop_database(database_name)
        # recheck
        if database_name not in [db['name'] for db in client.list_databases()]:
            cls.logger.info(f"successfully dropped database [{database_name}]")
            return True
        else:
            cls.logger.info(f"failed to drop database [{database_name}]")
            return False

            
    @classmethod
    def __create_collection(cls,
                            client: MongoClient,
                            database_name: str = None,
                            collection_name: str = None,
                            custom_schema: dict = None,
                            use_schema: bool = False,
                            create_if_not_exist: bool = False,
                            debug: bool = False,
    ) -> bool:

        if cls.__database_exists(client, database_name=database_name):
            # get db reference, it exists
            db = cls.__get_database(
                client,
                database_name=database_name
            )
            if cls.__collection_exists(client, database_name=database_name, collection_name=collection_name): # the collection already exists
                cls.logger.warning(f"The collection [{collection_name}] already exists in [{database_name}]")
                return False
            else: # no such collection
                if use_schema: # using a schema
                    cls.logger.debug(f"Using validation schemas") if debug else None
                    if custom_schema is None: # use default schema
                        cls.logger.debug(
                            f"Using default schema_template for [{collection_name}]"
                        ) if debug else None
                        schema_template = SchemaMigrationEngine.__get_schema_template(
                            schema_template_name=collection_name)
                        cls.logger.debug(
                            f"Compiling default schema from {schema_template} .."
                        ) if debug else None
                        schema = SchemaMigrationEngine.__compile_schema_template(
                            schema_template)
                    else: # use provided schema
                        schema = custom_schema
                        cls.logger.debug(
                            f"Using a provided custom schema"
                        ) if debug else None

                    if debug: # print schema_template and schema
                        cls.logger.debug(f"Schema template: {schema_template}")
                        cls.logger.debug(f"Schema data: {schema}")

                # create collection

                if use_schema: #create collection with validator
                    cls.logger.info(f"Creating collection {collection_name} in database {database_name} with [{schema}]")
                    db.create_collection(
                        name=collection_name,
                        validator=schema
                    )
                else: #create a collection
                    cls.logger.info(f"Creating collection {collection_name} in database {database_name}")
                    db.create_collection(
                        name=collection_name
                    )

                if cls.__collection_exists(client, database_name=database_name, collection_name=collection_name): # collection created successfully
                    cls.logger.info(f"succesfully created collection {collection_name} in database {database_name}")
                    return True
                else: #collection creation failed
                    cls.logger.error(f"failed to create collection {collection_name} in database {database_name}")
                    return False
        else:
            ### experimental recursive call, 
            if create_if_not_exist:
                cls.logger.info(
                    f"the flag [--create-if-not-exist] was enabled, the database {database_name} will be created as a dependency of creating collection {collection_name}"
                )
                if cls.__create_database(client=client,database_name=database_name):
                    # use recursion?
                    cls.logger.info(f"successfully created database dependency {database_name} for collection {collection_name}, calling myself to make your collection..")
                    cls.__create_collection(client=client, database_name=database_name, collection_name=collection_name, custom_schema=custom_schema, use_schema=use_schema, create_if_not_exist=False)
                    return True
                else:
                    cls.logger.error(f"failed to create database depencency {database_name} for collection {collection_name} ..")
                    return False
                    #print()
            else:
                cls.logger.warning(f"the database {database_name} does not yet exist, you should create it before creataing a collection in it")
                cls.logger.info(f"if you wish to create the database automatically, use [--create-if-not-exist]")
                return False


    @classmethod
    def __drop_collection(cls,
        client: MongoClient,
        database_name: str,
        collection_name: str,
        wipe_items: bool = True,
    ) -> bool:
        db = client[database_name]
        collections = [
            collection for collection in db.list_collections()
        ]
        if collection_name in [collection['name'] for collection in collections]:
            if len(cls.__list_items(client=client, database_name=database_name, collection_name=collection_name)) > 0: # data in collection
                cls.logger.warning("This collection contains data that will be wiped if dropped")
                if wipe_items:
                    db[collection_name].drop()
                else:
                    cls.logger.warning("Not dropping collection with data as --wipe-existing-data flag was not passed")
                    return False
            else:
                db[collection_name].drop()
            if collection_name not in [
                    collection['name'] for collection in db.list_collections()
            ]:
                cls.logger.info(f"successfully dropped collection {collection_name} in database {database_name}")
                return True
            else:
                cls.logger.error(f"failed to drop collection {collection_name} in database {database_name}")
                return False
        else:
            cls.logger.warning(f"the collection {collection_name} does not exist in the database {database_name}")
            return True

    ## schema methods
    @classmethod
    def __get_schema_template(cls,
        schema_template_name: str = None
    ) -> dict:
        """Returns schema from default schemas templates
        Args:
            schema_template_name ([str]): The name of the schema template 

        Returns:
            [dict]: Python dictionary representation of mongo schema template
        """
        #create a default
        schema_template = {
            'foo': str,
            'bar': int
        }
        if schema_template_name is None: #default to the system key
            cls.logger.warn(f"the provided schema_template_name was None, defaulting to system")
            schema_template_name = 'system'
        # TODO: find a better way to do this, setter and getter functions?
        try:
            cls.logger.info(f"getting default schema for {schema_template_name}")
            schema_template = StaticSchemas().__getattribute__(
                schema_template_name)
        except AttributeError as error_message:
            cls.logger.warning(f"the requested schema {schema_template_name} does not exist, using a bare template [{schema_template}]")
            #return False
        finally:
            return schema_template

    @classmethod
    def __compile_schema_template(cls,
        schema_template: dict = None
    ) -> dict:
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

    def __init__(self,
        mongo_host: str,
        mongo_port: int,
        admin_user: str,
        admin_password: str
    ) -> None:
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

    def list_databases(self,
        key: bool =None
    ) -> list:
        client = self.client
        return self.__class__.__list_databases(client, key)

    def list_collections(self,
        database_name: str = None,
        key: bool = None,
    ) -> list:
        client = self.client
        return self.__class__.__list_collections(client=client,
                                                 database_name=database_name,
                                                 key=key)

    def list_items(self,
        database_name: str = None,
        collection_name: str = None,
    ) -> list:
        client = self.client
        return self.__class__.__list_items(
            client=client,
            database_name=database_name,
            collection_name=collection_name,
        )


    def get_database(self,
        database_name: str = None
    ) -> Database:
        client = self.client
        if self.__class__.__database_exists(client, database_name):
            return self.__class__.__get_database(client, database_name)
        else:
            return False

    def database_exists(self,
        database_name: str = None
    ) -> bool:
        client = self.client
        if self.__class__.__database_exists(client, database_name):
            return True
        else:
            return False


    def create_database(self,
        database_name: str = None,
        drop: bool = False
    ) -> bool:
        client = self.client
        if self.__class__.__database_exists(client, database_name):
            if drop:
                self.__class__.logger.warning(f"drop flag enabled, deleting and recreating database")
                self.__class__.__drop_database(client, database_name)
                self.__class__.__create_database(client, database_name)
                if self.__class__.__database_exists(client, database_name):
                    return True
                else:
                    return False
            else:
                self.__class__.logger.warning(f"drop flag is disabled and database exists, not deleting existing database")
                self.__class__.logger.warning(f"please set the [--drop-existing] flag if so desired")
                return False

        else:
            self.__class__.__create_database(client, database_name)


    def drop_database(self,
        database_name: str = None
    ) -> bool:
        client = self.client
        if self.__class__.__database_exists(client, database_name):
            self.__class__.__drop_database(client, database_name)
            if database_name not in self.__class__.__list_databases(client):
                return True
            else:
                return False


    def create_collection(self,
        database_name: str = None,
        collection_name: str = None,
        custom_schema: dict = None,
        use_schema: bool = False,
        drop: bool = False,
        create_if_not_exist: bool = False,
        debug: bool = True,
    ) -> bool:
        client = self.client
        if use_schema: #using a schema
            if custom_schema is not None: # set schema based on provided dict
                schema = custom_schema
        if self.__class__.__collection_exists(client=client, database_name=database_name, collection_name=collection_name):
            if drop:
                self.__class__.logger.warning(f"drop flag enabled, deleting and recreating collection {collection_name} in database {database_name}")
                if self.__drop_collection(client=client, database_name=database_name, collection_name=collection_name):
                    if self.__class__.__create_collection(
                        client=client,
                        database_name=database_name,
                        collection_name=collection_name,
                        custom_schema=None,
                        use_schema=True,
                        create_if_not_exist=create_if_not_exist,
                        debug=debug
                    ):
                        return True
                    else:
                        return False
            else:
                self.__class__.logger.warning(
                    f"drop flag disabled and {collection_name} exists in database {database_name}"
                )
                self.__class__.logger.warning(
                    f"if you wish to remove this collection please provide the [--drop-existing] flag on the command line"
                )
                return False
        else:
            if self.__class__.__create_collection(
                client=client,
                database_name=database_name,
                collection_name=collection_name,
                custom_schema=None,
                use_schema=True,
                create_if_not_exist=create_if_not_exist,
                debug=debug
            ):
                return True
            else:
                return False

    def drop_collection(self,
        database_name: str = None,
        collection_name: str = None,
    ) -> bool:
        client = self.client
        if self.__class__.__collection_exists(
            client=client,
            database_name=database_name,
            collection_name=collection_name,
        ):
            if self.__class__.__drop_collection(
                client=client,
                database_name=database_name,
                collection_name=collection_name
            ):
                return True
            else:
                return False
        else:
            self.__class__.logger.warning(f"the collection {collection_name} in database {database_name} does not exit to drop")
            return True

    def get_schema(
        self,
        database_name: str = None,
        collection_name: str = None,
        pretty_print: bool = False
    ) -> dict:
        if database_name is None:
            database_name = 'static'
        #print(self.DEFAULT_MONGO_STRUCTURE)
        #db_key = self.DEFAULT_MONGO_STRUCTURE.get(database_name, None) #database
        #collection_key = db_key.get(collection_name, None)
        #print(f"db key: {db_key} collection_key: {collection_key}")
        if collection_name is not None:  # get the schema template to compile
            try:
                schema_template = self.__class__.__get_schema_template(schema_template_name=collection_name)
                schema = self.__class__.__compile_schema_template(schema_template)
                if pretty_print:
                    print(json.dumps(schema, indent=2))

                return schema
            except AttributeError as error_message:
                print(f"the requested template {collection_name} does not exist in [{self.SUPPORTED_STATIC_SCHEMAS}]")
                return None
        else:  # if no such template exists, fail
            print("on return none branch")
            return None