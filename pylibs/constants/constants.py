# {
#   key: database { 
#      key:input_arg*: collection-name*,
#      ... 
#     }
# }
#
#
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