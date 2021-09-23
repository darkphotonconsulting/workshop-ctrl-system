#!/usr/bin/python3
"""This script seeds data to a mongodb backend
"""
import os
import sys
import json
import bson
import collections
import argparse
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
#from pymongo.collection import 
from config.settings import Config
from pylibs.schema.schemas import HeadUnitMongoSchemas
from pylibs.pi import PiInfo, PiInfoEncoder

argparser = argparse.ArgumentParser(
    description='Generates JSON inputs for NoSQL backend(s). JSON object describes the running raspberry pi'
)
argparser.add_argument(
    '--data-dir',
    action='store',
    type=str,
    required=True
)


def get_pi_info():
    return PiInfo()

def mongo_connection():
    return MongoClient(
        f"mongodb://{Config.mongodb_host}:{Config.mongodb_port}")

def get_databases(client):
    return client.database_names()

def database_created(client, db):
    return True if db in get_databases(client) else False

def write_data(output, data):
    with open(f"{output}/pi.json", 'w') as file:
        file.write(data)

def main(a):
    piobj = get_pi_info()
    print(piobj.to_json())



if __name__ == '__main__':
    args = argparser.parse_args()
    main(args)


#print(databases)

# try:
#     if Config.mongodb_database not in databases:
#         db = client[Config.mongodb_database]
#         db.create_collection(
#             name='testing',
#         )
# except CollectionInvalid as err:
#     print()
# print(client.database_names())