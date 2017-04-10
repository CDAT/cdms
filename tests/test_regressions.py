import basetest
import cdat_info
import os
import cdms2
import numpy
import MV2
import regrid2
import cdtime
import datetime


class TestRegressions(basetest.CDMSBaseTest):
    def testCreateCopyLoseDType(self):
        incat = self.getFile(os.path.join(cdat_info.get_sampledata_path(), "tas_ccsr-95a.xml"))
        invar = incat['tas']
        intype = invar.dtype 

        outfile = self.getTempFile('newfile.nc', 'w')
        outfile.createVariableCopy(invar)

        outvar = outfile['tas']
        outtype = outvar.dtype

        self.assertEqual(outtype, intype)

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

    def testBadCalendar(self):
        t = cdms2.createAxis([1, 2, 3, 4])
        t.designateTime()
        t.setCalendar(cdtime.ClimCalendar)
        with self.assertRaises(cdms2.CDMSError):
            t.setCalendar(3421)

    def testAxisDatetime(self):
        ax = cdms2.createAxis([10.813224335543,],id="time")
        ax.units="seconds since 2014-10-06 10:12:13"
        ax.designateTime()

        dt = ax.asdatetime()

        self.assertEqual(dt[0], datetime.datetime(2014, 10, 6, 10, 12, 23, 813))

    def testFileURI(self):
        pth = os.path.join(cdat_info.get_sampledata_path(),"clt.nc")
        f = cdms2.open("file://"+pth)
        self.assertEqual("file://" + pth, f.uri)

    def testDefaultFillValueNotNAN(self):
        self.assertFalse(numpy.isnan(MV2.array(0.).fill_value))

    def testDimUnlimited(self):
        f = self.getDataFile("tas_mo_clim.nc")
        v = f.variables['climseas']
        t = v.getTime()
        self.assertTrue(t.isUnlimited())

    def testJSON(self):
        f = self.getFile(cdat_info.get_sampledata_path()+"/clt.nc")
        s = f("clt")
        jsn = s.dumps()
        s2 = cdms2.createVariable(jsn, fromJSON=True)
        assert(numpy.allclose(s2, s))

    def testAxisDetection(self):
        val = [1,2,3]
        a = cdms2.createAxis(val)

        #First let's make sure it does not detect anything
        self.assertFalse(a.isLatitude())
        self.assertFalse(a.isLongitude())
        self.assertFalse(a.isLevel())
        self.assertFalse(a.isTime())

        #Now quick tests for making it latitude
        for u in ["DEGREESN","  deGREEn  ","degrees_north","degree_north","degree_n","degrees_n","degreen","degreesn"]:
            a.units = u
            self.assertTrue(a.isLatitude())
            a.units=""
            self.assertFalse(a.isLatitude())
        for i in ["lat","LAT","latitude","latituDE"]:
            a.id = i
            self.assertTrue(a.isLatitude())
            a.id="axis"
            self.assertFalse(a.isLatitude())
        a.axis="Y"
        self.assertTrue(a.isLatitude())
        del(a.axis)
        self.assertFalse(a.isLatitude())
        #Now quick tests for making it longitude
        for u in ["DEGREESe","  deGREEe  ","degrees_east","degree_east","degree_e","degrees_e","degreee","degreese"]:
            a.units = u
            self.assertTrue(a.isLongitude())
            a.units=""
            self.assertFalse(a.isLongitude())
        for i in ["lon","LON","longitude","lOngituDE"]:
            a.id = i
            self.assertTrue(a.isLongitude())
            a.id="axis"
            self.assertFalse(a.isLongitude())
        a.axis="X"
        self.assertTrue(a.isLongitude())
        del(a.axis)
        self.assertFalse(a.isLongitude())
        #Now quick tests for making it level
        try:
            import genutil
            has_genutil = True
        except:
            has_genutil = False
        if has_genutil:
            for u in ["Pa","hPa","psi","N/m2","N*m-2","kg*m-1*s-2","atm","bar","torr"]:
                a.units = u
                self.assertTrue(a.isLevel())
                a.units=""
                self.assertFalse(a.isLevel())
        for i in ["lev","LEV","level","lEvEL","depth","  depth"]:
            a.id = i
            self.assertTrue(a.isLevel())
            a.id="axis"
            self.assertFalse(a.isLevel())
        a.axis="Z"
        self.assertTrue(a.isLevel())
        del(a.axis)
        self.assertFalse(a.isLevel())
        a.positive="up"
        self.assertTrue(a.isLevel())
        a.positive="positive"
        self.assertFalse(a.isLevel())

    def testSimpleWrite(self):
        f = self.getTempFile("test_simple_write.nc", "w")
        data = numpy.random.random((20, 64, 128))
        data = MV2.array(data)
        data.getAxis(0).designateTime()
        f.write(data, dtype=numpy.float32, id="test_simple")

    def testRegridZonal(self):
        f = self.getFile(os.path.join(cdat_info.get_sampledata_path(), "clt.nc"))
        s = f("clt", slice(0, 1))
        g = cdms2.createGaussianGrid(64)
        gl = cdms2.createZonalGrid(g)
        regridded = s.regrid(gl)

    def testAurore(self):
        """
        No idea what this is testing.
        """
        from cdms2.coord import TransientAxis2D, TransientVirtualAxis
        from cdms2.hgrid import TransientCurveGrid
        from cdms2.gengrid import TransientGenericGrid

        def CurveGrid(v, lat, lon):
            ni, nj = lat.shape
            idi = "i"
            idj = "j"
            lat_units = 'degrees_north'
            lon_units = 'degrees_east'
            iaxis = TransientVirtualAxis(idi, ni)
            jaxis = TransientVirtualAxis(idj, nj)
            lataxis = TransientAxis2D(lat, axes=(iaxis, jaxis), attributes={'units': lat_units}, id="latitude")
            lonaxis = TransientAxis2D(lon, axes=(iaxis, jaxis), attributes={'units': lon_units}, id="longitude")
            curvegrid = TransientGenericGrid(lataxis, lonaxis, tempmask=None)
            attributs = None
            vid = None
            if hasattr(v, 'attributes'): attributs = v.attributes
            if hasattr(v, 'id'): vid = v.id
            axis0 = v.getAxis(0)
            return cdms2.createVariable(v, axes=[axis0,iaxis,jaxis], grid=curvegrid, attributes=attributs, id=v.id)

        lat = MV2.array([[-20, -10, 0, -15, -5]], 'f')
        lon = MV2.array([[0, 10, 20, 50, 60]], 'f')

        data1 = MV2.array([[[2, 3, 1, 6, 2]]], 'f')
        data2 = MV2.array([[[2, 3, 1, 6, 2]]], 'f')

        data1 = CurveGrid(data1, lat, lon)
        data2 = CurveGrid(data2, lat, lon)

        result = MV2.concatenate([data1, data2], axis=0)

    def testSliceMetadata(self):
        f = self.getFile(cdat_info.get_sampledata_path() + "/clt.nc")
        s = f("clt")
        s0 = s[0]
        self.assertTrue(s0.getAxis(0).isLatitude())
        self.assertTrue(s0.getAxis(1).isLongitude())

    def testReshapeMaskedAverage(self):
        a = MV2.arange(100)
        a = MV2.reshape(a, (10, 10))
        self.assertEqual(a.shape, (10, 10))
        self.assertEqual(len(a.getAxisList()), 2)
        a = MV2.masked_greater(a, 23)
        b = MV2.average(a, axis=0)
        c = a - b

if __name__ == "__main__":
    basetest.run()
