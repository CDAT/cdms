"""
$Id: testEsmf.py 2389 2012-07-26 15:51:43Z dkindig $

Unit tests for regrid2.ESMF using file data
"""

import cdat_info
import cdms2
import regrid2
from regrid2.mvGenericRegrid import GenericRegrid
from cdms2.mvCdmsRegrid import _buildBounds
import unittest
import openCreateData
import ESMF
import numpy
import sys

class TestESMFRegridding(unittest.TestCase):

    def setUp(self):
        filename = cdat_info.get_sampledata_path() + \
            "/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc"
        h=cdms2.open(filename)
        self.hso = h('so')[0, 0, ...]
        self.hGrid = [self.hso.getLatitude(), self.hso.getLongitude()]
        h2D = self.hso.getGrid()
        self.hGrid2D = [h2D.getLatitude(), h2D.getLongitude()]

        filename = cdat_info.get_sampledata_path() + "/clt.nc"
        f=cdms2.open(filename)
        self.fclt = f('clt')
        self.fGrid = [self.fclt.getLatitude(), self.fclt.getLongitude()]
        g2D = self.fclt.getGrid().toCurveGrid()
        self.fGrid2D = [g2D.getLatitude()[:], g2D.getLongitude()[:]]

        filename = cdat_info.get_sampledata_path() + "/era40_tas_sample.nc"
        g=cdms2.open(filename)
        self.gtas = g('tas')
        self.gGrid = [self.gtas.getLatitude(), self.gtas.getLongitude()]
        g2D = self.gtas.getGrid().toCurveGrid()
        self.gGrid2D = [g2D.getLatitude()[:], g2D.getLongitude()[:]]

        self.eps = 1e-5

    def test1_ESMF_Basic(self):
        # Test ESMF
        title = "test ESMF - should be missing part."
        roESMF = GenericRegrid([numpy.array(g) for g in self.fGrid2D], 
                               [numpy.array(g) for g in self.gGrid2D],
                               'float64', 'linear', 'ESMF', 
                               coordSys = 'degr')

        roESMF.computeWeights()
        gclt = numpy.ones(self.gGrid2D[0].shape, 'float64') * self.fclt.missing_value
        roESMF.apply(self.fclt[0,...].data, gclt)
        roBack = GenericRegrid([numpy.array(g) for g in self.gGrid2D],
                               [numpy.array(g) for g in self.fGrid2D], 
                               'float64', 
                               'linear', 'ESMF', coordSys = 'cart')
        roBack.computeWeights()
        bclt = numpy.ones(self.fGrid2D[0].shape, 'float64') * self.fclt.missing_value
        roBack.apply(gclt, bclt)
        diff = abs(bclt -self.fclt[0,...])
        self.assertTrue(diff.all() < self.eps)

    def test2_ESMF_Basic_1dAxes_to_2DGrid(self):
        title = "test converting from 2 - 1d axes to a 2D grid"
        roESMF = GenericRegrid([numpy.array(g) for g in self.fGrid2D],
                               [numpy.array(g) for g in self.hGrid2D], 
                               'float64', 'linear', 'ESMF')
        roESMF.computeWeights()
        hclt = numpy.ones(self.hGrid2D[0].shape, 'float64') * self.fclt.missing_value
        roESMF.apply(self.fclt[0,...].data, hclt)
        roBack = GenericRegrid([numpy.array(g) for g in self.hGrid2D], 
                               [numpy.array(g) for g in self.fGrid2D], 
                               'float64', 'linear', 'ESMF')
        roBack.computeWeights()
        bclt = numpy.ones(self.fGrid2D[0].shape, 'float64') * self.fclt.missing_value
        roBack.apply(hclt[:], bclt)
        diff = abs(self.fclt[0,...] - bclt)
        self.assertTrue(numpy.all(diff) < self.eps)

    def test3_ESMF_Basic_2DGrid_to_1dAxes(self):
        title = "test converting from a 2D grid to 2 - 1d axes"
        roESMF = GenericRegrid([numpy.array(g) for g in self.hGrid2D], 
                               [numpy.array(g) for g in self.fGrid2D], 
                               'float64',  
                               'linear', 'ESMF')
        roESMF.computeWeights()
        fso = numpy.ones(self.fGrid2D[0].shape, 'float64') * self.hso.missing_value
        roESMF.apply(self.hso.data, fso)
        roBack = GenericRegrid([numpy.array(g) for g in self.fGrid2D], 
                               [numpy.array(g) for g in self.hGrid2D], 
                               self.hso.dtype, 'linear', 'ESMF')
        roBack.computeWeights()
        bso = numpy.ones(self.hGrid[0].shape, 'float64') * self.hso.missing_value
        roBack.apply(fso[:], bso)
        diff = abs(self.hso - bso)
        self.assertTrue(diff.all() < self.eps)

    def test4_ESMF_Rgd_w_Masking(self):
        title = "test ESMF - should be missing part."
        mask = self.hso.mask
        roESMF = GenericRegrid([numpy.array(g) for g in self.hGrid2D], 
                               [numpy.array(g) for g in self.fGrid2D], 
                               'float64', 
                               'linear', 'ESMF', srcMask = mask)
        roESMF.computeWeights()
        fso = numpy.ones(self.fGrid2D[0].shape, 'float64') * self.hso.missing_value
        roESMF.apply(self.hso.data, fso)
        roBack = GenericRegrid([numpy.array(g) for g in self.fGrid2D], 
                               [numpy.array(g) for g in self.hGrid2D], 
                               'float64', 'linear', 'ESMF')
        roBack.computeWeights()
        bso = numpy.ones(self.hGrid[0].shape, 'float64') * self.hso.missing_value
        roBack.apply(fso, bso)
        aa = fso < self.hso.max()+1
        bb = fso > 0
        cc = (numpy.array(aa,numpy.int32) + numpy.array(bb, numpy.int32)) == 2
        self.assertLess(abs(fso[cc].mean() - self.hso.mean()), 1)


    def test5_ESMF_Conservative(self):
        title = "Test Conservative regridding"
        mask = self.hso.mask
        hBnds = [_buildBounds(self.hGrid[0].getBounds()), 
                 _buildBounds(self.hGrid[1].getBounds())]
        fBnds = [_buildBounds(self.fGrid2D[0].getBounds()), 
                 _buildBounds(self.fGrid2D[1].getBounds())]
        roESMF = GenericRegrid([numpy.array(g) for g in self.hGrid2D], 
                               [numpy.array(g) for g in self.fGrid2D],
                               dtype = 'float64', 
                               regridMethod = 'conserv', 
                               regridTool = 'ESMF', 
                               srcBounds = hBnds,
                               dstBounds = fBnds,
                               srcGridMask = mask,
                               coordSys = 'degrees')
        roESMF.computeWeights()
        diag = {'srcAreas':0, 'dstAreas':0, 'srcAreaFractions':0, 'dstAreaFractions':0}
        cso = numpy.ones(self.fGrid2D[0].shape, 'float64') * self.hso.missing_value
        roESMF.apply(self.hso.data, cso)
        roESMF.fillInDiagnosticData(diag)
        srcResult = (self.hso * diag['srcAreas']).sum()# * numpy.nansum(diag['srcAreaFractions'])
        aa = cso < self.hso.max()+1
        bb = cso > 0
        cc = (numpy.array(aa,numpy.int32) + numpy.array(bb, numpy.int32)) == 2
        dstResult = (cso[aa] * diag['dstAreas'][aa]).sum()
        self.assertLess(abs(srcResult - dstResult), self.eps)


if __name__ == '__main__':
    ESMF.Manager()
    print ""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFRegridding)
    unittest.TextTestRunner(verbosity = 2).run(suite)

