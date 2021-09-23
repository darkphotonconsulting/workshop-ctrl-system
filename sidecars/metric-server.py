#!/usr/bin/python3


import json
import re
import time

import flask
import psutil
import requests
from bs4 import BeautifulSoup
from flask import jsonify, request
from gpiozero import *
from RPi import GPIO

#from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure

app = flask.Flask(__name__)
app.config["DEBUG"] = True

db = MongoClient(

)
@app.route('/api/v1/pi/cpu', methods=['GET'])
def api_pi_data():
    data = {
        "cpu_count": psutil.cpu_count(),
        "cpu_freq_min": psutil.cpu_freq().min,
        "cpu_freq_max": psutil.cpu_freq().max,
        "cpu_freq_current": psutil.cpu_freq().current
    }
    return jsonify(data)


app.run(
    host="0.0.0.0",
    port=5005
)