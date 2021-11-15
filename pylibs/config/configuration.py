""" Configuration
"""
import os
import sys
import abc

import shlex
import json
import logging

from collections import Iterable
from urllib.parse import quote_plus

from types import (
    FunctionType
)
from typing import (
    Any,
    Union,
    Optional
)
from attr import attr
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

    - Keep your version control repository & command history tidy by segregating app code from app configuration!
        
    - load configuration values from a JSON file, JSON string, or python dict object
    
    - Easily access configuration data safely and securely

    - dynamically adds class properties, getters and setters for each k/v pair defined in config source


    Examples:

        from config.config_loader import ConfigLoader
        
        config = ConfigLoader(from_file=True,config='settings/config.json')

        # access the values pythonically
        
        config.mongo_username
        
        config.mongo_password
        
        # or target a specfic config section:
        
        config.database (the entire database object)
        
        config.database['mongo_username']
        
        ...
    
    Class Attributes:
    
        config (dict): A python dictionary representation of the provided "config" data
        
        from_file (bool): True if the successfully sourced config data is from a JSON file
        
        from_string (bool): True if the successfully sourced config data is from a JSON string
        
        from_object (bool): True if the successfully sourced config data is from python dict object

        keys (list): list of top level sections in provided config

        input (dict): the parse config object
        
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
        self.__class__.__add_attributes(obj=self, attribs=self.config)
        self.keys = list(self.config.keys())
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
    def __dump_attributes(cls, 
        obj: Any = None, 
        attribs: dict = None,
        data: dict = None,
    ) -> dict:
        """__dump_attributes flattens a nested attribute dict and returns result

        Args:
        
            obj (Any, optional): Object. Defaults to None.
            
            attribs (dict, optional): attribs dict. Defaults to None.
            
            data (dict, optional): result dict (for recursion). Defaults to None.

        Returns:
        
            dict: [description]
        """
        data  = {} if data is None else data
        for k, v in attribs.items():
            if isinstance(v, dict):
                data[k] = v
                data = cls.__dump_attributes(obj=obj, attribs=v, data=data)
            else:
                data[k] = v
        return data        

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

        
        ```python
            cls.__add_attributes(
                obj=obj,
                attribs=obj.config
            )
        ``` 
        
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
        self.__class__.__add_attribute(obj=self, attrib=attrib, value=value)

    def print_config(self, ) -> None:
        """print_config - print the loaded configuration
        """
        print(json.dumps(self.config, indent=2))

    def get_config(self, ) -> dict:
        """get_config - return the python dict representation of loaded configuration data

        Returns:
            dict: the config dictionary
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

    def all(self,
    ) -> dict:
        """all return a dictionary containing all defined attributes

        Returns:
            dict: all parsed attributes
        """
        return self.__class__.__dump_attributes(obj=self, attribs=self.config)


class Configuration(object, metaclass=abc.ABCMeta):
    
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

    @classmethod
    def __get_attribute(
        cls,
        obj,
        attrib: str = None
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
            return getattr(obj, attrib)
        except:
            return False
             
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
    def __add_getter(
        cls,
        obj,
        attrib: str = None,
    ) -> bool:
        #print(f"{dir(obj)}")
        getter_code = compile(
            f"def get_{attrib}(): return getattr(self, {attrib})",
            "<string>",
            "exec"
        )
        getter_func = FunctionType(getter_code.co_consts[0], globals(), f"get_{attrib}")
        #print('getter function: ', getter_func)
        def getter():
            return getattr(obj, attrib)

        try:
            setattr(obj, f"get_{attrib}", getter)
            
            return True
        except:
            return False

    @classmethod
    def __add_setter(
        cls,
        obj,
        attrib: str = None,
        value: Union[dict, str, int, bool] = None,

    ):
        def setter(value: str = None):
            setattr(obj, attrib, value)
        setattr(obj, f"set_{attrib}", setter)

    @classmethod
    def __add_setters(cls,
        obj,
        attribs: dict = None
    ):
        """__add_setters add setters for attributes in attribs dict
        """

        for k,v in attribs.items():
            if isinstance(v, dict):
                cls.__add_setter(obj=obj, attrib=k, value=v)
                cls.__add_setters(obj=obj, attribs=attribs[k])
            else:
                cls.__add_setter(obj=obj, attrib=k, value=v)
        

    @classmethod
    def __add_getters(
        cls,
        obj,
        attribs: dict = None
    ):
        """__add_getters add getters for attributes in attribs dict
        """
        for k, v in attribs.items():
            # print(f"adding getter for {k}")
            if isinstance(v, dict): 
                cls.__add_getter(obj, attrib=k)
                cls.__add_getters(obj, attribs=attribs[k])
                #print(k, id(obj),dir(obj))
                
                #return obj
            else:
                cls.__add_getter(obj, attrib=k)
                #print(k, id(obj),dir(obj))
                #return obj
        
        #return obj

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

    @classmethod
    def __clean_dict(cls,
        attribs: dict = None,
        data: dict = None
    )-> dict:
        data = dict() if data is None else data
        attribs = dict() if attribs is None else attribs
        for k, v in attribs.items():
            if type(v).__name__ == 'function':
                continue
            if isinstance(v, dict):
                data[k] = v
                data = cls.__clean_dict(attribs=v, data=data)
            data[k] = v
        return data
        
    def __init__(self, 
        **kwargs):
        """__init__ return a Configuration object
        """
        self.config = kwargs
        self.keys = list(kwargs.keys())
        self.__class__.__add_attributes(obj=self, attribs=self.config)
        print(f"adding getters and setters..")
        self.__class__.__add_getters(obj=self, attribs=self.config)
        self.__class__.__add_setters(obj=self, attribs=self.config)
        #self.__dict__ = self.__class__.__clean_dict(attribs=self.__dict__)
        #print('flattened config: ',json.dumps(kwargs, indent=2))

    # def __dict__(self,
    # ) -> dict:
    #     return self.__class__.__clean_dict(attribs=self.__dict__)

    def print_config(self,
    ) -> None:
        """print_config print configured object values
        """
        print(json.dumps(self.config, indent=2))
        
    def mongo_connection_string(self,
        mongo_host: str = None,
        mongo_port: int = None,
        mongo_username: str = None,
        mongo_password: str = None,
        mongo_database: str = None,
    ) -> str:
        """mongo_connection_string - generates mongodb connection string based on provided values


        ### Example Usage:

        ```
        import pymongo
        
        configuration = backend.config_redux.Configuration()

        ```
        #### sane defaults allow no args to be passed in, an authless connection to localhost is assumed

        ```ipython
        In [260]: configuration.mongo_connection_string()
        
        Out[260]: 'mongodb://127.0.0.1:27017'

        ```
        
        #### validate a connection before using it

        ```ipython
        In [261]:  configuration.validate_mongo_connection_string()
        
        🍺 > > > > > > > > > > executionTime: [2021-10-09 04:24:31,207] - moduleName: [Configuration] - logLevel: [INFO] - msgContents: connected lineOfCode: (config_redux.py:227)
        
        Out[261]: True
        
        ```

        ```python
        if configuration.validate_mongo_connection_string(): 
            client = pymongo.MongoClient(configuration.mongo_connection_string())
            client.server_info()
        ```
        
        Returns:
        
            str: a usable mongodb connection string
        """
        #mongo_host = getattr(self, 'mongo_host') if (hasattr(self, 'mongo_host') and mongo_host is None) else mongo_host
        mongo_host = mongo_host if mongo_host is not None else getattr(self, 'mongo_host')
        #mongo_port = getattr(self, 'mongo_port') if (hasattr(self, 'mongo_port') and mongo_port is None) else mongo_port
        mongo_port = mongo_port if mongo_port is not None else getattr(self, 'mongo_port')

        # auth on or off
        if ( (hasattr(self, 'mongo_username') or mongo_username is not None) and (hasattr(self, 'mongo_password') or mongo_password is not None)): #auth is enabled
            mongo_username = mongo_username if mongo_username is not None else getattr(self, 'mongo_username')
            #mongo_username = getattr(self, 'mongo_username') if mongo_username is None else mongo_username
            #mongo_password = getattr(self, 'mongo_password') if mongo_password is None else mongo_password
            mongo_password = mongo_password if mongo_password is not None else getattr(self, 'mongo_password')
            if (hasattr(self, 'mongo_database') or mongo_database is not None): # use a database
                mongo_database = mongo_database if mongo_database is not None else getattr(self, 'mongo_database')
                return f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}"
                #return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}"
            else: # dont use a database
                return f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}"
        else: # auth is disabled
            if (hasattr(self, 'mongo_database') or mongo_database is not None): # use a database
                mongo_database = mongo_database if mongo_database is not None else getattr(self, 'mongo_database')
                return f"mongodb://{mongo_host}:{mongo_port}/{mongo_database}"
                #return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}"
            else: # dont use a database
                return f"mongodb://{mongo_host}:{mongo_port}"
            #mongo_port = getattr(self, 'mongo_port') if (hasattr(self, 'mongo_port') and mongo_port is None) else mongo_port
        
        # if hasattr(self, 'mongo_username') and hasattr(self, 'mongo_password'):  # auth args passed
        #     if not hasattr(self, 'mongo_database'):
        #         return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}"
        #     else:
        #         return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
        # else:  #generate noauth connection string
        #     if not hasattr(self, 'mongo_database'):
        #         return f"mongodb://{self.mongo_host}:{self.mongo_port}"
        #     else:
        #         return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"

    def validate_mongo_connection_string(self, 
        mongo_host: str = None,
        mongo_port: int = None,
        mongo_username: str = None,
        mongo_password: str = None,
        mongo_database: str = None,
    )-> bool:
        """validate_mongo_connection_string validate a mongodb connection string

        Returns:
        
            bool: True if connection is valid, False otherwise
        """

        try:
            client = MongoClient(self.mongo_connection_string(
                mongo_host=mongo_host,
                mongo_port=mongo_port,
                mongo_username=mongo_username,
                mongo_password=mongo_password,
                mongo_database=mongo_database,
            ))
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