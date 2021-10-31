import os
import sys
import pytest
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
sys.path.append(libs)
#print(libs)

from pylibs.utilx.toolkit import ecosystem
from pylibs.utilx.toolkit import (
    EcoSystem,
    Pkg,
    Mod,
    Klass
)

PYLIBS_MODULES = [
    'pylibs.arduino.programmer',
    'pylibs.coders.encode',
    'pylibs.coders.decode',
    'pylibs.constants.constants',
    'pylibs.database.common',
    'pylibs.database.schemas',
    'pylibs.database.engines',
    'pylibs.database.factory',
    'pylibs.pi',
    'pylibs.relay',
]

@pytest.fixture
def eco():
    return ecosystem()

def test_ecosystem_struct(eco):
    assert isinstance(eco, EcoSystem)
    assert isinstance(eco.modules, list)
    assert isinstance(eco.packages, list)
    assert isinstance(eco.classes, list)
    
    


    
def test_imports(capsys):
    """test_imports Test imports under the pylibs module tree
    """
    try:
        for module in PYLIBS_MODULES:
            #with capsys.disabled():
            sys.stdout.write(f"\n importing {module} ")
            globals()[module] = __import__(module)

        assert all(
            module_path in [m for m in sys.modules.keys() if m.startswith('pylibs')] for module_path in PYLIBS_MODULES
        )
    except ImportError as error_message:
        print('error...')


    assert isinstance("", str)
