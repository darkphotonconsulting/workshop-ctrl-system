from os.path import (
    dirname,
    abspath
)

from os import (
    environ,
    urandom
)

from json import (
    loads, 
    dumps
)

from sys import (
    stdout,
    stderr,
    path,
    modules
)

from flask import (
    flash, 
    jsonify
)

from flask import (
    request, 
    redirect
)


current_dir = dirname(abspath(__file__))
from microcontroller import create_app
from .config import HEADUNIT_CONFIG
current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-4])
path.append(libs)

print('ok..')


app = create_app()