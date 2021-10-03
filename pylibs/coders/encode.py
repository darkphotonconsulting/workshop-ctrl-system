import json
from json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId
from uuid import UUID


class MigrationEncoder(JSONEncoder):
    """JSON Encoder class overrides for generally unsupported data types common to pymongo/mongoengine, and MongoDB data

    This simply overrides the default method of the JSONEncoder
    For example: 
    - each mongo object has an id of type ObjectID (from the bson.objectid module)
    - UUID(s) are used internally by the application in default schemas to identify relations between pin data
    

    Inherits:
        json.JSONEncoder
    """
    def default(self, object):
        """default method

        Args:
            object: a value returned from JSONEncoder default encoder method

        Returns:
            converts UUIDs and ObjectId to strings, defaults to JSONEncoder defaults otherwise
        """
        if isinstance(object, UUID):
            return str(object)
        if isinstance(object, ObjectId):
            return str(object)

        return JSONEncoder.default(self, object)

class SchemaTemplateEncoder(JSONEncoder):
    """JSON Encoder class overrides for Schema Templates


    This simply overrides the default method of the JSONEncoder
    
    - A template is a python dictionary which in it's simplest form looks like this:

    {"keyName": "pythonType"}

    - The dictionary can be however many levels deep, 
      as long as each non-dict value is a simple string representing the values data type

     {"foo": "list" } 

    - A randomly complex example is below
     {
         "foo": {
             "bar": "list",
             "goo": "int",
             "boo": {
                 "baragain": "str
             }
         }
     } 
        
    Inherits:
        json.JSONEncoder
    """

    def default(self, object):
        """default method

        Args:
            object ([Any]): a value returned from JSONEncoder default encoder method

        Returns:
            Converts a python object type to it's string equivalent name
        """
        if isinstance(object, type):
            return object.__name__