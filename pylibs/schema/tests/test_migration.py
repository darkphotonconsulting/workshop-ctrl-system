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

from pylibs.schema.default_schemas import StaticSchemas, DynamicSchemas, SchemaFactory
from pylibs.schema.migration import SchemaMigrationEngine
from config.config_loader import ConfigLoader
from backend.config import BaseConfig


@pytest.fixture
def loader():
    """loader Python fixture which returns a ConfigLoader object
    Returns:
        [ConfigLoader]: A ConfigLoader object
    """
    return ConfigLoader(
        from_file=True,
        config='settings/config.json'
    )

@pytest.fixture
def migration_engine():
    """migration_engine Python fixture which returns a SchemaMigrationEngine object

    Returns:
        [SchemaMigrationEngine]: A SchemaMigrationEngine object
    """
    loader = ConfigLoader(
        from_file=True,
        config='settings/config.json'
    )
    loader.add_attributes()

    return SchemaMigrationEngine(
        **loader.database
    )


def test_loading(loader):
    loader.add_attributes()
    assert isinstance(loader, ConfigLoader)
    
    SchemaMigrationEngine(**loader.database)
    
def test_loader(loader):
    """test_loader test the ConfigLoader was successfully created


    Args:
        loader (@pytest.fixture): [description]
    """
    loader.add_attributes()
    assert isinstance(loader.__getattribute__('database'), dict)
    assert isinstance(loader.__getattribute__('mongo_username'), str)
    assert isinstance(loader.__getattribute__('mongo_port'), int)

def test_connection(migration_engine):
    assert isinstance(migration_engine, SchemaMigrationEngine)
    assert isinstance(migration_engine.client, MongoClient)
    assert isinstance(migration_engine.client.server_info(), dict)
    #assert isinstance(migration_engine.server_info(), dict)

def test_list_databases(migration_engine):
    assert isinstance(migration_engine.list_databases(), list)
    assert 'admin' in migration_engine.list_databases(key='name')

def test_database_crud(migration_engine):
    """test_database_crud test basic database CRUD operations

    - create a database, drop if exists 
    - drop previously created database
    - create database, don't drop if exists 
    - drop the previosuly created database

    Args:
        migration_engine (@pytest.fixture): uses the migration_engine fixture
    """
    assert migration_engine.create_database(
        database_name='pytest',
        drop=True
    ) == True
    assert migration_engine.drop_database(
        database_name='pytest'
    ) == True
    assert migration_engine.create_database(
        database_name='pytest',
        drop=False
    ) == True
    assert migration_engine.drop_database(database_name='pytest') == True

def test_collection_crud(migration_engine):
    """test_collection_crud test basic collections CRUD operations



    Args:
        migration_engine (@pytest.fixture): uses the migration_engine fixture
    """
    assert migration_engine.create_collection(
        database_name='pytest_database',
        collection_name='pytest_collection',
        create_if_not_exist=True,
        use_schema=False,
    ) == True
    assert isinstance(migration_engine.list_collections(
        database_name='pytest_database',
        key='name'
    ), list)
    assert migration_engine.drop_collection(
        database_name='pytest_database',
        collection_name='pytest_collection'
    ) == True
