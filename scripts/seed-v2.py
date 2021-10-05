import os
import sys
import json
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])
sys.path.append(libs)

from pymongo import MongoClient
from argparse import ArgumentParser
from pylibs.logging.loginator import Loginator
program_name = "HeadUnit Data Import & Export Tool"
parser = ArgumentParser(
    prog=program_name,

)


conn_args = parser.add_argument_group('connection')
action_args = parser.add_argument_group('actions')
conn_args.add_argument('--mongo-host',
                       type=str,
                       required=False,
                       action='store',
                       help='MongoDB host IP or FQDN',
                       default="mongo.darkphotonworks-labs.io"
)
conn_args.add_argument('--mongo-port',
                       type=int,
                       required=False,
                       action='store',
                       help='MongoDB Port',
                       default=27017
)
conn_args.add_argument('--mongo-username',
                       type=str,
                       required=True,
                       action='store',
                       help='MongoDB Application Username'
)
conn_args.add_argument('--mongo-password',
                       type=str,
                       required=True,
                       action='store',
                       help='MongoDB Application Password'
)


parser.parse_args()