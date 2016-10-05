import basetest
import cdms2
import MV2
import regrid2
import cdutil



class TestRegressions(basetest.CDMSBaseTest):
    def testDeleteAttributes(self):
        test_nm = 'CDMS_Test_del_attributes.nc'
        f = self.getTempFile(test_nm, "w")
        s = MV2.ones((20, 20))
        s.id = "test"
        s.test_attribute = "some variable attribute"
        f.test_attribute = "some file attribute"
        f.write(s)
        f.close()
        f = self.getTempFile(test_nm, "r+")
        delattr(f, 'test_attribute')
        s = f["test"]
        del(s.test_attribute)
        f.close()
        f = self.getTempFile(test_nm)

        self.assertFalse(hasattr(f, 'test_attribute'))
        s = f["test"]
        self.assertFalse(hasattr(s, 'test_attribute'))

    def testContiguousRegridNANIssue(self):
        a=MV2.reshape(MV2.sin(MV2.arange(20000)),(2,1,100,100))
        lon=cdms2.createAxis(MV2.arange(100)*3.6)
        lon.designateLongitude()
        lon.units="degrees_east"
        lon.id="longitude"

        lat = cdms2.createAxis(MV2.arange(100)*1.8-90.)
        lat.id="latitude"
        lat.designateLatitude()
        lat.units="degrees_north"

        lev = cdms2.createAxis([1000.])
        lev.id="plev"
        lev.designateLevel()
        lev.units="hPa"

        t=cdms2.createAxis([0,31.])
        t.id="time"
        t.designateTime()
        t.units="days since 2014"

        cdutil.setTimeBoundsMonthly(t)
        a.setAxisList((t,lev,lat,lon))
        a=MV2.masked_less(a,.5)
        grd=cdms2.createGaussianGrid(64)

        a=a.ascontiguous()
        a=a.regrid(grd, regridTool="regrid2")
        a=cdutil.averager(a, axis='txy')
        self.assertEqual(a[0], 0.7921019540305255)
