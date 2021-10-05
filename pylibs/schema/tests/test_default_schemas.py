import os
import sys
import json
import logging
from copy import copy
import shutil
#get home
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-3])
sys.path.append(libs)



import pytest
#import module
import pylibs.schema.default_schemas

#import classes
from pylibs.schema.default_schemas import (StaticSchemas, DynamicSchemas,
                                           SchemaFactory)

from pylibs.coders.decode import SchemaTemplateDecoder
from pylibs.coders.encode import SchemaTemplateEncoder


@pytest.fixture
def schema_template_file():
    with open("pylibs/schema/tests/serialized-schema.json", "r") as file:
        return file.read()

@pytest.fixture
def static_schema():
    return StaticSchemas()

@pytest.fixture
def dynamic_schema():
    return DynamicSchemas()

@pytest.fixture
def schema_factory():
    return SchemaFactory()

@pytest.fixture
def validator(schema_factory):
    return schema_factory.validator

@pytest.fixture
def schema_template(schema_factory):
    return schema_factory.get_default_schema_template(
        schema_type="system",
        schema_template_name="gpios"
    )

@pytest.fixture
def schema(static_schema):
    return static_schema.gpios

@pytest.fixture
def simple_schema_template():
    return {"foo": int}

@pytest.fixture
def complex_schema_template():
    return {
        "movieData": {
            "title": str,
            "director": str,
            "actors": list,
            "details": {
                "earnings": int,
                "ratings": {
                    "thumbs_up": int,
                    "thumbs_down": int
                }
            }
        }
    }

def test_static_schema_types(static_schema):
    """[summary]

    Args:
        static_schema ([type]): [description]

    Returns:
        [type]: [description]
    """
    assert isinstance(static_schema.system, dict)
    assert isinstance(static_schema.gpios, dict)
    assert isinstance(static_schema.relays, dict)
    return static_schema


def test_dymamic_schema_types(dynamic_schema):
    """[summary]

    Args:
        dynamic_schema ([type]): [description]

    Returns:
        [type]: [description]
    """
    assert isinstance(dynamic_schema.system_memory_stats, dict)
    assert isinstance(dynamic_schema.system_cpu_stats, dict)
    assert isinstance(dynamic_schema.system_net_stats, dict)
    return static_schema

def test_schema_factory(schema_factory, simple_schema_template, complex_schema_template):
    """[summary]

    Args:
        schema_factory ([type]): [description]
        simple_schema_template ([type]): [description]
        complex_schema_template ([type]): [description]
    """
    assert isinstance(schema_factory, SchemaFactory)
    assert isinstance(schema_factory.validator, dict)
    assert "$jsonSchema" in schema_factory.validator
    assert isinstance(
        schema_factory.generate_schema(simple_schema_template),
        dict
    )
    assert isinstance(
        schema_factory.generate_schema(complex_schema_template),
        dict
    )
    assert isinstance(
        schema_factory.list_default_schemas(), 
        list
    )
    assert isinstance(
        schema_factory.compile_default_schema_template(
            schema_type='static', 
            schema_template_name='system'
        ),
        dict
    )

def test_encoding_schema_template(schema_template):
    """[summary]

    Args:
        schema_template ([type]): [description]
    """
    assert isinstance(
        json.dumps(
            schema_template, 
            indent=2, 
            cls=SchemaTemplateEncoder
        ),
        str
    )

def test_decoding_schema_template(schema_template_file):
    """[summary]

    Args:
        schema_template_file ([type]): [description]
    """
    #encoded_schema_template = json.dumps(schema_template, cls=SchemaTemplateEncoder)
    assert isinstance(
        json.loads(
            schema_template_file, 
            cls=SchemaTemplateDecoder
        ), 
        dict
    )
    print(f"directory: {os.getcwd()}")
    #template = json.loads(file.read(), cls=SchemaTemplateDecoder)
    #assert "model" in template

# this test uses recursion...
def test_schema_recursion(schema_factory, validator, schema):
    """[summary]

    Args:
        schema_factory ([type]): [description]
        validator ([type]): [description]
        schema ([type]): [description]
    """
    assert isinstance(
        schema_factory.__class__._recurse_schema_keys(validator,schema),
        dict
    )
    assert "bsonType" in schema_factory.__class__._bson_typemap(key='foo',
                                                                value=str)
    assert "bsonType" in schema_factory.__class__._bson_typemap(key='foo',
                                                                value=int)
    assert "bsonType" in schema_factory.__class__._bson_typemap(key='foo',
                                                                value=list)
    assert "bsonType" in schema_factory.__class__._bson_typemap(key='foo',
                                                                value=bool)
    assert schema_factory.__class__._bson_typemap(
        key='foo', value=str)['bsonType'] == "string"
    assert schema_factory.__class__._bson_typemap(
        key='foo', value=int)['bsonType'] == "int"
    assert schema_factory.__class__._bson_typemap(
        key='foo', value=list)['bsonType'] == "array"
    assert schema_factory.__class__._bson_typemap(
        key='foo', value=bool)['bsonType'] == "boolean"
