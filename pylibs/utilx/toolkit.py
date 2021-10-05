import os
import sys
import logging
import shutil
import configparser




current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = "/".join(current_dir.split('/')[0:-2])

def set_sys_path():
    sys.path.append(project_root)

def get_root_path():
    return project_root

set_sys_path()

from pylibs.logging.loginator import Loginator

logger = logging.getLogger('SchemaMigrationEngine')
loginator = Loginator(
    logger=logger
)



    
