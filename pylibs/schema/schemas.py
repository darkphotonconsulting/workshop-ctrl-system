import json
import bson
from copy import copy

class DefaultSchemas(object):
    """Default Mongo DB static system schemas

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
    """Generic schema logic. 
    Compiles a mongodb compliant schema validator reference

    Args:
        None

    Returns:
        SchemaFactory
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
        """[summary]

        Args:
            schema_obj ([dict]): [a python representation of mongodb schema]

        Returns:
            [str]: [JSON string representing mongodb schema validator]
        """
        validator = copy(self.validator)
        return self.__class__._recurse_schema_keys(validator, schema_obj)

    @classmethod
    def _bson_typemap(cls, key, value):
        """Maps python types to bson types where applicable

        Args:
            key ([Any]): [a key in a dict]
            value ([Any]): [a value in a dict]

        Returns:
            [dict]: dictionary with bsonType for property (key)
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
        """Recurse a python schema template object dictionary and output a mongodb validator template

        Args:
            validator ([type]): [description]
            schema_obj ([type]): [description]

        Returns:
            [str]: [the schema]
        """
        props = {}
        for k, v in schema_obj.items():
            if v in [str, int, float, list]:
                props[k] = cls._bson_typemap(k, v)
            elif v in [dict] or isinstance(v, dict):
                props[k] = {}
                props[k]["bsonType"] = "object"
                props[k]["properties"] = cls._recurse_schema_keys(validator, v)
        return props

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
