"""
$Id: testEsmfSalinity.py 2434 2012-08-22 03:46:36Z pletzer $

Test interpolation on salinity datasets

"""

import pdb
import time
import re
import numpy
import cdat_info
import cdms2
import regrid2
import unittest
import ESMF
from regrid2 import esmf
import sys
PLOT = False
if PLOT:
    from matplotlib import pylab

HAS_MPI = False
try:
    from mpi4py import MPI
    HAS_MPI = True
except:
    pass

def _buildCorners(bounds):
    """
    Return an array of bounds converted from [x, [y], nDims] -> x+1, [y+1]
    @param bounds CdmsVar.getBounds()
    @return ndarrray of bounds
    """

    bndShape = [s+1 for s in bounds.shape[:-1]]
    bnd = numpy.ones(bndShape, dtype = bounds.dtype)
    if len(bndShape) == 1:
        bnd[:-1] = bounds[..., 0]
        bnd[ -1] = bounds[ -1, 1]
    elif len(bndShape) > 1:
        bnd[:-1, :-1] = bounds[  :,  :, 0]
        bnd[:-1,  -1] = bounds[  :, -1, 1]
        bnd[ -1,  -1] = bounds[ -1, -1, 2]
        bnd[ -1, :-1] = bounds[ -1,  :, 3]

    return bnd

def _getCorners(coordBounds):
    """
    Return a list of bounds built from a list of coordinates
    @param coordBounds boundary coordinate list
    @return [latBounds, lonBounds]
    """
    bounds = []
    for c in coordBounds:
        bnds = _buildCorners(c)
        bounds.append(bnds)

    return bounds


class Test(unittest.TestCase):

    def setUp(self):

        self.pe = 0
        self.nprocs = 1
        if HAS_MPI:
            self.pe = MPI.COMM_WORLD.Get_rank()
            self.nprocs = MPI.COMM_WORLD.Get_size()
        
    def test0_ESMP(self):
        
        srcF = cdms2.open(cdat_info.get_sampledata_path()+'/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = srcF['so'][0, 0,...]
        missing_value = 1.e20
        srcGrd = [srcF.variables['lat'][:], srcF.variables['lon'][:]]
        srcBounds = _getCorners([srcF.variables['lat_vertices'][:], srcF.variables['lon_vertices'][:]])

        lat1dBounds = numpy.arange(-90.0, 90.001, 5.0)
        lon1dBounds = numpy.arange(-180.0, 180.001, 5.0)
        lat1dCENTER = 0.5*(lat1dBounds[:-1] + lat1dBounds[1:])
        lon1dCENTER = 0.5*(lon1dBounds[:-1] + lon1dBounds[1:])
        lat2dBounds = numpy.outer(lat1dBounds, numpy.ones( (len(lon1dBounds),), lon1dBounds.dtype ) )
        lon2dBounds = numpy.outer(numpy.ones( (len(lat1dBounds),), lat1dBounds.dtype ), lon1dBounds )
        lat2dCENTER = numpy.outer(lat1dCENTER, numpy.ones( (len(lon1dCENTER),), lon1dCENTER.dtype ) )
        lon2dCENTER = numpy.outer(numpy.ones( (len(lat1dCENTER),), lat1dCENTER.dtype ), lon1dCENTER )
        dstGrd = [lat2dCENTER, lon2dCENTER]
        dstBounds = [lat2dBounds, lon2dBounds]
        
        coordSys = ESMF.CoordSys.SPH_DEG # ESMP.ESMP_COORDSYS_CART fails
        
        srcDims = srcGrd[0].shape
        dstDims = dstGrd[0].shape

        # do we need to revert the order here?
        srcMaxIndex = numpy.array(srcDims, numpy.int32) # number of cells
        dstMaxIndex = numpy.array(dstDims, numpy.int32) # number of cells

        # grids
        srcGrid = ESMF.Grid(srcMaxIndex, coord_sys=coordSys, staggerloc=[ESMF.StaggerLoc.CENTER])
        dstGrid = ESMF.Grid(dstMaxIndex, coord_sys=coordSys, staggerloc=[ESMF.StaggerLoc.CENTER])

        # it's a good idea to always add the nodal coordinates
        srcGrid.add_coords(ESMF.StaggerLoc.CORNER)
        dstGrid.add_coords(ESMF.StaggerLoc.CORNER)

        # masks
        srcGrid.add_item(item=ESMF.GridItem.MASK)
        dstGrid.add_item(item=ESMF.GridItem.MASK)

        srcGridMaskPtr = srcGrid.get_item(item=ESMF.GridItem.MASK)
        dstGridMaskPtr = srcGrid.get_item(item=ESMF.GridItem.MASK)

        # get pointer to coordinates array and dimensions
        # src
        srcXCorner = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CORNER)
        srcYCorner = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CORNER)

        srcLoCorner = srcGrid.lower_bounds[ESMF.StaggerLoc.CORNER]
        srcHiCorner = srcGrid.upper_bounds[ESMF.StaggerLoc.CORNER]

        srcXCENTER =  srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        srcYCENTER =  srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

        srcLoCENTER = srcGrid.lower_bounds[ESMF.StaggerLoc.CENTER]
        srcHiCENTER = srcGrid.upper_bounds[ESMF.StaggerLoc.CENTER]

        # dst
        dstXCorner = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CORNER)
        dstYCorner = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CORNER)

        dstLoCorner = dstGrid.lower_bounds[ESMF.StaggerLoc.CORNER]
        dstHiCorner = dstGrid.upper_bounds[ESMF.StaggerLoc.CORNER]

        dstXCENTER =  dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        dstYCENTER =  dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

        dstLoCENTER = dstGrid.lower_bounds[ESMF.StaggerLoc.CENTER]
        dstHiCENTER = dstGrid.upper_bounds[ESMF.StaggerLoc.CENTER]

        # fields
        srcFld = ESMF.Field(srcGrid, name='srcFld', 
                                        typekind = ESMF.TypeKind.R8,
                                        staggerloc = ESMF.StaggerLoc.CENTER)
        dstFld = ESMF.Field(dstGrid, name= 'dstFld', 
                                        typekind = ESMF.TypeKind.R8,
                                        staggerloc = ESMF.StaggerLoc.CENTER)
        srcAreaField = ESMF.Field(srcGrid, name='srcAreas', 
                                                 typekind = ESMF.TypeKind.R8,
                                                 staggerloc = ESMF.StaggerLoc.CENTER)
        dstAreaField = ESMF.Field(dstGrid, name='dstAreas',
                                                 typekind = ESMF.TypeKind.R8,
                                                 staggerloc = ESMF.StaggerLoc.CENTER)
        srcFracField = ESMF.Field(srcGrid, name='srcFracAreas',
                                                 typekind = ESMF.TypeKind.R8,
                                                 staggerloc = ESMF.StaggerLoc.CENTER)
        dstFracField = ESMF.Field(dstGrid, name='dstFracAreas',
                                                 typekind = ESMF.TypeKind.R8,
                                                 staggerloc = ESMF.StaggerLoc.CENTER)

        srcFieldPtr = srcFld.data
        srcFracPtr  = srcFracField.data
        dstFieldPtr = dstFld.data
        dstFracPtr  = dstFracField.data

        # set the coordinates and field values. In ESMP, arrays are column major!

        # src-corners
        srcYCorner[:] = srcBounds[0][:]
        srcXCorner[:] = srcBounds[1][:]

        # src-center coordinates, field, and mask 
        srcNx = srcHiCENTER[0] - srcLoCENTER[0]
        srcNy = srcHiCENTER[1] - srcLoCENTER[1]
        yc = numpy.array(srcGrd[0][:])
        xc = numpy.array(srcGrd[1][:])
        srcYCENTER[:] = yc
        srcXCENTER[:] = xc
        msk = numpy.array(so[:] == missing_value, numpy.int32)
        srcGridMaskPtr[:] = msk

        fld = numpy.array(so[:], so.dtype)
        # set to zero where masked
        fld *= (1 - msk)
        srcFieldPtr[:] = fld
        srcFracPtr[:] = 1.0
        
        # dst-corners
        dstYCorner[:] = dstBounds[0][:]
        dstXCorner[:] = dstBounds[1][:]

        # dst-center coordinates, field, and mask 
        yc = numpy.array(dstGrd[0][:])
        xc = numpy.array(dstGrd[1][:])

        dstYCENTER[:] = yc
        dstXCENTER[:] = xc

        dstGridMaskPtr[:] = 0
        dstFieldPtr[:] = missing_value
        dstFracPtr[:] = 1.0

        # interpolation
        maskVals = numpy.array([1], numpy.int32) # values defining mask
        regrid = ESMF.Regrid(srcFld, dstFld, 
                             src_mask_values=maskVals, 
                             dst_mask_values=maskVals,
                             regrid_method=ESMF.RegridMethod.CONSERVE, 
                             unmapped_action=ESMF.UnmappedAction.IGNORE, 
                             src_frac_field=srcFracField, 
                             dst_frac_field=dstFracField)

        regrid(srcFld, dstFld)

        # get the cell areas
        srcAreaField.get_area()
        dstAreaField.get_area()
        srcAreasPtr = srcAreaField.data
        dstAreasPtr = dstAreaField.data

        srcFracPtr = srcFracField.data
        dstFracPtr = dstFracField.data

        # check conservation
        srcFldSum, dstFldSum = srcFieldPtr.sum(), dstFieldPtr.sum()
        srcFldIntegral = (srcFieldPtr * srcAreasPtr * srcFracPtr).sum()
        dstFldIntegral = (dstFieldPtr * dstAreasPtr * dstFracPtr).sum()
        lackConservLocal = srcFldIntegral - dstFldIntegral

        # check for nans
        if numpy.isnan(srcFracPtr).sum() > 0:
            print '[%d] *** %d Nans found in srcFracPtr!!' % (self.pe, numpy.isnan().sum(srcFracPtr))
        if numpy.isnan(dstFracPtr).sum() > 0:
            print '[%d] *** %d Nans found in dstFracPtr!!' % (self.pe, numpy.isnan().sum(dstFracPtr))
                                                                              
        print '[%d] checksum of src: %g checksum of dst: %g' % (self.pe, srcFldSum, dstFldSum)
        print '[%d] src total area integral: %g dst total area integral: %g diff: %g\n' % \
            (self.pe, srcFldIntegral, dstFldIntegral, lackConservLocal)

        if HAS_MPI:
            lackConserv = MPI.COMM_WORLD.reduce(lackConservLocal, op=MPI.SUM, root=0)
        else:
          lackConserv = lackConservLocal
        
        if self.pe == 0:
            print 'ROOT: total lack of conservation (should be small): %f' % lackConserv

        # cleanup
#        ESMP.ESMP_FieldRegridRelease(regrid)
#        ESMP.ESMP_FieldDestroy(srcAreaField)
#        ESMP.ESMP_FieldDestroy(dstAreaField)
#        ESMP.ESMP_FieldDestroy(srcFracField)
#        ESMP.ESMP_FieldDestroy(dstFracField)
#        ESMP.ESMP_FieldDestroy(srcFld)
#        ESMP.ESMP_FieldDestroy(dstFld)
#        ESMP.ESMP_GridDestroy(srcGrid)
#        ESMP.ESMP_GridDestroy(dstGrid)


    def test1_esmf(self):
        srcF = cdms2.open(cdat_info.get_sampledata_path() + \
                              '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = srcF('so')[0, 0, ...]
        srcGridMask = numpy.array((so == so.missing_value), numpy.int32)
        clt = cdms2.open(cdat_info.get_sampledata_path() + '/clt.nc')('clt')[0,...]
        srcGrd = [so.getGrid().getLatitude(), so.getGrid().getLongitude()]
        dG = clt.getGrid().toCurveGrid()
        dstGrd = [dG.getLatitude()[:], dG.getLongitude()[:]]

        srcBounds = cdms2.mvCdmsRegrid.getBoundList(srcGrd)
        dstBounds = cdms2.mvCdmsRegrid.getBoundList(dstGrd)
            

        srcGrid = esmf.EsmfStructGrid(srcGrd[0].shape, 
                            coordSys = ESMF.CoordSys.SPH_DEG)
        srcGrid.setCoords([numpy.array(coord) for coord in srcGrd], 
                          staggerloc = ESMF.StaggerLoc.CENTER,
                          globalIndexing = True)
        srcGrid.setCoords(srcBounds, 
                          staggerloc = ESMF.StaggerLoc.CORNER,
                          globalIndexing = True)
        srcGrid.setMask(srcGridMask)

        dstGrid = esmf.EsmfStructGrid(dstGrd[0].shape, 
                            coordSys = ESMF.CoordSys.SPH_DEG)
        dstGrid.setCoords([numpy.array(coord) for coord in dstGrd], 
                            staggerloc = ESMF.StaggerLoc.CENTER,
                          globalIndexing = True)
        dstGrid.setCoords(dstBounds, 
                          staggerloc = ESMF.StaggerLoc.CORNER,
                          globalIndexing = True)

        srcFld = esmf.EsmfStructField(srcGrid, 'srcField', 
                                      datatype = so.dtype, 
                                      staggerloc = ESMF.StaggerLoc.CENTER)
        srcFld.setLocalData(numpy.array(so), 
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True)
        dstFld = esmf.EsmfStructField(dstGrid, 'dstField', 
                                      datatype = so.dtype, 
                                      staggerloc = ESMF.StaggerLoc.CENTER)
        dstFld.setLocalData(numpy.array(clt) * 0,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True)

        srcFracFld = esmf.EsmfStructField(srcGrid, 'srcFracAreasFld', 
                                          datatype = 'float64', 
                                          staggerloc = ESMF.StaggerLoc.CENTER)
        srcFracFld.setLocalData(numpy.ones(srcGrd[0].shape, dtype=srcGrd[0].dtype),
                                staggerloc = ESMF.StaggerLoc.CENTER,
                                globalIndexing = True)
        dstFracFld = esmf.EsmfStructField(dstGrid, 'dstFracAreasFld', 
                                          datatype = 'float64', 
                                          staggerloc = ESMF.StaggerLoc.CENTER)
        dstFracFld.setLocalData(numpy.ones(dstGrd[0].shape, dtype=dstGrd[0].dtype),
                                staggerloc = ESMF.StaggerLoc.CENTER,
                                globalIndexing = True)

        # this fails on 7 and 8 procs (passing dstFrac = None works)
        ro = esmf.EsmfRegrid(srcFld, dstFld,
                             srcFrac = srcFracFld, dstFrac = None,
                             srcMaskValues = numpy.array([1], numpy.int32),
                             dstMaskValues = numpy.array([1], numpy.int32),
                             regridMethod = ESMF.RegridMethod.CONSERVE,
                             unMappedAction = ESMF.UnmappedAction.IGNORE)
        # interpolate
        ro()
        dstData = dstFld.getData(rootPe = 0)
        if self.pe == 0:
            dstMask = (dstData >= 100 )
            dstDataM = numpy.ma.array(dstData, mask = dstMask)
            dstDataM.missing_value = so.missing_value

            zeroVal = (dstDataM == 0)

            dstDataMMin = dstDataM.min()
            dstDataMMax = dstDataM.max()
            print 'Number of zero valued cells', zeroVal.sum()
            print 'min/max value of dstDataM: %f %f' % (dstDataMMin, dstDataMMax)                               
            self.assertLess(dstDataMMax, so.max())

    def test2_ESMFRegrid(self):
        srcF = cdms2.open(cdat_info.get_sampledata_path() + \
                              '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = srcF['so']
        srcGridMask = numpy.array((so[0, 0,...] == so.missing_value) , numpy.int32)
        clt = cdms2.open(cdat_info.get_sampledata_path() + '/clt.nc')('clt')[0, ...]
        srcGrd = [so.getGrid().getLatitude(), so.getGrid().getLongitude()]
        srcBounds = cdms2.mvCdmsRegrid.getBoundList(srcGrd)
        dG = clt.getGrid().toCurveGrid()
        dstGrd = [dG.getLatitude()[:], dG.getLongitude()[:]]
        dstBounds = cdms2.mvCdmsRegrid.getBoundList(dstGrd)


        # create regrid object
        srcGrdShape = srcGrd[0].shape
        dstGrdShape = dstGrd[0].shape
        r = regrid2.mvESMFRegrid.ESMFRegrid(srcGrdShape, dstGrdShape, 
                                            dtype=so.dtype,
                                            regridMethod='conserve', 
                                            staggerLoc='center', 
                                            periodicity=0, 
                                            coordSys='deg',
                                            srcGridMask=srcGridMask, 
                                            hasSrcBounds = True,
                                            hasDstBounds = True)
        globalIndexing = False
        # Find the slabs for each processor
        dstSlab = r.getDstLocalSlab("center")
        srcSlab = r.getSrcLocalSlab("center")
        srcBSlab = r.getSrcLocalSlab("corner")
        dstBSlab = r.getDstLocalSlab("corner")

        r.setCoords([numpy.array(g[srcSlab]) for g in srcGrd], 
                    [numpy.array(g[dstSlab]) for g in dstGrd], 
                    srcGridMask=srcGridMask, 
                    srcBounds = [numpy.array(b[srcBSlab]) for b in srcBounds],
                    dstBounds = [numpy.array(b[dstBSlab]) for b in dstBounds], 
                    globalIndexing = globalIndexing)

        # compute weights
        start = time.time()
        r.computeWeights()
        finish = (time.time() - start)

        print '\nSeconds to computeWeights -> finish  = %f s' % numpy.round(finish,2)

        # Get the source data slab/ create dst data container
        localSrcData = so[0, 0, srcSlab[0], srcSlab[1]].data
        dstShp = dG.getLatitude().shape
        dstData = numpy.ones(dstShp, so.dtype)[dstSlab[0], dstSlab[1]] * so.missing_value

        # interpolate
        r.apply(localSrcData, dstData, rootPe = None, 
                globalIndexing = None)
        
        if self.pe == 0:
            # checks
            dstDataMask = (dstData == so.missing_value)
            print 'number of masked values = ', dstDataMask.sum()
            dstDataFltd = dstData * (1 - dstDataMask)
            if so.missing_value > 0:
                dstDataMin = dstData[:].min()
                dstDataMax = dstDataFltd.max()
            else:
                dstDataMin = dstDataFltd.min()
                dstDataMax = dstData[:].max()
            print 'min/max value of dstData: %f %f' % (dstDataMin, dstDataMax)                               
            self.assertLess(dstDataMax, so[0,0,...].max())

    def test3_genericRegrid(self):
        srcF = cdms2.open(cdat_info.get_sampledata_path() + \
                              '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = srcF('so')[0, 0, ...]
        srcGridMask = numpy.array((so == so.missing_value) , numpy.int32)
        clt = cdms2.open(cdat_info.get_sampledata_path() + '/clt.nc')('clt')
        srcGrd = [so.getGrid().getLatitude(), so.getGrid().getLongitude()]
        srcBounds = cdms2.mvCdmsRegrid.getBoundList(srcGrd)
        dG = clt.getGrid().toCurveGrid()
        dstGrd = [dG.getLatitude(), dG.getLongitude()]
        dstBounds = cdms2.mvCdmsRegrid.getBoundList(dstGrd)
        # create regrid object
        r = regrid2.mvGenericRegrid.GenericRegrid([numpy.array(coord) for coord in srcGrd],
                                                  [numpy.array(coord) for coord in dstGrd],
                                                  dtype=so.dtype,
                                                  regridMethod='conserve', 
                                                  regridTool='esmf',
                                                  srcGridMask=srcGridMask, 
                                                  srcBounds=srcBounds, 
                                                  srcGridAreas=None,
                                                  dstGridMask=None, 
                                                  dstBounds=dstBounds, 
                                                  dstGridAreas=None)
        # compute weights
        r.computeWeights()
        # create dst data container
        dstShp = dG.getLatitude().shape
        dstData = numpy.ones(dstShp, so.dtype) * so.missing_value
        # interpolate
        r.apply(numpy.array(so), dstData, rootPe = 0)

        if self.pe == 0:
            # checks
            dstDataMask = (dstData == so.missing_value)
            print 'number of masked values = ', dstDataMask.sum()
            dstDataFltd = dstData * (1 - dstDataMask)
            if so.missing_value > 0:
                dstDataMin = dstData.min()
                dstDataMax = dstDataFltd.max()
            else:
                dstDataMin = dstDataFltd.min()
                dstDataMax = dstData.max()
            print 'min/max value of dstData: %f %f' % (dstDataMin, dstDataMax)                               
            self.assertLess(dstDataMax, so.max())

    def test4_cdmsRegrid(self):
        srcF = cdms2.open(cdat_info.get_sampledata_path() + \
                              '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = srcF('so')[0, 0, ...]
        srcGridMask = numpy.array((so == so.missing_value) , numpy.int32)
        clt = cdms2.open(cdat_info.get_sampledata_path() + '/clt.nc')('clt')
        # create regrid object
        r = cdms2.CdmsRegrid(so.getGrid(), clt.getGrid(),
                             dtype=so.dtype,
                             regridMethod='conserve', 
                             regridTool='esmf',
                             srcGridMask=srcGridMask, 
                             srcGridAreas=None,
                             dstGridMask=None, 
                             dstGridAreas=None)
        dstData = r(so)

        # checks
        if self.pe == 0:
            dstDataMask = (dstData == so.missing_value)
            print 'number of masked values = ', dstDataMask.sum()
            self.assertTrue(str(type(dstData)), str(type(clt)))
            dstData.mask = (dstData == so.missing_value)
            dstDataMin = dstData.min()
            dstDataMax = dstData.max()
            zeroValCnt = (dstData == 0).sum()
            print 'Number of zero valued cells', zeroValCnt
            print 'min/max value of dstData: %f %f' % (dstDataMin, dstDataMax)
            self.assertLess(dstDataMax, so.max())


    def test5_regrid(self):
        srcF = cdms2.open(cdat_info.get_sampledata_path() + \
                              '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = srcF('so')[0, 0, ...]
        clt = cdms2.open(cdat_info.get_sampledata_path() + '/clt.nc')('clt')
        dstData = so.regrid(clt.getGrid(), 
                            regridTool = 'esmf', 
                            regridMethod='conserve')

        if self.pe == 0:
            dstDataMask = (dstData == so.missing_value)
            dstDataFltd = dstData * (1 - dstDataMask)
            zeroValCnt = (dstData == 0).sum()
            if so.missing_value > 0:
                dstDataMin = dstData.min()
                dstDataMax = dstDataFltd.max()
            else:
                dstDataMin = dstDataFltd.min()
                dstDataMax = dstData.max()
                zeroValCnt = (dstData == 0).sum()
            print 'Number of zero valued cells', zeroValCnt
            print 'min/max value of dstData: %f %f' % (dstDataMin, dstDataMax)                   
            self.assertLess(dstDataMax, so.max())
            if PLOT:
                pylab.figure(1)
                pylab.pcolor(so, vmin=20, vmax=40)
                pylab.colorbar()
                pylab.title('so')
                pylab.figure(2)
                pylab.pcolor(dstData, vmin=20, vmax=40)
                pylab.colorbar()
                pylab.title('dstData')

if __name__ == '__main__':
    print ""

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity = 1).run(suite)
    if PLOT: pylab.show()


