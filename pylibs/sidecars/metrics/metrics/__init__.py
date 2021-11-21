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
from pylibs.logging.loginator import Loginator


#from .model import db

HEADUNIT_CONFIG = Configuration(
    config=ConfigLoader(
        from_file=True, 
        config=environ['HEADUNIT_CONFIG']
    ).all()
)

SECRET_KEY = urandom(32)

def create_app(config=None):
    app = Flask(
        __name__,
        instance_relative_config=False,
    )
    app.config['MONGODB_SETTINGS'] = {
        'db': 'metrics-test',
        'host': HEADUNIT_CONFIG.mongo_connection_string(mongo_database='dynamic')
    }
    
    
    


    #db.init_app(app)
        
    return app