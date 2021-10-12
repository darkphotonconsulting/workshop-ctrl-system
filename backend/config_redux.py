import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])
sys.path.append(libs)

#import urllib.parse
#import urllib.parse
from urllib.parse import quote_plus
import abc

from attr import has

import logging
from pylibs.logging.loginator import Loginator
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ConnectionFailure

#custom exceptions?

        
class Configuration(object, metaclass=abc.ABCMeta):
    """Configuration Configuration Base Class


    Configuration data for backend connections and side car services
    - sets sane defaults
    - provides connection validation

    Attributes:
        logger (logging.logger) - the classes stream logger
        loginator (Loginator) - the Loginator configuration object
        mongo_host (str) - MongoDB host
        mongo_port (int) - MongoDB port
        mongo_username (str) - MongoDB host
        mongo_password (str) - MongoDB username
        mongo_database (str) - MongoDB database
        pi_host str - Pi Service host
        pi_port int - Pi Service port
        metrics_host str - Metrics Service host
        metrics_port int - Metrics Service port

    Returns:
        Configuration: A configuration object
    """
    #__metaclass__ = abc.ABCMeta
    logger: logging.Logger = logging.getLogger('Configuration')
    loginator: Loginator = Loginator(logger=logger)
    logger: logging.Logger = loginator.logger

    @classmethod
    def __reconfigure_logger(cls,
    ) -> logging.Logger:
        """__reconfigure_logger Configures logger for class


        Returns:
            logging.Logger: logger object
        """
        logger: logging.Logger = logging.getLogger(cls.__name__)
        loginator: Loginator = Loginator(logger=logger)
        logger: logging.Logger = loginator.logger
        return logger

    def __init__(
        self,
        mongo_host: str = None,
        mongo_port: int = None,
        mongo_username: str = None,
        mongo_password: str = None,
        mongo_database: str = None,
        pi_host: str = None,
        pi_port: int = None,
        metrics_host: str = None,
        metrics_port: int = None,
        #**kwargs
    ) -> None:
        """__init__ Creates an abstract configuration object 

        The class can be inherited by more specific classes to easily override values        

        Examples:
        
        # the base configuration class can be used to create generic configuration objects
        base_configuration = backend.config_redux.Configuration()
        
        In [253]: base_configuration.get_mongo_password
        Out[253]: 'unset'

        # environment level configuration classes preset some info for you
        dev_configuration = backend.config_redux.DevConfiguration( 
            mongo_username='USERNAME', 
            mongo_password='PASSWORD'
        )
        
        In [258]: dev_configuration.get_mongo_host
        Out[258]: 'mongo.darkphotonworks-labs.io'
        

        

        

        Args:
            mongo_host (str, optional): MongoDB FQDN or IP. Defaults to None.
            mongo_port (int, optional): MongoDB Port. Defaults to None.
            mongo_username (str, optional): MongoDB Username. Defaults to None.
            mongo_password (str, optional): MongoDB Password. Defaults to None.
            mongo_database (str, optional): MongoDB Database. Defaults to None.
            pi_host (str, optional): PiService FQDN or IP. Defaults to None.
            pi_port (int, optional): PiService Port. Defaults to None.
            metrics_host (str, optional): MetricsService FQDN or IP. Defaults to None.
            metrics_port (int, optional): MetricsService Port. Defaults to None.
        """
        self.__class__.logger = self.__class__.__reconfigure_logger()
        if mongo_username is None and mongo_password is None: # no auth provided
            self.__class__.logger.warning("neither mongo_username or mongo_password were provided, the connection will not use authentication")
            self.mongo_username: str = "unset"
            self.mongo_password: str = "unset"
        else: # use provided auth values
            # url parse values so the constructed connection string is valid
            self.mongo_username: str = quote_plus(mongo_username)
            self.mongo_password: str = quote_plus(mongo_password)

        # reconfigure logger
        
        # defaults for connecting to mongoDB
        self.__class__.logger.warning("mongo_host was not provided, assuming a mongo database is running locally on 127.0.0.1") if mongo_host is None else None
        self.mongo_host: str = '127.0.0.1' if mongo_host is None else mongo_host
        self.mongo_port: int = 27017 if mongo_port is None else mongo_port
        self.mongo_database: str = None if mongo_database is None else mongo_database
        # defaults for sidecars
        self.pi_host: str = '127.0.0.1' if pi_host is None else pi_host
        self.pi_port: int = 5000 if pi_port is None else pi_port
        self.metrics_host: str = '127.0.0.1' if metrics_host is None else metrics_host
        self.metrics_port: int = 5001 if metrics_port is None else metrics_port


    # getters/setters

    @property
    def get_mongo_database(self,
    ) -> str:
        """get_mongo_database getter for mongo_database

        Returns:
            str: the mongo database if set
        """
        return self.mongo_database

    @get_mongo_database.setter
    def set_mongo_database(self,
    value) -> None:
        """set_mongo_database setter for mongo database


        Args:
            value (str): A FQDN or IP for MongoDB
        """
        self.__class__.logger.info(f"setting mongo_database to: {value}")
        self.mongo_database = value

    @property
    def get_mongo_username(self,
    ) -> str:
        """get_mongo_database getter for mongo_database

        Returns:
            str: the mongo database if set
        """
        return self.mongo_username

    @get_mongo_username.setter
    def set_mongo_username(self,
        value: str = None,
    ) -> None:
        """set_mongo_username setter for mongo_username


        Args:
            value (str): The MongoDB Username
        """
        self.__class__.logger.info(f"setting mongo_username to: {value}")
        self.mongo_username = value

    @property
    def get_mongo_password(self,
    ) -> str:
        """get_mongo_password getter for mongo_password

        Returns:
            str: the mongo password
        """
        return self.mongo_password

    @get_mongo_password.setter
    def set_mongo_password(self,
        value: str = None,
    ) -> None:
        """set_mongo_password setter for mongo_password


        Args:
            value (str): The MongoDB Password
        """
        self.__class__.logger.info(f"setting mongo_password to: {value}")
        self.mongo_password = value

    @property
    def get_mongo_host(self,
    ) -> str:
        """get_mongo_host getter for mongo_host

        Returns:
            str: the mongo host if set
        """
        return self.mongo_host

    @get_mongo_host.setter
    def set_mongo_host(self,
        value: str = None,
    ) -> None:
        """set_mongo_host setter for mongo_host


        Args:
            value (str): The MongoDB FQDN or IP
        """
        self.__class__.logger.info(f"setting mongo_host to: {value}")
        self.mongo_host = value

    @property
    def get_mongo_port(self,
    ) -> int:
        """get_mongo_port getter for mongo_port

        Returns:
            int: the mongo port if set
        """
        return self.mongo_port

    @get_mongo_port.setter
    def set_mongo_port(self,
        value: int = None,
    ) -> None:
        """set_mongo_port setter for mongo_port


        Args:
            value (int): The MongoDB Port
        """
        self.__class__.logger.info(f"setting mongo_port to: {value}")
        self.mongo_port = int(value)

    @property
    def get_pi_host(self):
        """get_pi_host getter for pi_host

        Returns:
            str: the pi service host if set, this defines what host address the service runs on
        """
        return self.pi_host

    @get_pi_host.setter
    def set_pi_host(self,
        value
    ) -> None:
        """set_pi_host setter for pi_host


        Args:
            value (str): The PiService FQDN or IP
        """
        self.__class__.logger.info(f"setting pi_host to: {value}")
        self.pi_host = value

    @property
    def get_pi_port(self):
        """get_pi_port getter for pi_port

        Returns:
            str: the pi service port if set, this defines what host port the service runs on
        """
        return self.pi_port

    @get_pi_port.setter
    def set_pi_port(self,
        value
    ) -> None:
        """set_pi_port setter for pi_port


        Args:
            value (int): The PiService Port
        """
        self.__class__.logger.info(f"setting pi_port to: {value}")
        self.pi_port = int(value)

    @property
    def get_metrics_host(self):
        """get_metrics_host getter for metrics_host

        Returns:
            str: the metrics service host if set, this defines what host address the service runs on
        """
        return self.metrics_host

    @get_metrics_host.setter
    def set_metrics_host(self,
        value: str = None
    ) -> None:
        """set_metrics_host setter for metrics_host


        Args:
            value (str): The MetricsService FQDN or IP
        """
        self.__class__.logger.info(f"setting metrics_host to: {value}")
        self.metrics_host = value

    @property
    def get_metrics_port(self):
        """get_metrics_port getter for metrics_port

        Returns:
            str: the metrics service port if set, this defines what host port the service runs on
        """
        return self.metrics_port

    @get_metrics_port.setter
    def set_metrics_port(self,
        value: int = None
    ) -> None:
        """set_metrics_port setter for metrics_port


        Args:
            value (int): The MetricsService Port
        """
        self.__class__.logger.info(f"setting metrics_port to: {value}")
        self.metrics_port = int(value)

    def mongo_connection_string(self,
    ) -> str:
        """mongo_connection_string Intelligently generates mongodb connection string based on provided values


        Example:
        import pymongo
        
        configuration = backend.config_redux.Configuration()

        # sane defaults allow no args to be passed in, an authless connection to localhost is assumed
        In [260]: configuration.mongo_connection_string()
        Out[260]: 'mongodb://127.0.0.1:27017'

        # validate a connection before using it
        In [261]:  configuration.validate_mongo_connection_string()
        🍺 > > > > > > > > > > executionTime: [2021-10-09 04:24:31,207] - moduleName: [Configuration] - logLevel: [INFO] - msgContents: connected lineOfCode: (config_redux.py:227)
        Out[261]: True

        if configuration.validate_mongo_connection_string(): 
            client = pymongo.MongoClient(configuration.mongo_connection_string())
            client.server_info()
        
        Returns:
            str: a usable mongodb connection string
        """
        if self.mongo_username != "unset" and self.mongo_password != "unset": # auth args passed
            if self.mongo_database is None:
                return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}"
            else:
                return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
        else: #generate noauth connection string
            if self.mongo_database is None:
                return f"mongodb://{self.mongo_host}:{self.mongo_port}"
            else:
                return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"

    def validate_mongo_connection_string(self,):

        try:
            client = MongoClient(self.mongo_connection_string())
            if 'version' in client.server_info():
                self.__class__.logger.info('connected')
                return True
            else:
                self.__class__.logger.error('not connected')
                return False
        except OperationFailure as error_message:
            self.__class__.logger.error(f"{error_message}")
            return False
        except ConnectionFailure as error_message:
            self.__class__.logger.error(f"{error_message}")
            return False



class DevConfiguration(Configuration):
    def __init__(
        self,
        mongo_host: str = None,
        mongo_port: int = None,
        mongo_username: str = None,
        mongo_password: str = None,
        mongo_database: str = None,
    ):
        super().__init__(
            mongo_host=mongo_host,
            mongo_port=mongo_port,
            mongo_username=mongo_username,
            mongo_password=mongo_password,
            mongo_database=mongo_database

        )

        self.environment = 'dev'
        self.mongo_host = 'mongo.darkphotonworks-labs.io'


class ProdConfiguration(Configuration):
    def __init__(
        self,
        mongo_host: str = None,
        mongo_port: int = None,
        mongo_username: str = None,
        mongo_password: str = None,
        mongo_database: str = None,
    ):
        super().__init__(mongo_host=mongo_host,
                         mongo_port=mongo_port,
                         mongo_username=mongo_username,
                         mongo_password=mongo_password,
                         mongo_database=mongo_database)
        self.environment = 'prod'
        self.mongo_host = 'mongo.darkphotonworks-labs.io'


class PyTestConfiguration(Configuration):
    def __init__(
        self,
        mongo_host: str = None,
        mongo_port: int = None,
        mongo_username: str = None,
        mongo_password: str = None,
        mongo_database: str = None,
    ):
        super().__init__(mongo_host=mongo_host,
                         mongo_port=mongo_port,
                         mongo_username=mongo_username,
                         mongo_password=mongo_password,
                         mongo_database=mongo_database)
        self.environment = 'pytest'
        self.mongo_host = 'mongo.darkphotonworks-labs.io'