
from os.path import (
    dirname,
    abspath
)

from os import (
    environ,
    urandom
)
from time import (
    sleep
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

from psutil import (
    cpu_times
)

from typing import (
    Union,
    Any,
    Optional
)

from celery import Celery, Task
from celery.schedules import crontab

from kombu import Exchange, Queue, binding
#from celery.boosteps import StartStopStep
from celery.bootsteps import StartStopStep
from flask import Flask 


current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
#print(libs)
path.append(libs)

from pylibs.mq.rabbit import (
    MQ_TYPE,
    MQ_HOST,
    MQ_PORT,
    MQ_ADMIN_PORT
)


def amqp_connection_string(
    mq_host: str = None,
    mq_port: int = None,
    mq_user: str = None,
    mq_password: str = None,
) -> str:
    mq_host = MQ_HOST if mq_host is None else mq_host 
    mq_port = MQ_PORT if mq_port is None else mq_port
    if (mq_user is None and mq_password is None):
        return f"amqp://{mq_host}:{mq_port}"
    else: return f"amqp://{mq_user}:{mq_password}@{mq_host}:{mq_port}"

def broker_connection_string(
    mq_host: str = None,
    mq_port: int = None,
    mq_user: str = None,
    mq_password: str = None,
) -> str:
    mq_host = MQ_HOST if mq_host is None else mq_host 
    mq_port = MQ_PORT if mq_port is None else mq_port
    if (mq_user is None and mq_password is None):
        return f"pyamqp://{mq_host}:{mq_port}"
    else: return f"pyamqp://{mq_user}:{mq_password}@{mq_host}:{mq_port}"

def backend_connection_string(
    mq_host: str = None,
    mq_port: int = None,
    mq_user: str = None,
    mq_password: str = None,
) -> str:
    mq_host = MQ_HOST if mq_host is None else mq_host 
    mq_port = MQ_PORT if mq_port is None else mq_port
    if (mq_user is None and mq_password is None):
        return f"rpc://{mq_host}:{mq_port}"
    else: return f"rpc://{mq_user}:{mq_password}@{mq_host}:{mq_port}"

class PreloadBootstep(StartStopStep):
    def start(self, parent):
        app = parent.app
        print(type(app))
        print(type(app.amqp))
        #print(f"application import name: {app.import_name}")
        with app.producer_or_acquire() as producer:
            for queue in app.amqp.queues.values():
                print(f"preloading queue: {queue}")

                
def middleware(
    app: Flask = None,
    mq_host: str = None,
    mq_port: int = None,
    mq_user: str = None,
    mq_password: str = None,
) -> Celery:
    mq_host = "127.0.0.1" if mq_host is None else mq_host 
    mq_port = 5726 if mq_port is None else mq_port
    # print(f"import name: {app.import_name}")
    celery = Celery(
       app.import_name,
       broker=broker_connection_string(),
    #    result_backend='mongodb://mongo.darkphotonworks-labs.io:27017/',
    #    mongo_backend_settings={
    #        'database': 'metrics',
    #        'taskmeta_collection': 'metrics-meta',
    #        'options': {
    #            'authSource': 'admin',
    #            'user': 'root',
    #            'password': 'toor'
    #        }
    #    },
       backend='rpc://',
       result_backend='rpc://',
       result_persistent=True,
    #    result_exchange='metrics.system'
    )
    #celery.conf.task_default_queue = "metrics.system"
    celery.conf.update(app.config)
    celery.conf.update(
        result_backend = 'rpc',
        result_persistent = True,
        task_serializer = 'json',
        result_serializer = 'json'
    )


    #debug boot queues
    celery.steps['worker'].add(PreloadBootstep)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

