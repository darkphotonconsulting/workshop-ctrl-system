""" Constants
This file contains constants whose values are frequently referenced within the headunit software ecosystem
"""
import sys
import os

__all__ = [
    'STOP_CODES',
    'ARDUINO_RESP_OK',
    'ARDUINO_RESP_FAILED',
    'ARDUINO_RESP_UNKNOWN',
    'ARDUINO_RESP_NODEV',
    'ARDUINO_RESP_INSYNC',
    'ARDUINO_RESP_NOSYNC',
    'ARDUINO_RESP_ADC_CHAN_ERROR',
    'ARDUINO_RESP_ADC_MEAS_OK',
    'ARDUINO_RESP_PWM_CHAN_ERROR',
    'ARDUINO_RESP_PWM_ADJUST_OK',
    'ARDUINO_SYNC_CRC_EOP',
    'ARDUINO_CMD_GET_SYNC',
    'ARDUINO_CMD_SET_PARAM',
    'ARDUINO_CMD_GET_PARAM',
    'ARDUINO_CMD_SET_DEV',
    'ARDUINO_CMD_SET_DEV_EXT',
    'ARDUINO_CMD_READ_SIGN',
    'ARDUINO_HOME',
    'AVRDUDE_BIN',
    'ARDUINO_BOARDS',
    'AVRDUDE_CONF',
    'AVRDUDE_PART_KEYS',
    'AVRDUDE_MEMORY_KEYS',
    'MONGO_STRUCTURE',
    'SUPPORTED_DATABASE_NAMES',
    'COLLECTION_ALIAS_MAP',
    'SUPPORTED_COLLECTIONS_MAP',
    'FILE_MAP'
]

# --------- GENERAL ---------

STOP_CODES: dict = {
    """ A mapping of exit codes to their english meaning
    """
    'SUCCESS': 0,
    'ARGUMENTS': 1,
    'EXECUTION_ERROR': -1,
}

# --------- ARDUINO ---------

ARDUINO_RESP_OK: int = 0x10
ARDUINO_RESP_FAILED: int = 0x11
ARDUINO_RESP_UNKNOWN: int = 0x12
ARDUINO_RESP_NODEV: int = 0x13
ARDUINO_RESP_INSYNC: int = 0x14
ARDUINO_RESP_NOSYNC: int = 0x15
ARDUINO_RESP_ADC_CHAN_ERROR: int = 0x16
ARDUINO_RESP_ADC_MEAS_OK: int = 0x17
ARDUINO_RESP_PWM_CHAN_ERROR: int = 0x18
ARDUINO_RESP_PWM_ADJUST_OK: int = 0x19
ARDUINO_SYNC_CRC_EOP: int = 0x20
ARDUINO_CMD_GET_SYNC: int = 0x30
ARDUINO_CMD_SET_PARAM: int = 0x40
ARDUINO_CMD_GET_PARAM: int = 0x41
ARDUINO_CMD_SET_DEV: int = 0x42
ARDUINO_CMD_SET_DEV_EXT: int = 0x43
ARDUINO_CMD_READ_SIGN: int = 0x75

ARDUINO_HOME: str = "/usr/share/arduino"
AVRDUDE_BIN: str = os.path.join(ARDUINO_HOME, 
    "hardware", 
    "tools", 
    "avr", 
    "bin", 
    "avrdude"
)
ARDUINO_BOARDS: str = os.path.join(ARDUINO_HOME, 
    "hardware", 
    "arduino", 
    "boards.txt"
)
AVRDUDE_CONF: str = os.path.join(ARDUINO_HOME, 
    "hardware", 
    "tools", 
    "avrdude.conf"
)

AVRDUDE_PART_KEYS: list = [
    'id',
    'desc',
    'has_jtag',
    'has_debugwire',
    'has_pdi',
    'has_updi',
    'has_tpi',
    'devicecode',
    'stk500_devcode',
    'avr910_devcode',
    'signature',
    'usbpid',
    'chip_erase_delay',
    'reset',
    'retry_pulse',
    'pgm_enable',
    'chip_erase',
    'pagel',
    'bs2',
    'serial',
    'parallel',
    'timeout',
    'stabdelay',
    'cmdexedelay',
    'synchloops',
    'bytedelay',
    'pollvalue',
    'pollindex',
    'predelay',
    'postdelay',
    'pollmethod',
    'mode',
    'delay',
    'blocksize',
    'readsize',
    'hvspcmdexedelay',
    'pp_controlstack',
    'hvsp_controlstack',
    'hventerstabdelay',
    'progmodedelay',
    'latchcycles',
    'togglevtg',    
    'poweroffdelay',
    'hvleavestabdelay',
    'resetdelayms',
    'resetdelayus',
    'resetdelay',
    'synchcycles',
    'chiperasepulsewidth',
    'chiperasepolltimeout',
    'chiperasetime',
    'programfusepulsewidth',
    'programfusepolltimeout',
    'programlockpulsewidth',
    'programlockpolltimeout',
    'allowfullpagebitstream',
    'enablepageprogramming',
    'idr',
    'rampz',
    'spmcr',
    'eecr',
    'is_at90s1200',
    'is_avr32',
]

AVRDUDE_MEMORY_KEYS: list = [
    'paged',
    'size',
    'page_size',
    'num_pages',
    'min_write_delay',
    'max_write_delay',
    'readback_p1',
    'readback_p2',
    'pwroff_after_write',
    'read',
    'write',
    'read_lo',
    'read_hi',
    'write_lo',
    'write_hi',
    'loadpage_lo',
    'loadpage_hi',
    'writepage',
]

# DATABASE 

MONGO_STRUCTURE: dict = {
    'static': {
        'system': 'static-system',
        'gpios': 'static-gpios',
        'relays': 'static-relays',
        'all': ['static-system', 'static-gpios']
    },
    'dynamic': {
        'system_memory_stats': 'dynamic-system-memory-statistics',
        'system_net_stats': 'dynamic-system-network-statistics',
        'system_cpu_stats': 'dynamic-system-memory-statistics'
    }
}
# database names the application knows how to configure
SUPPORTED_DATABASE_NAMES: list = list(MONGO_STRUCTURE.keys())
# collection aliases that can be passed into functions that need to lookup the proper schema templates
COLLECTION_ALIAS_MAP: dict = {k: list(MONGO_STRUCTURE[k].keys()) for k in MONGO_STRUCTURE.keys() }
# list of supported collection names mapped to their containing databases
SUPPORTED_COLLECTIONS_MAP: dict = {k: list(MONGO_STRUCTURE[k].values()) for k in MONGO_STRUCTURE.keys() }
# list of defaults used when writing data to file
FILE_MAP: dict = {
    'extension': 'json',
    'system': 'system',
    'gpios': 'gpios',
    'relays': 'user-relays'
}