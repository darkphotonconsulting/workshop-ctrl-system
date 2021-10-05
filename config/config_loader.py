import json
import os, sys
import shlex
from collections import Iterable
from typing import Union, Optional



class ConfigLoader():

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
            key_name (str, optional): [description]. Defaults to None.
            value_only (bool, optional): [description]. Defaults to False.
            data (dict, optional): [description]. Defaults to None.

        Returns:
            Union[dict, int, str, list]: [description]
        """
        ret = {"error": "not found"}
        if data is None:
            return {"error": "please pass a python dictionary into the data arg"}

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
        config: Union[dict,str] = None
    ) -> dict:
        """__conf_handler Handles loading configuration data from various sources

        [extended_summary]

        Args:
            from_file (bool, optional): [Load configuration from a JSON format file]. Defaults to False.
            from_string (bool, optional): [Load configuration from a JSON string]. Defaults to False.
            from_object (bool, optional): [Load configuration from a python dictionary]. Defaults to False.
            config (Union[dict,str], optional): [A path to a file, a JSON string, or a python dictionary]. Defaults to None.

        Returns:
            dict: [the configuration loaded as a python dictionary]
        """

        if (not from_file and from_string and from_object):
            return {
                "error": f"please set atleast one of `from_file` `from_string` or `from_object`"
            }
        if from_object and not ( from_string and from_file):
            print(f"getting config data from object")
            return config

        elif from_string and not ( from_file and from_object):
            print(f"getting config data from string")
            if isinstance(config, str):
                try:
                    return json.loads(
                        config
                    )
                except:
                    return {"error": "can not load string"}
        elif from_file and not ( from_string and from_object):
            print(f"getting config data from file")
            if os.path.exists(config):
                with open(config,'r') as file:
                    try:
                        return json.load(file)
                    except:
                        return {"error": "can not load file"}
        else:
            print(f"failed to parse provided configuration")
            return  {"error": "failed to parse inputs"}

    @classmethod
    def __add_attribute(cls,
        obj,
        attrib: str = None,
        value: Union[list, dict, str, int, bool] = None,
    )-> bool:
        """__add_attribute Add a class attribute to an object

        Adds a class attribute with value to a python object

        Args:
            obj ([obj]): [This should be an instance of ConfigLoader]
            attrib (str, optional): [The name of the attribute]. Defaults to None.
            value (Union[list, dict, str, int, bool], optional): [the value of the attribute]. Defaults to None.

        Returns:
            bool: [True if successful, False if not]
        """
        try:
            setattr(obj, attrib, value)
            return True
        except:
            return False

    @classmethod
    def __add_attributes(cls,
        obj,
        attribs: dict = None,
    ):
        """__add_attributes Iterates through a dictionary recursively adding each key and value as a class attribute

        Adds class attributes with values to a python object based on the provided `attribs` dictionary

        Args:
            obj ([obj]): [This should be an instance of ConfigLoader]
            attribs (dict, optional): [The dict attributes object, `ConfigLoader.config`]. Defaults to None.

        Returns:
            obj: the modified object
        """
        for k,v in attribs.items():
            if isinstance(v, dict):
                cls.__add_attribute(obj=obj, attrib=k, value=v)
                #setattr(obj, k, v)
                cls.__add_attributes(obj=obj, attribs=v)
                #return obj
            else:
                cls.__add_attribute(
                    obj=obj,
                    attrib=k,
                    value=v
                )
        return obj


    def __init__(self,
        from_file: bool = False,
        from_string: bool = False,
        from_object: bool = False,
        config: Union[dict,str] = None
    ) -> None:
        """__init__ Create a ConfigLoader object

        The Config Loader helps with storing and making available configuration values used in the backend, scripts and development

        \U0001F4A1 - keep your version control repository & command history tidy by segregating app code from app configuration!
        
        - load configuration values from a JSON file, JSON string, or python dict object
        - Easily access configuration data safely and securely

        Args:
            from_file (bool, optional): [Load a configuration from a JSON file]. Defaults to False.
            from_string (bool, optional): [Load a configuration from a JSON string]. Defaults to False.
            from_object (bool, optional): [Load a configuration from a python dictionary]. Defaults to False.
            config (Union[dict,str], optional): [A path to a JSON file, A JSON string, or a python dictionary]. Defaults to None.
        """
        self.config = self.__class__.__conf_handler(
            from_file=from_file,
            from_string=from_string,
            from_object=from_object,
            config=config
        )
        self.from_file = from_file
        self.from_string = from_string
        self.from_object = from_object
        self.input = config


    def add_attributes(self,
    ) -> None:
        self.__class__.__add_attributes(
            attribs=self.config,
            obj=self,
        )

    def set_attribute(self,
        attrib: str = None,
        value: Union[list, dict, int, bool, str] = None,
    ) -> None:
        # just reuse this to reset some attribute
        self.__class__.__add_attribute(
            obj=self,
            attrib=attrib,
            value=value
        )


    def print_config(self,
    ) -> None:
        """print_config print the loaded configuration
        """
        print(
            json.dumps(
                self.config, indent=2
            ))

    def get_config(self,) -> dict:
        """get_config return the loaded configuration

        Returns:
            dict: [the config dictionary]
        """
        return self.config

    def set_config(self,
        from_file: bool = False,
        from_string: bool = False,
        from_object: bool = False,
        config: Union[dict,str] = None
    ) -> Union[dict, int, str, list]:
        """set_config Update the initialized configuration

        Useful for switching contexts at run-time, or if the first load failed because of a typo =)!
        
        \U0001F4D3 -> failure to load a file will not block the object creation ...
        it will create an object with an error message in it's config attribute

        Args:
            from_file (bool, optional): [description]. Defaults to False.
            from_string (bool, optional): [description]. Defaults to False.
            from_object (bool, optional): [description]. Defaults to False.
            config (Union[dict,str], optional): [description]. Defaults to None.

        Returns:
            Union[dict, int, str, list]: [description]
        """
        if config is not None:
            self.config = self.__class__.__conf_handler(
                from_file=from_file,
                from_string=from_string,
                from_object=from_object,
                config=config
            )
        else:
            print(f"please set the config value accordingly based on config type.")

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
            key_name (str, optional): [The key to find]. Defaults to None.
            value_only (bool, optional): [Only return the value]. Defaults to False.
            data (dict, optional): [The data to search, by default self.config]. Defaults to None.

        Returns:
            Union[dict, int, str, list]: [The function may return a dict {k:v} or a bare value based on the args provided]
        """
        del data
        return self.__class__.__get_key(
            key_name=key_name,
            value_only=value_only,
            data=self.config
        )
