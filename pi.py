import flask
from flask import request, jsonify
from gpiozero import *
import time
import json
from RPi import GPIO
from bs4 import BeautifulSoup
import requests
import re

from urllib.parse import (
    urlparse, 
    urljoin)


def deepsearch(data, search, keys=True):
    results = []
    for key, value in data.items():
        if keys is True:
            if key == search:
                results.append({search: data[key]})
            elif isinstance(data[key], dict):
                nkey = data[key]
                for nval in deepsearch(nkey, search, keys):
                    results.append(nval)
        else:
            #broken
            if value == search:
                print("value is {}".format(value))
                results.append({search: value})
            elif isinstance(value, dict):
                nval = value
                for val in deepsearch(nval, search, keys):
                    results.append(val)
    return results
            
        
class HeadUnit:    
    """
    Abstract
    --------

    Interacts with several libraries to provide robust gpio and raspberry pi status

    Returns:
        [HeadUnit]: [A python object representing the init state of the running raspberry pi]
    """

    GPIO_FUNCTIONS = {
    'input':   GPIO.IN,
    'output':  GPIO.OUT,
    'i2c':     GPIO.I2C,
    'spi':     GPIO.SPI,
    'pwm':     GPIO.HARD_PWM,
    'serial':  GPIO.SERIAL,
    'unknown': GPIO.UNKNOWN,
    }

    GPIO_PULL_UPS = {
    'up':       GPIO.PUD_UP,
    'down':     GPIO.PUD_DOWN,
    'floating': GPIO.PUD_OFF,
    }

    GPIO_EDGES = {
    'both':    GPIO.BOTH,
    'rising':  GPIO.RISING,
    'falling': GPIO.FALLING,
    }

    def __init__(self):   
        self.factory = Device._default_pin_factory()
        self.j8 = pi_info().headers['J8']
        self.pins = self.j8.pins
        self.gpiopins = self.pins
        self.info = pi_info()

    def system(self):  
        self.info = pi_info()
        return {
            'manufacturer': self.info.manufacturer,
            'system': "Raspberry Pi {} ({})".format(self.info.model, self.info.revision),
            'released': self.info.released, 
            'model': self.info.model, 
            'revision': self.info.revision,
            'soc': self.info.soc, 
            'pcb_revision': self.info.pcb_revision,
            'memory': self.info.memory,
            'storage': self.info.storage, 
            'ethernet_speed': self.info.eth_speed, 
            'has_wifi': self.info.wifi, 
            'has_bluetooth': self.info.bluetooth, 
            'usb_ports': self.info.usb, 
            'usb3_ports': self.info.usb3,
            'board_headers': list( self.info.headers.keys() )
        }

    @classmethod
    def pinout(cls, pin: int = None, label: str = None):
        base_url = "https://pinout.xyz/pinout/"
        powerpins = {
            'GND': 'ground',
            '3V3': '3v3_power',
            '5V': '5v_power'   
        }
        if label.startswith("GPIO"):
            return urljoin(base_url, "pin{}_{}".format(pin, label.lower()))
        if label in powerpins.keys():
            return urljoin(base_url, powerpins[label])

    @classmethod
    def pindata(cls, pin: int = None, label: str = None):
        parser = ""
        powerpins = {
            'GND': 'page_ground',
            '3V3': 'page_3v3_power',
            '5V': 'page_5v_power'   
        }
        if label.startswith("GPIO"):
            articleid = "pin{}_{}".format(pin, label.lower())
            parser = "gpiopin"
        if label in powerpins.keys():
            articleid = powerpins[label]
            parser = "power"
        pin_url = cls.pinout(pin, label)
        response = requests.get(pin_url)
        html = BeautifulSoup(response.text, 'html.parser')
        article = html.find('article', class_="{}".format(articleid))
        if parser == "gpiopin":
            pin_map_rgx = r".*pin\s(\d+)"
            key_map_rgx = r"(.+) .*pin\s.+"
            phys_key, gpio_key, wiringpi_key = [
                re.search(key_map_rgx, i.string).group(1) for i in article.contents[2].find_all('li')
            ][0:3]
            phys_val, gpio_val, wiringpi_val = [
                re.search(pin_map_rgx, i.string).group(1) for i in article.contents[2].find_all('li')
            ][0:3]
            print("pinmap data = {}".format(article.contents[2].find_all('li')))
            boardmap = dict(
                list(
                    zip(
                        [
                            phys_key, gpio_key, wiringpi_key 
                        ],
                        [
                            phys_val, gpio_val, wiringpi_val    
                        ]
                    )
                )
            )
            funcs = [i.string for i in article.contents[1].find_all('td')]
            if None in funcs:  
                funcs.remove(None)
            #print(funcs)  
            return {
                "title" : article.contents[0].string,
                "descr": "{}".format(articleid),
                "funcs" : funcs,
                "boardmap": boardmap
            }
        else:
            desc = list(filter(
                lambda x: type(x.string) is not type(None),
                list(article.find_all('p'))
            ))

            return {
                "title": "{}".format(article.contents[0].string),
                "descr": " ".join([i.string.replace("\n", " ") for i in desc]),
                "funcs": "this is a {} pin!!!".format(parser),
                "boardmap": label
            }


    def pinmap(self):
        mapping = {
        str(pin.number): {
                'label': pin.function,
                # 'function': factory.pin_class(factory, pin.number).function,
                'header_row': pin.row,
                'header_col': pin.col,
                'info_url': self.__class__.pinout(pin.number, pin.function),
                'data': self.__class__.pindata(pin.number, pin.function)
            } for pin in self.gpiopins.values()
        }
        return dict(sorted(
            mapping.items(),
            key=lambda x: x[0]
        ))

# sysmap = system()

# pimap = {
#     'system': sysmap, 
#     'gpio': pinmap
# }




hu = HeadUnit()
#print(hu.system())


data = {
    "system": hu.system(),
    "gpio": hu.pinmap()
}
#print(json.dumps(data))
print(deepsearch(data, "label" ))


app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route(
    '/api/v1/pi/data', 
    methods=['GET']
)
def api_pi_data():
    return jsonify(data)

@app.route(
    '/api/v1/pi/system/data', 
    methods=['GET']
)
def api_pi_system_data():
    return jsonify(data['system'])

@app.route(
    '/api/v1/pi/gpio/data', 
    methods=['GET']
)
def api_pi_gpio_data():
    args = request.args
    types = {

    }
    try:
        print("ok")
    except KeyError as e:  
        print("uh oh")

    return jsonify(data['gpio'])

@app.route(
    '/api/v1/relays/data', 
    methods=['GET']
)
def api_relays_data():
    types = {
        "board_port": int, 
        "description": str,
        "gpio_port": int, 
        "normally_open": bool
    }
    args = request.args
    results = []
    with open("relay.json") as relays:
        relays = json.load(relays)
        try:
            if all(k in args for k in ['k', 'v']):
                userkey = args.get('k')
                userval = types[userkey](args.get('v'))
                for relay in relays:
                    if relay[userkey] == userval:
                        results.append(relay)
            else:
                results = relays
            return jsonify(results)
        except KeyError as error:
            print(dir(error))
            return jsonify(
                message="key does not exist",
                category="error",
                status=404
            )

app.run()