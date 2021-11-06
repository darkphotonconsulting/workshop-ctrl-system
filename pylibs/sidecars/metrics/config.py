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


from flask import Flask
from flask import (
    jsonify,
    render_template
)

from flask_mongoengine import (
    MongoEngine, 
    Document
)
# add libs
current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-4])
path.append(libs)

# set default configuration file 
if 'HEADUNIT_CONFIG' not in environ:
    environ['HEADUNIT_CONFIG'] = 'settings/config.json'

from pylibs.config.configuration import (ConfigLoader, Configuration)
from pylibs.database.orm_schemas import System, Relay, Pin
from pylibs.logging.loginator import Loginator

HEADUNIT_CONFIG = Configuration(
    config=ConfigLoader(
        from_file=True, 
        config=environ['HEADUNIT_CONFIG']
    ).all()
)

SECRET_KEY = urandom(32)
