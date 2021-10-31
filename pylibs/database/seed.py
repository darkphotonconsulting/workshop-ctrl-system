""" Not used
"""
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
from pylibs.database.schemas import StaticSchemas, SchemaFactory
from pylibs.constants.constants import FILE_MAP, MONGO_STRUCTURE
#from backend.config import BaseConfig
# replace base config 

from pylibs.config.configuration import (
    ConfigLoader, 
    Configuration
)
from pylibs.logging.loginator import Loginator
from pylibs.pi import PiInfo
from pylibs.relay import RelayInfo
class DataSeedEngine():
    """DataSeedEngine [summary]

    Attributes: 

    

    Returns:
        [type]: [description]
    """
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
        config: Configuration = None
    ) -> MongoClient:
        """__initialize_mongo_connection [summary]

        [extended_summary]

        Args:
            mongo_host (str): [description]
            mongo_port (int): [description]
            mongo_username (str): [description]
            mongo_password (str): [description]

        Returns:
            MongoClient: [description]
        """
        # config = BaseConfig(mongo_host=mongo_host,
        #                     mongo_port=mongo_port,
        #                     mongo_username=mongo_username,
        #                     mongo_password=mongo_password)
        return MongoClient(config.mongo_connection_string())

    @classmethod 
    def __get_server_info(cls,
        client: MongoClient = None
    ) -> dict:
        """__get_server_info [summary]

        [extended_summary]

        Args:
            client (MongoClient, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        return client.server_info()
    
    @classmethod    
    def __pretty_print_server_info(cls,
        client: MongoClient = None,
    ) -> None:
        """__pretty_print_server_info [summary]

        [extended_summary]

        Args:
            client (MongoClient, optional): [description]. Defaults to None.
        """
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
        """__piinfo_system [summary]

        [extended_summary]

        Returns:
            dict: [description]
        """
        return PiInfo().system

    @classmethod
    def __piinfo_gpios(cls,
    ) -> list:
        """__piinfo_gpios [summary]

        [extended_summary]

        Returns:
            list: [description]
        """
        return PiInfo().gpios

    @classmethod
    def __relaysinfo(cls,
    ) -> list:
        """__relaysinfo [summary]

        [extended_summary]

        Returns:
            list: [description]
        """
        return RelayInfo().data
    
    @classmethod
    def __load_items_from_file(cls,
        items_file_path: str = None
    ) -> Union[list, dict]:
        """__load_items_from_file [summary]

        [extended_summary]

        Args:
            items_file_path (str, optional): [description]. Defaults to None.

        Returns:
            Iterable[Union[list, dict]]: [description]
        """
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
        """_insert_item [summary]

        [extended_summary]

        Args:
            client (MongoClient, optional): [description]. Defaults to None.
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.
            item (dict, optional): [description]. Defaults to None.
        """
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
        """_insert_items [summary]

        [extended_summary]

        Args:
            client (MongoClient, optional): [description]. Defaults to None.
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.
            items (list, optional): [description]. Defaults to None.
        """
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
        """_insert_each_item [summary]

        [extended_summary]

        Args:
            client (MongoClient, optional): [description]. Defaults to None.
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.
            items (list, optional): [description]. Defaults to None.
        """
        db = client[database_name]
        collection = db.get_collection(name=collection_name)
        for item in items:
            collection.insert_one(
                item
            )
        
    def __init__(self, 
        config: Configuration = None
    ) -> None:
        """__init__ Initialize a DataSeedEngine

        Args:
            config (Configuration): a Configuration object with standard database keys

            
        """
        self.client = self.__class__.__initialize_mongo_connection(
            config)
        self.server_info = self.client.server_info()
        self.server_version = self.server_info['version']
        #initialize parameters on self, will be updated
        self.database = ""

    def print_server_info(self,
    ) -> None:
        """print_server_info pretty print the server_info object
        """
        self.__class__.__pretty_print_server_info(
            client=self.client
        )

    def insert_item(self,
        database_name: str = None,
        collection_name: str = None,
        item: dict = None
    ):
        """insert_item [summary]

        [extended_summary]

        Args:
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.
            item (dict, optional): [description]. Defaults to None.
        """
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
        """insert_items [summary]

        [extended_summary]

        Args:
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.
            items (list, optional): [description]. Defaults to None.
        """
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
        """insert_each_item [summary]

        [extended_summary]

        Args:
            database_name (str, optional): [description]. Defaults to None.
            collection_name (str, optional): [description]. Defaults to None.
            items (list, optional): [description]. Defaults to None.
        """
        self.__class__._insert_each_item(
            client=self.client,
            database_name=database_name,
            collection_name=collection_name,
            items=items
        )
    