#!/usr/bin/python3
import json
from pylibs.schema.default_schemas import DefaultSchemas

schemas = DefaultSchemas()
gpios = schemas.gpios
with open('data/raspberrypi.json','r') as file_data:
    data = json.load(file_data)


def _bson_typemap(key, value):
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


def recurse(d):
    ret = {}
    """recursese dictionary making a perfect copy no matter how deep"""
    for k,v in d.items():
        if isinstance(v, (str, int, list)):
            # print(f"{k} ->{v}")
            ret[k] = v
        elif isinstance(v, dict) or type(v)==dict:
            ret[k] = recurse(v)
    #print(ret)
    return ret

def recurse2(d):
    props = {}
    """recursese dictionary making a perfect copy no matter how deep"""
    for k, v in d.items():
        #print(f"key: {k} val: {v}")
        if v in [str, int, float, list]:
            #print(f"value is not a container")
            # print(f"{k} ->{v}")
            props[k] = v
            #return ret
        elif v in [dict] or isinstance(v, dict):
            #print(f"value is a container {v}")
            props[k] = recurse2(v)
            #return ret
    #print(ret)
    return props
#print(type(data))
#print(type(gpios))
print(recurse2(gpios))
#print("-"*10)
#print(gpios['data'])
#print(recurse(data))
