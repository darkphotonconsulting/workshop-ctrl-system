from os.path import (
    dirname,
    abspath
)

from os import (
    environ,
    urandom
)

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

# from psutil import (
#     cpu_times
# )

#from flask import Flask
#from flask_mongoengine import MongoEngine, Document
#import celery
#from celery import Celery, Task
#from celery.schedules import crontab

from kombu import Exchange, Queue, binding
from flask import flash, jsonify
from flask import request, redirect
from flask_graphql import GraphQLView
from json import loads
from .config import HEADUNIT_CONFIG
from .metrics import create_app
from .metrics.middleware import middleware
from .metrics.model import db, graphql

current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-4])
path.append(libs)


from pylibs.database.dynamic_schemas import (
    SystemMetricCPUStats,
    SystemMetricCPUTime,
    SystemMetricVirtualMemory,
    SystemMetricSwap,
    SystemMetricDiskUsageStats,
    SystemMetricNetIOStats,
)

from pylibs.metrics.system import (
    SystemMetrics
)

from pylibs.docker.containerflow import (
    build,
    run,
    rmi,
    image_list,
    container_list,
)

from pylibs.mq.rabbit import (
    Rabbit
)


# rabbit = Rabbit(
#     config=HEADUNIT_CONFIG
# )
# print(HEADUNIT_CONFIG.containers)
app = create_app()
celery = middleware(
    app=app
)

## start a rabbitmq container if one is not running 

# if HEADUNIT_CONFIG.rabbitmq_image_tag not in container_list():
#     if HEADUNIT_CONFIG.rabbitmq_image_tag not in image_list():
#         build(
#             image_tag=HEADUNIT_CONFIG.rabbitmq_image_tag, 
#             dockerfile=HEADUNIT_CONFIG.rabbitmq_dockerfile
#         )
#         run(
#             image_name=HEADUNIT_CONFIG.rabbitmq_image_tag,
#             ports={i[0]: i[1] for i in HEADUNIT_CONFIG.rabbitmq_ports}
#         )
#     else:
#         run(
#             image_name=HEADUNIT_CONFIG.rabbitmq_image_tag,
#             ports={i[0]: i[1] for i in HEADUNIT_CONFIG.rabbitmq_ports}
#         )
    
celery.conf.task_create_missing_queues = False
celery.conf.update(
    task_routes = {
        'pylibs.sidecars.metrics.app.publish_vmem': 
            {
                'queue': 'metrics.system.vmem',
                'routing_key': 'metrics.system.vmem'
            }
    }
)

celery.conf.update(beat_schedule = {
    'publish-vmem-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_vmem',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.vmem',
            'routing_key': 'metrics.system.vmem',
            'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-swap-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_swap',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.swap',
            'routing_key': 'metrics.system.swap',
            'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-cputime-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_cputime',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.cputime',
            'routing_key': 'metrics.system.cputime',
            'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-cpustats-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_cpustats',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.cpustats',
            'routing_key': 'metrics.system.cpustats',
            'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-temperature-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_temps',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.temps',
            'routing_key': 'metrics.system.temps',
            'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
    'publish-disk-usage-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_diskusage',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.diskusage',
            'routing_key': 'metrics.system.diskusage',
            'exchange': 'metrics',            
            'exchange_type': 'direct',
            'priority': 1,

        },
    },
    'publish-netio-60s': {
        'task': 'pylibs.sidecars.metrics.app.publish_netio',
        'schedule': 60.0*5,
        'options': {
            # 'queue': 'metrics.system.netio',
            'routing_key': 'metrics.system.netio',
            'exchange': 'metrics',         
            'exchange_type': 'direct',
            'priority': 1,
        },
    },
})

# metrics application exchanges 

metrics_exchange = Exchange('metrics', type='direct')
default_exchange = Exchange('default', type='direct')

# metrics application queues
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
                exchange=Exchange(
                    'metrics.system.vmem',
                    type='direct',
                    delivery_mode=1,
                ),
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

# celery AMQP defaults
celery.conf.default_queue = 'metrics.system'
celery.conf.task_default_queue = 'metrics.system'
celery.conf.task_default_exchange = 'metrics'
celery.conf.task_default_exchange_type = 'direct'
celery.conf.task_default_routing_key = 'metrics.system'
celery.conf.timezone = 'UTC'

# define Tasks
@celery.task()
def test_celery(message):
    return message

@celery.task(
    bind=True, 
    name='pylibs.sidecars.metrics.app.publish_vmem' 
)
def publish_vmem(self):
    #print(self)
    metrics = SystemMetrics(interval=30)
    mem = metrics.vmem()
    entry = SystemMetricVirtualMemory(**mem)
    saved = entry.save()
    print(saved)
    return dumps(mem)

@celery.task(
    bind=True, 
    name='pylibs.sidecars.metrics.app.publish_swap'
)
def publish_swap(self):
    metrics = SystemMetrics(interval=30)
    swap = metrics.swap()
    entry = SystemMetricSwap(**swap)
    saved = entry.save()

    return dumps(swap)

@celery.task(
    bind=True, 
    # queue='metrics.system.cputime', 
    name='pylibs.sidecars.metrics.app.publish_cputime'
)
def publish_cputime(self):
    metrics = SystemMetrics(interval=30)
    cputimes = metrics.cputime()
    entries = [SystemMetricCPUTime(**cputime).save() for cputime in cputimes]
    return dumps(cputimes)

@celery.task(
    bind=True, 
    # queue='metrics.system.cpustats', 
    name='pylibs.sidecars.metrics.app.publish_cpustats'
)
def publish_cpustats(self):
    metrics = SystemMetrics(interval=30)
    cpustats = metrics.cpustats()
    entry = SystemMetricCPUStats(**cpustats).save()
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
    usages = metrics.diskusage()
    entries = [SystemMetricDiskUsageStats(**usage).save() for usage in usages]
    return dumps(usages)

@celery.task(
    bind=True, 
    # queue='metrics.system.netio', 
    name='pylibs.sidecars.metrics.app.publish_netio'
)
def publish_netio(self):
    metrics = SystemMetrics(interval=30)
    netios = metrics.netio()
    entries = [SystemMetricNetIOStats(**netio).save() for netio in netios]
    return dumps(netios)

db.init_app(app)


@app.route(rule='/api/v1/metrics/system/graphql', 
    methods=[
        'GET',
        'POST'
    ]
)
def api_v1_metrics_system_graphql():
    return GraphQLView.as_view(
        'graphql',
        schema=graphql.schema,
        graphiql=True,
    )()
    
@app.route(rule='/api/v1/metrics/system', 
    methods=[
        'GET', 
        'POST',
        'DELETE'
    ]
)
def api_v1_metrics_system():

    metric_class_map = {
        'vmem':  SystemMetricVirtualMemory,
        'swap': SystemMetricSwap,
        'cputime': SystemMetricCPUTime,
        'cpustats': SystemMetricCPUStats,
        'diskusage': SystemMetricDiskUsageStats,
        'netio': SystemMetricNetIOStats,
    }
    
    
    args = request.args
    metric_type = args.get('metric_type', 'vmem')
    order_by = args.get('order_by', 'timestamp')
    start = args.get('start', 0)
    end = args.get('end', -1)
    req_json = request.json
    results = []
    try:
        if request.method in ['GET', 'POST']:
            if req_json is None:
                objs = metric_class_map[metric_type].objects().order_by(order_by)#[start:]
                print("printing all objects")
            else:
                objs = metric_class_map[metric_type].objects(**req_json).order_by(order_by)#[start:]
                print("printing selected objects")

            for obj in objs:
                #print(system.model)
                results.append(loads(obj.to_json()))
        elif request.method in ['DELETE']:
            if req_json is None:
                objs = metric_class_map[metric_type].objects().order_by(order_by)
                print("deleting all objects")

            else:
                objs = metric_class_map[metric_type].objects(**req_json).order_by(order_by)
                print("deleting selected objects")

            for obj in objs:
                print('deleting: ', f"{obj.to_json()}")
                results.append(loads(obj.to_json()))
                obj.delete()
                # should actually return remaining results?
    except RuntimeError as err:
        print('complete with result set')
    finally:
        return jsonify(results)


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

