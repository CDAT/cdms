import cdms2
import numpy
import cdat_info
import basetest


class TestFormats(basetest.CDMSBaseTest):
    def dtestPP(self):
        f = self.getDataFile('testpp.pp')
        data = f['ps']
        self.assertEqual(data.missing_value, -1.07374182e+09)

    def dtestHDF(self):
        if cdat_info.CDMS_INCLUDE_HDF == "yes":
            f = self.getDataFile("tdata.hdf")  # noqa

    def dtestDRS(self):
        f = self.getDataFile("dvtest1.dic")
        data = f['a']
        self.assertEqual(data.time, '15:17:00')

    def dtestDAP(self):
        f = cdms2.open(
            'http://test.opendap.org/opendap/hyrax/data/nc/coads_climatology.nc')
        data = f['SST']
        self.assertEqual(data.missing_value, -1e34)
        f.close()

    def dtestESGF(self):
        f = cdms2.open(
            "https://esgf.nccs.nasa.gov/thredds/dodsC/CREATE-IP/" +
            "reanalysis/NASA-GMAO/GEOS-5/MERRA/mon/atmos/tas/tas_Amon_reanalysis_MERRA_197901-201312.nc")
        data = f['tas'][0, :, 0]
        self.assertEqual(
            data.missing_value, numpy.array(
                1e+20, dtype=numpy.float32))
        self.assertAlmostEqual(min(data), 243.47097778320312)
        self.assertAlmostEqual(max(data), 301.8772277832031)
        self.assertAlmostEqual(
            numpy.mean(data),
            numpy.array(
                279.23455810546875,
                dtype=numpy.float32))
        f.close()

    def dtestGRIB2(self):
        f = self.getDataFile("testgrib2.ctl")
        data = f['wvhgtsfc']
        self.assertEqual(data.missing_value, 9.999e20)

    def dtestnetCDF(self):
        f = self.getDataFile("stereographic.nc")
        data = f('seaice_conc_cdr')
        self.assertAlmostEqual(data.mean(), 0.143803220111, 10)
        self.assertEqual(data.max(), 1.0)

    def testGPCP(self):
        f = self.getDataFile("gpcp_cdr_v23rB1_y2016_m08.nc")
        data = f('precip')
        self.assertAlmostEqual(data.mean(), 2.40109777451, 8)
        self.assertAlmostEqual(data.max(), 30.859095, 5)
        self.assertEqual(data.min(), 0.0)


if __name__ == "__main__":
    basetest.run()
