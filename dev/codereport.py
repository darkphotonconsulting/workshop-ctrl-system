import os 
import sys 
import inspect
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = "/".join(CURRENT_DIR.split('/')[0:-1])
#print(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)
from pylibs.utilx.toolkit import (
    ecosystem, 

)
from pylibs.utilx.toolkit import (
    EcoSystem,
    Pkg, 
    Mod, 
    Klass 
)
from dataclasses import dataclass
from typing import (
    Any
)

@dataclass
class PkgReport:
    total_packages: int
    missing_docs: list
    has_docs: list

    def doc_coverage(self):
        total = self.total_packages
        return len(self.has_docs)/total*100
        

@dataclass
class ModReport:
    total_modules: int
    total_loc: int
    missing_docs: list
    has_docs: list


    def doc_coverage(self):
        total = self.total_modules
        return len(self.has_docs)/total*100

@dataclass
class KlassReport:
    total_classes: int
    total_loc: int
    missing_docs: list
    has_docs: list


    def doc_coverage(self):
        total = self.total_classes
        return len(self.has_docs)/total*100

@dataclass
class EcoSystemReport:
    packages: PkgReport
    modules: ModReport
    classes: KlassReport

eco = ecosystem()


def package_report(
    ecosys: EcoSystem = None
): 
    report = {}
    total_loc = 0
    total_packages = 0
    missing_docs = []
    ecosys = eco if ecosys is None else ecosys
    for i, pkg in enumerate(ecosys.packages):
        total_packages = i
        report[pkg.name] = dict()
        report[pkg.name]['absolute_file'] = inspect.getabsfile(pkg.ref)
        report[pkg.name]['doc'] = inspect.getdoc(pkg.ref)
        if inspect.getdoc(pkg.ref) is None: missing_docs.append(pkg.name)
        # report[pkg.name]['source'] = inspect.getsourcelines(pkg.ref) if type(inspect.getsourcelines(pkg.ref)) == tuple and len(inspect.getsourcelines(pkg.ref))>0 else ""
        #report[pkg.name]['loc'] = len(inspect.getsourcelines(pkg.ref)[0]) if type(inspect.getsourcelines(pkg.ref)) == tuple and len(inspect.getsourcelines(pkg.ref))==2 else 0
        #total_loc += report[pkg.name]['loc'] 
    return report, total_loc, missing_docs, total_packages        



    
def module_report(
    ecosys: EcoSystem = None
) -> dict:
    report = {}
    total_loc = 0
    total_modules = 0
    missing_docs = []
    ecosys = eco if ecosys is None else ecosys
    for i, pkg in enumerate(ecosys.modules):
        total_modules = i
        report[pkg.name] = dict()
        report[pkg.name]['absolute_file'] = inspect.getabsfile(pkg.ref)
        report[pkg.name]['doc'] = inspect.getdoc(pkg.ref)
        if inspect.getdoc(pkg.ref) is None: missing_docs.append(pkg.name)
        # report[pkg.name]['source'] = inspect.getsourcelines(pkg.ref) if type(inspect.getsourcelines(pkg.ref)) == tuple and len(inspect.getsourcelines(pkg.ref))>0 else ""
        report[pkg.name]['loc'] = len(inspect.getsourcelines(pkg.ref)[0]) if type(inspect.getsourcelines(pkg.ref)) == tuple and len(inspect.getsourcelines(pkg.ref))==2 else 0
        total_loc += report[pkg.name]['loc'] 
    return report, total_loc, missing_docs, total_modules

def class_report(
    ecosys: EcoSystem = None
) -> dict:
    report = {}
    total_loc = 0
    total_classes = 0
    missing_docs = []
    ecosys = eco if ecosys is None else ecosys
    for i, klass in enumerate(ecosys.classes):
        total_classes = i
        report[klass.name] = dict()
        report[klass.name]['absolute_file'] = inspect.getabsfile(klass.ref)
        report[klass.name]['doc'] = inspect.getdoc(klass.ref)
        if inspect.getdoc(klass.ref) is None: missing_docs.append(klass.name)
        # report[pkg.name]['source'] = inspect.getsourcelines(pkg.ref) if type(inspect.getsourcelines(pkg.ref)) == tuple and len(inspect.getsourcelines(pkg.ref))>0 else ""
        report[klass.name]['loc'] = len(inspect.getsourcelines(klass.ref)[0]) if type(inspect.getsourcelines(klass.ref)) == tuple and len(inspect.getsourcelines(klass.ref))==2 else 0
        total_loc += report[klass.name]['loc'] 
    return report, total_loc, missing_docs, total_classes


def report(
    ecosys: EcoSystem = None
) -> EcoSystemReport:
        ecosys = eco if ecosys is None else ecosys
        return EcoSystemReport(
            packages = PkgReport(
                total_packages=len(ecosys.packages),
                missing_docs=[
                    pkg.name for pkg in ecosys.packages if inspect.getdoc(pkg.ref) is None
                ],
                has_docs=[
                    pkg.name for pkg in ecosys.packages if inspect.getdoc(pkg.ref) is not None
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
                ]
                
            )
        )


rep = report()


print(rep)

print("Package Document Coverage: ",rep.packages.doc_coverage(), "%")

print("Module Document Coverage: ", rep.modules.doc_coverage(), "%")

print("Class Document Coverage", rep.classes.doc_coverage(), "%")