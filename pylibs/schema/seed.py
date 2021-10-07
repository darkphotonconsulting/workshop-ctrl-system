import os
import sys
import json
import logging
from copy import copy
from collections import Iterable
from typing import Union

from pymongo import collection
from pymongo import database

#make my path the root
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
from pylibs.pi import PiInfo
from pylibs.relay import RelayInfo
class DataSeedEngine():
    logger = logging.getLogger('DataSeedEngine')
    loginator = Loginator(logger=logger)
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
        mongo_username: str,
        mongo_password: str
    ) -> MongoClient:
        config = BaseConfig(mongo_host=mongo_host,
                            mongo_port=mongo_port,
                            mongo_username=mongo_username,
                            mongo_password=mongo_password)
        return MongoClient(config.mongo_connect_string)

    @classmethod 
    def __get_server_info(cls,
        client: MongoClient = None
    ) -> dict:
        return client.server_info()
    
    @classmethod    
    def __pretty_print_server_info(cls,
        client: MongoClient = None,
    ) -> None:
        print(
            json.dumps(
                cls.__get_server_info(
                    client=client
                ), 
                indent=2
            )
        )

    @classmethod
    def __piinfo_system(cls,
    ) -> dict:
        return PiInfo().system

    @classmethod
    def __piinfo_gpios(cls,
    ) -> list:
        return PiInfo().gpios

    @classmethod
    def __relaysinfo(cls,
    ) -> list:
        return RelayInfo().data
    
    @classmethod
    def __load_items_from_file(cls,
        items_file_path: str = None
    ) -> Iterable[Union[list, dict]]:
        items = []
        if os.path.exists(items_file_path):
            with open(items_file_path, 'r') as file:
                items = json.load(file)
        return items

    @classmethod
    def _insert_item(cls,
        client: MongoClient = None,
        database_name: str = None,
        collection_name: str = None,
        item: dict = None,
    ) -> None:
        db = client[database_name]
        collection = db.get_collection(name=collection_name)
        collection.insert_one(
            item
        )

    @classmethod
    def _insert_items(cls,
        client: MongoClient = None,
        database_name: str = None,
        collection_name: str = None,
        items: list = None,
    ) -> None:
        db = client[database_name]
        collection = db.get_collection(name=collection_name)
        collection.insert_many(
            items
        )

    @classmethod
    def _insert_each_item(cls,
        client: MongoClient = None,
        database_name: str = None,
        collection_name: str = None,
        items: list = None, 
    ) -> None:
        db = client[database_name]
        collection = db.get_collection(name=collection_name)
        for item in items:
            collection.insert_one(
                item
            )
        
    def __init__(self, 
        mongo_host: str, 
        mongo_port: int, 
        mongo_username: str,
        mongo_password: str
    ) -> None:
        self.client = self.__class__.__initialize_mongo_connection(
            mongo_host=mongo_host,
            mongo_port=mongo_port,
            mongo_username=mongo_username,
            mongo_password=mongo_password)
        self.server_info = self.client.server_info()
        self.server_version = self.server_info['version']
        #initialize parameters on self, will be updated
        self.database = ""

    def server_info(self,
    ) -> dict:
        self.__class__.__pretty_print_server_info(
            client=self.client
        )

    def insert_item(self,
        database_name: str = None,
        collection_name: str = None,
        item: dict = None
    ):
        self.__class__._insert_item(
            client=self.client,
            database_name=database_name,
            collection_name=collection_name,
            item=item
        )

    def insert_items(self,
        database_name: str = None,
        collection_name: str = None,
        items: list = None
    ):
        self.__class__._insert_items(
            client=self.client,
            database_name=database_name,
            collection_name=collection_name,
            items=items
        )

    def insert_each_item(self,
        database_name: str = None,
        collection_name: str = None,
        items: list = None
    ):
        self.__class__._insert_each_item(
            client=self.client,
            database_name=database_name,
            collection_name=collection_name,
            items=items
        )
    