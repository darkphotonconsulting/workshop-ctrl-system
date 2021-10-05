import os
import sys
import json
import logging
from copy import copy
import shutil
#get home
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-3])
sys.path.append(libs)

import pytest

from pylibs.schema.default_schemas import StaticSchemas, DynamicSchemas, SchemaFactory
from pylibs.schema.migration import SchemaMigrationEngine
from backend.config import BaseConfig

# the right way to go about testing MongoDB functions is to use a mockapi
# https://pytest-mock-resources.readthedocs.io/en/latest/quickstart.html
# we are limited due to MongoDB versions available on armv7 32-bit OS
# recent mongo versions require 64 bit OS
# latest raspbian officials are still 32-bit

