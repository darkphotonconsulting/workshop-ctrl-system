import urllib.parse


class DevelopmentConfig(object):
    """Configuration Class
    """
    raspi_service_host = '0.0.0.0'
    raspi_service_port = 5001
    metrics_service_host = '0.0.0.0'
    metrics_service_port = 5002
    mongodb_host = '127.0.0.1'
    mongodb_port = 27017

    def __init__(self,
                 mongo_host: str = None,
                 mongo_port: int = None,
                 mongo_username: str = None,
                 mongo_password: str = None,
                 **kwargs):

        print(kwargs)
        if mongo_host is None:
            self.mongo_host = '127.0.0.1'
        else:
            self.host = mongo_host
        if mongo_port is None:
            self.mongo_port = 27017
        else:
            self.mongo_port = mongo_port

        if mongo_username is not None and mongo_password is not None:
            self.mongo_username = urllib.parse.quote_plus(mongo_username)
            self.mongo_password = urllib.parse.quote_plus(mongo_password)
            self.mongo_connect_string = f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{str(self.mongo_port)}"
        else:
            self.mongo_username = None
            self.mongo_password = None
            self.mongo_connect_string = f"mongodb://{self.mongo_host}:{str(self.mongo_port)}"

        if 'raspi_service_host' in kwargs:
            self.raspi_service_host = kwargs.get('raspi_service_host',
                                                 '0.0.0.0')
        else:
            self.raspi_service_host = '0.0.0.0'

        if 'raspi_service_port' in kwargs:
            self.raspi_service_port = kwargs.get('raspi_service_port',
                                                 5001)
        else:
            self.raspi_service_port = 5001

        if 'metrics_service_host' in kwargs:
            self.metrics_service_host = kwargs.get('metrics_service_host',
                                                   '0.0.0.0')
        else:
            self.metrics_service_host = '0.0.0.0'

        if 'metrics_service_port' in kwargs:
            self.metrics_service_port = kwargs.get('metrics_service_port',
                                                   5002)
        else:
            self.metrics_service_port = 5002


class ProductionConfig(object):
    """Production Config class"""
    raspi_service_host = '0.0.0.0'
    raspi_service_port = 5001
    metrics_service_host = '0.0.0.0'
    metrics_service_port = 5002
    #mongo_host = 'mongo.darkphotonworks-labs.io'
    #mongo_port = 27017

    def __init__(self,
                 mongo_host: str = None,
                 mongo_port: int = None,
                 mongo_username: str = None,
                 mongo_password: str = None,
                 **kwargs):

        print(kwargs)
        if mongo_host is None:
            self.mongo_host = 'mongo.darkphotonworks-labs.io'
        else:
            self.mongo_host = mongo_host
        if mongo_port is None:
            self.mongo_port = 27017
        else:
            self.mongo_port = mongo_port

        if mongo_username is not None and mongo_password is not None:
            self.mongo_username = urllib.parse.quote_plus(mongo_username)
            self.mongo_password = urllib.parse.quote_plus(mongo_password)
            self.mongo_connect_string = f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{str(self.mongo_port)}"
        else:
            self.mongo_username = None
            self.mongo_password = None
            self.mongo_connect_string = f"mongodb://{self.mongo_host}:{str(self.mongo_port)}"

        if 'raspi_service_host' in kwargs:
            self.raspi_service_host = kwargs.get('raspi_service_host',
                                                 '0.0.0.0')
        else:
            self.raspi_service_host = '0.0.0.0'

        if 'raspi_service_port' in kwargs:
            self.raspi_service_port = kwargs.get('raspi_service_port', 5001)
        else:
            self.raspi_service_port = 5001

        if 'metrics_service_host' in kwargs:
            self.metrics_service_host = kwargs.get('metrics_service_host',
                                                 '0.0.0.0')
        else:
            self.metrics_service_host = '0.0.0.0'

        if 'metrics_service_port' in kwargs:
            self.metrics_service_port = kwargs.get('metrics_service_port', 5002)
        else:
            self.metrics_service_port = 5002
