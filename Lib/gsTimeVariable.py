#/usr/bin/env python

"""
A variable-like object extending over multiple tiles and time slices
Dave Kindig and Alex Pletzer, Tech-X Corp. (2011)
This code is provided with the hope that it will be useful. 
No guarantee is provided whatsoever. Use at your own risk.
"""

import operator
import cdms2
from cdms2.MV2 import concatenate
from cdms2.gsStaticVariable import StaticVariable
from cdms2.error import CDMSError
from cdms2.hgrid import AbstractCurveGrid, TransientCurveGrid
from cdms2.coord import TransientAxis2D, TransientVirtualAxis

class TimeVariable(StaticVariable):

    def __init__(self, HostObj, varName, isFileVariable = False, **slicekwargs):
        """
        Constructor
        @param HostObj host object 
        @param varName variable name
        @param slicekwargs eg lon=(-180,180), lat=(-90,90), time=5
                           cf Packages/cdms2/Lib/cudsinterface.py for 
                           a list of keywords
        """
        self.varName = varName
        self.ntimeSlices = HostObj.ntimeSlices

        self.vars = []
#        if self.ntimeSlices > 0:
#            self.vars = [None for i in range(HostObj.ngrids)]


        kwargs = {}
        for k in slicekwargs.keys():
            kwargs[k.lower()] = slicekwargs[k]

        # time dependent variable. Create a list of list. One list for each
        # grid populated by a list for each time file.
        if ('time' in kwargs.keys() and len(slicekwargs) <= 1) or \
                len(slicekwargs) == 0:
            for gfindx in range(HostObj.ngrids):

                gFName = HostObj.gridFilenames[gfindx]
                
                for tfindx in range(HostObj.ntimeSlices):

                    fName = HostObj.timeDepVars[varName][tfindx][gfindx]
                    fh = cdms2.open(fName, HostObj=HostObj)

                    if isFileVariable:
                        var = fh[varName]
                        if tfindx == 0: 
                            new = [var]
                        else: 
                            new.append(var)
                    else:
                        # TransientVariable
                        var = fh(varName, **slicekwargs)

                        # Attach the grid to the variable
                        grid = cdms2.gsStaticVariable.createTransientGrid(gFName, \
                                             var.attributes['coordinates'])
                        axis0 = var.getAxis(0)
                        gridaxes = grid.getAxisList()
                        axes = [axis0, gridaxes[0], gridaxes[1]]
                        atts = dict(var.attributes)
                        atts.update(fh.attributes)

                        # Create cdms2 transient variable
                        tmp = cdms2.createVariable(var, 
                                    axes = axes, 
                                    grid = grid, 
                                    attributes = atts, 
                                    id = var.standard_name)
                        if tfindx == 0:
                            new = [tmp]
                        else:
                            new.append(tmp)
                        fh.close()

                # Add the variable to the index
                self.vars.append(new)

    def aggregateInTime(self, grid):
        """
        Aggregate a time variable per grid.
        timeVariable[grid]
        @return timeVariable
        """
        pass
        for gfindx in range(HostObj.ngrids):

            # Create the horizontal curvilinear grid.
            # But how do I add the time grid? I don't know it yet.
            # It is known after looping over the time files for a given
            # variable
            gFName = HostObj.gridFilenames[gfindx]
            
            for tfindx in range(HostObj.ntimeSlices):
                fName = HostObj.timeDepVars[varName][tfindx][gfindx]
                fh = cdms2.open(fName)
                print isFileVariable
                if isFileVariable:
                    var = fh[varName]
                    print type(var)
                    if tfindx == 0: 
                        new = var
                    else: 
                        tmp = concatenate((new, var))
                        new = tmp
                else:
                    # TransientVariable
                    var = fh(varName, **slicekwargs)

                    # Attach the grid to the variable
                    grid = cdms2.gsStaticVariable.createTransientGrid(gFName, \
                                         var.attributes['coordinates'])
                    axis0 = var.getAxis(0)
                    gridaxes = grid.getAxisList()
                    axes = [axis0, gridaxes[0], gridaxes[1]]
                    atts = dict(var.attributes)
                    atts.update(fh.attributes)

                    # Create cdms2 transient variable
                    if tfindx == 0:
                        new = cdms2.createVariable(var, 
                                    axes = axes, 
                                    grid = grid, 
                                    attributes = atts, 
                                    id = var.standard_name)
                    else:
                        tmp = concatenate((new, var))
                        axis0 = tmp.getAxis(0)
                        gridaxes = grid.getAxisList()
                        axes = [axis0, gridaxes[0], gridaxes[1]]

                        # Recreate the variable with all the decorations
                        new  = cdms2.createVariable(tmp, 
                                    axes = axes, 
                                    grid = grid, 
                                    attributes = atts, 
                                    id = var.standard_name)
                        
                    fh.close()

            # Add the variable to the index
            print type(new)
            self.vars[gfindx] = new

###################################################################

def test():
    pass

if __name__ == '__main__': test()

