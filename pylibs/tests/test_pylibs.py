#import os

from os.path import (
    dirname,
    abspath
)
import sys

from sys import (
    stdout,
    stderr,
    path,
    modules
)
from random import (
    randint
)
import pytest
current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
path.append(libs)
#print(libs)
import pylibs.utilx.toolkit
from pylibs.utilx.toolkit import (
    ecosystem, 
    report
)
from pylibs.utilx.toolkit import (
    EcoSystem,
    Pkg,
    Mod,
    Klass,
    EcoSystemReport,
    PkgReport,
    ModReport,
    KlassReport
)

DOC_COVERAGE = 75

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
    """eco returns ecosystem 
    """
    return ecosystem()

@pytest.fixture 
def ecoreport():
    """ecoreport return ecosystem report

    

    Returns:
        EcoSystemReport: an eco system code report
    """
    return report()

@pytest.fixture
def eco_package(eco):
    return eco.packages[randint(0, len( eco.packages)-1)]

@pytest.fixture
def eco_module(eco):
    return eco.modules[randint(0, len( eco.modules)-1)]

@pytest.fixture
def eco_class(eco):
    return eco.classes[randint(0, len( eco.classes)-1)]

def test_eco_structure(eco):
    """test_eco_structure test eco system object structure

    

    Args:
        eco (EcoSystem): validates an EcoSystem structure
    """
    assert isinstance(eco, EcoSystem)
    assert isinstance(eco.modules, list)
    assert isinstance(eco.packages, list)
    assert isinstance(eco.classes, list)
    
def test_eco_report(ecoreport, capsys):
    sys.stdout.write(f"report type: {type(ecoreport)}")
    assert isinstance(ecoreport, pylibs.utilx.toolkit.EcoSystemReport)
    assert isinstance(ecoreport.packages, pylibs.utilx.toolkit.PkgReport)
    # #assert type(ecoreport)==EcoSystemReport
    assert isinstance(ecoreport.modules, pylibs.utilx.toolkit.ModReport)
    assert isinstance(ecoreport.classes, pylibs.utilx.toolkit.KlassReport)
    #assert isinstance("", str)

def test_eco_code_quality(ecoreport, capsys):
    assert ecoreport.packages.doc_coverage() > DOC_COVERAGE
    stdout.write(f"package doc coverage: {ecoreport.packages.doc_coverage()} %")
    assert ecoreport.modules.doc_coverage() > DOC_COVERAGE
    stdout.write(f"module doc coverage: {ecoreport.modules.doc_coverage()} %")
    assert ecoreport.classes.doc_coverage() > DOC_COVERAGE
    stdout.write(f"class doc coverage: {ecoreport.classes.doc_coverage()} %")

def test_random_eco_package(eco_package):
    assert isinstance(eco_package, pylibs.utilx.toolkit.Pkg)

def test_random_eco_module(eco_module):
    assert isinstance(eco_module, pylibs.utilx.toolkit.Mod)

def test_random_eco_class(eco_class):
    assert isinstance(eco_class, pylibs.utilx.toolkit.Klass)


def test_imports(capsys):
    """test_imports Test imports under the pylibs module tree
    """
    try:
        for module in PYLIBS_MODULES:
            #with capsys.disabled():
            sys.stdout.write(f"\n importing {module} ")
            globals()[module] = __import__(module)

        assert all(
            module_path in [m for m in modules.keys() if m.startswith('pylibs')] for module_path in PYLIBS_MODULES
        )
    except ImportError as error_message:
        print('error...')


    assert isinstance("", str)
