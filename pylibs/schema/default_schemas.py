import json
import yaml
import csv
import bson
import os
import sys
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
sys.path.append(libs)

from pylibs.logging.loginator import Loginator
from pylibs.coders.encode import SchemaTemplateEncoder
from pylibs.coders.decode import SchemaTemplateDecoder

from copy import copy
from pymongo.database import Database
from mongoengine import (
    Document,
    StringField,
    EmbeddedDocumentField,
    IntField,
    DateTimeField,
    ListField,
    BooleanField
)


MONGO_STRUCTURE = {
    'static': {
        'system': 'static-system',
        'gpios': 'static-gpios',
        'relays': 'static-relays',
        'all': ['static-system', 'static-gpios']
    },
    'dynamic': {
        'system_memory_stats': 'dynamic-system-memory-statistics',
        'system_net_stats': 'dynamic-system-network-statistics',
        'system_cpu_stats': 'dynamic-system-memory-statistics'
    }
}


class DynamicSchemas(object):
    """DynamicSchemas - default MongoDB Schema templates for dynamic collections


    Attributes:

    system_memory_stats (dict) - schema template for system memory stats
    system_net_stats (dict) - schema template for system network stats
    system_cpu_stats (dict) - schema template for system cpu stats
    
    """
    system_memory_stats = {
        "total": int,
        "available": int,
        "used": int,
        "active": int,
        "inactive": int,
        "buffers": int,
        "cached": int,
        "shared": int,
        "slab": int
    }
    system_net_stats = {

    }
    system_cpu_stats = {

    }
class StaticSchemas(object):
    """StaticSchemas - default MongoDB Schema templates for static collections


    Attributes:

    system (dict) - schema template for system
    gpios (dict) - schema template for gpios
    relays (dict) - schema template for relays
    """
    system = {
        "manufacturer": str,
        "system": str,
        "model": str,
        "revision": str,
        "soc": str,
        "pcb_revision": str,
        "memory": int,
        "storage": str,
        "ethernet_speed": int,
        "has_wifi": bool,
        "has_bluetooth": bool,
        "usb_ports": int,
        "usb3_ports": int,
        "board_headers": list
    }

    gpios = {
        "data": {
            "title": str,
            "descr": str,
            "funcs": list,
            "boardmap": {
                "physical_board": str,
                "gpio_bcm": str,
                "wiring_pi": str
            },
        "header_col": int,
        "header_row": int,
        "label": str
        }
    }

    relays = {
        "model": str,
        "state": bool,
        "description": str,
        "manufacturer": str,
        "relay_channel": int,
        "normally_open": bool,
        "ac_voltage_max": int,
        "ac_voltage_min": int,
        "dc_voltage_max": int,
        "dc_voltage_min": int,
        "ac_amperage_max": int,
        "ac_amperage_min": int,
        "dc_amperage_max": int,
        "dc_amperage_min": int,
        "activation_type": str,
        "activation_voltage": int
    }


class SchemaFactory(object):
    """SchemaFactory - Compiles MongoDB validation schemas 

    MongoDB schema validation specs are defined here https://docs.mongodb.com/manual/core/schema-validation/
    
    - Can compile schemas from default defined schemas (StaticSchemas and DynamicSchemas)
    - Can compile a schema from file sources
    - Export Schema templates, and schemas to JSON, YAML, etc.

    Attributes:
        validator (dict) - the top level keys for a compliant mongodb validation schema
    """

    logger = logging.getLogger('SchemaFactory')
    loginator = Loginator(logger=logger)
    logger = loginator.logger
    nested = False
    last_seen = None
    def __init__(self):
        """__init__ Create a SchemaFactory object

        """
        self.required = []
        self.validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {}
            }
        }


    def pretty_print(self, it: dict) -> None:
        """Pretty print schemas or schema templates

        Args:
            it (dict): [description]
        """
        print(json.dumps(it, indent=2, cls=SchemaTemplateEncoder))

    @classmethod
    def load_schema_template_from_file(cls,
        schema_template_path: str = None,
    ) -> dict:
        """load_schema_template_from_file load a schema template previously serialized to file

        Args:
            schema_template_path (str, optional): Path to a serialized JSON format schema template file. Defaults to None.

        Returns:
            dict: a python decoded dict representing the schema
        """
        schema_template = {}
        if os.path.exists(schema_template_path):
            with open(schema_template_path) as file:
                schema_template = json.load(
                    file,
                    cls=SchemaTemplateDecoder
                )
                return schema_template

        cls.logger.warning(f"your file did not exist, sorry, I compiled a bare bones schema for you")
        return schema_template
        #print()

    def compile_schema_template_from_file(self,
        schema_template_path: str = None
    ) -> dict:
        """Compile an arbitrary schema serialized to file

        Args:
            schema_template_path (str, optional): [Path to schema template file]. Defaults to None.

        Returns:
            dict: Compiled decoded schema object
        """
        schema_template = self.__class__.load_schema_template_from_file(schema_template_path=schema_template_path)
        factory = self
        validator = copy(factory.validator)
        schema = factory.generate_schema(schema_template)
        validator['$jsonSchema']['properties'] = schema
        return validator

    def write_compiled_schema_to_file(self,
        schema_file_path: str = None,
        schema_type: str = None,
        schema_template_name: str = None,
    ) -> bool:
        """Write a compiled scheme object to JSON format file

        Args:
            schema_file_path (str, optional): [description]. Defaults to None.
            schema_type (str, optional): [description]. Defaults to None.
            schema_template_name (str, optional): [description]. Defaults to None.

        Returns:
            bool: True if successful, False if failed
        """
        schema = self.compile_default_schema_template(
            schema_type=schema_type,
            schema_template_name=schema_template_name
        )
        path_contains_slashes = len(schema_file_path.split('/'))
        self.__class__.logger.info(f"writing schema [{schema_template_name}] type [{schema_type}] to [{schema_file_path}]")
        if path_contains_slashes > 1:
            if os.path.exists(
                os.path.dirname(
                    schema_file_path
                )
            ):
                self.__class__.logger.info(f"writing your file to {schema_file_path}")
                with open(schema_file_path, 'w') as file:
                    file.write(
                        json.dumps(schema, indent=2,)
                    )
            else:
                self.__class__.logger.warning(f"The provided path can't be written to because the parent directory does not exist")
                self.__class__.logger.warning(f"Since you are dumping a __schema__ ... try the path './schemas/yourfile.json' ")
                return False
            #file created?
            if os.path.exists(schema_file_path):
                self.__class__.logger.info(f"The schema was successfully dumped to file")
                return True
            else:
                self.__class__.logger.error((f"Dumping the schema to file failed"))
                return False
        else:
            self.__class__.logger.info(f"writing your file to {os.path.join('schemas', schema_file_path)}")
            with open( os.path.join('schemas', schema_file_path)) as file:
                file.write(
                    json.dumps(schema, indent=2)
                )

            if os.path.exists(os.path.join('schemas', schema_file_path)): # file was created
                self.__class__.logger.info(f"The schema was successfully dumped to file")
                return True
            else: # file creation failed
                self.__class__.logger.error((f"Dumping the schema to file failed"))
                return False
        #print('fin')

    def write_default_schema_template_to_file(self,
        schema_type: str = None,
        schema_template_name: str = None,
        schema_template_file_path: str = None,
    ) -> bool:
        """Serialize a default schema template to file

        Args:
            schema_type (str, optional): [`static` or `dynamic`]. Defaults to None.
            schema_template_name (str, optional): [see valid collection names for valid values]. Defaults to None.
            schema_template_file_path (str, optional): [description]. Defaults to None.

        Returns:
            bool: True if successful, False if failed
        """
        schema_template = self.get_default_schema_template(
            schema_type=schema_type,
            schema_template_name=schema_template_name
        )
        path_contains_slashes = len(schema_template_file_path.split('/'))
        if path_contains_slashes > 1: # provided value is a path to file
            if os.path.exists(
                os.path.dirname(
                    schema_template_file_path
                )
            ): # the parent folder exists
                self.__class__.logger.info(f"writing your schema to file {schema_template_file_path}")
                with open(schema_template_file_path, 'w') as file:
                    file.write(
                        json.dumps(schema_template, indent=2, cls=SchemaTemplateEncoder)
                    )
                if os.path.exists(schema_template_file_path): # file was created
                    self.__class__.logger.info(f"The schema template was successfully dumped to file")
                    return True
                else: # file creation failed
                    self.__class__.logger.error(f"The schema template dump failed")
                    return False
            else: # the parent folder does not exist
                self.__class__.logger.error(f"The requested parent folder does not exist")
                return False
        elif path_contains_slashes == 1: # provided value is just a file
            self.__class__.logger.info(f"writing your schema template to {os.path.join('schemas', schema_template_file_path)}")
            with open( os.path.join( 'schemas', schema_template_file_path), 'w') as file:
                file.write(
                    json.dumps(schema_template, indent=2, cls=SchemaTemplateEncoder)
                )
            if os.path.exists(
                os.path.join('schemas', schema_template_file_path)
            ): # file was created
                self.__class__.logger.info(f"succesfully dumped schema template to file")
                return True
            else:
                self.__class__.logger.info(f"failed to dump schema template to file")
                return False


    @classmethod
    def get_default_schema_template(cls,
            schema_type: str = None,
            schema_template_name: str = None
    ) -> dict:
        """Returns schema from default schemas

        Args:
            schema_template_name ([str]): The name of the schema template 

        Returns:
            [dict]: Python dictionary representation of mongo schema template
        """
        schema = {}
        static_defaults = StaticSchemas()
        dynamic_defaults = DynamicSchemas()
        if schema_type is None:
            schema_type = "static"

        if schema_template_name is None:
            schema_template_name = 'system'

        if schema_type == 'static':
            defaults = static_defaults
            if schema_template_name == 'all':
                schema = {
                    "system": defaults.system,
                    "gpios": defaults.gpios,
                    "relays": defaults.system
                }
            else:
                # TODO: find a better way to do this, setter and getter functions?
                schema = defaults.__getattribute__(schema_template_name)
            return schema
        elif schema_type == 'dynamic':
            defaults = dynamic_defaults
            if schema_template_name == 'all':
                schema = {
                    "system_memory_stats": defaults.system_memory_stats,
                    "system_net_stats": defaults.system_net_stats,
                    "system_cpu_stats": defaults.system_cpu_stats
                }
            else:
                # TODO: find a better way to do this, setter and getter functions?
                schema = defaults.__getattribute__(schema_template_name)
            return schema


    def compile_default_schema_template(self,
        schema_type: str = None,
        schema_template_name: str = None
    ) -> dict:
        """Compiles a Mongo DB compliant validator schema from the user selected schema template object, 
        This is used when creating the initial database resources in MongoDB and defines the data types of the attributes within each collection

        Args:
            schema_template dict: The dict reprsentation of the mongo schema template

        Returns:
            dict: compiled validator schema python object
        """
        schema_template = self.__class__.get_default_schema_template(
            schema_type=schema_type,
            schema_template_name=schema_template_name
        )
        factory = self
        validator = copy(factory.validator)
        schema = factory.generate_schema(schema_template)
        validator['$jsonSchema']['properties'] = schema
        return validator
    

    def list_default_schemas(self,
    ) -> list:
        """list defined default schemas

        Returns:
            list: [description]
        """
        results = []
        for klass in [StaticSchemas, DynamicSchemas]:
            klass_name = klass.__name__
            klass_keys = [k for k in list(klass.__dict__.keys()) if not k.startswith('__')]
            results.append(
                { klass_name: klass_keys}
            )
        return results

    def print_default_schemas(self,
    ) -> None:
        """Pretty print defined default schemas
        """
        print(json.dumps(
            self.list_default_schemas(),
            indent=2
        ))


    def generate_schema(self, schema_obj):
        """Generate a schema

        Args:
            schema_obj ([dict]): a python representation of mongodb schema

        Returns:
            [str]: [JSON string representing mongodb schema validator]
        """
        validator = copy(self.validator)
        return self.__class__._recurse_schema_keys(validator, schema_obj)

    @classmethod
    def _bson_typemap(cls, key, value):
        """Maps python types to bson types where applicable

        Args:
            key (str): a key in a dict
            value ([Any]): a value in a dict

        Returns:
            (dict): dictionary with bsonType for property (key)
        """
        if value is str or isinstance(value, str):
            return {'bsonType': 'string'}
        elif value is list or isinstance(value, list):
            return {'bsonType': 'array'}
        elif value is int or isinstance(value, int):
            return {'bsonType': 'int'}
        elif value is dict or isinstance(value, dict):
            return {'bsonType': 'object'}
        elif value is bool or isinstance(value, bool):
            return {'bsonType': 'boolean'}
        else:
            return {'bsonType': ''}


    @classmethod
    def _map_nested_object(cls,label, o):
        """[unused]

        Args:
            label ([type]): [description]
            o ([type]): [description]

        Returns:
            [type]: [description]
        """
        keys = list(o.keys())
        obj = {
            label: {
                "bsonType": "object",
                "properties": {
                    key: cls._bson_typemap(key,o[key]) for key in keys
                },
                "required": [key for key in keys]
            }
        }
        return obj


    @classmethod
    def _recurse_schema_keys(cls, validator, schema_obj):
        """_recurse_schema_keys Recurse a python schema template object dictionary & output a subset of the mongodb validator template

        The subset can be plugged under the "properties" key of a validator dict

        Args:
            validator (dict): a copy of the SchemaFactory objects validator key works here
            schema_obj (dict): the schema template dict object

        Returns:
            props (dict): the user data portion of mongodb validation schema as a dict
        
        """

        props = {}
        #print(validator)
        for k, v in schema_obj.items():
            if v in [str, int, float, list]:
                props[k] = cls._bson_typemap(k, v)
            elif v in [dict] or isinstance(v, dict):
                props[k] = {}
                props[k]["bsonType"] = "object"
                props[k]["properties"] = cls._recurse_schema_keys(validator, v)
        #validator["$jsonSchema"]["properties"] = props

        return props
        #eturn validator

    @classmethod
    def _recurse_schema_keys_nope(cls, validator, schema_obj, levels=[]):
        """[unused]

        Args:
            validator ([type]): [description]
            schema_obj ([type]): [description]
            levels (list, optional): [description]. Defaults to [].

        Returns:
            [type]: [description]
        """
        required = []
        if isinstance(schema_obj, dict):
            for key, value in schema_obj.items():
                required.append(key)
                #print(f"{key} {value}")
                validator["$jsonSchema"]["required"] = required
                prop = cls._bson_typemap(key, value)
                validator["$jsonSchema"]["properties"][key] = prop
                #cls.last_seen = key
                if isinstance(value, dict):
                    required.append(key)
                    levels.append(key)
                    #cls.nested = True
                    #create nested key and recurse into key level
                    #print(f"adding nested object {key} to properties")
                    validator["$jsonSchema"]["properties"][key] = {
                        "bsonType": "object",
                        "properties": {}
                    }
                    # validator["$jsonSchema"]["properties"][key][
                    #     'properties'] = cls._map_nested_object(key, value)
                    #cls._recurse_schema_keys(validator, value)
                    vals = cls._recurse_schema_keys(validator, value)
        return validator
