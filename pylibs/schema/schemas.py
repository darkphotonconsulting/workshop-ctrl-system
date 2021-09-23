"""[summary]

Returns:
    [type]: [description]
"""
import json
import bson
from copy import copy

class DefaultSchemas(object):
    """[summary]

    Args:
        object ([type]): [description]
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
                "Physical/Board": str,
                "GPIO/BCM": str,
                "Wiring Pi": str
            },
        "header_col": int,
        "header_row": int,
        "label": str
        }
    }

class SchemaFactory(object):
    """[summary]

    Args:
        object ([type]): [description]

    Returns:
        [type]: [description]
    """

    nested = False
    last_seen = None
    def __init__(self):
        self.required = []
        self.validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {}
            }
        }


    def generate_schema(self, schema_obj):
        #print(f"schema is: {schema_obj}")
        validator = copy(self.validator)
        return self.__class__._recurse_schema_keys(validator, schema_obj)

    @classmethod
    def _bson_typemap(cls, key, value):
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
        keys = list(o.keys())
        #print(f"mapping obj keys: {keys}")
        # obj = {
        #     label: {
        #         "bsonType": "object",
        #         "properties": {
        #             key: cls._bson_typemap(key, o[key])
        #         }
        #     }
        #     for key in keys
        # }
        obj = {
            label: {
                "bsonType": "object",
                "properties": {
                    key: cls._bson_typemap(key,o[key]) for key in keys
                },
                "required": [key for key in keys]
            }
        }
        print(f"created object: {obj}")
        return obj

    @classmethod
    def _recurse_schema_keys(cls, validator, schema_obj, levels=[]):
        required = []
        #print(f"last seen key: {cls.last_seen}")
        #print(f"nest state {cls.nested}")
        if isinstance(schema_obj, dict):
            for key, value in schema_obj.items():
                #print(f"current key: {key}")
                #if value is not isinstance(value, dict):
                #    cls.nested = False
                if len(required) > 0:
                    print(f"last seen key {required[-1]}")
                required.append(key)
                #print(f"{key} {value}")
                validator["$jsonSchema"]["required"] = required
                prop = cls._bson_typemap(key, value)
                validator["$jsonSchema"]["properties"][key] = prop
                #cls.last_seen = key
                if isinstance(value, dict):
                    if len(required) > 0:
                        print(f"last seen key {required[-1]}")
                    required.append(key)
                    levels.append(key)
                    print(f"key {key} is a dictionary")
                    print(f"levels contains {levels}")
                    #cls.nested = True
                    #create nested key and recurse into key level
                    #print(f"adding nested object {key} to properties")
                    validator["$jsonSchema"]["properties"][key] = {
                        "bsonType": "object",
                        "properties": {}
                    }
                    # validator["$jsonSchema"]["properties"][key][
                    #     'properties'] = cls._map_nested_object(key, value)
                    print(type(cls._map_nested_object(key, value)))
                    #cls._recurse_schema_keys(validator, value)
                    vals = cls._recurse_schema_keys(validator, value)
                    print(f"recursion returns: {vals}")
        return validator



factory = SchemaFactory()
gpioschema = DefaultSchemas().gpios
print(json.dumps(factory.generate_schema(gpioschema)))
