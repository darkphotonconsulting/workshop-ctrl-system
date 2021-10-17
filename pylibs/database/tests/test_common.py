import os
import sys
import json
import logging
from copy import copy
import shutil
from pymongo.mongo_client import MongoClient
#get home
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-3])
sys.path.append(libs)

import pytest

#from pylibs.database.default_schemas import StaticSchemas, DynamicSchemas, SchemaFactory
#from pylibs.database.migration import SchemaMigrationEngine
#from config.config_loader import ConfigLoader

# replace BaseConfig
from pylibs.config.configuration import ConfigLoader, Configuration 
from pylibs.database.common import Mongo


@pytest.fixture 
def loader(
):
    loader = ConfigLoader(
        from_file=True,
        config='settings/config.json'   
    )
    loader.add_attributes()
    return loader

@pytest.fixture
def config(
    loader
):
    return Configuration(**loader.database)

@pytest.fixture
def mongo(
    config
):
    return Mongo(config)


def test_server_connection(mongo):
    assert mongo.validate_connection() is True
    
def test_server_info(mongo):
    assert isinstance(mongo.server_info, dict)