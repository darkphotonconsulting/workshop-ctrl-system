from os.path import (
    dirname,
    abspath
)

from os import (
    environ,
    urandom
)
#import sys
from json import (
    loads
)
from sys import (
    stdout,
    stderr,
    path,
    modules
)

from flask_mongoengine import MongoEngine

current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-4])
path.append(libs)
# set default configuration file 
if 'HEADUNIT_CONFIG' not in environ:
    environ['HEADUNIT_CONFIG'] = 'settings/config.json'

from pylibs.logging.loginator import Loginator

from pylibs.database.orm_schemas import (
    System, 
    Relay, 
    Pin
)
from pylibs.database.orm_schemas import (
    SystemGraphQL, 
    RelayGraphQL, 
    PinGraphQL, 
    Query, 
    GraphQLFactory
)


db = MongoEngine()
graphql = GraphQLFactory(
    Query, 
    [
        SystemGraphQL, 
        RelayGraphQL, 
        PinGraphQL
    ]
)