import cdms2
import os
import numpy
import basetest
import MV2


class TestFormats(basetest.CDMSBaseTest):

    def testAxisID(self):
        a = MV2.ones((12,12))
        ax = cdms2.createAxis(MV2.arange(12))
        ax.id = "1234567890"*26
        a.setAxis(0,ax)
        with cdms2.open("bad.nc","w") as f:
            f.write(a)
        f=cdms2.open("bad.nc")
        listdim = f.listdimension()
        self.assertEqual(listdim[0], ax.id[0:127])
        f.close()

    def testVarID(self):
        NLAT=16
        NLON=32
        latarr = numpy.ma.arange(NLAT) * (180. / (NLAT - 1)) - 90.
        lonarr = numpy.ma.arange(NLON) * (360.0 / NLON)
        timearr = numpy.ma.array([0.0, 366.0, 731.0])
        u = self.test_arr[0]
        tobj = cdms2.createAxis(id='time', data=timearr)
        tobj.units = 'days since 2000-1-1'
        latobj = cdms2.createAxis(id='latitude', data=latarr)
        latobj.units = 'degrees_north'
        lonobj = cdms2.createAxis(id='longitude', data=lonarr)
        lonobj.units = 'degrees_east'
        varid = "1234567890"*26
        var = cdms2.createVariable(u,id=varid, typecode=numpy.float, axes=(tobj, latobj, lonobj))
        var.units = 'm/s'
        with cdms2.open("bad.nc","w") as f:
            f.write(var)
        f.close()
        f=cdms2.open("bad.nc")
        listvar = f.listvariables()
        self.assertEqual(listvar[2], varid[:127])
        f.close()
       
    def tearDown(self):
        os.unlink("bad.nc")



if __name__ == "__main__":
    basetest.run()
