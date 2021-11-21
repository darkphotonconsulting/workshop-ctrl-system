""" Arduino Info
"""
import os 
import sys
import json
import subprocess
from pyudev import Context, Device, Devices
from glob import glob
from copy import copy
from typing import (
    Union, 
    Optional
)

from pymata4.pymata4 import Pymata4
# access pylibs path
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
sys.path.append(libs)

from pylibs.device.avrdude import (
    processconfig,
    sig,
    validatesig
)
from pylibs.constants.constants import (
    ARDUINO_BOARDS,

)
from pylibs.config.configuration import (
    ConfigLoader, 
    Configuration
)

from pylibs.coders.encode import ArduinoInfoEncoder


UDEV_RULES='/etc/udev/rules.d/99-platformio-udev.rules'

BOARD_MAP = {
    'uno': [
        'Arduino Uno'
    ]
}
class ArduinoInfo(object):
    """ArduinoInfo an object containing information about the connected Arduino
    """
    loader = ConfigLoader(
        from_file=True,
        config='settings/config.json'
    )
    configuration = Configuration(**loader.arduino)

    @classmethod
    def __get_attribute(
        cls,
        obj,
        attrib: str = None
    ) -> bool:
        """__add_attribute return a class attribute of an object


        Args:
            obj (object): The python object to add attributes to
            
            attrib (str, optional): The attribute name. Defaults to None.
            


        Examples:
        
            cls.__get_attribute(
                obj=obj,
                attrib='foo',
            )
            
        Returns:
            Any: the attribute value
        """
        try:
            return getattr(obj, attrib)
        except:
            return False
             
    @classmethod
    def __add_attribute(
        cls,
        obj,
        attrib: str = None,
        value: Union[list, dict, str, int, bool] = None,
    ) -> bool:
        """__add_attribute Add a class attribute to an object

        Adds a class attribute with a value to the user-provided python object

        Args:
            obj (object): The python object to add attributes to
            attrib (str, optional): The attribute name. Defaults to None.
            value (Union[list, dict, str, int, bool], optional): The attribute value. Defaults to None.

        Examples:
        
            cls.__add_attribute(
                obj=obj,
                attrib='foo',
                value='bar'
            )
            
        Returns:
            bool: True if values added, False if otherwise
        """
        try:
            setattr(obj, attrib, value)
            return True
        except:
            return False

    @classmethod
    def __add_getter(
        cls,
        obj,
        attrib: str = None,
    ):
        """__add_getter adds a getter for the given attribute to a class object


        Args:
            obj ([type]): Object to add getter method to
            
            attrib (str, optional): attribute the getter will return. Defaults to None.
        """
        def getter():
            return getattr(obj, attrib)
        
        setattr(obj, f"get_{attrib}", getter)

    @classmethod
    def __add_setter(
        cls,
        obj,
        attrib: str = None,
        value: Union[dict, str, int, bool] = None,

    ):
        """__add_setter adds a setter for the given attrib to a class object

        Args:
            obj ([type]): the object to add the setter method to
            
            attrib (str, optional): [description]. the name of the attribute this method sets
            
            value (Union[dict, str, int, bool], optional): [description] some value
            
        """
        def setter(value: str = None):
            setattr(obj, attrib, value)
        setattr(obj, f"set_{attrib}", setter)

    @classmethod
    def __add_setters(cls,
        obj,
        attribs: dict = None
    ):
        """__add_setters adds setters for all keys defined in some dict

        Args:
            obj ([type]): object to add setters to
            
            attribs (dict, optional): attribute dictionary. Defaults to None.
        """
        for k,v in attribs.items():
            if isinstance(v, dict):
                cls.__add_setter(obj=obj, attrib=k, value=v)
                cls.__add_setters(obj=obj, attribs=attribs[k])
            else:
                cls.__add_setter(obj=obj, attrib=k, value=v)

    @classmethod
    def __add_getters(
        cls,
        obj,
        attribs: dict = None
    ):
        """__add_getters add getters to object defined in attribs dictionary

        Args:
            obj ([type]): [description]
            
            attribs (dict, optional): [description]. Defaults to None.
        """
        for k, v in attribs.items():
            if isinstance(v, dict): 
                cls.__add_getter(obj, attrib=k)
                cls.__add_getters(obj, attribs=attribs[k])
            else:
                cls.__add_getter(obj, attrib=k)

    @classmethod
    def __add_attributes(
        cls,
        obj,
        attribs: dict = None,
    ):
        """__add_attributes Iterates through a dictionary recursively adding each key and value as a class attribute

        For each key-value pair found in a recursrive, add a class attribute correlating to the 
        key and value of a python object based on the provided `attribs` python dictionary.

        Examples:
            cls.__add_attributes(
                obj=obj,
                attribs=obj.config
            )
        Args:
            obj ([obj]): Any object, however This _should_ be an instance of ConfigLoader<class<object>>
            attribs (dict, optional): The dict attributes object, should be the `ConfigLoader.config`<dict>. Defaults to None.

        Returns:
            obj: returns a reference to the modified object.
        """
        for k, v in attribs.items():
            if isinstance(v, dict):
                cls.__add_attribute(obj=obj, attrib=k, value=v)
                #setattr(obj, k, v)
                cls.__add_attributes(obj=obj, attribs=v)
                #return obj
            else:
                cls.__add_attribute(obj=obj, attrib=k, value=v)
        return obj

    
    @classmethod
    def __arduino_confs(cls,
    ) -> list:
        """__arduino_confs returns a list of lines from ARDUINO_BOARDS text file



        Returns:
            list: relevant lines from boards.txt
        """
        boards = ARDUINO_BOARDS
        if os.path.exists(boards):
            with open(boards, 'r') as file:
                data = [line.strip() for line in file.readlines() if "=" in line]
                return data

    @classmethod
    def __parse_arduino_conf(cls,
        data: list = None
    ) -> dict:
        """__parse_arduino_conf parse boards.txt to a dictionary


        Args:
            data (list, optional): a list of lines from the boards.txt . Defaults to None.

        Returns:
            dict: representation of boards.txt
        """
        ret = {}
        if data is None:
            data = cls.__arduino_confs()
        for item in data:
            key_part, value_part = item.split('=')
            dots = key_part.split('.')
            dotslen = len(dots)
            if dotslen == 2: # name
                board, name = dots
                if board not in ret:
                    ret[board] = {}
                    ret[board][name] = value_part
                    #print(ret)
            if dotslen == 3: #nested
                board, category, k = dots
                if board in ret:
                    if category not in ret[board]:
                        ret[board][category] = {}
                    ret[board][category][k] = value_part
        return ret

    @classmethod
    def __arduino_conf(cls,
        confs: dict = None,
        arduino_board: str = None,
    ) -> dict:
        """__arduino_conf extract board configuration for provided arduino_board

        Args:
            confs (dict, optional): optionally pass in the dict representation of boards.txt. Defaults to None.
            
            arduino_board (str, optional): a board name, ex: atmega2500. Defaults to None.

        Returns:
        
            dict: [description]
        """
        if confs is None:
            confs = cls.__parse_arduino_conf()
        return confs.get(arduino_board, {})
    
    @classmethod 
    def __arduino_connected(cls,
        search: str = None
    ) -> bool:
        """__arduino_connected determine if an arduino board is connected via USB/serial

        Returns:
            bool: True if an arduino is located, False otherwise
        """
        context = Context()
        for device in context.list_devices(subsystem='tty'):
            if device.get('ID_MODEL_FROM_DATABASE', None) is None:
                continue
            serial = device.get('ID_MODEL_FROM_DATABASE')
            if search in serial:
                return True
            else:
                return False

    @classmethod 
    def __arduino_device(cls,
        search: str = None
    ) -> Union[Device, bool]:
        """__arduino_device get a reference to the OS device which represents the connected arduino

        Returns:
        
            Union[Device, bool]: a pyudev Device or False
        """
        context = Context()
        for device in context.list_devices(subsystem='tty'):
            if device.get('ID_MODEL_FROM_DATABASE', None) is None:
                continue
            serial = device.get('ID_MODEL_FROM_DATABASE')
            if search in serial:
                return device
            else:
                return False
        return False
            

        
    def __init__(self,
        config: Configuration = None
    ) -> None:
        """__init__ Create an ArduinoInfo object

        Args:
        
            config (Configuration, optional): [description]. Defaults to None.
        """
        config = self.__class__.configuration if config is None else config            
        self.arduino_board_name =  config.arduino_board_name if hasattr(config, 'arduino_board_name') else None
        self.avrdude_part_id =  config.avrdude_part_id if hasattr(config, 'avrdude_part_id') else None
        self.udev_board_search = config.udev_board_search if hasattr(config, 'udev_board_search') else None
        
        if self.__class__.__arduino_connected(search=self.udev_board_search):
            self.error = False
            self.connected = True
            self.device = self.__class__.__arduino_device(search=self.udev_board_search)
            self.device_node = self.device.device_node
            #self.arduino_boards = self.__class__.__parse_arduino_conf()
            arduino_board = self.__class__.__arduino_conf(
                arduino_board=self.arduino_board_name
            )
            
            if 'name' in arduino_board: # arduino boards attributes
                self.__class__.__add_attributes(obj=self, attribs=arduino_board)

            avrconf = processconfig()
            self.part = avrconf['parts'][self.avrdude_part_id]

            if os.path.exists(UDEV_RULES): # udev labels
                self.enhanced = True
                for k, v in self.device.items():
                    setattr(self, k.lower(), v)


            # firmata data
            board = Pymata4()
            self.board = board
            #print(dir(self.board))
            #print(type(self.board))
            self.analog_pins = [i for i,analog in enumerate(board.get_analog_map()) if analog != 127]
            self.digital_pins = [i for i,analog in enumerate(board.get_analog_map()) if analog == 127]                
        else:
            self.error = True


    def to_json(self,
    ) -> str:
        """to_json return a JSON string representing object


        Returns:
            str: [description]
        """
        return json.dumps(
            self.__dict__, 
            indent=2,
            cls=ArduinoInfoEncoder
        )

