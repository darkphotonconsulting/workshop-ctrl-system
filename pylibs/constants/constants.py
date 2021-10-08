""" constants

This file contains constants frequently referenced by other components in the headunit ecosystem
"""
MONGO_STRUCTURE = {
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
FILE_MAP = {
    'extension': 'json',
    'system': 'system',
    'gpios': 'gpios',
    'relays': 'user-relays'
}