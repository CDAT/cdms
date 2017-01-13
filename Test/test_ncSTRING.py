# Automatically adapted for numpy.oldnumeric Aug 01, 2007 by ^F^F^F^F^F

import pdb
import urllib
import cdms2
import MV2
import os
import basetest
import numpy


class TestNCString(basetest.CDMSBaseTest):
    def setUp(self):
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/prcp_1951.nc"
        super(TestNCString, self).setUp()
        urllib.urlretrieve(myurl, "prcp_1951.nc")

    def tearDown(self):
        super(TestNCString, self).tearDown()
        os.remove("prcp_1951.nc")



    def testNCStringWrite(self):
        cdms2.setNetcdf4Flag(1)
        cdms2.setNetcdfClassicFlag(0)
        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevelFlag(0)
        NYR = 6
        NMO = 12
        NLAT = 16
        NLON = 32
        timear = MV2.arange(NYR*NMO, dtype=MV2.float)
        time = cdms2.createAxis(timear, id='time')
        time.units = "months since 2000-1"
        g = cdms2.createUniformGrid(-90.0, NLAT,
                                    180./(NLAT-1), 0., NLON, 360./NLON)

        uar = numpy.arange(NYR*NMO*NLAT*NLON)
        uar.shape = (NYR*NMO, NLAT, NLON)
        u = cdms2.createVariable(uar,
                                 id='u',
                                 axes=(time, g.getLatitude(),
                                       g.getLongitude()))
        u.units = 'm/s'

        f = self.getTempFile("junk.nc", "w")
        f.myNCSTRING=["1","2","3","4"]
        u.long_name=["aaa","bbbb","cccc","dddd"]
        f.write(u)
        f.close()
        # assert values
        f = self.getTempFile("junk.nc", "r")
        self.assertEqual(f.listglobal(),['myNCSTRING','Conventions'])
        self.assertEqual(f.listattribute('u'),
                         ['units',
                             '_FillValue',
                             'missing_value',
                             'long_name'])
        self.assertEqual(f['u'].long_name, ["aaa", "bbbb", "cccc", "dddd"])
        f.close()


    def t3stNCStringArray(self):
        f = cdms2.open("prcp_1951.nc", "r")
        # Verify if all attributes are presents.
        self.assertEqual(f.listglobal(),
                         ['history',
                             'Conventions',
                             'references',
                             'institution',
                             'title'])
        self.assertEqual(f.listattribute('prcp'),
                         ['_FillValue', 'grid_mapping',
                             'valid_min', 'long_name', 'standard_name',
                             'units', 'missing_value', 'valid_max'])
        self.assertEqual(f['prcp'].long_name,
                         ['Daily precipitation', 'coucou', 'Charles', 'Denis'])

if __name__ == "__main__":
    basetest.run()
