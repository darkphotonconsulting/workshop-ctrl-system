"""Common Database classes and methods
"""
from abc import ABCMeta
import os
import sys
import json
import logging
from copy import copy
from typing import (
    Tuple,
    Union,
    Optional,
    Type
)
import typing
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])
sys.path.append(libs)

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.errors import OperationFailure, ConnectionFailure
from pylibs.logging.loginator import Loginator
from pylibs.config.configuration import (
    Configuration
)

# from pylibs.coders.decode import SchemaTemplateDecoder
# from pylibs.coders.encode import SchemaTemplateEncoder
from pylibs.constants.constants import (
    #FILE_MAP,
    MONGO_STRUCTURE
)

MODULE = True
__all__ = ['Mongo']
class Mongo(object, metaclass=ABCMeta):
    """Mongo Base Mongo Database class

    - easily configured by a `Configuration` class object
    - supports commonly used MongoDB `CRUD` operations
    - idempotent operations, run, and re-run infinitely



    Class Attributes:
      logger (`logging.Logger`) - a logger object configured with a Loginator formatter for this class 
      
      SUPPORTED_STRUCTURE  (`dict`) - describes the supported MongoDB layout as a python dict
      
      SUPPORTED_DATABASES (`list`) - a list of supported databases
      
      SUPPORTED_COLLECTION_ALIASES (`list`) - a list of supported collection aliases
      
      SUPPORTED_COLLECTION_NAMES (`list`) - a list of supported collection names
      
    Attributes:
    
        client (`MongoClient`) - A mongo client configured by the `Configuration` object passed to this class on __init__
        
        server_info (`dict`) - the server info object returned by a MongoDB server
        
        server_version (`str`) - the MongoDB server version for the connected client
        
        server_git_version (`str`) - the mongoDB git version for the connected client
        
        database_name (`str`) - the default database_name passed to __init__
        
        collection_name (`str`) - the default collection_name passed to __init__
        
        additional_args (`dict`) - **kwargs
        
        error (`bool`) - if any critical operation fails during __init__, the object is created with an error key set to True
    """


    logger = Loginator(
        logger=logging.getLogger('Mongo')
    ).logger


    SUPPORTED_STRUCTURE = MONGO_STRUCTURE
    SUPPORTED_DATABASES = list(MONGO_STRUCTURE.keys())
    SUPPORTED_COLLECTION_ALIASES = [list(MONGO_STRUCTURE[database].keys()) for database in SUPPORTED_DATABASES]
    SUPPORTED_COLLECTION_NAMES = [list(MONGO_STRUCTURE[database].values()) for database in SUPPORTED_DATABASES]

    def __init__(self,
            config: Configuration = None,
            database_name: str = None,
            collection_name: str = None,
            **kwargs,
        ) -> None:
        """__init__ Create a Mongo object

        Mongo objects provide general methods for CRUD operations on databases, collections and items within MongoDB

        Args:
            config (`Configuration`, optional): Provide a `Configuration` object with the bare minimum database key present. Defaults to None.
            
            database_name (`str`, optional): A default database to operate on, if provided, CRUD operations within the object context are performed on this database. Defaults to None.
            
            collection_name (`str`, optional): a default collection to operate on, if provided, CRUD operations within the object context are performed on this collection. Defaults to None.

            **kwargs (`dict`, optional): a set of arguments loaded as additional_args (currently unused)
        """

        self.client = self.__class__.__initialize_mongo_connection(
            config)
        if self.__class__.__validate_mongo_connection(
            client=self.client,
        ):
            self.server_info = self.client.server_info()
            self.server_version = self.server_info.get('version')
            self.server_git_version = self.server_info.get('gitVersion')
            self.js_engine = self.server_info.get('javascriptEngine')
            self.database_name =  database_name
            self.collection_name = collection_name
            self.additional_args = kwargs
            self.error = False
        else: self.error = True



    # utility methods
    def supported_mongo_structure(self,
    ) -> dict:
        """supported_mongo_structure return suported MongoDB structure as dict

        Returns:
        
            `dict`: suported MongoDB structure
        """
        return self.__class__.__show_supported_structure()

    def supported_database_names(self,
    ) -> list:
        """supported_database_names suported MongoDB database names

        Returns:
        
            `list`: list of supported database names
        """
        return self.__class__.__show_supported_database_names()

    def supported_collection_aliases(self,
    ) -> list:
        """supported_collection_aliases supported collection aliases

        Returns:
        
            `list`: a list of lists of supported collection names, 1 list for each supported database name
        """
        return self.__class__.__show_supported_collection_aliases()

    def validate_connection(self,
    ) -> bool:
        """validate_connection validates the MongoDB connection

        Returns:
        
            bool: `True` if valid, `False` if not
        """
        return self.__class__.__validate_mongo_connection(
            client=self.client
        )

    # MongoDB - database methods

    def database_exists(self,
        database_name: str = None
    ) -> bool:
        """database_exists check if a database exists in MongoDB

        Args:
        
            database_name (`str`, optional): the database name. Defaults to None.

        Returns:
        
            bool: `True` if exists, `False` if not
        """
        if self.database_name is not None: # use class default
            return self.__class__.__database_exists(
                client=self.client,
                database_name=self.database_name
            )
        elif database_name is not None: # use provided arg
            return self.__class__.__database_exists(
                client=self.client,
                database_name=database_name
            )
        else: return False # no proper args provided


    def get_database(self,
        database_name: str = None
    ) -> Union[Database,bool]:
        """get_database get a pymongo reference to a database

        Args:
        
            database_name (str, optional): the database name. Defaults to None.

        Returns:
        
            Union[Database,bool]: pymongo.database.Database if exists, False otherwise
        """
        if database_name is not None:
            return self.__class__.__get_database(
                client=self.client,
                database_name=database_name
            )
        elif self.database_name is not None:
            return self.__class__.__get_database(
                client=self.client,
                database_name=self.database_name
            )
        else: return False

    def list_databases(self,
        key: str = None,
    ) -> list:
        """list_databases list all databases visible to client

        Args:
        
            key (str, optional): If set, list contains only value of `key` instead of each database object. Defaults to None.

        Returns:
        
            list: list of database objects
        """
        return self.__class__.__list_databases(
            client=self.client,
            key=key
        )

    def create_database(self,
        database_name: str = None,
    ) -> bool:
        """create_database create a MongoDB database

        Args:
        
            database_name (str, optional): The database name. Defaults to None.

        Returns:
        
            bool: True if created, False otherwise
        """
        if self.database_name is not None:
            return self.__class__.__create_database(
                client=self.client,
                database_name=self.database_name
            )
        elif database_name is not None:
            return self.__class__.__create_database(
                client=self.client,
                database_name=database_name
            )
        else: return False

    def drop_database(self,
        database_name: str = None,
    ) -> bool:
        """drop_database Drop MongoDB database

        Args:
        
            database_name (str, optional): The database name. Defaults to None.

        Returns:
        
            bool: True if dropped, False otherwise
        """
        if self.database_name is not None:
            return self.__class__.__drop_database(
                client=self.client,
                database_name=self.database_name,
            )
        elif database_name is not None:
            return self.__class__.__drop_database(
                client=self.client,
                database_name=database_name,
            )
        else: return False



    # MongoDB - collection methods

    def collection_exists(self,
        database_name: str = None,
        collection_name: str = None,
    ) -> bool:
        """collection_exists Check if a MongoDB collection exists


        Args:
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.

        Returns:
            bool: [description]
        """
        if self.database_name is not None and self.collection_name is not None:
            return self.__class__.__collection_exists(
                client=self.client,
                database_name=database_name,
                collection_name=self.collection_name
            )
        if database_name is not None and collection_name is not None:
            return self.__class__.__collection_exists(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name
            )
        else: return False

    def get_collection(
        self,
        database_name: str = None,
        collection_name: str = None,
    ) -> Union[Collection, bool]:
        """get_collection return reference to pymongo.collection.Collection object



        Args:
        
            database_name (`str`, optional): The database name. Defaults to None.
            
            collection_name (`str`, optional): The collection name. Defaults to None.

        Returns:
            Union[Collection, bool]: [description]
        """
        if self.database_name is not None and self.collection_name is not None:
            return self.__class__.__get_collection(
                client=self.client,
                database_name=self.database_name,
                collection_name=self.collection_name)
        if database_name is not None and collection_name is not None:
            return self.__class__.__get_collection(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name)
        else:
            return False

    def list_collections(
        self,
        database_name: str = None,
        key: str = None,
    ) -> list:
        """list_collections list MongoDB collections visible to client

        Args:
        
            database_name (`str`, optional): The database name. Defaults to None.
            
            key (`str`, optional): If set, list contains only value of `key` instead of each collection object. Defaults to None.

        Returns:
        
            list: list of collections, or list of collections keys values
        """
        if self.database_name is not None:
            return self.__class__.__list_collections(
                client=self.client,
                database_name=self.database_name,
                key=key
            )
        elif database_name is not None:
            return self.__class__.__list_collections(
                client=self.client,
                database_name=database_name,
                key=key
            )



    def create_collection(self,
        database_name: str = None,
        collection_name: str = None,
        use_schema: bool = None,
        schema: dict = None,
        create_if_not_exist: bool = None,
        debug: bool = None,
    ) -> bool:
        """create_collection create a MongoDB collection



        Args:
        
            database_name (`str`, optional): The database name. Defaults to None.
            
            collection_name (`str`, optional): The collection name. Defaults to None.
            
            use_schema (`bool`, optional): If True, collections are created with validation schemas. Defaults to None.
            
            schema (`dict`, optional): A "compiled" validation schema. Defaults to None.
            
            create_if_not_exist (`bool`, optional): If database does not exist, create it. Defaults to None.
            
            debug (`bool`, optional): Print addtional messages to log. Defaults to None.

        Returns:
        
            bool: [description]
        """
        if self.database_name is not None and self.collection_name is not None:
            return self.__class__.__create_collection(
                client=self.client,
                database_name=self.database_name,
                collection_name=self.collection_name,
                use_schema=use_schema,
                schema=schema,
                create_if_not_exist=create_if_not_exist,
                debug=debug
            )
        elif database_name is not None and collection_name is not None:
            return self.__class__.__create_collection(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name,
                use_schema=use_schema,
                schema=schema,
                create_if_not_exist=create_if_not_exist,
                debug=debug
            )
        else: return False

    def drop_collection(self,
        database_name: str = None,
        collection_name: str = None,
        wipe_items: bool = None,
    ) -> bool:
        """drop_collection drop a mongodb collection

        Args:
        
            database_name (str, optional): The database name. Defaults to None.
            
            collection_name (str, optional): The collection name. Defaults to None.
            
            wipe_items (bool, optional): drop collection if items exist in it. Defaults to None.
            

        Returns:
        
            bool: True if successful, false if not
        """
        if database_name is not None and collection_name is not None:
            if self.items_exist(database_name=database_name, collection_name=collection_name):
                if wipe_items:
                    return self.__class__.__drop_collection(
                        client=self.client,
                        database_name=database_name,
                        collection_name=collection_name)
                else:
                    #print('this collection contains and `wipe_items` is False')
                    return False
            else:
                return self.__class__.__drop_collection(
                    client=self.client,
                    database_name=database_name,
                    collection_name=collection_name
                )
        else: return False

    def items_exist(self,
        database_name: str = None,
        collection_name: str = None,
    ) -> bool:
        """items_exist check if items exist in a collection



        Args:
        
            database_name (str, optional): The database name. Defaults to None.
            
            collection_name (str, optional): The collection name. Defaults to None.
            

        Returns:
        
            bool: True if items exist, False if not
        """
        if database_name is not None and collection_name is not None:
            if self.__class__.__collection_exists(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name
            ):
                return True if len(self.__class__.__list_items(
                    client=self.client,
                    database_name=database_name,
                    collection_name=collection_name
                )) > 0 else False
            else: return False
            #else: return False
        else: return False


    def list_items(self,
        database_name: str = None,
        collection_name: str = None,
    ) -> Union[list,bool]:
        """list_items list items in collection



        Args:

            database_name (str, optional): The database name. Defaults to None.
            
            collection_name (str, optional): The collection name. Defaults to None..

        Returns:
            Union[list,bool]: list of items, or False if errored
        """
        if database_name is not None and collection_name is not None:
            # if self.__class__.__database_exists(
            #     client=self.client,
            #     database_name=database_name
            # ):
            if self.__class__.__collection_exists(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name
            ):
                return self.__class__.__list_items(
                    client=self.client,
                    database_name=database_name,
                    collection_name=collection_name
                )
            else: return False
            #     else: return False
            # else: return False
        #else: return False


    def get_items(self,
        database_name: str = None,
        collection_name: str = None,
        as_list: bool = None,
    ) -> Union[Cursor,bool]:
        """get_items get reference to items Cursor object



        Args:

            database_name (str, optional): The database name. Defaults to None.
            
            collection_name (str, optional): The collection name. Defaults to None.
            
            as_list (bool, optional): Return a list and not the bare cursor object. Defaults to None.

        Returns:

            Union[Cursor,bool]: the items, or False if errored
        """

        if self.__class__.__collection_exists(
            client=self.client,
            database_name=database_name,
            collection_name=collection_name
        ):
            return [item for item in self.__class__.__get_items(
                    client=self.client,
                    database_name=database_name,
                    collection_name=collection_name
                )] if as_list else self.__class__.__get_items(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name
            )
        else: return False



    def insert_item(self,
        database_name: str = None,
        collection_name: str = None,
        data: dict = None,
    ) -> bool:
        """insert_item insert a record into a mongodb collection

        Args:
        
            database_name (str, optional): The database name. Defaults to None.
            
            collection_name (str, optional): The collection name. Defaults to None.
            
            data (dict, optional): mongodb record. Defaults to None.

        Returns:
        
            bool: True if an object ID is returned from the insert operation, False if not
        """
        if database_name is not None and collection_name is not None:
            if self.__class__.__collection_exists(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name
            ):
                self.__class__.__insert_item(
                    client=self.client,
                    database_name=database_name,
                    collection_name=collection_name,
                    data=data
                )
            else: return False
        else: return False


    def insert_items(self,
        database_name: str = None,
        collection_name: str = None,
        data: list = None,
    ) -> bool:
        if database_name is not None and collection_name is not None:
            if self.__class__.__collection_exists(
                client=self.client,
                database_name=database_name,
                collection_name=collection_name
            ):
                self.__class__.__insert_items(
                    client=self.client,
                    database_name=database_name,
                    collection_name=collection_name,
                    data=data
                )
            else: return False
        else: return False


    # * class methods

    # Mongo connection methods

    @classmethod
    def __initialize_mongo_connection(cls,
        config: Configuration = None
    ) -> MongoClient:
        return MongoClient(
            host=config.mongo_connection_string()
        )


    @classmethod
    def __validate_mongo_connection(cls,
        client: MongoClient = None
    ) -> bool:
        if client is not None:
            try:
                client.admin.command('ismaster')
            except OperationFailure as e:
                return False
            except ConnectionFailure as e:
                return False
        else:
            return False

        return True

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
    def __get_database(cls,
        client: MongoClient,
        database_name: str
    ) -> Database:

        if cls.__database_exists(
                client=client,
                database_name=database_name,
        ):  #database exists
            cls.logger.info(f"getting database [{database_name}]")
            return client[database_name]
        else:  #database does not exist
            cls.logger.error(
                f"can't get database [{database_name}] because it does not exist"
            )
            return False


    @classmethod
    def __create_database(cls,
        client: MongoClient,
        database_name: str
    ) -> bool:

        dbs = [db['name'] for db in client.list_databases()]
        if database_name not in dbs:
            cls.logger.info(
                f"creating the requested database [{database_name}]")
            db = client[database_name]
            # creates a placeholder collection to ensure the db is saved in Mongo
            db.create_collection(name='__pymongo__',
                                 validator={
                                     "$jsonSchema": {
                                         "bsonType": "object",
                                         "properties": {
                                             "foo": {
                                                 "bsonType": "string"
                                             }
                                         }
                                     }
                                 })
        else:
            cls.logger.warning(
                f"the database [{database_name}] already exists")
            return False
        # naïve verification the DB was created
        if database_name in [db['name'] for db in client.list_databases()]:
            cls.logger.info(
                f"the database [{database_name}] was successfully created")
            return True
        else:
            cls.logger.error(
                f"the database [{database_name}] was not successfully created")
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

    # * collection methods
    @classmethod
    def __collection_exists(cls, client: MongoClient, database_name: str,
        collection_name: str
    ) -> bool:

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

    @classmethod
    def __list_collections(cls,
        client: MongoClient,
        database_name: str,
        key: str = None
    ) -> list:

        db = client[database_name]
        collections = [collection for collection in db.list_collections()]
        if key is None:
            return collections
        else:
            collections = [
                collection.get(key, None) for collection in collections
            ]
            if None in collections:
                return f"the key [{key}] does not exist in a pymongo collection object"
            else:
                return collections

    @classmethod
    def __get_collection(
        cls,
        client: MongoClient,
        database_name: str = None,
        collection_name: str = None,
    ) -> Collection:

        if cls.__database_exists(
                client=client,
                database_name=database_name):  #database exists
            db = cls.__get_database(client=client, database_name=database_name)
            if cls.__collection_exists(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name):  #collection exists
                return db.get_collection(name=collection_name)
            else:  # collection does not exist
                cls.logger.error(
                    f"can't get collection [{collection_name}] in database [{database_name}], the collection does not exist"
                )
                return False
        else:  # database does not exist
            cls.logger.error(
                f"can't get collection [{collection_name}] in database [{database_name}], the database does not exist"
            )
            return False

    @classmethod
    def __create_collection(cls,
        client: MongoClient,
        database_name: str = None,
        collection_name: str = None,
        schema: dict = None,
        use_schema: bool = False,
        create_if_not_exist: bool = False,
        debug: bool = False,
    ) -> bool:


        if cls.__database_exists(client, database_name=database_name): # get db reference, it exists
            db = cls.__get_database(
                client,
                database_name=database_name
            )
            if cls.__collection_exists(client, database_name=database_name, collection_name=collection_name): # the collection already exists
                cls.logger.warning(f"The collection [{collection_name}] already exists in [{database_name}]")
                return False
            else: # the collection does not exist
                if use_schema: # using a schema
                    cls.logger.debug(f"Using validation schemas") if debug else None
                    if schema is None: # no schema provided, use default schema
                        cls.logger.debug(f"please provide a dictionary object as a schema") if debug else None
                        return False
                    else: # use provided schema
                        schema = schema

                # create collection
                if use_schema: #create collection with attached schema
                    cls.logger.info(f"Creating collection [{collection_name}] in database [{database_name}] with schema [{schema}]")
                    db.create_collection(
                        name=collection_name,
                        validator=schema
                    )
                else: # create a collection with no schema
                    cls.logger.info(f"Creating collection [{collection_name}] in database [{database_name}]")
                    db.create_collection(
                        name=collection_name
                    )

                if cls.__collection_exists(client, database_name=database_name, collection_name=collection_name): # collection created successfully
                    cls.logger.info(f"succesfully created collection [{collection_name}] in database [{database_name}]")
                    return True
                else: #collection creation failed
                    cls.logger.error(f"failed to create collection [{collection_name}] in database [{database_name}]")
                    return False
        else:
            ### experimental recursive call,
            if create_if_not_exist:
                cls.logger.info(
                    f"`create_if_not_exist` was enabled, the database [{database_name}] will be created as a dependency of creating the collection [{collection_name}]"
                )
                if cls.__create_database(client=client,database_name=database_name):
                    # use recursion?
                    cls.logger.info(f"successfully created database dependency [{database_name}] for collection [{collection_name}], calling myself")
                    cls.__create_collection(
                        client=client,
                        database_name=database_name,
                        collection_name=collection_name,
                        schema=schema,
                        use_schema=use_schema,
                        create_if_not_exist=False
                    )
                    return True
                else:
                    cls.logger.error(f"failed to create database depencency [{database_name}] for collection [{collection_name}] ..")
                    return False
                    #print()
            else:
                cls.logger.warning(f"the database [{database_name}] does not yet exist, you should create it before creataing a collection in it")
                cls.logger.info(f"if you wish to create the database automatically, set create_if_not_exist to True")
                return False


    @classmethod
    def __drop_collection(
        cls,
        client: MongoClient,
        database_name: str,
        collection_name: str,
        wipe_items: bool = True,
    ) -> bool:

        db = client[database_name]
        collections = [collection for collection in db.list_collections()]
        if collection_name in [
                collection['name'] for collection in collections
        ]:
            if len(
                    cls.__list_items(client=client,
                                     database_name=database_name,
                                     collection_name=collection_name
                    )
            ) > 0:  # items in collection
                cls.logger.warning(
                    "This collection contains data that will be wiped if dropped"
                )
                if wipe_items:
                    db[collection_name].drop()
                else:
                    cls.logger.warning(
                        "Not dropping collection with data as --wipe-existing-data flag was not passed"
                    )
                    return False
            else: # no items, clear to drop
                db[collection_name].drop()
            if collection_name not in [
                    collection['name'] for collection in db.list_collections()
            ]:
                cls.logger.info(
                    f"successfully dropped collection {collection_name} in database {database_name}"
                )
                return True
            else:
                cls.logger.error(
                    f"failed to drop collection {collection_name} in database {database_name}"
                )
                return False
        else:
            cls.logger.warning(
                f"the collection {collection_name} does not exist in the database {database_name}"
            )
            return True

    @classmethod
    def __list_items(
        cls,
        client: MongoClient,
        database_name: str = None,
        collection_name: str = None,
    ) -> list:
        if cls.__database_exists(client=client, database_name=database_name):
            if cls.__collection_exists(client=client,
                                       database_name=database_name,
                                       collection_name=collection_name):
                db = cls.__get_database(client=client,
                                        database_name=database_name)
                collection = db.get_collection(name=collection_name)
                items = [i for i in collection.find({})]
                return items

    @classmethod
    def __get_items(cls,
        client: MongoClient = None,
        database_name: str = None,
        collection_name: str = None,
    ) -> Union[Cursor, bool]:
        if cls.__database_exists(
            client=client,
            database_name=database_name
        ):
            if cls.__collection_exists(
                client=client,
                database_name=database_name,
                collection_name=collection_name,
            ):
                collection = cls.__get_collection(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name
                )
                return collection.find({})
            else: return False
        else: return False

    @classmethod
    def __insert_item(cls,
        client: MongoClient = None,
        database_name: str = None,
        collection_name: str = None,
        data: dict = None,
    ) -> bool:
        if cls.__database_exists(client=client, database_name=database_name):
            if cls.__collection_exists(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name,
            ):
                collection = cls.__get_collection(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name)
                try:
                    cls.logger.info(f"inserting {data} into {database_name} {collection_name}")
                    insert = collection.insert_one(
                        data
                    )
                    if isinstance(insert.inserted_id, ObjectId):
                        cls.logger.info(
                            f"successfully inserted {data} records")
                        return True
                    else:
                        cls.logger.warning(
                            f"failed to insert {data} records")
                        return False
                except:
                    cls.logger.warning(f"failed to insert {data}")
                    return False
            else:
                cls.logger.warning(f"failed to insert {data} , collection {collection_name} does not exit")
                return False
        else:
            cls.logger.warning(f"failed to insert {len(data)} records, database {database_name} does not exist")
            return False

    @classmethod
    def __insert_items(
        cls,
        client: MongoClient = None,
        database_name: str = None,
        collection_name: str = None,
        data: list = None,
    ) -> bool:
        if cls.__database_exists(client=client, database_name=database_name):
            if cls.__collection_exists(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name,
            ):
                collection = cls.__get_collection(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name)
                try:
                    cls.logger.info(f"inserting {len(data)} records into {database_name} {collection_name}")
                    items = collection.insert_many(data)
                    if isinstance(items.inserted_ids, list):
                        ## placeholder
                        if ObjectId in [type(item) for item in items.inserted_ids]:
                            cls.logger.info(f"successfully inserted {len(data)} records")
                            return True
                        else:
                            cls.logger.warning(f"failed to insert {len(data)} records")
                            return False
                except:
                    cls.logger.warning(f"failed to insert {len(data)} records")
                    return False
            else:
                cls.logger.warning(f"failed to insert {len(data)} records, the collection {collection_name} does not exist")
                return False
        else:
            cls.logger.warning(f"failed to insert {len(data)} records, the database {database_name} does not exist")
            return False


    @classmethod
    def __show_supported_structure(cls,
    ) -> dict:
        return cls.SUPPORTED_STRUCTURE

    @classmethod
    def __show_supported_database_names(cls,
    ) -> list:
        return cls.SUPPORTED_DATABASES

    @classmethod
    def __show_supported_collection_aliases(cls,
    ) -> list:
        return cls.SUPPORTED_COLLECTION_ALIASES