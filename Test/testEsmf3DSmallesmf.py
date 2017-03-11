"""
$Id: testEsmf3DSmallesmf.py 2403 2012-07-31 23:07:16Z dkindig $
3D Bilinear test of ESMF through esmf, regrid, and standalone
With and without masking
"""

import pdb
import cdms2  # ESMP_Initialize()
import unittest
import ESMF
from regrid2 import esmf
from regrid2 import ESMFRegrid
import numpy
import numpy as np

HAS_MPI = False
try:
        from mpi4py import MPI
        HAS_MPI = True
except:
        pass

import re

ESMF.Manager(debug=True)

def makeGrid(nx,ny,nz):
        dims = (nz, ny, nx )
        dimb = (nz+1, ny+1,nx+1)
        xbot, xtop, ybot, ytop, zbot, ztop = 1,4,1,5,.5,6
        xbob, xtob, ybob, ytob, zbob, ztob = .5,4.5,.5,5.5,0,6.5
        x = numpy.linspace(xbot, xtop, nx)
        y = numpy.linspace(ybot, ytop, ny)
        z = numpy.linspace(zbot, ztop, nz)

        xb = numpy.linspace(xbob, xtob, nx+1)
        yb = numpy.linspace(ybob, ytob, ny+1)
        zb = numpy.linspace(zbob, ztob, nz+1)
        
        xx = numpy.outer(numpy.ones(ny), x)
        yy = numpy.outer(y, numpy.ones(nx))

        ones = numpy.outer(numpy.ones(nx), numpy.ones(ny))
        xxx = numpy.outer(xx, numpy.ones(nz)).reshape(dims)
        yyy = numpy.outer(yy, numpy.ones(nz)).reshape(dims)
        zzz = numpy.outer(ones, z).reshape(dims)

        xxb = numpy.outer(xb, numpy.ones(ny+1))
        yyb = numpy.outer(numpy.ones(nx+1), yb)
        ones = numpy.outer(numpy.ones(nx+1), numpy.ones(ny+1))
        xxxb = numpy.outer(xxb, numpy.ones(nz+1)).reshape(dimb)
        yyyb = numpy.outer(yyb, numpy.ones(nz+1)).reshape(dimb)
        zzzb = numpy.outer(ones, zb).reshape(dimb)

# Order here is level, lat, lon as required by esmf.py
        theVolume = [zzz, yyy, xxx]
        theBounds = [zzzb, yyyb, xxxb]

        theData = xxx * yyy + zzz

        return dims, theVolume, theData, theBounds

class TestESMPRegridderConserve(unittest.TestCase):
    def setUp(self):
        """
        Unit test set up
        """
        self.rootPe = 0
        self.pe = 0
        self.np = 1
        if HAS_MPI:
                self.pe = MPI.COMM_WORLD.Get_rank()
                self.np = MPI.COMM_WORLD.Get_size()

    def dtest1_3D_esmf_Bilinear(self):
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        # Establish the destination grid
        dstGrid3D = esmf.EsmfStructGrid(dstData.shape, periodicity=1,
                                        coordSys = None)
        dstGrid3D.setCoords(dstXYZCenter, 
                            staggerloc = ESMF.StaggerLoc.CENTER_VFACE,
                              globalIndexing = True) 

        # Establish the Source grid
        srcGrid3D = esmf.EsmfStructGrid(srcData.shape, periodicity=1,
                                        coordSys = None)
        srcGrid3D.setCoords(srcXYZCenter, 
                            staggerloc = ESMF.StaggerLoc.CENTER_VFACE,
                            globalIndexing = True) 

        # Create and populate the fields
        dstField = esmf.EsmfStructField(dstGrid3D, 'dstDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER_VCENTER)
        srcField = esmf.EsmfStructField(srcGrid3D, 'srcDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER_VCENTER)
        srcFldIn = esmf.EsmfStructField(srcGrid3D, 'srcDataInterp', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER_VCENTER)
        srcField.setLocalData(srcData, ESMF.StaggerLoc.CENTER_VCENTER,
                              globalIndexing = True)
        dstField.setLocalData(dstData*0, ESMF.StaggerLoc.CENTER_VCENTER,
                              globalIndexing = True)
        srcFldIn.setLocalData(srcData*0, ESMF.StaggerLoc.CENTER_VCENTER,
                              globalIndexing = True)

        # Regrid
        regridOut = esmf.EsmfRegrid(srcField, dstField,
                               srcMaskValues = None,
                               dstMaskValues = None,
                               regridMethod = ESMF.RegridMethod.BILINEAR,
                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridOut()

        regridBck = esmf.EsmfRegrid(dstField, srcFldIn,
                               srcMaskValues = None,
                               dstMaskValues = None,
                               regridMethod = ESMF.RegridMethod.BILINEAR,
                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridBck()
        
        soInterp = dstField.getData(rootPe = self.rootPe)
        soInterpInterp = srcFldIn.getData(rootPe = self.rootPe)

        if self.pe == self.rootPe:
            minlsd, maxlsd = srcData.min(), srcData.max()
            minlsi, maxlsi = soInterp.min(), soInterp.max()
            minlii, maxlii = soInterpInterp.min(), soInterpInterp.max()
            self.assertEqual(minlsd, minlsi.round(2))
            self.assertEqual(minlsd, minlii.round(2))
            self.assertEqual(maxlsd, maxlsi.round(2))
            self.assertEqual(maxlsd, maxlii.round(2))

        # Regrid
        regridOut = esmf.EsmfRegrid(srcField, dstField,
                               srcMaskValues = None,
                               dstMaskValues = None,
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridOut()

        regridBck = esmf.EsmfRegrid(dstField, srcFldIn,
                               srcMaskValues = None,
                               dstMaskValues = None,
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridBck()
        
        soInterp = dstField.getData(rootPe = self.rootPe)
        soInterpInterp = srcFldIn.getData(rootPe = self.rootPe)

        if self.pe == self.rootPe:
            minlsd, maxlsd = srcData.min(), srcData.max()
            minlsi, maxlsi = soInterp.min(), soInterp.max()
            minlii, maxlii = soInterpInterp.min(), soInterpInterp.max()
            self.assertEqual(minlsd, minlsi.round(2))
            self.assertEqual(minlsd, minlii.round(2))
            self.assertEqual(maxlsd, maxlsi.round(2))
            self.assertEqual(maxlsd, maxlii.round(2))

    def dtest2_3D_Native_Conserve(self):
        print
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        print srcData.dtype
        # Establish the Destination grid

        dstGrid3D = esmf.EsmfStructGrid(dstData.shape, periodicity=1,
                                        coordSys = None,
                                        hasBounds = True)
        dstGrid3D.setCoords(dstXYZCenter, 
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True) 

        dstGrid3D.setCoords(dstBounds, 
                            staggerloc = ESMF.StaggerLoc.CORNER_VCENTER,
                            globalIndexing = True) 

        # Establish the Source grid
        srcGrid3D = esmf.EsmfStructGrid(dstData.shape, periodicity=1,
                                        coordSys = None,
                                        hasBounds = True)
        srcGrid3D.setCoords(dstXYZCenter, 
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True) 

        srcGrid3D.setCoords(dstBounds, 
                            staggerloc = ESMF.StaggerLoc.CORNER_VCENTER,
                            globalIndexing = True) 

        # Create and populate the fields
        dstField = esmf.EsmfStructField(dstGrid3D, 'dstDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)
        srcField = esmf.EsmfStructField(srcGrid3D, 'srcDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)
        srcFldIn = esmf.EsmfStructField(srcGrid3D, 'srcDataInterp', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)

        srcField.setLocalData(srcData, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)
        dstField.setLocalData(dstData*0, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)
        srcFldIn.setLocalData(srcData*0, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)

        # Regrid
        pdb.set_trace()

        regridOut = esmf.EsmfRegrid(srcField, dstField,
                               srcMaskValues = numpy.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.ERROR)
#                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridOut()

        regridBck = esmf.EsmfRegrid(dstField, srcFldIn,
                               srcMaskValues = numpy.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        pdb.set_trace() 
        regridBck()
        
        soInterp = dstField.getData(rootPe = self.rootPe)
        soInterpInterp = srcFldIn.getData(rootPe = self.rootPe)

        if self.pe == self.rootPe:
            minlsd, maxlsd = srcData.min(), srcData.max()
            minlsi, maxlsi = soInterp.min(), soInterp.max()
            minlii, maxlii = soInterpInterp.min(), soInterpInterp.max()

            self.assertEqual(minlsd, minlsi)
            self.assertEqual(maxlsd, maxlsi)

    def test2_3D_Native_Conserve(self):
        print
#        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
#        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        [z, y, x] = [0, 1, 2]
        xdom=[1,5]
        nx=5 
        xs = np.linspace(xdom[0], xdom[1], nx + 1)
        xcorner = np.array([xs[0:-1], xs[1::]]).T
        xcenter = (xcorner[:, 1] + xcorner[:, 0]) / 2

        ydom=[1,4]
        ny=4 
        # +1 because corners have one more than center
        ys = np.linspace(ydom[0], ydom[1], ny + 1)
        ycorner = np.array([ys[0:-1], ys[1::]]).T
        ycenter = (ycorner[:, 1] + ycorner[:, 0]) / 2

        zdom=[1,3]
        nz=3 
        # +1 because corners have one more than center
        zs = np.linspace(zdom[0], zdom[1], nz + 1)
        zcorner = np.array([zs[0:-1], zs[1::]]).T
        zcenter = (zcorner[:, 1] + zcorner[:, 0]) / 2

       
        srcData = np.random.rand(zs.shape[0]-1,ys.shape[0]-1,xs.shape[0]-1)*100
        dstData = np.random.rand(zs.shape[0]-1,ys.shape[0]-1,xs.shape[0]-1)*100

        print srcData.dtype
        # Establish the Destination grid


#        myCenter = [dstXYZCenter[0][:,:,:], dstXYZCenter[1][:,:,:],dstXYZCenter[2][:,:,:]]
        ZCenter = np.zeros([nz,ny,nx])
        YCenter = np.zeros([nz,ny,nx])
        XCenter = np.zeros([nz,ny,nx])

        ZCenter[...]=zcenter[0:nz].reshape(nz,1,1)
        YCenter[...]=ycenter[0:ny].reshape(1,ny,1)
        XCenter[...]=xcenter[0:nx].reshape(1,1,nx)

        boundsz=np.zeros([nz+1,ny+1,nx+1])
        boundsy=np.zeros([nz+1,ny+1,nx+1])
        boundsx=np.zeros([nz+1,ny+1,nx+1])

        for i0 in range(nz):
           boundsz[i0,:,]=zcorner[i0,0]
        boundsz[-1,:,:]=zcorner[-1,1]

        for i1 in range(ny):
           boundsy[:,i1,:]=ycorner[i1,0]
        boundsy[:,-1,:]=ycorner[-1,1]

        for i2 in range(nx):
           boundsx[:,:,i2]=xcorner[i2,0]
        boundsx[:,:,-1]=xcorner[-1,1]


        print boundsz[:,1,1]
        print boundsy[1,:,1]
        print boundsx[1,1,:]

        myCenter = [ZCenter, YCenter, XCenter]

        pdb.set_trace()
        dstGrid3D = esmf.EsmfStructGrid(dstData.shape, periodicity=0,
                                        coordSys = ESMF.CoordSys.CART,
                                        hasBounds = True)
        dstGrid3D.setCoords(myCenter,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True) 

#        myBounds = [dstBounds[0][:,:,:], dstBounds[1][:,:,:], dstBounds[2][:,:,:]]
        myBounds = [boundsz,boundsy,boundsx]
        dstGrid3D.setCoords(myBounds,
                            staggerloc = ESMF.StaggerLoc.CORNER_VFACE,
                            globalIndexing = True) 

        # Establish the Source grid
#        myCenter = [srcXYZCenter[0][:,:,:], srcXYZCenter[1][:,:,:], srcXYZCenter[2][:,:,:]]
#        myBounds = [srcBounds[0][:,:,:], srcBounds[1][:,:,:], srcBounds[2][:,:,:]]
        srcGrid3D = esmf.EsmfStructGrid(srcData.shape, periodicity=0,
                                        coordSys = ESMF.CoordSys.CART,
                                        hasBounds = True)
        srcGrid3D.setCoords(myCenter,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True) 

        srcGrid3D.setCoords(myBounds,
                            staggerloc = ESMF.StaggerLoc.CORNER_VFACE,
                            globalIndexing = True) 

        # Create and populate the fields
        dstField = esmf.EsmfStructField(dstGrid3D, 'dstDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)
        srcField = esmf.EsmfStructField(srcGrid3D, 'srcDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)
        srcFldIn = esmf.EsmfStructField(srcGrid3D, 'srcDataInterp', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)

        srcField.setLocalData(srcData, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)
        dstField.setLocalData(dstData*0, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)
        srcFldIn.setLocalData(srcData*0, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)

        # Regrid
        pdb.set_trace()

        regridOut = esmf.EsmfRegrid(srcField, dstField,
                               srcMaskValues = numpy.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.ERROR)
#                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridOut()

        regridBck = esmf.EsmfRegrid(dstField, srcFldIn,
                               srcMaskValues = numpy.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.ERROR)
#                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        pdb.set_trace() 
        regridBck()
        
        soInterp = dstField.getData(rootPe = self.rootPe)
        soInterpInterp = srcFldIn.getData(rootPe = self.rootPe)

        if self.pe == self.rootPe:
            minlsd, maxlsd = srcData.min(), srcData.max()
            minlsi, maxlsi = soInterp.min(), soInterp.max()
            minlii, maxlii = soInterpInterp.min(), soInterpInterp.max()

            self.assertEqual(minlsd, minlsi)
            self.assertEqual(maxlsd, maxlsi)

    def test2_2D_Native_Conserve(self):
        print
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 1)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 1)

        # Establish the Destination grid
        dstGrid2D = esmf.EsmfStructGrid(dstData.shape[0:2], periodicity=0,
                                        coordSys = None,
                                        hasBounds = True)

        myCenter = [dstXYZCenter[0][:,:,0], dstXYZCenter[1][:,:,0]]
        dstGrid2D.setCoords(myCenter,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True) 

        myBounds = [dstBounds[0][:,:,0], dstBounds[1][:,:,0]]
        dstGrid2D.setCoords(myBounds,
                            staggerloc = ESMF.StaggerLoc.CORNER,
                            globalIndexing = True) 

        # Establish the Source grid
        myCenter = [srcXYZCenter[0][:,:,0], srcXYZCenter[1][:,:,0]]
        myBounds = [srcBounds[0][:,:,0], srcBounds[1][:,:,0]]
        srcGrid2D = esmf.EsmfStructGrid(srcData.shape[0:2], periodicity=0,
                                        coordSys = None,
                                        hasBounds = True)
        srcGrid2D.setCoords(myCenter,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True) 

        srcGrid2D.setCoords(myBounds,
                            staggerloc = ESMF.StaggerLoc.CORNER,
                            globalIndexing = True) 

        # Create and populate the fields
        dstField = esmf.EsmfStructField(dstGrid2D, 'dstDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)
        srcField = esmf.EsmfStructField(srcGrid2D, 'srcDataCtr', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)
        srcFldIn = esmf.EsmfStructField(srcGrid2D, 'srcDataInterp', srcData.dtype,
                                    ESMF.StaggerLoc.CENTER)

        srcField.setLocalData(srcData[:,:,0], ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)
        dstField.setLocalData(dstData[:,:,0]*0, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)
        srcFldIn.setLocalData(srcData[:,:,0]*0, ESMF.StaggerLoc.CENTER,
                              globalIndexing = True)

        # Regrid

        regridOut = esmf.EsmfRegrid(srcField, dstField,
                               srcMaskValues = numpy.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.ERROR)
#                               unMappedAction = ESMF.UnmappedAction.IGNORE)
        regridOut()

        regridBck = esmf.EsmfRegrid(dstField, srcFldIn,
                               srcMaskValues = numpy.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.ERROR)
        regridBck()
        
        soInterp = dstField.getData(rootPe = self.rootPe)
        soInterpInterp = srcFldIn.getData(rootPe = self.rootPe)

        if self.pe == self.rootPe:
            minlsd, maxlsd = srcData.min(), srcData.max()
            minlsi, maxlsi = soInterp.min(), soInterp.max()
            minlii, maxlii = soInterpInterp.min(), soInterpInterp.max()

            self.assertEqual(minlsd, minlsi)
            self.assertEqual(maxlsd, maxlsi)

if __name__ == '__main__':
    print "" # Spacer
    ESMF.Manager(debug=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMPRegridderConserve)
    unittest.TextTestRunner(verbosity = 1).run(suite)
