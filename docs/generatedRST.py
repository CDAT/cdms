#!/bin/env python
from inspect import getmembers, isfunction, isclass, ismethod, isbuiltin
import importlib
import sys
import cdms2
import regrid2

def getMember(imported_module):
    member_list = []
#    member_list = [o for o in getmembers(imported_module) if isclass(o[1])]
    member_list += [o for o in getmembers(imported_module) if isfunction(o[1])]
    member_list += [o for o in getmembers(imported_module) if ismethod(o[1]) if o[1].__doc__ is not None]
    return member_list

def RSTwrite(module, memberlist):
    if module.find(":") != -1:
        currentmodule = ".".join(module.split(":")[:-1])
    else:
        currentmodule = module
    print currentmodule
    auto = ".".join(module.split(":")[1:])
    for member in memberlist:
        print member[0]
        modulemember = module.replace(":",".") + "." + member[0]
        f = open("/tmp/" + modulemember + ".rst", "w")
        f.write(module+"\n")
        f.write(len(module) * "="+"\n")
        f.write("\n")
        f.write(".. currentmodule:: " + currentmodule+"\n")
        f.write("\n")
        if isfunction(member[1]): 
            if auto == "":
                f.write(".. autofunction:: " +  member[0]+"\n")
            else:
                f.write(".. autofunction:: " +  auto + "." + member[0]+"\n")
        elif isclass(member[1]) and member[0] != "__class__":
            f.write(".. autoclass:: " + member[0]+"\n")
            sublist = getMember(modulemember)
            print modulemember
            createRSTfiles([modulemember])
        elif ismethod(member[1]):
            f.write(".. automethod:: " + auto+"."+member[0]+"\n")
        f.close()

def createRSTfiles(modules):
    for module in modules:
        try:
            import importlib
            m=importlib.import_module(module.replace(":","."))
        except:
            m = eval(module.replace(":","."))
 
        cdms2_all_list = getMember(m)
        print cdms2_all_list
        RSTwrite(module, cdms2_all_list)

if __name__ == "__main__":

    modules = ["cdms2.hgrid", "cdms2.hgrid:AbstractHorizontalGrid", "cdms2.hgrid.DatasetCurveGrid","cdms2.hgrid.FileCurveGrid", "cdms2.hgrid:TransientCurveGrid","cdms2.hgrid:AbstractCurveGrid", "cdms2.grid:AbstractGrid:hasCoordType", "cdms2.grid:AbstractRectGrid","cdms2.grid:FileRectGrid", "cdms2.grid:TransientRectGrid", "cdms2.grid", "cdms2.grid:AbstractGrid","cdms2.avariable:AbstractVariable","regrid2.horizontal", "regrid2.esmf", "regrid2.esmf:EsmfUnstructGrid","regrid2.esmf:EsmfStructField","regrid2.esmf:EsmfRegrid", "regrid2.esmf:EsmfStructGrid","regrid2.crossSection","regrid2.mvESMFRegrid","regrid2.mvGenericRegrid","regrid2.pressure","regrid2.scrip","regrid2.pressure","regrid2.scrip","regrid2.mvGenericRegrid:GenericRegrid","regrid2.scrip","regrid2.scrip.ScripRegridder","regrid2.scrip.ConservativeRegridder","regrid2.scrip.BilinearRegridder","regrid2.scrip.BicubicRegridder","regrid2.scrip.DistwgtRegridder","regrid2.horizontal","cdms2.forecast:forecasts","cdms2.forecast:forecast","cdms2.forecast","cdms2.database", "cdms2.database:AbstractDatabase","cdms2.database:LDAPDatabase","cdms2.database:AbstractSearchResult","cdms2.database:LDAPSearchResult","cdms2.database:AbstractResultEntry","cdms2.cudsinterface:cuDataset","cdms2.convention", "cdms2.convention:AliasList", "cdms2.convention.AbstractConvention", "cdms2.convention:NUGConvention", "cdms2.convention:COARDSConvention", "cdms2.convention:CFConvention","cdms2.cdxmllib:XMLParser","cdms2.cdurlparse", "cdms2.cache","cdms2.cache:Cache","cdms2.cdurllib:CDURLopener","cdms2.dataset", "cdms2.dataset:Dataset", "cdms2.dataset:CdmsFile", "cdms2.bindex", "MV2", "cdms2.variable", "cdms2.variable:DatasetVariable", "cdms2.fvariable:FileVariable", "cdms2.axis", "cdms2.axis:AbstractAxis", "cdms2.axis:Axis", "cdms2.axis:TransientAxis", "cdms2.axis:TransientVirtualAxis", "cdms2.axis:FileAxis", "cdms2.axis:FileVirtualAxis", "cdms2.tvariable", "cdms2.tvariable:TransientVariable", "cdms2.avariable","cdms2.avariable:AbstractVariable"]
    createRSTfiles(modules)


#numpy.ndarray.flags

#===================
#
#.. currentmodule:: numpy
#
#.. autoattribute:: ndarray.flags

