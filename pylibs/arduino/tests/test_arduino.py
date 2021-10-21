import os
import sys
import pytest
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-3])
sys.path.append(libs)

from pylibs.arduino.programmer import (
    ArduinoMakeFile,
    ArduinoProgrammer
)


programmer = ArduinoProgrammer()


REQUIRED_KEYS = [
    'arduino_dir', 'arduino_libs', 'arduino_port', 'arduino_core_path',
    'board_tag', 'board_txt', 'bootloader_parent', 'user_lib_path'
]

@pytest.fixture
def makefile():
    return ArduinoMakeFile(target_path='/tmp')

@pytest.fixture
def programmer():
    return ArduinoProgrammer()

def test_makefile_object(makefile):
    assert isinstance(makefile.to_dict(), dict)
    assert isinstance(makefile.to_make(), str)

def test_makefile_keys(makefile):
    assert all(key in makefile.to_dict()
               for key in REQUIRED_KEYS
    )

def test_makefile_values(makefile):
    makefile_dict = makefile.to_dict()
    assert all(
        isinstance(value, str) for attr, value in makefile_dict.items() if attr != 'error'
    )

    
    # all(k in args for k in ['find_by', 'value'])