import json
from json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId
from uuid import UUID


class SchemaTemplateDecoder(json.JSONDecoder):
    """Decode a Schema template JSON string to a native python dict object

    Args:
        json ([type]): [description]
    """
    def __init__(self, *args, **kwargs):
        """Calls json.JSONDecoder init with custom object_hook enabled for decoding schema templates appropriately
        """
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """[summary]

        Args:
            obj ([Any]): object returned by json.JSONDecoder calls to decode

        Returns:
            Converts string representation of python objects found in schema templates back to native python object types
        """
        if obj is str:
            return obj
        if obj is list:
            return obj
        if obj is int:
            return obj
        if isinstance(obj, dict):  # recurse dict keys
            for k in obj.keys():
                obj[k] = self.object_hook(obj[k])
            return obj
        if isinstance(obj, str):# convert str values back to python `types`
            #print('working on a string')
            obj = eval(obj)
            return obj




