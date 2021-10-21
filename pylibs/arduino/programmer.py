import os
import sys
import subprocess
import shutil
import json
from shlex import shlex
from time import time
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
from pyudev import Context, Device
from glob import glob
from copy import copy
#import tempfile
from tempfile import (
    TemporaryDirectory,
    TemporaryFile
)

from pymata4.pymata4 import Pymata4

from SCons.Script import (
#    Environment, 
    DefaultEnvironment, 
#    DEFAULT_TARGETS,
#    AlwaysBuild, 
#    Default, 
#    Import, 
    Variables, 
#    ARGUMENTS
)  # pylint: disable=import-eror
import re


#from jinja2 import Template
from platformio import fs
from platformio.proc import get_pythonexe_path
#from platformio.platform.base import PlatformBase
from platformio.builder.tools.pioproject import (
    # GetProjectConfig, 
    # GetProjectOption, 
    # GetProjectOptions, 
    ProjectConfig, 
    # LoadProjectOptions
)
#from platformio.builder.tools.piomisc import InoToCPPConverter, ConvertInoToCpp
# from platformio.builder.tools.pioplatform import (
#     PioPlatform, 
#     BoardConfig, 
#     GetFrameworkScript, 
#     LoadPioPlatform, 
#     PrintConfiguration
# )
# from platformio.builder.tools.pioupload import (
#     FlushSerialBuffer,
#     TouchSerialPort,
#     WaitForNewSerialPort,
#     AutodetectUploadPort,
#     UploadToDisk,
#     CheckUploadSize,
#     PrintUploadInfo
# )
from platformio.project.helpers import (
    get_project_dir,
)


SKETCH_FILE = "FirmataExpress.cpp"
SKETCH_DEPENDENCIES = [
    'FirmataExpress'
]
SKETCH_LIBRARIES = [
    'DHTStable', 
    'FirmataExpress', 
    'Ultrasonic', 
    'Wire', 
    'Servo', 
    'Stepper', 
]
    

@contextmanager
def chdir(path: Path = None):
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


class MakeFile(object):
    """MakeFile Does nothing
    """
    pass
class ArduinoMakeFile(MakeFile):
    """ArduinoMakeFile Abstracts creation of Makefile for the arduino-mk OS package

    [extended_summary]

    Args:
        MakeFile ([type]): [description]

    Returns:
        [type]: [description]
    """

    MASKED = ['error', 'ardmk_file']
    FIRMATA_DEPENDS = [
        #'gaitolini/SoftwareSerial@1.0', 
        #'featherfly/SoftwareSerial@^1.0'
        #'Firmata@2.5.5',
        #'arduino-libraries/Servo@1.1.8'
        'FirmataExpress',
    ]
    #USER_LIBS = "SoftwareSerial SoftwareSerial/include Firmata Firmata/utility Wire Servo"
    USER_LIBS = "DHTStable FirmataExpress Ultrasonic Wire Servo Stepper"
    ARDUINO_LIBS = [
        'DHTStable', 
        'FirmataExpress', 
        'Ultrasonic', 
        'Wire', 
        'Servo', 
        'Stepper',
    ]

    def __init__(self,
        board_tag: str = None,
        device_port: str = None,
        arduino_dir: str = None,
        arduino_make_files: str = None,
        board_protocol: str = None,
        bootloader: str = None,
        variant: str = None,
        target_path: str = None,
        user_lib_path: str = None,
        arduino_libs: list = None,
        user_libs: list = None,

    ) -> None:
        if target_path is not None:
            board_tag = "mega2560" if board_tag is None else board_tag
            device_port = "/dev/ttyacm0" if device_port is None else device_port
            bootloader = "stk500v2" if bootloader is None else bootloader
            variant = "mega" if variant is None else variant
            self.arduino_dir = "/usr/share/arduino" if arduino_dir is None else arduino_dir
            self.arduino_core_path =  os.path.join(self.arduino_dir, "hardware/arduino/cores/arduino")
            #target = standardfirmata         # the same as your ino file name
            self.board_tag    = board_tag           # can also be mega2560
            self.arduino_port = device_port  # be sure to change this to the port used by your board
            self.monitor_port = device_port
            self.isp_port = device_port
            self.ardmk_dir = self.arduino_dir if arduino_make_files is None else arduino_make_files
            self.ardmk_file = os.path.join(self.ardmk_dir, "Arduino.mk")
            self.user_lib_path = os.path.join(target_path, 'libraries') if user_lib_path is None else user_lib_path
            # make ARDUINO_LIBS a list and use this for the ARDUINO_LIBS parameter 
            self.arduino_libs = " ".join(self.__class__.ARDUINO_LIBS) if user_libs is None else " ".join(user_libs)
            #self.user_libs = self.__class__.USER_LIBS if user_libs is None else user_libs
            
            self.avr_tools_path = os.path.join(self.arduino_dir,
                                            "hardware/tools/avr/bin")
            self.avr_dude = os.path.join(self.arduino_dir, "hardware/tools/avrdude")
            self.avrdude_ard_programmer = "wiring" if board_protocol is None else board_protocol
            self.avrdude_conf = os.path.join(self.arduino_dir,
                                            "hardware/tools/avrdude.conf")
            self.board_txt = os.path.join(self.arduino_dir, "hardware/arduino/boards.txt")
            #architecture = avr
            self.bootloader_parent = os.path.join(self.arduino_dir, "hardware/arduino/bootloaders", bootloader)
            self.arduino_var_path = os.path.join(self.arduino_dir, "hardware/arduino/variants")
            self.error = False
        else:
            self.error = True

    def to_dict(self,
    ) ->dict:
        return dict(sorted(self.__dict__.items(), key=lambda k: k[0]))

    def to_json(self,
    ) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def print_json(self,
    ) -> None:
        print(json.dumps(self.to_dict(), indent=2))

    def to_make(self,
    ) -> str:
        make = f"# Arduino Makefile compiled by {self.__class__.__name__} on {str(datetime.now())}\n" +"\n".join([
            f"{k.upper()}={v}" for k, v in self.to_dict().items()
            if k not in self.__class__.MASKED
        ]) + f"\ninclude {self.ardmk_file}"
        return make

    def print_make(self,
    ) -> None:
        make = f"# Arduino Makefile compiled by {self.__class__.__name__} on {str(datetime.now())}\n" + "\n".join([
            f"{k.upper()}={v}" for k, v in self.to_dict().items()
            if k not in self.__class__.MASKED
        ]) + f"\ninclude {self.ardmk_file}"
        print(make)

    def make(self,
      target_path: str = None
    ) -> bool:
        if target_path is not None:
            if os.path.exists(target_path):
                with open(target_path, 'w') as file:
                    file.write(self.to_make)

#include /usr/share/arduino/Arduino.mk
class ArduinoProgrammer(object):

    VARS = Variables((
        ('PLATFORM_MANIFEST', ),
        ('BUILD_SCRIPT', ),
        ('PIOENV', 'arduino_mega'),
        ('PIOTEST_RUNNING_NAME', ),
        ('UPLOAD_PORT', ),
    ))
    CMD_STRINGS = dict(
        ARCOM="Archiving",
        LINKCOM="Linking",
        RANLIBCOM="Indexing",
        ASCOM="Compiling",
        ASPPCOM="Compiling",
        CCCOM="Compiling",
        CXXCOM="Compiling",
    )
    DEFAULT_ENV_OPTIONS = dict(
        tools=[
            "ar",
            "as",
            "cc",
            "c++",
            "link",
            "platformio",
            "piotarget",
            "pioplatform",
            "pioproject",
            "piomaxlen",
            "piolib",
            "pioupload",
            "piomisc",
            "pioide",
            "piosize",
        ],
        toolpath=[os.path.join(fs.get_source_dir(), "builder", "tools")],
        variables=VARS,
        # Propagating External Environment
        ENV=os.environ,
        UNIX_TIME=int(time()),
        BUILD_DIR=os.path.join("$PROJECT_BUILD_DIR", "$PIOENV"),
        BUILD_SRC_DIR=os.path.join("$BUILD_DIR", "src"),
        BUILD_TEST_DIR=os.path.join("$BUILD_DIR", "test"),
        COMPILATIONDB_PATH=os.path.join("$BUILD_DIR", "compile_commands.json"),
        LIBPATH=["$BUILD_DIR"],
        #PROGNAME="program",
        PROG_PATH=os.path.join("$BUILD_DIR", "$PROGNAME$PROGSUFFIX"),
        PYTHONEXE=get_pythonexe_path(),
        IDE_EXTRA_DATA={},
    )
    HOME_DIR = os.path.dirname(os.path.abspath(__file__))
    ARDUINO_HOME = '/usr/share/arduino'
    ARDUINO_CORE = os.path.join(ARDUINO_HOME, 'hardware/arduino/cores/arduino')
    ARDUINO_SKEL = os.path.join(ARDUINO_CORE, 'main.cpp')
    ARDUINO_HEADER = os.path.join(ARDUINO_CORE, 'Arduino.h')
    ARDUINO_LIBRARIES = os.path.join(ARDUINO_HOME, 'libraries')
    # switching to firmata express
    #FIRMATA_FILE = "StandardFirmata.cpp"
    FIRMATA_FILE = "FirmataExpress.cpp"
    FIRMATA_DEPENDS = [
        #'featherfly/SoftwareSerial@^1.0'
        'FirmataExpress'
        #'arduino-libraries/Servo@1.1.8'
    ]
    #USER_LIBS = "SoftwareSerial SoftwareSerial/include Firmata Firmata/utility Wire Servo"
    #USER_LIBS = "DHTStable FirmataExpress Ultrasonic Wire Servo Stepper"
    USER_LIBS = [
       'DHTStable', 
       'FirmataExpress', 
       'Ultrasonic', 
       'Wire', 
       'Servo', 
       'Stepper', 
    ]
    


    ARDUINO_SKETCH_EXTENSION = '.ino'

    AVR_HOME = os.path.join(ARDUINO_HOME, 'hardware/tools/avr/bin')
    AVR_BIN_PREFIX = os.path.join(AVR_HOME, 'avr-')
    AVR_DUDE_HOME = os.path.join(ARDUINO_HOME, 'hardware/tools')
    AVR_DUDE_CONF = os.path.join(AVR_HOME, 'avrdude.conf')
    CC_FLAGS = [
        "-std=gnu11",
        "-fno-fat-lto-objects",
        "-Os",
        "-Wall",
        "-ffunction-sections",
        "-fdata-sections",
        "-flto",
        #"-mmcu=atmega2560"
    ]
    CXX_FLAGS = [
        "-fno-exceptions",
        "-fno-threadsafe-statics",
        "-fpermissive",
        "-std=gnu++11",
        "-Os",
        "-Wall",
        "-ffunction-sections",
        "-fdata-sections",
        "-flto",
        #"-mmcu=atmega2560"
    ]
    CPP_DEFAULT_DEFINES = [
        "PLATFORMIO=50200", "ARDUINO_AVR_MEGA2560", "F_CPU=16000000L",
        "ARDUINO_ARCH_AVR", "ARDUINO=10808", "__AVR_ATmega2560__"
    ]
    #LIBRARIES = ARDUINO_LIBS

    @classmethod
    def __arduino_confs(cls,
    ) -> list:
        boards = os.path.join(cls.ARDUINO_HOME, 'hardware/arduino/boards.txt')
        if os.path.exists(boards):
            with open(boards, 'r') as file:
                data = [line.strip() for line in file.readlines() if "=" in line]
                return data

    @classmethod
    def __parse_arduino_conf(cls,
        data: list = None
    ) -> dict:
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
        arduino_board: str = "mega2560",
    ) -> dict:
        if confs is None:
            confs = cls.__parse_arduino_conf()
        return confs.get(arduino_board, {})


    @classmethod
    def __arduino_runs_firmata(cls,
    ) -> bool:
        board = Pymata4()
        if isinstance(board.get_protocol_version(), str):
            return True
        else:
            return False

    @classmethod
    def __arduino_connected(cls,
    ) -> bool:
        """__arduino_connected Determine if an Arduino Board is connected


        Returns:
        
            bool: True if board found, False if not found, False if multiple boards found
        """
        context = Context()
        boards = []
        for device in context.list_devices(subsystem='tty'):
            #print(dir(device))
            if device.get('ID_SERIAL', None) is None:
                continue

            serial = device.get('ID_SERIAL')
            if 'arduino' in serial:
                boards.append(device)

        if len(boards) == 0: # no boards found
            return False
        elif len(boards) == 1: # one board connected
            return True
        elif len(boards) > 1: # multiple boards found
            return False
        else: # not a number or negative boards found?
            return False


    @classmethod
    def __arduino_device(cls,
    ) -> Device:
        """__arduino_device returns the linux device associated associated with the Arduino eg: Device(/dev/ttyUSB0)

        Returns:
        
            Device: the pyudev.Device reference
        """
        context = Context()
        for device in context.list_devices(subsystem='tty'):
            #print(dir(device))
            if device.get('ID_SERIAL', None) is None:
                continue
            serial = device.get('ID_SERIAL')
            if 'arduino' in serial:
                return device

    @classmethod
    def __arduino_device_node(cls,
    ) -> str:
        """__arduino_device_node Return the linux device node associated with Arduino (ex: /dev/ttyUSB0)

        

        Returns:
            str: The device node, returns an empty string if there is no connected arduino
        """
        if cls.__arduino_connected():
            device = cls.__arduino_device()
            return device.device_node
        else:
            return ""


    @classmethod
    def __arduino_device_serial(cls,
    ) -> str:
        """__arduino_device_serial Return the serial ID for the connected arduino

        

        Returns:
            str: The serial ID for the connected arduino
        """
        if cls.__arduino_connected():
            device = cls.__arduino_device()
            return device.get('ID_SERIAL')
        else:
            return ""

    @classmethod
    def __arduino_device_pci_slot(cls,
    ) -> str:
        """arduino_device_pci_slot - identify the PCI slot the arduino is attached to



        Returns:
            str: PCI slot
        """
        if cls.__arduino_connected():
            device = cls.__arduino_device()
            return device.find_parent('pci').properties['PCI_SLOT_NAME']
        else:
            return ""

    @classmethod
    def __builddir(cls,
    ) -> TemporaryDirectory:
        """builddir returns a temporary directory object suitable for usage as a context manager
        Returns:
        
            TemporaryDirectory: a TemporaryDirectory object
        """
        return TemporaryDirectory()


    @classmethod
    def __buildenv(cls,
    ) -> DefaultEnvironment:
        return DefaultEnvironment()

    @classmethod
    def __locate_binary(cls,
        binary_name: str = None
    ):
        return shutil.which(binary_name)

    @classmethod
    def __compile(cls,
        maker: str = None,
    ) -> bool:
        if os.path.exists('Makefile'):
            maker = cls.__locate_binary('make') if maker is None else maker
            make = subprocess.Popen(
                [
                    maker,
                    #"-n"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, stderr = make.communicate()
            if stderr is None:
                print(f"make was successful")
                print(f"{stdout.decode('UTF-8')}")
                return True
            else:
                print(f"make failed {stderr.decode('UTF-8')}")
                return False

    @classmethod
    def __upload(
        cls,
        maker: str = None,
    ) -> bool:
        if os.path.exists('Makefile'):
            maker = cls.__locate_binary('make') if maker is None else maker

            make = subprocess.Popen([
                maker,
                'upload'
            ],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout, stderr = make.communicate()
            if stderr is None:
                print(f"make upload was successful")
                print(f"{stdout.decode('UTF-8')}")
                return True
            else:
                print(f"make failed {stderr.decode('UTF-8')}")
                return False

    @classmethod
    def __stage_user_libraries(
        cls,
        downloader: str = None,
        user_libraries: list = None,
        target_path: str = None
    ) -> bool:
        if downloader is None:
            downloader = cls.__locate_binary(binary_name='pio')

        if user_libraries is None:
            user_libraries = cls.FIRMATA_DEPENDS

        deps = " ".join(user_libraries)
        if not os.path.exists(os.path.join(target_path, 'libraries')):
            print("creating libraries directory")
            os.mkdir(
                os.path.join(target_path, 'libraries'),
                mode=0o777,
            )
        print(f"installing {deps} in {target_path}")
        for dep in user_libraries:
            print(f"installing {dep} in {target_path}")
            download = subprocess.Popen(
                [downloader,
                'lib',
                '--storage-dir',
                os.path.join(target_path, 'libraries'),
                'install',
                dep
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout, stderr = download.communicate()
            if stderr is None:
                #print(type(stdout))
                print(f"successfully installed dependency {dep}")
                print(stdout.decode('UTF-8'))
            else:
                print(f"failed to install dependency {dep}")
                print(stderr)
                return False

            staged_files = glob(target_path + f"/libraries/{dep}/**")
            print(staged_files)

        #for dep in deps:
        #    dep_path = os.path.join(target_path, 'libraries', 'dep')
        #    if not os.path.exists(dep_path):
        #        return False
        return True

        #return binary

    @classmethod
    def __write_makefile(cls,
        obj = None,
        target_path: str = None,
    ):
        makefile = ArduinoMakeFile(
            board_tag = obj.arduino_board,
            device_port = obj.arduino_port,
            board_protocol = obj.board_data['upload']['protocol'],
            bootloader=obj.board_data['bootloader']['path'],
            variant=obj.board_data['build']['variant'],
            arduino_libs=obj.user_libs,
            target_path=target_path
            #arduino_libs=
        )
        if target_path is not None:
            if os.path.exists(target_path):
                with open(os.path.join(target_path, 'Makefile'), 'w') as file:
                    file.write(makefile.to_make())

        if os.path.exists(os.path.join(target_path, 'Makefile')):
            staged_files = glob(target_path + "/**")
            print(f"successfully wrote {os.path.join(target_path, 'Makefile')}")
            print(staged_files)
            with open(os.path.join(target_path, 'Makefile'), 'r') as file:
                print(f"printing Makefile contents")
                data = file.readlines()
                for line in data:
                    print(line)
            return True
        else:
            print(f"failed to write {os.path.join(target_path, 'Makefile')}")
            return False

    @classmethod
    def __stage_standard_firmata_ino(cls,
        arduino_libraries: str = None,
        ino_path: str = None,
        ino_file: str = None,
        target_path: str = None
    ) -> bool:

        if ino_file is None:
            ino_file = cls.FIRMATA_FILE
            print(f"using default: {ino_file}")
            
        if arduino_libraries is None:
            ino_path = os.path.dirname(os.path.abspath(__file__)) if ino_path is None else ino_path
            print("/".join(ino_path.split('/')[0:-2]))
            ino_path =  os.path.join(
                "/".join(ino_path.split('/')[0:-2]),
                "pylibs", 
                "arduino", 
                "catalog"
            ) # modify the path so it is right
            print(f"configured path to INO is {ino_path}")
            ino_file = os.path.join(ino_path,  ino_file)
            print(f"using locally housed {ino_path}  {ino_file}")
            shutil.copy(
                src=ino_file,
                dst=os.path.join(target_path, os.path.basename(ino_file))
            )
            if os.path.exists(os.path.join(target_path, os.path.basename(ino_file))):
                print("copied file successfully")
                return True
            else:
                print("failed to copy file")
                return False
        elif arduino_libraries is not None:
            for root, dir, files, in os.walk(arduino_libraries):
                for file in files:
                    if file == ino_file:
                        print(f"found it {os.path.join(root,file)}")
                        shutil.copy(
                            src=os.path.join(root, file),
                            dst=os.path.join(target_path, file)
                        )
                        staged_files = glob(target_path + "/**")
                        if os.path.exists(os.path.join(target_path, file)):
                            print('successfully staged file')
                            print(staged_files)
                            return True
                        else:
                            print('failed to stage file')
                            return False
        else:
            return False

    @classmethod
    def __build_steps(cls,
        obj = None,
        builddir: str = None
    ) -> bool:


        with builddir as place:
            if os.path.exists(place):
                #os.chdir(place)
                #print(f"origin: {origin}")
                
                with chdir(Path(place)):
                    print(os.getcwd())
                    # create StandardFirmata.ino
                    cls.__stage_standard_firmata_ino(
                        #arduino_libraries=cls.ARDUINO_LIBRARIES,
                        #ino_file=cls.FIRMATA_FILE,
                        target_path=place
                    )
                    # stage libs
                    cls.__stage_user_libraries(
                        downloader='pio',
                        user_libraries=obj.arduino_libs,
                        target_path=place
                    )
                    ## write makefile
                    cls.__write_makefile(
                        obj=obj,
                        target_path=place
                    )
                    files = glob('libraries/**')
                    print(f"staged library files: {files}")
                    ## run makefile
                    cls.__compile()
                    #shutil.copytree(place, '/tmp/whatthefuck')

                    ## upload to board
                    cls.__upload()

            else:
                print("please rerun builddir()")
                return False


    @classmethod
    def __prep_buildenv(cls,
        env: DefaultEnvironment = None,
        obj = None,
    ) -> DefaultEnvironment:
        print(cls.CC_FLAGS)
        config = ProjectConfig.get_instance()
        return env.Replace(
            AR=f"{cls.AVR_BIN_PREFIX}ar",
            AS=f"{cls.AVR_BIN_PREFIX}as",
            CC=f"{cls.AVR_BIN_PREFIX}gcc",
            CXX=f"{cls.AVR_BIN_PREFIX}g++",
            OBJCOPY=f"{cls.AVR_BIN_PREFIX}objcopy",
            OBJDUMP=f"{cls.AVR_BIN_PREFIX}objdump",
            RANLIB=f"{cls.AVR_BIN_PREFIX}ranlib",
            CCFLAGS=cls.CC_FLAGS,
            CXXFLAGS=cls.CXX_FLAGS,
            PROJECT_DIR=get_project_dir(),
            PROJECT_PACKAGES_DIR=config.get_optional_dir("packages"),
            PROJECT_WORKSPACE_DIR=config.get_optional_dir("workspace"),
            PROJECT_LIBDEPS_DIR=config.get_optional_dir("libdeps"),
            PROJECT_INCLUDE_DIR=config.get_optional_dir("include"),
            PROJECT_SRC_DIR=config.get_optional_dir("src"),
            PROJECTSRC_DIR=config.get_optional_dir(
                "src"),  # legacy for dev/platform
            PROJECT_TEST_DIR=config.get_optional_dir("test"),
            PROJECT_DATA_DIR=config.get_optional_dir("data"),
            PROJECTDATA_DIR=config.get_optional_dir(
                "data"),  # legacy for dev/platform
            PROJECT_BUILD_DIR=config.get_optional_dir("build"),
            #BUILD_CACHE_DIR=config.get_optional_dir("build_cache"),
            LIBSOURCE_DIRS=[
                config.get_optional_dir("lib"),
                os.path.join("$PROJECT_LIBDEPS_DIR", "$PIOENV"),
                config.get_optional_dir("globallib"),
            ],
            PIOENV=obj.pioenv
        )

    def __init__(self,
        arduino_board: str = None, #mega2560 #megaatmega2560
        arduino_port: str = None,
        board_protocol: str = None,
        bootloader: str = None,
        variant: str = None,
        arduino_libs: list = None,
        user_libs: str = None,
        pioenv: str = "arduino_mega",
        target: str = None,
    ) -> None:
        if self.__class__.__arduino_connected():
            self.error = False
            self.user_libs = self.__class__.USER_LIBS if user_libs is None else user_libs
            self.arduino_board = "mega2560" if arduino_board is None else arduino_board
            #self.arduino_port = "/dev/ttyACM0" if arduino_port is None else arduino_port


            self.board_data = self.__class__.__arduino_conf(
                arduino_board=self.arduino_board
            )
            self.board_confs = self.__class__.__parse_arduino_conf()


            if arduino_port is None: # if a device is connected, we can autoconfigure the port
                self.device = self.__class__.__arduino_device()
                self.device_node = self.__class__.__arduino_device_node()
                self.arduino_port = self.device_node
            else:
                self.arduino_port = arduino_port
                cxt = Context()
                self.device = Device.from_device_file(cxt, arduino_port)
                self.device_node = self.device.device_node
            self.env = self.__class__.__buildenv()

            self.arduino_libs = self.__class__.FIRMATA_DEPENDS if arduino_libs is None else arduino_libs
            self.variant = self.board_data.get('build', {}).get('variant', "undefined") if variant is None else variant
            self.bootloader = self.board_data.get('bootloader', {}).get('path', "undefined") if bootloader is None else bootloader
            self.board_protocol = self.board_data.get('upload', {}).get('protocol') if board_protocol is None else board_protocol
            self.pioenv = pioenv
            self.serial = self.__class__.__arduino_device_serial().split('__')[-1]
            self.platform = self.env.get('PLATFORM', 'undefined')
            self.pci_slot = self.__class__.__arduino_device_pci_slot()

            self.build_overrides = list(self.board_data['build'].keys())
            self.project = ProjectConfig.get_instance()
            self.project_dir = self.project.get_default_path()
            if target is not None:
                if os.path.exists(target):
                    self.target = target
            else:
                self.target = "undefined"
        else:
            self.error = True

    def prep_buildenv(self,
    ) -> None:
        self.__class__.__prep_buildenv(
            env = self.env,
            obj=self
        )
        self.env.get('CCFLAGS').append(f"-mmcu={self.arduino_board}")
        self.env.get('CXXFLAGS').append(f"-mmcu={self.arduino_board}")


    def print_conf(self,
    ) -> None:
        print(json.dumps(self.board_data, indent=2))

    def get_override(self,
        key: str = None,
    ) -> str:
        if key in self.build_overrides:
            return self.board_data['build'].get(key, "")
        else:
            return f"no key exists with name {key}"

    def builddir(self,
    ):
        self.build_dir = self.__class__.__builddir()
        return self.build_dir

    def prep_builddir(self,
        builddir: str = None,
    ):
        if builddir is None:
            self.__class__.__build_steps(obj=self,builddir=self.build_dir)
        else:
            self.__class__.__build_steps(obj=self,builddir=builddir)

    def program(self,
    ):
        self.prep_buildenv()
        build_dir = self.builddir()
        self.prep_builddir(builddir=build_dir)