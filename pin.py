from gpiozero import *
import time
import json
from RPi import GPIO
from bs4 import BeautifulSoup
import requests

from urllib.parse import (
    urlparse, 
    urljoin)

##GPIO.setmode(GPIO.BCM)
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

factory = Device._default_pin_factory()

j8 = pi_info().headers['J8']
gpiopins = j8.pins


def pinout(pin: int = None, label: str = None):
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

def pindata(pin: int = None, label: str = None):
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
    pin_url = pinout(pin, label)
    response = requests.get(pin_url)
    html = BeautifulSoup(response.text, 'html.parser')
    article = html.find('article', class_="{}".format(articleid))
    if parser == "gpiopin":
        funcs = [i.string for i in article.contents[1].find_all('td')]
        if None in funcs:  
            funcs.remove(None)
        #print(funcs)  
        return {
            "title" : article.contents[0].string,
            "descr": "{}".format(articleid),
            "funcs" : funcs
        }
    else:
        desc = list(filter(
            lambda x: type(x.string) is not type(None),
            list(article.find_all('p'))
        ))

        return {
            "title": "{}".format(article.contents[0].string),
            "descr": " ".join([i.string.replace("\n", " ") for i in desc]),
            "funcs": "this is a {} pin!!!".format(parser)
        }

    
    #return article


# for pin in gpiopins.values():
#     #time.sleep(1)
    
#     print({
#         'label': pin.function,
#         #'function': factory.pin_class(factory, pin.number).function,
#         'header_row': pin.row,
#         'header_col': pin.col,
#         'info_url': pinout(pin.number, pin.function),
#         'data': pindata(pin.number, pin.function)
#     })


pinmap = {
   str(pin.number): {
        'label': pin.function,
        # 'function': factory.pin_class(factory, pin.number).function,
        'header_row': pin.row,
        'header_col': pin.col,
        'info_url': pinout(pin.number, pin.function),
        'data': pindata(pin.number, pin.function)
    } for pin in gpiopins.values()
}


pinmap = dict(sorted(
    pinmap.items(),
    key=lambda x: x[0]
))
print(json.dumps(pinmap))
#print(pinmap)
