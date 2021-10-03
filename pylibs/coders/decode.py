import json
from json import JSONEncoder, JSONDecoder
from bson.objectid import ObjectId
from uuid import UUID


class SchemaTemplateDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        #print(f"The object {obj} is of type {type(obj)}")
        #print(f"function received a: {obj.__name__}")

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
        # if isinstance(obj, list):
        #     print(f"working on a list {obj}")
        #     for i in range(0, len(obj)):
        #         obj[i] = self.object_hook(obj[i])
        #         print(obj[i])
        #     return obj
        if isinstance(obj, str):# convert str values back to python `types`
            #print('working on a string')
            obj = eval(obj)
            return obj




