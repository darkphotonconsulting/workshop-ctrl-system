import json
from json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId
from uuid import UUID


class MigrationEncoder(JSONEncoder):
    """MigrationEncoder - Serialize Schema Templates to JSON format

    Override for json.JSONEncoder which allows a HeadUnit mongo schema template object to be serialized 
    to a compliant JSON formatted string for the purpose of being written to files by the data 
    migration tool set. 

    Allows objects containing ObjectId or UUID types as values to be encoded

    This class override method is documented in https://docs.python.org/3/library/json.html#module-json

    Some useful details about JSON:
    
        - https://datatracker.ietf.org/doc/html/rfc7159.html
        - https://www.ecma-international.org/publications-and-standards/standards/ecma-404/


    - The override allows UUIDs and ObjectIds to be serialized properly 

    """
    def default(self, object):
        """default - a function that gets called for objects that can’t otherwise be serialized. 

        It should return a JSON encodable version of the object or raise a TypeError. If not specified, TypeError is raised.

        https://docs.python.org/3/library/json.html#json.JSONEncoder.default
        
        Args:
            object (object): JSON encodable object (dict, list, ...)

        Returns:
            object: a JSON encodable version of the object or raise a TypeError.
        """
        if isinstance(object, UUID):
            return str(object)
        if isinstance(object, ObjectId):
            return str(object)

        return JSONEncoder.default(self, object)

class SchemaTemplateEncoder(JSONEncoder):
    """SchemaTemplateEncoder - Serialize Schema Templates to JSON format

    Override for json.JSONEncoder which allows a HeadUnit mongo schema template object to be serialized 
    to a compliant JSON formatted string

    This class override method is documented in https://docs.python.org/3/library/json.html#module-json

    Some useful details about JSON:
    
        - https://datatracker.ietf.org/doc/html/rfc7159.html
        - https://www.ecma-international.org/publications-and-standards/standards/ecma-404/


    - The dictionary can be infinitely n-levels levels deep:
    - Rules: each non-key value is a simple string representing the values data type
    - Rules: if a key is a nested dict object, simple use the enclosed bracket syntax to nest into the key...
    - A schema template is simply a python dictionary which in it's simplest form looks like this:
        - A simple template
            {
                "keyName": type
            }
        - A complex template
            {
                "foo": list,
                "bar": {
                    "foo": true,
                    "alist": list,
                    "ainteger": int,
                    "astring", str
                } 
            }
    - The encoder supports any type which has a `__name__` attribute
    """

    def default(self, object):
        """default - a function that gets called for objects that can’t otherwise be serialized. 

        It should return a JSON encodable version of the object or raise a TypeError. If not specified, TypeError is raised.

        https://docs.python.org/3/library/json.html#json.JSONEncoder.default
        
        Args:
            object (object): JSON encodable object (dict, list, ...)

        Returns:
            object: a JSON encodable version of the object or raise a TypeError.
        """
        if isinstance(object, type): # return the type.__name__ of any object
            # TODO: support bools properly
            return object.__name__