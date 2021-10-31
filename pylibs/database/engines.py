"""Schema Migration Engine
"""
import os
import sys
import json
import logging
from copy import copy
#from types import NoneType
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])
sys.path.append(libs)

from typing import (
    Union,
)

from .common import Mongo
from .schemas import StaticSchemas, DynamicSchemas
from .schemas import SchemaFactory
from pylibs.logging.loginator import Loginator
from pylibs.coders.decode import SchemaTemplateDecoder
from pylibs.coders.encode import SchemaTemplateEncoder
from pylibs.config.configuration import Configuration

__all__ = [
    'SchemaMigrationEngine',
    'DataSeedEngine'
]
NoneType = type(None)

class SchemaMigrationEngine(Mongo, metaclass=object):
    STATIC_SCHEMAS = StaticSchemas()
    DYNAMIC_SCHEMAS = DynamicSchemas()
    DEFAULT_SCHEMAS = dict(**STATIC_SCHEMAS.__dict__, **DYNAMIC_SCHEMAS.__dict__)
    #logger = Loginator(logger=logging.getLogger('SchemaMigration')).logger

    def __init__(self,
        schema_factory: SchemaFactory = None,
        database_name: str = None,
        collection_name: str = None,
        config: Configuration = None,
        use_default_schemas: bool = True,
        schema: dict = None,
        schema_template: dict = None,
        **kwargs
    ) -> None:

        super().__init__(
            config = config,
            database_name=database_name,
            collection_name=collection_name,
            **kwargs
        )
        self.__class__.logger = self.__class__.__init_logger__()
        self.schema_factory: SchemaFactory = SchemaFactory() if schema_factory is None else schema_factory
        if use_default_schemas:
            self.schema_template: dict = self.__class__.STATIC_SCHEMAS.system if schema_template is None else schema_template
            self.schema: dict = self.compile_schema_template(schema_template=self.schema_template) if schema is None else schema
        else:
            self.schema_template: Union[dict, None] = schema_template
            self.schema: Union[dict, NoneType] = schema

    @classmethod
    def __init_logger__(cls,

        ) -> logging.Logger:
        """__reconfigure_logger Configures the inherited logger for current class


        Returns:
            logging.Logger: logger object
        """
        logger = Loginator(
            logger=logging.getLogger(cls.__name__)
        ).logger
        return logger


    def get_default_schema_template(self,
        schema_template_name: str = None,
        pretty_print: bool = None,
    ) -> dict:
        #print(self.__class__.SCHEMAS)
        print(
            json.dumps(
                self.__class__.DEFAULT_SCHEMAS.get(
                    schema_template_name, {}
                ),
                indent=2,
                cls=SchemaTemplateEncoder
            )
        ) if pretty_print else None
        #print('here')
        return self.__class__.DEFAULT_SCHEMAS.get(
            schema_template_name, {}
        )
        #print()

    def read_template(self,
        file_path: str = None
    ):
        return self.schema_factory.load_schema_template_from_file(
            schema_template_path=file_path
        )

    def write_template(self,
        schema_template: dict = None,
        file_path: str = None,
    ) -> bool:
        file_path = 'schemas/schema.json' if file_path is None else file_path
        if len(file_path.split('/'))>1:
            if os.path.exists(os.path.dirname(file_path)):
                if schema_template is not None:
                    with open(file_path, 'w') as file:
                        file.write(
                            json.dumps(
                                schema_template,
                                indent=2,
                                cls=SchemaTemplateEncoder,
                            )
                        )

                    if os.path.exists(file_path):
                        return True
                    else: return False
                else: return False




    def compile_schema_template(self,
        schema_template: dict = None,
    ) -> dict:
        schema_template = self.schema_template if schema_template is None else schema_template
        schema_factory = copy(self.schema_factory)
        validator = copy(schema_factory.validator)
        schema = schema_factory.generate_schema(schema_template)
        validator['$jsonSchema']['properties'] = schema
        return validator


    def set_schema_template(self,
        schema_template: dict = None
    ) -> None:
        self.schema_template = schema_template

    #pass

class DataSeedEngine(Mongo, metaclass=object):
    pass