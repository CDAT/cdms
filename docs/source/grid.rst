.. _grid:

grid
====

.. currentmodule:: cdms2.grid 

.. autosummary::
   :toctree:  ./generated

   AbstractGrid.hasCoordType
   isGrid
   setClassifyGrids
   createRectGrid
   createUniformGrid
   createGlobalmeanGrid
   createZonalGrid
   createGenericGrid
   createGaussianGrid
   defaultRegion
   setRegionSpecs

   AbstractGrid
   listall
   str
   info
   writeToFile
   subSlice
   hasCoordType
   getAxisList
   isClose
   checkAxes
   reconcile
   clone
   flatAxes
   size
   writeScrip    

   AbstractRectGrid.classify
   listall
   getshape
   getAxis
   getBounds
   getLatitude
   getLongitude
   getMask
   setMask
   GetOrder
   getType
   setType
   getWeights
   subGrid
   subGridRegion
   transpose
   classify
   classifyInFamily     
   genBounds   
   writeToFile
   getMesh
   glatAxes
   size
   writeScrip
   toCurveGrid
   toGenericGrid
   initDomain
   getMask
   getMaskVar

   FileRectGrid
   setBounds
   getMask
   setMask
   getMaskVar

   TransientRectGrid
   getMask
   setMask
   setBounds
   isGrid
   writeScripGrid
    




    
    

    
    getAxis(naxis)
    getBounds       
    getLatitude
    getLongitude
    getMask
    getMesh
        Generate a mesh array for the meshfill graphics method.
    getOrder
    getType
    getWeights
    setMask(mask, permanent=0)
    setType(gridtype)
    size
        Return number of cells in the grid
    subGrid(latinterval, loninterval
    subGridRegion(latRegion, lonRegion)
    toCurveGrid(gridid=None)
        Convert to a curvilinear grid.
        Parameters:	
            gridid – is the string identifier of the resulting curvilinear grid object.
            _ (None) –

    toGenericGrid(gridid=None)
    transpose
    writeScrip(cufile, gridTitle=None)
        Write a grid to a SCRIP file.
        Parameters:	

            cufile – is a Cdunif file, NOT a CDMS file.
            gridtitle – is a string identifying the grid.

    writeToFile(file)
class FileRectGrid(parent, gridname, latobj, lonobj, order, gridtype, maskobj=None, tempMask=None)
    getMask
    getMaskVar
    setBounds(latBounds, lonBounds, persistent=0)
    setMask(mask, persistent=0)
class RectGrid(parent, rectgridNode=None)
    getMask
    getMaskVar
    initDomain(axisdict, vardict)
class TransientRectGrid(latobj, lonobj, order, gridtype, maskarray=None)
    Grids that live in memory only.
    getMask
    setBounds(latBounds, lonBounds)
    setMask(mask, persistent=0)
createGaussianGrid(nlats, xorigin=0.0)
    Create a Gaussian grid, with shape (nlats, 2*nlats).
    Parameters:	
        nlats – is the number of latitudes.
        xorigin – is the origin of the longitude axis
        order – is either “yx” or “xy”
createGenericGrid(latArray, lonArray, latBounds=None, lonBounds=None, order='yx', mask=None)
createGlobalMeanGrid(grid)
createRectGrid(lat, lon, order='yx', type='generic', mask=None)
createUniformGrid(startLat, nlat, deltaLat, startLon, nlon, deltaLon, order='yx', mask=None)
createZonalGrid(grid)
defaultRegion()
    Returns:	a specification for a default (full) region.
isGrid(grid)
    Is grid a grid?
    Parameters:	
        grid-cdms2 – contruct to be examined
        _ (None) –
setClassifyGrids(mode)
    setRegionSpecs(grid, coordSpec, coordType, resultSpec)
    Modify a list of coordinate specifications, given a coordinate type and a specification for that coordinate.
    Parameters:	
        grid – is the grid object to be associated with the region.
        coordSpec –
        is a coordinate specification, having one of the forms:
            x
        (x,y)
        (x,y,’co’)
        (x,y,’co’,cycle)
        ’:’
        None
        coordType – is one of CoordinateTypes
        resultSpec – is a list of 4-tuples of the form (x,y,’co’,cycle), or None if no spec for the corresponding dimension type. The function sets the appropriate coordinate in resultSpec, in the canonical form (x,y,’co’,cycle). A CDMSError exception is raised if the entry in resultSpec is not None.
    Note: that time coordinate types are not permitted.
writeScripGrid(path, grid, gridTitle=None)
    Write a grid to a SCRIP grid file.
    Parameters:	
        path – is the path of the SCRIP file to be created.
        grid – is a CDMS grid object.
        gridTitle – is a string ID for the grid.

Table Of Contents

    1. Introduction
    2. CDMS Python Application Programming Interface
    3. Module: CdTime
    4. Regridding Data
    5. Plotting CDMS data in Python
    6. Climate Data Markup Language (CDML)
    7. CDMS Utilities
    8. APPENDIX A
    9. APPENDIX B
    10. APPENDIX C
    11. CDMS Sample Dataset
    12. API

Search
