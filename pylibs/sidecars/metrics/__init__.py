from celery import Celery
from flask import Flask

from .metrics.middleware import middleware
#from .metrics.app import app


#celery = middleware(app=app)
#celery = middleware()

