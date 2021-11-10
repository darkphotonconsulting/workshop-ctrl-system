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

from psutil import (
    cpu_times
)

from flask import Flask
#import celery
from celery import Celery

from flask import flash, jsonify
from flask import request, redirect
from flask_graphql import GraphQLView
from json import loads
from .config import HEADUNIT_CONFIG
from .metrics import create_app
from .metrics.model import db, graphql 
from .metrics.model import System, Relay, Pin
from .metrics.middleware import middleware

current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-4])
path.append(libs)
# set default configuration file 
from pylibs.database.orm_schemas import System, Relay, Pin
#from pylibs.logging.loginator import Loginator




app = create_app()
celery = middleware(
    app=app
)
app.config['MONGODB_SETTINGS'] = {
    #'db': 'static',
    'host': HEADUNIT_CONFIG.mongo_connection_string()
}
db.init_app(app)

@app.route('/api/v1/graphql', methods=['GET', 'POST'])
def api_v1_graphql():
    req_args = request.args
    req_json = request.json
    return GraphQLView.as_view(
        'graphql',
        schema=graphql.schema,
        graphiql=True
    )()

@app.route('/api/v1/pi/system', methods=['GET'])
def api_v1_pi_system():
    req_args = request.args
    req_json = request.json
    results = []
    try:
        for obj in System.objects():
            #print(system.model)
            results.append(loads(obj.to_json()))
    except RuntimeError as err:
        print('complete with result set')
    finally:
        return jsonify(results)

@app.route('/api/v1/pi/pin', methods=['GET'])
def api_v1_pi_pin():
    req_args = request.args
    req_json = request.json
    results = []
    try:
        for obj in Pin.objects():
            #print(system.model)
            results.append(loads(obj.to_json()))
    except RuntimeError as err:
        print('complete with result set')
    finally:
        return jsonify(results)

@app.route('/api/v1/generic/relay', methods=['GET'])
def api_v1_generic_relay():
    req_args = request.args
    req_json = request.json
    results = []
    try:
        for obj in Relay.objects():
            #print(system.model)
            results.append(loads(obj.to_json()))
    except RuntimeError as err:
        print('complete with result set')
    finally:
        return jsonify(results)

@celery.task()
def test_celery(message):
    return message

# @app.route('/api/v1/metrics/')




def run(
    host: str = None,
    port: int = None,
    debug: bool = None,
):
    host: str = HEADUNIT_CONFIG.pi_host if host is None else host 
    port: int = HEADUNIT_CONFIG.pi_port if port is None else port
    debug: bool = False if debug is None else debug
    app.run(
        host=host,
        port=port,
    )

