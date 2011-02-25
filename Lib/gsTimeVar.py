#/usr/bin/env python

"""
A variable-like object extending over multiple tiles and time slices
$Id: gsTimeVar.py 1654 2011-01-18 22:11:06Z pletzer $
"""

import operator
import ctypes
import cdms2
from cdms2.MV2 import concatenate
from cdms2.gsStatVar import GsStatVar
from cdms2.error import CDMSError
from cdms2.hgrid import AbstractCurveGrid
import types

import sys

#class SV(AbstractVariable):
#    def __init__(self, var):
#        self.var = var
#    def getLatitude(self):
#        print 'do stuff'

class GsTimeVar:

    def __init__(self, GsHost, varName):
        """
        Constructor
        @param varName variable name
        @param ntimeSlices number time files
        @param ngrids number of grids
        """
        self.varName = varName
        self.ntimeSlices = GsHost.ntimeSlices

        self.vars = []
        if self.ntimeSlices > 0:
            self.vars = [None for i in range(GsHost.ngrids)]

        # time dependent variable. Concatenate the current file variable
        # into the last for a given grid. This builds gives a consisent
        # variable across time.
        for gfindx in range(GsHost.ngrids):

            # Create the horizontal curvilinear grid.
            # But how do I add the time grid? I don't know it yet.
            # It is known after looping over the time files for a given
            # variable
            gName = GsHost.gridFilenames[gfindx]
            g  = cdms2.open(gName)
            lon = g('lon')
            lat = g('lat')
            curvegrid = AbstractCurveGrid(lat, lon)
            
            for tfindx in range(GsHost.ntimeSlices):
                fName = GsHost.timeDepVars[varName][tfindx][gfindx]
                fh = cdms2.open(fName)
                # TransientVariable
                var = fh(varName)

                # Create cdms2 transient variable
                if tfindx == 0:
                    tmp = cdms2.createVariable(var, datatype = var, 
                        axes = [var.getAxis(0), lon.getAxis(0), lon.getAxis(1)])
                else:
                    tmp = concatenate((tmp, var))

                fh.close()

            # Attach the grid to the variable
            print var.getAxis(1)
            print lon.getAxis(1)
            Domain = tmp.getDomain()
            self.vars[gfindx] = cdms2.createVariable(tmp)
            print '\nCreateVar\n'
            print self.vars[gfindx].setGrid(curvegrid)
            sys.exit(1)

            # Concatenate is messing with the attributes, so I am reattaching them
            self.vars[gfindx].attributes = {}
            for key in var.attributes.keys():
                self.vars[gfindx].__setattr__(key, var.attributes[key])

            # Add some methods to GsTimeVar[gfindx]
            addGetLatitudeToAbstractVariable(self.vars[gfindx])
            addGetLongitudeToAbstractVariable(self.vars[gfindx])
            addGetGridToAbstractVariable(self.vars[gfindx])
            addGetCoordinatesToAbstractVariable(self.vars[gfindx])

            # Add some other attributes
            self.vars[gfindx].tile_name    = fh.tile_name
            self.vars[gfindx].gridFilename = gName
            grids = cdms2.open(gName)
            self.vars[gfindx].gridIndex    = gfindx
#            self.vars[gfindx].setGrid(grids('lon'))

    def __getitem__(self, tfindx):
        """
        Data accessor
        @param tfindx file file index
        @return variable at tfindx
        """
        return self.vars[tfindx]

    def __setitem__(self, tfindx, vals):

        """
        Data setter
        @param tfindx time file indexer
        @param vals values to set
        """
        self.vars[tfindx] = vals

    def shape(self, gfindx):
        """
        Return the shape in the format (n0, n1, ...)
        @param gfindx time file index
        @return result
        """
        v = self.vars[gfindx]
        if v:
            return self.vars[tfindx].shape
        else:
            return []

    def getLatitude(self, gfindx):
        """
        Return the coordinate data associated with variable
        @param AbstractVariable a Abstract variable
        """

        aa = self[gfindx]
        fh = cdms2.open(self[gfindx].gridFilename)
        if 'coordinates' in self[gfindx].attributes.keys():
          xn, yn = self[gfindx].attributes['coordinates'].split()

          y = fh(yn)

          return y
        else:
            raise CDMSError, "No 'coordinates' attribute. Can't getLatitude"

    def getLongitude(self, gfindx):
        """
        Return the coordinate data associated with variable
        @param AbstractVariable a Abstract variable
        """

        fh = cdms2.open(self[gfindx].gridFilename)
        print self[gfindx].attributes.keys()
        if 'coordinates' in self[gfindx].attributes.keys():
          xn, yn = self[gfindx].attributes['coordinates'].split()

          y = fh(yn)

          return y
        else:
            raise CDMSError, "No 'coordinates' attribute. Can't getLongitude"

    def size(self):
        """
        Return the total number of elements
        @return number of elements
        """
        return reduce(operator.mul, [v.size() for v in self.vars])

    def typecode(self):
        """
        Return the type of the data
        @return type
        """
        v = self.vars[0]
        if v:
            return self.vars[0].typecode()
        return None

    def __repr__(self):
        res = ""
        for gfindx in range(len(self.vars)):
            res += (" Grid slice %d: " % gfindx) + repr(self.vars[gfindx])
        return res

###############################################################################

# Add getCoordinates and use these versions of getLongitude and getLatitude
# for each grid in a GsStatVar
#
# This is not very satisfactory, since I am having to duplicate the code in
# gsStatVar.py
def addGetLatitudeToAbstractVariable(AbstractVariable):
    """
    Update the AbstractVariable method getLatitude
    @param AbstractVariable a Abstract variable
    """
    def getLatitude(self):
        """
        Return the coordinate data associated with variable
        @param AbstractVariable a Abstract variable
        @return latitude from a cdms2.hgrid.AbstrctCurveGrid
        """
        if 'coordinates' in self.attributes.keys():
          return self.getGrid().getLatitude()

        else:
            raise CDMSError, "No 'coordinates' attribute. Can't getLatitude"
            

    # Add getLatitude to the AbstractVariable Class
    AbstractVariable.getLatitude = types.MethodType(getLatitude, AbstractVariable)

def addGetLongitudeToAbstractVariable(AbstractVariable):
    """
    Update the AbstractVariable method getLongitude
    @param AbstractVariable a Abstract variable
    @return grid a cdms2.hgrid.AbstrctCurveGrid object
    """
    def getLongitude(self):
        """
        Return the coordinate data associated with variable
        @param AbstractVariable a Abstract variable
        @return longitude from a cdms2.hgrid.AbstrctCurveGrid
        """

        if 'coordinates' in self.attributes.keys():
          return self.getGrid().getLongitude()
        else:
            raise CDMSError, "No 'coordinates' attribute. Can't getLongitude"

    # Add getLongitude to the AbstractVariable Class
    AbstractVariable.getLongitude = types.MethodType(getLongitude, AbstractVariable)

def addGetGridToAbstractVariable(AbstractVariable):
    """
    Update getGrid in the Class AbstractVariable
    @param AbstractVariable a Abstract variable
    """
    def getGrid(self):
        """
        Return the coordinate data associated with variable
        @param AbstractVariable a Abstract variable
        @return grid a cdms2.hgrid.AbstrctCurveGrid object
        """

        fh = cdms2.open(self.gridFilename)
        if 'coordinates' in self.attributes.keys():
            xn, yn = self.attributes['coordinates'].split()
    
            x = fh(xn)
            y = fh(yn)
            grid = AbstractCurveGrid(x, y)
    
            return grid
        else:
            raise CDMSError, "No 'coordinates' attribute. Can't getLongitude"

    # Add getGrids to the AbstractVariable Class
    AbstractVariable.getGrid = types.MethodType(getGrid, AbstractVariable)

def addGetCoordinatesToAbstractVariable(AbstractVariable):
    """
    Add getCoordinates to the Class AbstractVariable
    @param AbstractVariable a Abstract variable
    """
    def getCoordinates(AbstractVariable):
        """
        Return the coordinate data associated with variable
        @param AbstractVariable a Abstract variable
        @return a tuple of lon and lat
        """
        av = AbstractVariable

        fh = cdms2.open(av.gridFilename)
        if 'coordinates' in av.attributes.keys():
            xn, yn = av.attributes['coordinates'].split()
    
            x = fh(xn)
            y = fh(yn)
    
            return (x, y)
        else:
            raise CDMSError, "No 'coordinates' attribute. Can't getLongitude"

    # Add getCoordinates to the AbstractVariable Class
    AbstractVariable.getCoordinates = types.MethodType(getCoordinates, AbstractVariable)


###################################################################
def test():
    pass

if __name__ == '__main__': test()

