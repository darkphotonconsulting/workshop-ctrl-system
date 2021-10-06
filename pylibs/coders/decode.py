import json
from json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId
from uuid import UUID


class SchemaTemplateDecoder(json.JSONDecoder):
    """SchemaTemplateDecoder - Deserialize a Schema Templates from JSON string to a python object

    Override for json.JSONDecoder which allows a HeadUnit mongo schema template object to be deserialized
    from a compliant JSON formatted string to a native python object

    This class override method is documented in https://docs.python.org/3/library/json.html#module-json

    Some useful details about JSON:
    
        - https://datatracker.ietf.org/doc/html/rfc7159.html
        - https://www.ecma-international.org/publications-and-standards/standards/ecma-404/


    - The override allows the string type values found in a serialized template file to be decoded into a native python object
    """
    def __init__(self, *args, **kwargs):
        """__init__ Patches the __init__ method of json.JSONDecoder

        [extended_summary]
        """
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """object_hook - is an optional function that will be called with the result of any object literal decoded (a dict). 
        
        - The return value of object_hook will be used instead of the dict. 
        - This feature can be used to implement custom decoders (e.g. JSON-RPC class hinting).

        Args:
            object: object returned by json.JSONDecoder calls to decode

        Returns:
            object: an object containing the decoded string representation of python objects converted back to their native python object types
        """
        #TODO: support bool properly
        if obj is str:  # set k -> v
            return obj
        if obj is list: # set k -> v
            return obj
        if obj is int: # set k -> v
            return obj
        if isinstance(obj, dict):  # recurse
            for k in obj.keys():
                obj[k] = self.object_hook(obj[k])
            return obj
        if isinstance(obj, str): # set k-> v
            obj = eval(obj)
            return obj
