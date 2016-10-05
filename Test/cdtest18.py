import numpy
import cdms2
import os
import basetest


class TestNumpyWithNetCDF4(basetest.CDMSBaseTest):
    def testTypes(self):
        cdms2.setNetcdfClassicFlag(0)
        #for t in [numpy.byte,numpy.short,numpy.int,numpy.int32,numpy.float,numpy.float32,numpy.double,numpy.ubyte,numpy.ushort,numpy.uint,numpy.int64,numpy.uint64]:
        for t in [numpy.uint]:
            data = numpy.array([0], dtype=t)
            var = cdms2.createVariable(data)
            f = self.getTempFile('test_%s.nc' % data.dtype.char, 'w')
            f.write(var, id='test')
            f.close()
            f = self.getTempFile('test_%s.nc'%data.dtype.char)
            s = f("test")
            self.assertEqual(s.dtype, t)

        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevelFlag(0)

        var = cdms2.createVariable(numpy.array([0], dtype=numpy.int64))
        f = self.getTempFile('test.nc', 'w')
        f.write(var, id='test')


if __name__ == "__main__":
    basetest.run()
