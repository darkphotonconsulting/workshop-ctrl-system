from gpiozero import *
import time
import json
from json import JSONEncoder
from RPi import GPIO
from bs4 import BeautifulSoup
import requests
import re
from uuid import uuid4

from urllib.parse import (
    urlparse,
    urljoin)


class PiInfoEncoder(JSONEncoder):
    """JSON Encoder class for PiInfo objects

    @Inherits:
        JSONEncoder : This class inherits from JSONEncoder, overriding the default method
        - allows a PiInfo object to be JSON encoded
    """
    def default(self, object, klass):
        if isinstance(object, klass):
            return object.__dict__
        else:
            return JSONEncoder.default(
                self,
                object
            )
class PiInfo(object):
    """Data container class for Raspberry Pi static system information

    @Args:
        None

    @Returns:
        A PiInfo object
    """

    data = pi_info()



    def __init__(self):
        """initializes a PiInfo object for the running system (supports Raspberry 4 B+)"""
        data = self.__class__.data
        factory = Device._default_pin_factory()
        self.GPIO_FUNCTIONS = {
        'input':   GPIO.IN,
        'output':  GPIO.OUT,
        'i2c':     GPIO.I2C,
        'spi':     GPIO.SPI,
        'pwm':     GPIO.HARD_PWM,
        'serial':  GPIO.SERIAL,
        'unknown': GPIO.UNKNOWN,
        }

        self.GPIO_PULL_UPS = {
        'up':       GPIO.PUD_UP,
        'down':     GPIO.PUD_DOWN,
        'floating': GPIO.PUD_OFF,
        }

        self.GPIO_EDGES = {
        'both':    GPIO.BOTH,
        'rising':  GPIO.RISING,
        'falling': GPIO.FALLING,
        }


        self.headers = list(
            data.headers.keys()
        )

        j8 = data.headers['J8']
        poe = data.headers['POE']
        self.poepins = poe.pins
        self.gpiopins = j8.pins
        self.system = {
            'manufacturer': data.manufacturer,
            'system': "Raspberry Pi {} ({})".format(data.model, data.revision),
            'released': data.released,
            'model': data.model,
            'revision': data.revision,
            'soc': data.soc,
            'pcb_revision': data.pcb_revision,
            'memory': data.memory,
            'storage': data.storage,
            'ethernet_speed': data.eth_speed,
            'has_wifi': data.wifi,
            'has_bluetooth': data.bluetooth,
            'usb_ports': data.usb,
            'usb3_ports': data.usb3,
            'board_headers': list(data.headers.keys())
        }
        pinmap = {
            str(pin.number): {
                'label': pin.function,
                'header_row': pin.row,
                'header_col': pin.col,
                'info_url': self.__class__.__pinout(pin.number, pin.function),
                'data': self.__class__.__pindata(pin.number, pin.function)
            }
            for pin in self.gpiopins.values()
        }
        self.pinmap = dict(sorted(pinmap.items(), key=lambda x: x[0]))
        self.gpios = [i for i in self.pinmap.values()]
        self.pimap = {'system': self.system, 'gpio': self.gpios}

    def to_json(self):
        """Standard to_json method"""
        return json.dumps(self.__dict__,
                          cls=PiInfoEncoder,
                          indent=2,
                          sort_keys=True)


    @classmethod
    def __pinout(cls,pin: int = None, label: str = None):
        """Derives pinout URL based on BCM board number and pin label

        Args:
            pin (int, optional): Pin number
            label (str, optional): Pin label

        Returns:
            str - pinout.xyz URL for given pin
        """
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
    def __pindata(cls, pin: int = None, label: str = None) -> dict:
        """pindata - Enriches the PiInfo.gpios entry for each GPIO by scraping pinout.xyz for valuable information

        Scrapes pinout.xyz to enrich PiInfo object with mappings of additional data _not_ found from board itself for each pin on the J8 header
            - GPIO functions (PWM, I2C, etc)
            - variant board addresses (BCM, Wiring Pi, Board)
            - description
            - title (as seen on pinout.xyz)

        Output Example

        {
            "boardmap": {
                "gpio_bcm": "The GPIO/BCM address",
                "physical_board: "physical board address",
                "wiring_pi": "wiring pi address"
            },
            "descr": "description from pinout.xyz",
            "funcs : [
                "detailed function list",
                "str",
                "str",
                ...
            ],
            "title : "article title from pinout.xyz" 
        }

        Args:
            pin (int, optional): [The pin number to return data for]. Defaults to None.
            label (str, optional): [The pin label to return data for]. Defaults to None.

        Returns:
            dict: pin data dict
        """
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
        pin_url = cls.__pinout(pin, label)
        response = requests.get(pin_url)
        html = BeautifulSoup(response.text, 'html.parser')
        article = html.find('article', class_="{}".format(articleid))
        if parser == "gpiopin":
            #print("CONT: ".format(article.contents))
            pin_map_rgx = r".*pin\s(\d+)"
            key_map_rgx = r"(.+) .*pin\s.+"
            phys_key, gpio_key, wiringpi_key = [
                re.search(key_map_rgx, i.string).group(1) for i in article.contents[2].find_all('li')
            ][0:3]
            # fix key names to not have spaes or odd characters
            phys_key = re.sub(r'[/\s]', '_', phys_key).lower()
            gpio_key = re.sub(r'[/\s]', '_', gpio_key).lower()
            wiringpi_key = re.sub(r'[/\s]', '_', wiringpi_key).lower()
            phys_val, gpio_val, wiringpi_val = [
                re.search(pin_map_rgx, i.string).group(1) for i in article.contents[2].find_all('li')
            ][0:3]
            boardmap = dict(
                list(
                    zip(
                        [
                            phys_key, gpio_key, wiringpi_key
                        ],
                        [
                            int(phys_val), int(gpio_val), int(wiringpi_val)
                        ]
                    )
                )
            )

            # add a uuid in boardmap for better mongoing
            boardmap['uuid'] = str(uuid4())
            #add a better description...
            desc = list(
                filter(lambda x: type(x.string) is not type(None),
                       list(article.find_all('p'))))

            if len(desc) > 0:
                description_text = " ".join([
                    i.string.replace("\n", " ").replace("\"", "") for i in desc
                ])
            else:
                description_text = "General Purpose (IO)"

            funcs = [i.string for i in article.contents[1].find_all('td')]
            if None in funcs:
                funcs.remove(None)

            return {
                "title": article.contents[0].string,
                "descr": description_text,
                "funcs": funcs,
                "boardmap": boardmap,
                "uuid": str(uuid4())
                #"id"
            }
        else:
            print(f"processing {label} as a power pin")
            desc = list(filter(
                lambda x: type(x.string) is not type(None),
                list(article.find_all('p'))
            ))
            print(f"got description: {desc}")

            return {
                "title": "{}".format(article.contents[0].string),
                "descr": " ".join([i.string.replace("\n", " ") for i in desc]),
                "funcs": ["{}".format(parser)],
                "boardmap": {
                    "physical_board": -1,
                    "gpio_bcm" : -1,
                    "wiring_pi": -1,
                    "uuid": str(uuid4())
                },
                "uuid": str(uuid4())
            }