import basetest
import cdms2
import numpy


class CDMSBadBoundsMonoMeter(basetest.CDMSBaseTest):
    def testGetBounds(self):
        axis = cdms2.createAxis(list(range(5837500,-5337500,-24944)))
        axis.id = "latitude"
        axis.units="m"
        bnds = axis.getBounds()
        self.assertTrue(numpy.allclose(bnds[0],[ 5849972.,  5825028.]))
        self.assertTrue(numpy.allclose(bnds[-1],[-5324940., -5349884.]))

    def testFromFile(self):
        f = self.getDataFile("sterographic.nc")
        s = f("seaice_conc_cdr")
        y = s.getAxis(1)
        bnds = y.getBounds()
        self.assertTrue(numpy.allclose(bnds[0],[ 5850000.,  5825000.]))
        self.assertTrue(numpy.allclose(bnds[-1],[-5325000., -5350000.]))
