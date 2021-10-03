import json
from json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId
from uuid import UUID


class MigrationEncoder(JSONEncoder):
    """JSON Encoder for non-standard data types found in Mongo schemas and obects (eg, object ids, UUIDs, etc)

    Inherits:
        json.JSONEncoder
    """
    def default(self, object):
        if isinstance(object, UUID):
            return str(object)
        if isinstance(object, ObjectId):
            return str(object)

        return JSONEncoder.default(self, object)

class SchemaTemplateEncoder(JSONEncoder):
    """[summary]

    Args:
        JSONEncoder ([type]): [description]
    """

    def default(self, object):
        if isinstance(object, type):
            return object.__name__