""" Utility functions

Returns:
    [type]: [description]
"""
import os
import sys
import re
import logging
import inspect
#import pkgutil
from pkgutil import ModuleInfo
from pkgutil import walk_packages
import shutil
import importlib
import platform
from dataclasses import dataclass
from typing import (
    Any
)

@dataclass
class EcoSystem:
    packages: dict
    modules: dict
    classes: dict

@dataclass
class Pkg:
    name: str
    ref: Any
    package: bool
@dataclass 
class Mod:
    name: str
    ref: Any
    package: bool

@dataclass
class Klass:
    name: str
    ref: Any
    funcs: list

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = "/".join(CURRENT_DIR.split('/')[0:-2])
# print(CURRENT_DIR)
# print(PROJECT_ROOT)

def mach(
) -> str:
    """mach return the machine type

    Returns:
        str: machine type
    """
    return platform.machine()

def arch(
) -> tuple:
    """arch return the system architecture

    Returns:
        tuple: (bits, architecture)
    """
    return platform.architecture()

def system(
) -> str:
    """system return OS system



    Returns:
        str: OS system
    """
    return platform.system()

def name(
) -> str:
    """name return host name

    Returns:
        str: host name
    """
    return platform.node()

def projectpath(  
) -> str:
    """projectpath project root path

    Returns:
        str: root path
    """
    return PROJECT_ROOT

def libpath(   
) -> str:
    """libpath python libs path


    Returns:
        str: library path
    """
    return os.path.join(PROJECT_ROOT, "pylibs")

def addroot(
) -> list:
    """addroot Add the absolute path to project root into sys path

    Returns:
        list: the modified sys.path
    """
    sys.path.append(PROJECT_ROOT)
    return sys.path

def packages(
    ignore: list = None
) -> list:
    """packages list of packages in PROJECT_ROOT

    Args:
        ignore (list, optional): package names to ignore. Defaults to None.

    Returns:
        list: packages defined within ecosystem
    """
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    return [i for i in walk_packages([PROJECT_ROOT]) if i.ispkg==True and i.name not in ignore]

def package_names(
    ignore: list = None
) -> list:
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    return list(sorted(set([ name for finder, name, ispkg in walk_packages([PROJECT_ROOT]) if ispkg==True ]) - ignore))


def modulesv2(
    package: ModuleInfo = None, 
    ignore: list = None
):
    modules = []
    if package is None:
        for loader, name, pkg in packages():

                _pkg = loader.find_module(name).load_module(name)
                #print(_pkg)
                mods = [mod for mod in inspect.getmembers(_pkg, ) if type(mod[-1]).__name__=='module']
                #print(mods)
                modules.extend(mods)

    return modules

def module_namesv2(
    package: ModuleInfo = None, 
    ignore: list = None
):
    modules = []
    if package is None:
        for loader, name, pkg in packages():
                _pkg = loader.find_module(name).load_module(name)
                mods = inspect.getmembers(_pkg, inspect.ismodule)
                modules.extend([mod.__name__ for mod in mods if '__name__' in mod])

    return modules

def classesv2(
    module: ModuleInfo = None, 
    ignore: list = None,
) -> list:
    #package = set(packages())
    klasses = []
    if module is None:
        for loader, name, pkg in modules():
            if 'pylibs' in name:
                _pkg = loader.find_module(name).load_module(name)
                pkg_classes = [klass for klass in inspect.getmembers(_pkg, inspect.isclass) if name in str(klass[-1])]
                klasses.extend(pkg_classes)
    else:
        for loader, name, pkg in modules():
            if 'pylibs' in name and module.name==name:
                _pkg = loader.find_module(name).load_module(name)
                pkg_classes = [klass for klass in inspect.getmembers(_pkg, inspect.isclass) if module.name in str(klass[-1])]
                klasses.extend(pkg_classes)        
    return klasses
                
                #print(mods)
def modules(
    package: ModuleInfo = None,
    ignore: list = None
) -> list:
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    if package is None:
        return [i for i in walk_packages([PROJECT_ROOT]) if i.ispkg==False and i.name not in ignore ]
    else:
        return [i for i in walk_packages([PROJECT_ROOT]) if i.ispkg==False and i.name not in ignore and package.name in i.name]
        


def module_names(
    package: ModuleInfo,
    ignore: list = None
) -> list:
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    if package is None:
        return list(sorted(set([ name for finder, name, ispkg in walk_packages([PROJECT_ROOT]) if ispkg==False ]) - ignore))
    else:
        return list(sorted(set([ name for finder, name, ispkg in walk_packages([PROJECT_ROOT]) if ispkg==False  and package.name in name]) - ignore))

def classes(
    module: ModuleInfo = None
) -> list:
    #modules = modules() if module is None else [i for i in modules()]
    klasses = []
    for loader, name, pkg in modules():
        #print(name)
        _mod = loader.find_module(name).load_module(name)
        builtins = set(_mod.__builtins__)
        _mod_defs = list(
            builtins - 
            set(
                list(
                    _mod.__dict__.keys()
                )
            )
        )
        globals()[name] = _mod
        module_members = inspect.getmembers(_mod, inspect.isclass)
        for name, obj in module_members:
            
            if "pylibs" in str(obj):
                
                if module is not None:
                    if module.name in str(obj):
                        print(obj)
                        klasses.append(obj)
                else: 
                    print(obj)
                    klasses.append(obj)
                          
    return klasses
        
def class_names(
    module: ModuleInfo = None
) -> list:
    klasses = []
    for loader, name, pkg in modules():
        #print(name)
        _mod = loader.find_module(name).load_module(name)
        builtins = set(_mod.__builtins__)
        _mod_defs = list(
            builtins - 
            set(
                list(
                    _mod.__dict__.keys()
                )
            )
        )
        globals()[name] = _mod
        module_members = inspect.getmembers(_mod, inspect.isclass)
        for name, obj in module_members:
            if "pylibs" in str(obj):
                if module is None:
                    klass = re.match(
                        r".*\'(?P<className>.+)\'.*",
                        str(obj)
                    ).groups('className')[0]
                    klasses.append(klass)
                else:
                    if module.name in str(obj):
                        klass = re.match(
                            r".*\'(?P<className>.+)\'.*",
                            str(obj)
                        ).groups('className')[0]
                        klasses.append(klass)
    return klasses

def functions(
    klass: object = None
) -> list:
  funcs = []
  for k, v in klass.__dict__.items():
      if k.startswith('__'): continue
      if type(v).__name__ == 'function': funcs.append(v)
  return funcs     

def function_names(
    klass: object = None
) -> list:
  funcs = []
  for k, v in klass.__dict__.items():
      if k.startswith('__'): continue
      if type(v).__name__ == 'function': funcs.append(v)
  return funcs



def ecosystem() -> EcoSystem:
    
    eco = EcoSystem(
        packages={
            package.name: {
                'ref': package.module_finder.find_module(package.name).load_module(package.name),
                'package': package.ispkg,
                
            } for package in packages()
            },
        modules={
            module.name: {
                'ref': module.module_finder.find_module(module.name).load_module(module.name), 
                'package': module.ispkg
            } for module in modules()
            },
        classes={
            
        }
    )

    for mod in modules():
        klasses = classesv2(module=mod)
        for klass_name, klass in klasses:
            eco.classes[klass_name] = dict(
                ref=klass,
                funcs=[]
            )
            
            funcs = functions(klass)
            eco.classes[klass_name]['funcs'].extend(funcs)            
    return eco



    
