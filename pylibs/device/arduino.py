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

UDEV_RULES='/etc/udev/rules.d/99-platformio-udev.rules'

BOARD_MAP = {
    'uno': [
        'Arduino Uno'
    ]
}
class ArduinoInfo(object):

    @classmethod 
    def __arduino_connected(cls,
    ) -> bool:
        """__arduino_connected determine if an arduino board is connected via USB/serial

        Returns:
            bool: True if an arduino is located, False otherwise
        """
        context = Context()
        for device in context.list_devices(subsystem='tty'):
            if device.get('ID_SERIAL', None) is None:
                continue
            serial = device.get('ID_SERIAL')
            if 'arduino' in serial:
                return True
            else:
                return False

    @classmethod 
    def __arduino_device(cls,
    ) -> Union[Device, bool]:
        """__arduino_device get a reference to the OS device which represents the connected arduino

        Returns:
        
            Union[Device, bool]: a pyudev Device or False
        """
        context = Context()
        for device in context.list_devices(subsystem='tty'):
            if device.get('ID_SERIAL', None) is None:
                continue
            serial = device.get('ID_SERIAL')
            if 'arduino' in serial:
                return device
            else:
                return False
        return False
            

        
    def __init__(self
    ) -> None:
        if self.__class__.__arduino_connected():
            self.error = False
            self.device = self.__class__.__arduino_device()
            self.device_node = self.device.device_node
        else:
            self.error = True

        if os.path.exists(UDEV_RULES):
            self.enhanced = True

            for k, v in self.device.items():
                setattr(self, k.lower(), v)
            
