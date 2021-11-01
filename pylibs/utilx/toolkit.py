""" Utility functions
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
    """ Describes the headunit python ecosystem
    """
    packages: list
    modules: list
    classes: list


@dataclass
class Pkg:
    """ A package within the ecosystem
    """
    name: str
    ref: Any
    package: bool


@dataclass 
class Mod:
    """ A module within the ecosystem
    """
    name: str
    ref: Any
    package: bool

@dataclass
class Klass:
    """ A class within the ecosystem
    """
    name: str
    ref: Any
    funcs: list

@dataclass
class PkgReport:
    """ Pkg Report
    """
    total_packages: int
    missing_docs: list
    has_docs: list
    missing_all: list
    has_all: list

    def doc_coverage(self):
        total = self.total_packages
        return len(self.has_docs)/total*100

    def all_coverage(self):
        total = self.total_packages
        return len(self.has_all)/total*100
        

@dataclass
class ModReport:
    """ Mod Report
    """
    total_modules: int
    total_loc: int
    missing_docs: list
    has_docs: list
    missing_all: list
    has_all: list


    def doc_coverage(self):
        total = self.total_modules
        return len(self.has_docs)/total*100

    def all_coverage(self):
        total = self.total_modules
        return len(self.has_all)/total*100

@dataclass
class KlassReport:
    total_classes: int
    total_loc: int
    missing_docs: list
    has_docs: list
    missing_all: list
    has_all: list


    def doc_coverage(self):
        total = self.total_classes
        return len(self.has_docs)/total*100

    def all_coverage(self):
        total = self.total_classes
        return len(self.has_all)/total*100

@dataclass
class EcoSystemReport:
    packages: PkgReport
    modules: ModReport
    classes: KlassReport

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
    """package_names a list of package names


    Args:
        ignore (list, optional): [description]. Defaults to None.

    Returns:
        list: [description]
    """
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    return list(sorted(set([ name for finder, name, ispkg in walk_packages([PROJECT_ROOT]) if ispkg==True ]) - ignore))


def modulesv2(
    package: ModuleInfo = None, 
    ignore: list = None
) -> list:
    """modulesv2 a list of modules


    Args:
        package (ModuleInfo, optional): [description]. Defaults to None.
        ignore (list, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
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
) -> list:
    """module_namesv2 return list of module names

    Args:
        package (ModuleInfo, optional): a package module info object. Defaults to None.
        ignore (list, optional): list of packages to ignore. Defaults to None.

    Returns:
        [type]: [description]
    """
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
    """modules list of module info objects

    Args:
        package (ModuleInfo, optional): a package module info object. Defaults to None.
        ignore (list, optional): list of packages to ignore. Defaults to None.

    Returns:
        list: list of module info objects
    """
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    if package is None:
        return [i for i in walk_packages([PROJECT_ROOT]) if i.ispkg==False and i.name not in ignore ]
    else:
        return [i for i in walk_packages([PROJECT_ROOT]) if i.ispkg==False and i.name not in ignore and package.name in i.name]
        


def module_names(
    package: ModuleInfo,
    ignore: list = None
) -> list:
    """module_names list of module names

    Args:
        package (ModuleInfo): [description]
        ignore (list, optional): [description]. Defaults to None.

    Returns:
        list: [description]
    """
    ignore = set(['pylibs']) + set(ignore) if ignore is not None else set(['pylibs'])
    if package is None:
        return list(sorted(set([ name for finder, name, ispkg in walk_packages([PROJECT_ROOT]) if ispkg==False ]) - ignore))
    else:
        return list(sorted(set([ name for finder, name, ispkg in walk_packages([PROJECT_ROOT]) if ispkg==False  and package.name in name]) - ignore))

def classes(
    module: ModuleInfo = None
) -> list:
    """classes return list of tuples [(klassName, klass), ...]

    Args:
        module (ModuleInfo, optional): [description]. Defaults to None.

    Returns:
        list: [description]
    """
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
    """class_names return list of class names

    

    Args:
        module (ModuleInfo, optional): module to list classes in. Defaults to None.

    Returns:
        list: list of class names
    """
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
    """functions list of functions defined in class



    Args:
        klass (object, optional): the class object. Defaults to None.

    Returns:
        list: list of functions
    """
    funcs = []
    for k, v in klass.__dict__.items():
        if k.startswith('__'): continue
        if type(v).__name__ == 'function': funcs.append(v)
    return funcs     

def function_names(
    klass: object = None
) -> list:
    """function_names [summary]

    [extended_summary]

    Args:
        klass (object, optional): [description]. Defaults to None.

    Returns:
        list: [description]
    """
    funcs = []
    for k, v in klass.__dict__.items():
        if k.startswith('__'): continue
        if type(v).__name__ == 'function': funcs.append(v)
    return funcs



def ecosystem(
) -> EcoSystem:
    """ecosystem return an EcoSystem object

    

    Returns:
        EcoSystem: an EcoSystem object describing the code defined in pylibs
    """
    return EcoSystem(
        packages=[
            Pkg(
                name=package.name,
                ref=package.module_finder.find_module(package.name).load_module(package.name),
                package=package.ispkg 
            ) for package in packages()
        ],
        modules=[
            Mod(
                name=module.name,
                ref=module.module_finder.find_module(module.name).load_module(module.name),
                package=module.ispkg
            ) for module in modules()
        ],
        classes=[
            Klass(
                name=klass_name,
                ref=klass,
                funcs=functions(klass)
            ) for klass_name, klass in classesv2()
        ]
    )

def report(
    ecosys: EcoSystem = None
) -> EcoSystemReport:
        ecosys = ecosystem() if ecosys is None else ecosys
        return EcoSystemReport(
            packages = PkgReport(
                total_packages=len(ecosys.packages),
                missing_docs=[
                    pkg.name for pkg in ecosys.packages if inspect.getdoc(pkg.ref) is None
                ],
                has_docs=[
                    pkg.name for pkg in ecosys.packages if inspect.getdoc(pkg.ref) is not None
                ],
                missing_all=[
                    pkg.name for pkg in ecosys.packages if '__all__' not in pkg.ref.__dict__
                ],
                has_all=[
                    pkg.name for pkg in ecosys.packages if '__all__' in pkg.ref.__dict__
                ]
            ),
            modules = ModReport(
                total_modules=len(ecosys.modules),
                total_loc=sum([
                    len(inspect.getsourcelines(mod.ref)[0]) for mod in ecosys.modules if type(inspect.getsourcelines(mod.ref))==tuple and len(inspect.getsourcelines(mod.ref))==2
                ]),
                missing_docs=[
                    mod.name for mod in ecosys.modules if inspect.getdoc(mod.ref) is None
                ],
                has_docs=[
                    mod.name for mod in ecosys.modules if inspect.getdoc(mod.ref) is not None
                ],
                missing_all=[
                    mod.name for mod in ecosys.modules if '__all__' not in mod.ref.__dict__
                ],
                has_all=[
                    mod.name for mod in ecosys.modules if '__all__' in mod.ref.__dict__
                ]
            ), 
            classes = KlassReport(
                total_classes=len(ecosys.classes),
                total_loc=sum([ len(inspect.getsourcelines(klass.ref)[0]) for klass in ecosys.classes if type(inspect.getsourcelines(klass.ref))==tuple and len(inspect.getsourcelines(klass.ref))==2 ]),
                missing_docs=[
                    klass.name for klass in ecosys.classes if inspect.getdoc(klass.ref) is None
                ],
                has_docs=[
                    klass.name for klass in ecosys.classes if inspect.getdoc(klass.ref) is not None
                ],
                missing_all=[
                    klass.name for klass in ecosys.classes if '__all__' not in klass.ref.__dict__
                ],
                has_all=[
                    klass.name for klass in ecosys.classes if '__all__' in klass.ref.__dict__
                ]
                
            )
        )


    
