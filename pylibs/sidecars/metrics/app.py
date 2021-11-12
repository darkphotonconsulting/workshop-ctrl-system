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
    loads, 
    dumps
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
from celery.schedules import crontab
from kombu import Exchange, Queue
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
from pylibs.metrics.system import SystemMetrics
#from pylibs.logging.loginator import Loginator




app = create_app()
celery = middleware(
    app=app
)


# def route_tasks(name, args, kwargs, options, task=None, **kw):
#     ret = dict()
#     if name=="pylibs.sidecars.metrics.app.publish_vmem":
#         ret = {
#             'exchange': 'metrics',
#             'exchange_type': 'topic',
#             'routing_key' : 'metrics.vmem'
#         }
#     else:
#         ret = {
#             'exchange': 'metrics',
#             'exchange_type': 'topic',
#             'routing_key' : 'metrics.nocategory' 
#         }
#     return ret
        
# celery.conf.task_routes = (route_tasks,)

@celery.task
def test_celery(message):
    return message


@celery.task(queue='metrics')
def publish_vmem():
    metrics = SystemMetrics(interval=30)
    mem = metrics.vmem()
    return dumps(mem)

@celery.task(queue='metrics')
def publish_swap():
    metrics = SystemMetrics(interval=30)
    swap = metrics.swap()
    return dumps(swap)

@celery.task(queue='metrics')
def publish_cputime():
    metrics = SystemMetrics(interval=30)
    cputime = metrics.cputime()
    return dumps(cputime)

@celery.task(queue='metrics')
def publish_cpustats():
    metrics = SystemMetrics(interval=30)
    cpustats = metrics.cpustats()
    return dumps(cpustats)

@celery.task(queue='metrics')
def publish_temps():
    metrics = SystemMetrics(interval=30)
    temps = metrics.temperatures()
    return dumps(temps)

@celery.task(queue='metrics')
def publish_diskusage():
    metrics = SystemMetrics(interval=30)
    usage = metrics.diskusage()
    return dumps(usage)

@celery.task(queue='metrics')
def publish_netio():
    metrics = SystemMetrics(interval=30)
    netio = metrics.netio()
    return dumps(netio)

## setup queues
metrics_exchange = Exchange('metrics_exchange', type='direct')
celery.conf.task_queues = (
    Queue('metrics', metrics_exchange, routing_key='metrics.*'),
)
celery.conf.task_default_queue = 'metrics'
celery.conf.task_default_exchange = 'metrics_exchange'
celery.conf.task_default_routing_key = 'metrics.general'
celery.conf.task_routes = {
    'pylibs.sidecars.metrics.app.celery.tasks.publish_vmem': {
        'queue': 'metrics',
        'routing_key': 'metrics.vmem',
    },
    'pylibs.sidecars.metrics.app.celery.tasks.publish_swap': {
        'queue': 'metrics',
        'routing_key': 'metrics.swap',
    },
    'pylibs.sidecars.metrics.app.celery.tasks.publish_cputime': {
        'queue': 'metrics',
        'routing_key': 'metrics.cputime',
    },
    'pylibs.sidecars.metrics.app.celery.tasks.publish_cpustats': {
        'queue': 'metrics',
        'routing_key': 'metrics.cpustats',
    },
    'pylibs.sidecars.metrics.app.celery.tasks.publish_temps': {
        'queue': 'metrics',
        'routing_key': 'metrics.temperature',
    },
    'pylibs.sidecars.metrics.app.celery.tasks.publish_diskusage': {
        'queue': 'metrics',
        'routing_key': 'metrics.diskusage',
    },
    'pylibs.sidecars.metrics.app.celery.tasks.publish_netio': {
        'queue': 'metrics',
        'routing_key': 'metrics.netio',
    },
}

# celery beat

celery.conf.beat_schedule = {
    'publish-vmem-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_vmem',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.vmem'            
        },
    },
    'publish-swap-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_swap',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.swap'            
        },
    },
    'publish-cputime-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_cputime',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.cputime'            
        },
    },
    'publish-cpustats-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_cpustats',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.cpustats'            
        },
    },
    'publish-temperature-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_temps',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.temperature'            
        },
    },
    'publish-disk-usage-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_diskusage',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.diskusage'            
        },
    },
    'publish-netio-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_netio',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics',
            'routing_key': 'metrics.netio'            
        },
    },
}
celery.conf.timezone = 'UTC'
# celery.conf.task_default_queue = 'metrics'
# celery.conf.task_queues = (
#     Queue('metrics', routing_key='metric.*')
# )
# celery.conf.task_routes = {
#     'pylibs.sidecars.metrics.app.publish_vmem': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.vmem'
#     },
#     'pylibs.sidecars.metrics.app.publish_swap': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.swap'
#     },
#     'pylibs.sidecars.metrics.app.publish_cputime': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.cputime'
#     },
#     'pylibs.sidecars.metrics.app.publish_cpustats': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.cpustats'
#     },
#     'pylibs.sidecars.metrics.app.publish_temps': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.temperature'
#     },
#     'pylibs.sidecars.metrics.app.publish_diskusage': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.diskusage'
#     },
#     'pylibs.sidecars.metrics.app.publish_netio': {
#         'queue': 'metrics',
#         'routing_key': 'metric.system.netio'
#     },
# }

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

