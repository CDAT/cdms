import cdms2
import numpy
import os
import sys
import cdat_info
import basetest


class TestFormats(basetest.CDMSBaseTest):
    def testPP(self):
        f = self.getDataFile('testpp.pp')
        data = f['ps']
        self.assertEqual(data.missing_value, -1.07374182e+09)

    def testHDF(self):
        if cdat_info.CDMS_INCLUDE_HDF == "yes":
            f = self.getDataFile("tdata.hdf")

    def testDRS(self):
        f = self.getDataFile("dvtest1.dic")
        data = f['a']
        self.assertEqual(data.missing_value, 1e20)

    def testDAP(self):
        f = cdms2.open(
            'http://test.opendap.org/opendap/hyrax/data/nc/coads_climatology.nc')
        data = f['SST']
        self.assertEqual(data.missing_value, -1e34)
        f.close()

    def testESGF(self):
        f=cdms2.open("https://esgf.nccs.nasa.gov/thredds/dodsC/CREATE-IP/reanalysis/NASA-GMAO/GEOS-5/MERRA/mon/atmos/tas/tas_Amon_reanalysis_MERRA_197901-201312.nc")
        data = f['tas'][0,:,0]
        self.assertEqual(data.missing_value, numpy.array(1e+20,dtype=numpy.float32))
        self.assertAlmostEqual(min(data), 243.47097778320312)
        self.assertAlmostEqual(max(data), 301.8772277832031)
        self.assertAlmostEqual(numpy.mean(data), numpy.array(279.23455810546875,dtype=numpy.float32))
        f.close()

    def testGRIB2(self):
        f = self.getDataFile("testgrib2.ctl")
        data = f['wvhgtsfc']
        self.assertEqual(data.missing_value, 9.999e20)


if __name__ == "__main__":
    basetest.run()
