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
from celery import Celery, Task
from celery.schedules import crontab

from kombu import Exchange, Queue, binding
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



#t = Task()
app = create_app()
celery = middleware(
    app=app
)

celery.conf.task_create_missing_queues = False
metrics_exchange = Exchange('metrics', type='direct')
default_exchange = Exchange('default', type='direct')
celery.conf.task_queues = (
    Queue(
        name='default', 
        exchange=default_exchange, 
        bindings=[
            binding(
                exchange=default_exchange, 
                routing_key='default'
            )
        ], 
        routing_key='default'
    ),
    Queue(
        name='metrics.system', 
        exchange=metrics_exchange, 
        bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system'
            )
        ], 
        routing_key='metrics.system'
    ),
    Queue(
        name='metrics.system.vmem', 
        exchange=metrics_exchange,
        bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.vmem'
            )
        ], 
        routing_key='metrics.system.vmem'
    ),
    Queue(
        name='metrics.system.swap', 
        exchange=metrics_exchange,
        bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.swap'
            )
        ], 
        routing_key='metrics.system.swap'
    ),
    Queue(
        name='metrics.system.cputime', 
        exchange=metrics_exchange,
        bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.cputime'
            )
        ], 
        routing_key='metrics.system.cputime'
    ),
    Queue(
        name='metrics.system.cpustats', 
        exchange=metrics_exchange,
        bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.cpustats'
            )
        ], 
        routing_key='metrics.system.cpustats'
    ),
    Queue(
        name='metrics.system.temps', 
        exchange=metrics_exchange,bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.temps'
            )
        ], 
        routing_key='metrics.system.temps'),
    Queue(
        name='metrics.system.diskusage', 
        exchange=metrics_exchange,bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.diskusage'
            )
        ], 
        routing_key='metrics.system.diskusage'),
    Queue(
        name='metrics.system.netio', 
        exchange=metrics_exchange,bindings=[
            binding(
                exchange=metrics_exchange, 
                routing_key='metrics.system.netio'
            )
        ], 
        routing_key='metrics.system.netio'),
)

# AMQP defaults
celery.conf.default_queue = 'metrics.system'
celery.conf.task_default_queue = 'metrics.system'
celery.conf.task_default_exchange = 'metrics'
celery.conf.task_default_exchange_type = 'direct'
celery.conf.task_default_routing_key = 'metrics.system'
celery.conf.update(task_routes = {
    'pylibs.sidecars.metrics.app.publish_vmem': 
        {
            'queue': 'metrics.system.vmem',
            'routing_key': 'metrics.system.vmem'
        }
})

celery.conf.update(beat_schedule = {
    'publish-vmem-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_vmem',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.vmem',
            'routing_key': 'metrics.system.vmem',
            # 'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-swap-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_swap',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.swap',
            'routing_key': 'metrics.system.swap',
            # 'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-cputime-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_cputime',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.cputime',
            'routing_key': 'metrics.system.cputime',
            # 'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-cpustats-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_cpustats',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.cpustats',
            'routing_key': 'metrics.system.cpustats',
            #'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-temperature-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_temps',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.temps',
            'routing_key': 'metrics.system.temps',
            # 'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-disk-usage-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_diskusage',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.diskusage',
            'routing_key': 'metrics.system.diskusage',
            # 'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,

        },
    },
    'publish-netio-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_netio',
        'schedule': 60.0,
        'options': {
            'queue': 'metrics.system.netio',
            'routing_key': 'metrics.system.netio',
            # 'exchange': 'metrics',         
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
})
celery.conf.timezone = 'UTC'

# define Tasks

@celery.task()
def test_celery(message):
    return message

@celery.task(
    bind=True, 
    queue='metrics.system.vmem', 
    reply_to='metrics.system.vmem',
    name='pylibs.sidecars.metrics.app.publish_vmem' 
)
def publish_vmem(self):
    metrics = SystemMetrics(interval=30)
    mem = metrics.vmem()
    return dumps(mem)

@celery.task(
    bind=True, 
    queue='metrics.system.swap', 
    name='pylibs.sidecars.metrics.app.publish_swap'
)
def publish_swap(self):
    metrics = SystemMetrics(interval=30)
    swap = metrics.swap()
    return dumps(swap)

@celery.task(
    bind=True, 
    queue='metrics.system.cputime', 
    name='pylibs.sidecars.metrics.app.publish_cputime'
)
def publish_cputime(self):
    metrics = SystemMetrics(interval=30)
    cputime = metrics.cputime()
    return dumps(cputime)

@celery.task(
    bind=True, 
    queue='metrics.system.cpustats', 
    name='pylibs.sidecars.metrics.app.publish_cpustats'
)
def publish_cpustats(self):
    metrics = SystemMetrics(interval=30)
    cpustats = metrics.cpustats()
    return dumps(cpustats)

@celery.task(
    bind=True, 
    # exchange='metrics',
    queue='metrics.system.temps', 
    name='pylibs.sidecars.metrics.app.publish_temps'
)
def publish_temps(self):
    metrics = SystemMetrics(interval=30)
    temps = metrics.temperatures()
    return dumps(temps)


#Task.apply_async()

@celery.task(
    bind=True, 
    queue='metrics.system.diskusage', 
    name='pylibs.sidecars.metrics.app.publish_diskusage'
)
def publish_diskusage(self):
    metrics = SystemMetrics(interval=30)
    usage = metrics.diskusage()
    return dumps(usage)

@celery.task(
    bind=True, 
    queue='metrics.system.netio', 
    name='pylibs.sidecars.metrics.app.publish_netio'
)
def publish_netio(self):
    metrics = SystemMetrics(interval=30)
    netio = metrics.netio()
    return dumps(netio)

# setup Exchanges & Queues

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

