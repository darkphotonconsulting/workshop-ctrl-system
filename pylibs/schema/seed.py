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
        admin_user: str,
        admin_password: str
    ) -> MongoClient:
        config = BaseConfig(mongo_host=mongo_host,
                            mongo_port=mongo_port,
                            mongo_username=admin_user,
                            mongo_password=admin_password)
        return MongoClient(config.mongo_connect_string)

    @classmethod
    def __pretty_print_server_info(cls,
        server_info: dict = None
    ) -> None:
        if server_info is not None:
            print(json.dumps(server_info, indent=2))
        else:
            cls.logger.warning(f"the server_info object None? are you connected to mongo?")
            
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
        self.database = ""