""" constants

This file contains constants frequently referenced by other components in the headunit ecosystem
"""

# defines the resultant mongo structure after seed/migration
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


STOP_CODES: dict = {
    'SUCCESS': 0,
    'ARGUMENTS': 1,
    'EXECUTION_ERROR': -1,
}