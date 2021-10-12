class ConfigurationException(Exception):
    pass


class BadArgumentPairException(ConfigurationException):
    def __init__(self, *args):
        super().__init__(*args)
        