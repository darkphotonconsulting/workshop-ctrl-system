import os
import sys
import abc

import shlex
import json
import logging

from collections import Iterable
from urllib.parse import quote_plus
from typing import (
    Union,
    Optional
)
from pymongo import MongoClient
from pymongo.errors import (
    OperationFailure,
    ConnectionFailure
)

# adjust path to reuse pylibs
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])
sys.path.append(libs)


from pylibs.logging.loginator import Loginator


class ConfigLoader():
    """ConfigLoader - Load configuration files from various sources

    The ConfigLoader helps with the task of seperating code from configuration,
    define configuration(s) in simple JSON files and make the keys and values available to other libs.

    \U0001F4A1 - Keep your version control repository & command history tidy by segregating app code from app configuration!

    \U0001F4D3 - Each ConfigLoader instance has the capability of dynamically adding it's loaded configuration key value pairs as attributes on itself. 
    This means those values become available as class attributes
        
    - load configuration values from a JSON file, JSON string, or python dict object
    - Easily access configuration data safely and securely

    An example of the supported configuration file structure

        {
            "database": {
                "mongo_host": "mongo.io.com",
                "mongo_port": 27017,
                "mongo_username": "superuser",
                "mongo_password": "myhardpassword"
            },
            "metrics": {
                "metrics_host": "0.0.0.0",
                "metrics_port": 5000,
            },
            "pi_service": {
                "pi_service_host": "0.0.0.0",
                "pi_service_port": 5001
            }
        }

    Examples:
        from config.config_loader import ConfigLoader
        config = ConfigLoader(from_file=True,config='settings/config.json')
        # enhance the object by recursing the config dict and addign k-v pairs as object attributes
        config.add_attributes()

        # access those values pythonically
        config.mongo_username
        config.mongo_password
        # or ..
        config.database (the entire database object)
        config.database['mongo_username']
        ...
    
    Attributes:
        config (dict): A python dictionary representation of the provided "config" data
        from_file (bool): True if the successfully sourced config data is from a JSON file
        from_string (bool): True if the successfully sourced config data is from a JSON string
        from_object (bool): True if the successfully sourced config data is from python dict object
        
    """
    def __init__(self,
                 from_file: bool = False,
                 from_string: bool = False,
                 from_object: bool = False,
                 config: Union[dict, str] = None) -> None:
        """__init__ Create a ConfigLoader object

        Args:
            from_file (bool, optional): [description]. Defaults to False.
            from_string (bool, optional): [description]. Defaults to False.
            from_object (bool, optional): [description]. Defaults to False.
            config (Union[dict, str], optional): [description]. Defaults to None.
        """
        self.config = self.__class__.__conf_handler(from_file=from_file,
                                                    from_string=from_string,
                                                    from_object=from_object,
                                                    config=config)
        self.from_file = from_file
        self.from_string = from_string
        self.from_object = from_object
        self.input = config

    @classmethod
    def __get_key(
        cls,
        key_name: str = None,
        value_only: bool = False,
        data: dict = None,
    ) -> Union[dict, int, str, list]:
        """__get_key - recursively searches a dictionary for a key, extracts and returns {k: v}
        
        Iterates through a python dictionary recursively searching for the provided "key_name"
        By default, returns a dictionary containing the key and value, an extraction
        setting the value_only arg to True, alters the behaviour of the function to only return the key value

        On an error condition, a dictionary is returned with a message about what went wrong
        to validate the function succeeded, check if the return type is dict, and contains 'error'
        
        ```if isinstance(ret, dict) and 'error' in ret: return False```
        
        Args:
            key_name (str, optional): key within config dictionary to search for. Defaults to None.
            value_only (bool, optional): return only the value. Defaults to False.
            data (dict, optional): ConfigLoader.config<dict>. Defaults to None.

        Returns:
            Union[dict, int, str, list]: Returns the extracted `{k:v}` by default, if the arg `value_only` is True,
            return only the value of extracted dict key
        """
        ret = {"error": "not found"}
        if data is None:
            return {
                "error": "please pass a python dictionary into the data arg"
            }

        keys = data.keys()
        if key_name in keys:
            if not value_only:
                ret = {key_name: data.get(key_name, 'unavailable')}
            else:
                ret = data.get(key_name, 'unavailable')
            return ret
        for key in keys:
            if isinstance(data[key], dict):
                ret = cls.__get_key(key_name=key_name,
                                    data=data[key],
                                    value_only=value_only)
                return ret
        return ret

    @classmethod
    def __conf_handler(cls,
                       from_file: bool = False,
                       from_string: bool = False,
                       from_object: bool = False,
                       config: Union[dict, str] = None) -> dict:
        """__conf_handler Handles loading configuration data from various sources

        Makes it really fucking simple to load data from various sources, k doc_strings?

        Args:
            from_file (bool, optional): [Load configuration from a JSON format file]. Defaults to False.
            from_string (bool, optional): [Load configuration from a JSON string]. Defaults to False.
            from_object (bool, optional): [Load configuration from a python dictionary]. Defaults to False.
            config (Union[dict,str], optional): [A path to a file, a JSON string, or a python dictionary]. Defaults to None.

        Examples:
            # load a file
            cls.__conf_handler(
                from_file=True,
                from_string=False,
                from_object=False,
                config="/path/to/config.json"
            )
            # load a string
            cls.__conf_handler(
                from_file=False,
                from_string=True,
                from_object=False,
                config='{"database": { ...see SETTINGS.md ... }}'
            )
            # load a object
            cls.__conf_handler(
                from_file=False,
                from_string=False,
                from_object=True,
                config=config<dict>'
            )


        Returns:
            dict: [the configuration loaded as a python dictionary]
        """

        if (not from_file and from_string and from_object):
            return {
                "error":
                f"please set atleast one of `from_file` `from_string` or `from_object`"
            }
        if from_object and not (from_string and from_file):
            return config

        elif from_string and not (from_file and from_object):
            if isinstance(config, str):
                try:
                    return json.loads(config)
                except:
                    return {"error": "can not load string"}
        elif from_file and not (from_string and from_object):
            if os.path.exists(config):
                with open(config, 'r') as file:
                    try:
                        return json.load(file)
                    except:
                        return {"error": "can not load file"}
        else:
            print(f"failed to parse provided configuration")
            return {"error": "failed to parse inputs"}

    @classmethod
    def __add_attribute(
        cls,
        obj,
        attrib: str = None,
        value: Union[list, dict, str, int, bool] = None,
    ) -> bool:
        """__add_attribute Add a class attribute to an object

        Adds a class attribute with a value to the user-provided python object

        Args:
            obj (object): The python object to add attributes to
            attrib (str, optional): The attribute name. Defaults to None.
            value (Union[list, dict, str, int, bool], optional): The attribute value. Defaults to None.

        Examples:
        
            cls.__add_attribute(
                obj=obj,
                attrib='foo',
                value='bar'
            )
            
        Returns:
            bool: True if values added, False if otherwise
        """
        try:
            setattr(obj, attrib, value)
            return True
        except:
            return False

    @classmethod
    def __add_attributes(
        cls,
        obj,
        attribs: dict = None,
    ):
        """__add_attributes Iterates through a dictionary recursively adding each key and value as a class attribute

        For each key-value pair found in a recursrive, add a class attribute correlating to the 
        key and value of a python object based on the provided `attribs` python dictionary.

        Examples:
            cls.__add_attributes(
                obj=obj,
                attribs=obj.config
            )
        Args:
            obj ([obj]): Any object, however This _should_ be an instance of ConfigLoader<class<object>>
            attribs (dict, optional): The dict attributes object, should be the `ConfigLoader.config`<dict>. Defaults to None.

        Returns:
            obj: returns a reference to the modified object.
        """
        for k, v in attribs.items():
            if isinstance(v, dict):
                cls.__add_attribute(obj=obj, attrib=k, value=v)
                #setattr(obj, k, v)
                cls.__add_attributes(obj=obj, attribs=v)
                #return obj
            else:
                cls.__add_attribute(obj=obj, attrib=k, value=v)
        return obj

    def add_attributes(self, ) -> None:
        """add_attributes Wrapper for cls.__add_attributes
        """
        self.__class__.__add_attributes(
            attribs=self.config,
            obj=self,
        )

    def set_attribute(
        self,
        attrib: str = None,
        value: Union[list, dict, int, bool, str] = None,
    ) -> None:
        """set_attribute Sets an attribute on the instantiated class object

        Args:
            attrib (str, optional): attribute name. Defaults to None.
            value (Union[list, dict, int, bool, str], optional): attribute value. Defaults to None.
        """
        # reuse this to reset some attribute
        self.__class__.__add_attribute(obj=self, attrib=attrib, value=value)

    def print_config(self, ) -> None:
        """print_config - print the loaded configuration
        """
        print(json.dumps(self.config, indent=2))

    def get_config(self, ) -> dict:
        """get_config - return the python dict representation of loaded configuration data

        Returns:
            dict: [the config dictionary]
        """
        return self.config

    def set_config(
            self,
            from_file: bool = False,
            from_string: bool = False,
            from_object: bool = False,
            config: Union[dict, str] = None) -> Union[dict, int, str, list]:
        """set_config Update the initialized configuration

        Useful for switching contexts at run-time, or if the first load failed because of a typo =)!
        
        \U0001F4D3 -> failure to load a file will not block the object creation ...
        it will create an object with an error message in it's config attribute

        Args:
        config (dict): A python dictionary representation of the provided "config" data
        from_file (bool): True if the successfully sourced config data is from a JSON file
        from_string (bool): True if the successfully sourced config data is from a JSON string
        from_object (bool): True if the successfully sourced config data is from python dict object

        Returns:
            Union[dict, int, str, list]: [description]
        """
        if config is not None:
            self.config = self.__class__.__conf_handler(
                from_file=from_file,
                from_string=from_string,
                from_object=from_object,
                config=config)
        else:
            print(
                f"please set the config value accordingly based on config type."
            )

    def get_key(
        self,
        key_name: str = None,
        value_only: bool = False,
        data: dict = None,
    ) -> Union[dict, int, str, list]:
        """get_key recursively search the config object for `key_name`

        Searches a config dictionary recursively for requested key_name, returns
        - dict by default
        - value only when `value_only` is True 

        Args:
            key_name (str, optional): key within config dictionary to search for. Defaults to None.
            value_only (bool, optional): return only the value. Defaults to False.
            data (dict, optional): ConfigLoader.config<dict>. Defaults to None.

        Returns:
            Union[dict, int, str, list]: [The function may return a dict {k:v} or a bare value based on the args provided]
        """
        del data
        return self.__class__.__get_key(key_name=key_name,
                                        value_only=value_only,
                                        data=self.config)


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
    def __reconfigure_logger(cls, ) -> logging.Logger:
        """__reconfigure_logger Configures logger for class


        Returns:
            logging.Logger: logger object
        """
        logger: logging.Logger = logging.getLogger(cls.__name__)
        loginator: Loginator = Loginator(logger=logger)
        logger: logging.Logger = loginator.logger
        return logger

    def __init__(self,
                 mongo_host: str = None,
                 mongo_port: int = None,
                 mongo_username: str = None,
                 mongo_password: str = None,
                 mongo_database: str = None,
                 pi_host: str = None,
                 pi_port: int = None,
                 metrics_host: str = None,
                 metrics_port: int = None,
                 **kwargs) -> None:
        """__init__ Creates an abstract configuration object 

        The class can be inherited by more specific classes to easily override values, or used on its own as a swiss-army knife configuration factory

        This class paired with the loader class allow flexible loading of configuration values


        Examples:

        # make a loader object and reference some settings file
        
        loader = pylibs.config.config_loader.ConfigLoader(from_file=True, config='settings/config.json')

        # warm up the config attributes
        loader.add_attributes()   

        # reference the loader in the Configuration class
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
        if mongo_username is None and mongo_password is None:  # no auth provided
            self.__class__.logger.warning(
                "neither mongo_username or mongo_password were provided, the connection will not use authentication"
            )
            self.mongo_username: str = "unset"
            self.mongo_password: str = "unset"
        else:  # use provided auth values
            # url parse values so the constructed connection string is valid
            self.mongo_username: str = quote_plus(mongo_username)
            self.mongo_password: str = quote_plus(mongo_password)

        # reconfigure logger

        # defaults for connecting to mongoDB
        self.__class__.logger.warning(
            "mongo_host was not provided, assuming a mongo database is running locally on 127.0.0.1"
        ) if mongo_host is None else None
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
    def get_mongo_database(self, ) -> str:
        """get_mongo_database getter for mongo_database

        Returns:
            str: the mongo database if set
        """
        return self.mongo_database

    @get_mongo_database.setter
    def set_mongo_database(self, value) -> None:
        """set_mongo_database setter for mongo database


        Args:
            value (str): A FQDN or IP for MongoDB
        """
        self.__class__.logger.info(f"setting mongo_database to: {value}")
        self.mongo_database = value

    @property
    def get_mongo_username(self, ) -> str:
        """get_mongo_database getter for mongo_database

        Returns:
            str: the mongo database if set
        """
        return self.mongo_username

    @get_mongo_username.setter
    def set_mongo_username(
        self,
        value: str = None,
    ) -> None:
        """set_mongo_username setter for mongo_username


        Args:
            value (str): The MongoDB Username
        """
        self.__class__.logger.info(f"setting mongo_username to: {value}")
        self.mongo_username = value

    @property
    def get_mongo_password(self, ) -> str:
        """get_mongo_password getter for mongo_password

        Returns:
            str: the mongo password
        """
        return self.mongo_password

    @get_mongo_password.setter
    def set_mongo_password(
        self,
        value: str = None,
    ) -> None:
        """set_mongo_password setter for mongo_password


        Args:
            value (str): The MongoDB Password
        """
        self.__class__.logger.info(f"setting mongo_password to: {value}")
        self.mongo_password = value

    @property
    def get_mongo_host(self, ) -> str:
        """get_mongo_host getter for mongo_host

        Returns:
            str: the mongo host if set
        """
        return self.mongo_host

    @get_mongo_host.setter
    def set_mongo_host(
        self,
        value: str = None,
    ) -> None:
        """set_mongo_host setter for mongo_host


        Args:
            value (str): The MongoDB FQDN or IP
        """
        self.__class__.logger.info(f"setting mongo_host to: {value}")
        self.mongo_host = value

    @property
    def get_mongo_port(self, ) -> int:
        """get_mongo_port getter for mongo_port

        Returns:
            int: the mongo port if set
        """
        return self.mongo_port

    @get_mongo_port.setter
    def set_mongo_port(
        self,
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
    def set_pi_host(self, value) -> None:
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
    def set_pi_port(self, value) -> None:
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
    def set_metrics_host(self, value: str = None) -> None:
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
    def set_metrics_port(self, value: int = None) -> None:
        """set_metrics_port setter for metrics_port


        Args:
            value (int): The MetricsService Port
        """
        self.__class__.logger.info(f"setting metrics_port to: {value}")
        self.metrics_port = int(value)

    def mongo_connection_string(self, ) -> str:
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
        if self.mongo_username != "unset" and self.mongo_password != "unset":  # auth args passed
            if self.mongo_database is None:
                return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}"
            else:
                return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
        else:  #generate noauth connection string
            if self.mongo_database is None:
                return f"mongodb://{self.mongo_host}:{self.mongo_port}"
            else:
                return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"

    def validate_mongo_connection_string(self, ):

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
        super().__init__(mongo_host=mongo_host,
                         mongo_port=mongo_port,
                         mongo_username=mongo_username,
                         mongo_password=mongo_password,
                         mongo_database=mongo_database)

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