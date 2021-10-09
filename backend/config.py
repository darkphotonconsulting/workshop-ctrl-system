import urllib.parse


class BaseConfig(object):
    """BaseConfig - A Generic configuration class

    Examples:

        from pymongo import MongoClient

        # connect to local db instance with no authentication configured
        client = MongoClient(BaseConfig().mongo_connect_string)
        ...
        
        # or connect to a custom DB with authentication
        base = BaseConfig(
            mongodb_host='my.mongodb.io',
            mongodb_port=27017,
            mongodb_username='myusername',
            mongodb_password='apassword',
        )
        client = MongoClient(base.mongo_connect_string)
        ...

                
    Attributes:
        mongo_username (str): the provided mongodb username
        mongo_password (str): the provided mongodb password
        mongo_connect_string (str): an autogenerated connection string based on provided inputs
        raspi_service_host (str): the host address raspi service runs on
        raspi_service_port  (int): the port the raspi service runs on
        metrics_service_host (str): the metrics service host address
        metrics_service_port (int): the metrics service port
        mongodb_host (str): mongodb host
        mongodb_port (int): mongodb port
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
        #: str: the MongoDB host
        if mongo_host is None:
            self.mongo_host = '127.0.0.1'
        else:
            self.mongo_host = mongo_host
        #: int: the MongoDB host
        if mongo_port is None:
            self.mongo_port = 27017
        else:
            self.mongo_port = mongo_port
        #: str: the MongoDB username
        if mongo_username is not None and mongo_password is not None:
            self.mongo_username = urllib.parse.quote_plus(mongo_username) #: str: the MongoDB username
            self.mongo_password = urllib.parse.quote_plus(
                mongo_password)  #: str: the MongoDB password
            self.mongo_connect_string = f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{str(self.mongo_port)}"  #: str: the MongoDB connection string
        else:
            self.mongo_username = None
            self.mongo_password = None
            self.mongo_connect_string = f"mongodb://{self.mongo_host}:{str(self.mongo_port)}"

        if 'raspi_service_host' in kwargs:
            self.raspi_service_host = kwargs.get(
                'raspi_service_host', '0.0.0.0')  #: str: the Raspberry Pi service host address
        else:
            self.raspi_service_host = '0.0.0.0'

        if 'raspi_service_port' in kwargs:
            self.raspi_service_port = kwargs.get(
                'raspi_service_port',
                5001)  #: str: the Raspberry Pi service port
        else:
            self.raspi_service_port = 5001

        if 'metrics_service_host' in kwargs:
            self.metrics_service_host = kwargs.get(
                'metrics_service_host',
                '0.0.0.0')  #: str: the Metrics service host address
        else:
            self.metrics_service_host = '0.0.0.0'

        if 'metrics_service_port' in kwargs:
            self.metrics_service_port = kwargs.get('metrics_service_port',
                                                   5002) #: str: the Metrics service port
        else:
            self.metrics_service_port = 5002


class DevelopmentConfig(object):
    """DevelopmentConfig  - A configuration class warmed up for development instance 

    \U0001F6D1 the development mongodb is like version 2.4 and will ultimately not work with the current pymongo version, sorry.

    Examples:

        from pymongo import MongoClient

        # connect to local db instance with no authentication configured
        client = MongoClient(DevelopmentConfig().mongo_connect_string)
        ...
        
    Attributes:
        mongo_username (str): the provided mongodb username
        mongo_password (str): the provided mongodb password
        mongo_connect_string (str): an autogenerated connection string based on provided inputs
        raspi_service_host (str): the host address raspi service runs on
        raspi_service_port  (int): the port the raspi service runs on
        metrics_service_host (str): the metrics service host address
        metrics_service_port (int): the metrics service port
        mongodb_host (str): mongodb host
        mongodb_port (int): mongodb port
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


        if mongo_host is None:
            self.mongo_host = '127.0.0.1'
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
    """ProductionConfig -  A configuration class warmed up for production instance 

    This connects you to a mongo instance running in EKS k8s exposed via an NLB

    Examples:

        from pymongo import MongoClient

        # connect to local db instance with no authentication configured
        client = MongoClient(ProductionConfig().mongo_connect_string)
        ...


    Attributes:
        mongo_username (str): the provided mongodb username
        mongo_password (str): the provided mongodb password
        mongo_connect_string (str): an autogenerated connection string based on provided inputs
        raspi_service_host (str): the host address raspi service runs on
        raspi_service_port  (int): the port the raspi service runs on
        metrics_service_host (str): the metrics service host address
        metrics_service_port (int): the metrics service port
        mongodb_host (str): mongodb host
        mongodb_port (int): mongodb port
    """
    raspi_service_host = '0.0.0.0'
    raspi_service_port = 5001
    metrics_service_host = '0.0.0.0'
    metrics_service_port = 5002


    def __init__(self,
                 mongo_host: str = None,
                 mongo_port: int = None,
                 mongo_username: str = None,
                 mongo_password: str = None,
                 **kwargs
    ) -> None:
        """__init__ Create a basic Config object

        [extended_summary]

        Args:
            mongo_host (str, optional): MongoDB host. Defaults to None.
            mongo_port (int, optional): MongoDB port. Defaults to None.
            mongo_username (str, optional): MongoDB username. Defaults to None.
            mongo_password (str, optional): MongoDB password. Defaults to None.
        """

        self.mongo_host = 'mongo.darkphotonworks-labs.io' if mongo_host is None else mongo_host
        self.mongo_port = 27017 if mongo_port is None else mongo_port
        
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
