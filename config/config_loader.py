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
        """__get_key [summary]

        [extended_summary]

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
        try:
            setattr(obj, attrib, value)
            return True
        except:
            return False

    @classmethod
    def __add_attributes(cls,
        obj,
        attribs: dict = None,
    ) -> bool:
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
        print(
            json.dumps(
                self.config, indent=2
            ))

    def get_config(self,) -> dict:
        return self.config

    def set_config(self,
        from_file: bool = False,
        from_string: bool = False,
        from_object: bool = False,
        config: Union[dict,str] = None
    ) -> Union[dict, int, str, list]:
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
        del data
        return self.__class__.__get_key(
            key_name=key_name,
            value_only=value_only,
            data=self.config
        )
