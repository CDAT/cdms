
import cdms2
import numpy.ma
import regrid2 as regrid
import os
import sys
from regrid2 import Horizontal
import numpy
import basetest


class TestRegridding(basetest.CDMSBaseTest):

    def testRegrid2(self):
        outgrid = cdms2.createGaussianGrid(32)

        pth = os.path.dirname(os.path.abspath(__file__))
        f = self.getDataFile('readonly.nc')
        u = f.variables['u']
        ingrid = u.getGrid()

        sh = ingrid.shape

        regridf = Horizontal(ingrid, outgrid)
        newu = regridf(u)

        self.assertLess(abs(newu[0, 0, -1] - 488.4763488), 1.e-3)
        newu = u.regrid(outgrid, regridTool='regrid2')
        self.assertLess(abs(newu[0, 0, -1] - 488.4763488), 1.e-3)

        # Regrid TV
        tv = u.subSlice(0)
        newtv = regridf(tv)
        self.assertLess(abs(newtv[0, 0, -1] - 488.4763488), 1.e-3)
        newtv = tv.regrid(outgrid, regridTool='regrid2')
        self.assertLess(abs(newtv[0, 0, -1] - 488.4763488), 1.e-3)

        # Regrid numpy.ma
        ma = u[0]
        newma = regridf(ma)
        # Force slice result to be a scalar
        self.assertLess(abs(newma[0][-1] - 488.4763488), 1.e-3)

        # Regrid numpy
        numar = numpy.ma.filled(u[0])
        newar = regridf(numar)
        self.assertLess(abs(newar[0][-1] - 488.4763488), 1.e-3)

        # Regrid masked Variable
        umasked = f.variables['umasked']
        newum = regridf(umasked)
        self.assertLess(abs(newum[0, 0, -1] - 488.4763488), 1.e-3)

        # Set explicit missing variable
        numar = numpy.ma.filled(umasked[0])
        newar = regridf(numar, missing=-99.9)
        self.assertLess(abs(newar[0][-1] - 488.4763488), 1.e-3)

        # Set explicit mask
        mask = umasked.subRegion().mask[0]
        newar = regridf(numar, mask=mask)
        self.assertLess(abs(newar[0][-1] - 488.4763488), 1.e-3)

        # Set the input grid mask
        ingrid.setMask(mask)
        regridf2 = Horizontal(ingrid, outgrid)
        newar = regridf2(numar)
        self.assertLess(abs(newar[0][-1] - 488.4763488), 1.e-3)

        # Dataset
        g = self.getDataFile('test.xml')
        u = g.variables['u']
        outgrid = cdms2.createGaussianGrid(24)
        regridf3 = Horizontal(u.getGrid(), outgrid)
        try:
            unew = regridf3(u)
        except BaseException:
            markError('regrid dataset variable')

        lon2 = numpy.ma.array([90., 101.25, 112.5, 123.75, 135., 146.25, 157.5, 168.75, 180.,
                               191.25, 202.5, 213.75, 225., 236.25, 247.5, 258.75, ])
        lat2 = numpy.ma.array([-42., -30., -18., -6., 6., 18., 30., 42., ])
        grid2 = cdms2.createGenericGrid(lat2, lon2)
        b1, b2 = grid2.getBounds()
        grid2.setBounds(b1, b2)
        latw, lonw = grid2.getWeights()

        g = cdms2.createGaussianGrid(16)
        levs = numpy.array([1.0, 3.0, 5.0])
        lev = cdms2.createAxis(levs, id='level')
        levsout = numpy.array([2.0, 4.0])
        levout = cdms2.createAxis(levsout, id='level')
        dat = numpy.zeros((3, 16, 32), numpy.float32)
        dat2 = numpy.zeros((2, 16, 32), numpy.float32)
        dat[0] = 2.0
        dat[1] = 4.0
        dat[2] = 6.0
        import pdb
        pdb.set_trace()
        var = cdms2.createVariable(
            dat, axes=(
                lev, g), attributes={
                'units': 'N/A'}, id='test')
        result = var.pressureRegrid(levout)

        self.assertLess(abs(result[0, 0, 0] - 3.26185), 1.e-4)
        # Test cross-section regridder --------------------------------
        latin = cdms2.createGaussianAxis(16)
        latout = cdms2.createGaussianAxis(24)
        levsin = numpy.array([1.0, 3.0, 5.0])
        lev = cdms2.createAxis(levsin, id='level')
        levsout = numpy.array([2.0, 4.0])
        levout = cdms2.createAxis(levsout, id='level')
        dat = numpy.zeros((3, 16), numpy.float32)
        dat[0] = 2.0
        dat[1] = 4.0
        dat[2] = 6.0
        var = cdms2.createVariable(
            dat, axes=(
                lev, latin), attributes={
                'units': 'N/A'}, id='test')
        dat2 = var.crossSectionRegrid(levout, latout)
        self.assertLess(abs(dat2[0, 0] - 3.26185), 1.e-4)


if __name__ == "__main__":
    basetest.run()
