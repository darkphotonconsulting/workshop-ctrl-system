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
    loads
)
from sys import (
    stdout,
    stderr,
    path,
    modules
)
from types import (
    FunctionType
)
from typing import (
    Any,
    Union,
    Optional
)


from pymata4.pymata4 import Pymata4


current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
path.append(libs)

from pylibs.device.arduino import (
    ArduinoInfo
)

from pylibs.config.configuration import (
    ConfigLoader,
    Configuration
)

config = Configuration(
    **ConfigLoader(
        from_file=True, 
        config='settings/config.json'
    ).all()
)


class ArduinoController(object):
    modes = {
        0x00: "DIN",  # digital input
        0x01: "DO",   # digital output
        0x02: "AIN",  # analog input
        0x03: "PWM",  # pwm output
        0x04: "SRV",  # servo output
        0x05: "SFT",  # shift
        0x06: "I2C",  # I2C
        0x07: "WIR",  # ONEWIRE
        0x08: "STP",  # STEPPER
        0x09: "ENC",  # ENCODER
        0x0A: "SRL",  # SERIAL
        0x0B: "INP",  # INPUT_PULLUP
        0x0C: "SPI",   # SPI
        0x0D: "SONAR", # Sonar 
        0x0E: "TONE", # Tone
        0x0F: "DHT", # DHT Device
    }
    pin_modes = {
        0x00: "INPUT",
        0x01: "OUTPUT",
        0x02: "ANALOG INPUT",
        0x03: "PWM OUTPUT",
        0x04: "SERVO OUTPUT",
        0x06: "I2C",
        0x08: "STEPPER",
        0x0b: "PULLUP",
        0x0c: "SONAR",
        0x0d: "TONE",
    }
    def __init__(self,
        config: Configuration = config
    ):
        self.configuration = config
        self.active_digital_pins = []
        self.active_analog_pins = []
        self.info = ArduinoInfo(config=config)
        self.board = self.info.board
        self.arduino_config = config.arduino


    def get_pin_count(self,
        mode: str = None,
    ):
        if mode == 'digital': 
            return len(self.info.digital_pins)
        if mode == 'analog':
            return len(self.info.analog_pins)
        if mode is None:
            return len(self.info.digital_pins) + len(self.info.analog_pins)
        
    def get_pin_capabilities(self,
        pin: int = None
    ):
        #print('modes: ', self.__class__.modes)
        report = {}
        capabilities = self.board.get_capability_report()
        k = 0
        pin_idx = 0
        while k < len(capabilities):
            
            report[pin_idx] = dict()
            while capabilities[k] < 127:
                #print('pin: ', pin, 'k: ', k, 'capabilities: ', capabilities[k])
                report[pin_idx][self.__class__.modes[ capabilities[k]]] = capabilities[k+1]
                k += 2
            k+=1
            pin_idx+=1

                
        pin_cap = report.get(pin, None)
        if isinstance(pin_cap, dict): 
            return list(pin_cap.keys())
        else: return None

    def close_connection(self,
    ):
        self.board.shutdown()


    def reset_connection(self,
    ):
        self.close_connection()
        self.info = ArduinoInfo(config=self.configuration)
        self.board = self.info.board

    def write_pin(self,
        pin: int = None,
        value: Union[int,float] = None,
        mode: str = None
    ):
        if mode == 'digital':
            print('digital mode')
            try:
                self.set_pin_mode(
                    pin=pin,
                    mode='digital',
                    direction='output',
                )
                start_state = self.get_pin_state(pin=pin)
                self.board.digital_write(pin=pin, value=value)
                end_state = self.get_pin_state(pin=pin)
                print('start: ', start_state, 'end: ',end_state)
                
                # if start_state[-1] != end_state[-1]: #verify the pin state changed
                #     return True
                # else: return False
            except:
                return False
        elif mode == 'pwm':
            try:
                start_state = self.get_pin_state(pin=pin)
                self.board.pwm_write(pin=pin, value=value)
                end_state = self.get_pin_state(pin=pin)
                # if start_state[-1] != end_state[-1]: #verify the pin state changed
                #     return True
                # else: return False
            except:
                return False
            
            

    def get_pin_state(self,
        pin: int = None
    ):
        pin_state = self.board.get_pin_state(pin=pin)
        if len(pin_state)==3:
            return (
                self.__class__.pin_modes[pin_state[1]],
                self.__class__.modes[pin_state[-1]],
            )

    def set_pin_mode(self,
        pin: int = None,
        mode: str = None,
        direction: str = None,
        callback = None,
    ):  
        if mode == 'digital' and direction == 'output':
            self.board.set_pin_mode_digital_output(
                pin_number=pin       
            )

        if mode == 'digital' and direction == 'input':
            if callback is not None and type(callback).__name__ == 'function':
                self.board.set_pin_mode_digital_input(
                    pin_number=pin,
                    callback=callback,
                )
            else:
                self.board.set_pin_mode_digital_input(
                    pin_number=pin,
                )


        if mode == 'analog' or 'pwm' and direction == 'input':
            if callback is not None and type(callback).__name__ == 'function':
                self.board.set_pin_mode_analog_input(
                    pin_number=pin,
                    callback=callback,
                )
            else:
                self.board.set_pin_mode_analog_input(
                    pin_number=pin,
                )