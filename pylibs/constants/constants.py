MONGO_STRUCTURE = {
    'static': {
        'system': 'static-system',
        'gpios': 'static-gpios',
        'relays': 'static-relays',
        'all': ['static-system', 'static-gpios']
    },
    'dynamic': {}
}
FILE_MAP = {
    'extension': 'json',
    'all': 'raspberrypi',
    'system': 'system',
    'gpios': 'gpios',
    'relays': 'user-relays'
}