import basetest
import cdms2
import numpy
import os
import hashlib


class TestCDMSFileIO(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestCDMSFileIO, self).setUp()
        self.readOnly = self.getDataFile("readonly.nc")
        self.clt = self.getDataFile("clt.nc")["clt"]
        self.u = self.readOnly["u"]
        self.u_masked = self.readOnly["umasked"]

    def tearDown(self):
        super(TestCDMSFileIO, self).tearDown()

    def testModes(self):
        data = cdms2.createVariable(numpy.random.random(size=(20, 20)))

        uid = hashlib.sha256().hexdigest()[:8]
        test_name = "{}.nc".format(uid)

        with cdms2.open(test_name, 'w') as f:
            f.write(data)

        # Read
        with cdms2.open(test_name):
            pass

        # Explicit read
        with cdms2.open(test_name, 'r'):
            pass

        uid = hashlib.sha256().hexdigest()[:8]
        fname = "{}.nc".format(uid)

        # Write, file does not exist
        with cdms2.open(fname, 'w'):
            pass

        # Write, file exists
        with cdms2.open(test_name, 'w'):
            pass

        uid = hashlib.sha256().hexdigest()[:8]
        fname = "{}.nc".format(uid)

        # Append, file does not exist
        with cdms2.open(fname, 'a'):
            pass

        # Append, file exists
        with cdms2.open(test_name, 'a'):
            pass

        uid = hashlib.sha256().hexdigest()[:8]
        fname = "{}.nc".format(uid)

        with open(fname, 'w') as f:
            f.write("bad file")

        with self.assertRaises(cdms2.Cdunif.CdunifError):
            cdms2.open(fname)

    def testZSS(self):
        out_file = cdms2.open("temp.nc", "w")
        out_file.write(self.clt[0:10, :])
        out_file.write(self.clt[10:20, :])
        out_file.close()

    def testSize(self):
        self.assertEqual(self.u.size(), 512)

    def testAxisRead(self):
        lon = self.readOnly["longitude"]
        self.assertTrue(numpy.ma.allequal(lon.getValue(), lon[:]))
        self.assertTrue(lon.isVirtual() == 0)

    def testSliceRead(self):
        uslice = self.u[:, 4:12, 8:24]
        compare = self.test_arr[0, 0, 4:12, 8:24]
        self.assertTrue(numpy.ma.allequal(uslice, compare))

    def testMaskedSlice(self):
        sliceMasked = self.u_masked[:, 0:4, 8:24]
        compmask = self.test_arr[0, 0, 0:4, 8:24]
        self.assertTrue(numpy.ma.allequal(sliceMasked, compmask))

    def testVarAttributes(self):
        self.assertEqual(self.u.units, "m/s")

    def testVarAxis(self):
        t = self.u.getTime()
        self.assertTrue(numpy.ma.allequal(t[:], [0.0]))
        self.assertEqual(t.units, "days since 2000-1-1")

    def testVarGrid(self):
        g = self.u.getGrid()
        self.assertEqual(g.id, "grid_16x32")

    def testShuffleDeflateFlags(self):
        cdms2.setNetcdfShuffleFlag(1)
        cdms2.setNetcdfDeflateFlag(1)
        cdms2.setNetcdfDeflateLevelFlag(4)
        self.assertEqual(cdms2.getNetcdfShuffleFlag(), 1)
        self.assertEqual(cdms2.getNetcdfDeflateFlag(), 1)
        self.assertEqual(cdms2.getNetcdfDeflateLevelFlag(), 4)
        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(0)
        self.assertEqual(cdms2.getNetcdfShuffleFlag(), 0)
        self.assertEqual(cdms2.getNetcdfDeflateFlag(), 0)

    def testClassicFlags(self):
        cdms2.setNetcdfClassicFlag(1)
        self.assertEqual(cdms2.getNetcdfClassicFlag(), 1)
        cdms2.setNetcdfClassicFlag(0)
        self.assertEqual(cdms2.getNetcdfClassicFlag(), 0)

    def testFileAppend(self):
        # Just make sure we don't get any exceptions
        f = cdms2.open(os.path.join(self.tempdir, "junk.nc"), "a")
        xx = self.u.subSlice()
        f.write(xx)
        f.close()

    def testWraparoundGrid(self):
        uwrap = self.u.subRegion(longitude=(-180, 180))
        self.assertIsNotNone(uwrap.getGrid())

    def testwith(self):
        try:
            with cdms2.open("something.nc") as f:
                f["dd"]
        except FileNotFoundError:
            pass

    def testClosedOperations(self):
        u = self.u
        transient_u = self.u[:]
        assert transient_u is not None
        self.readOnly.close()
        with self.assertRaises(cdms2.CDMSError):
            u[:, 4:12, 8:24]
            u.getValue()

        with self.assertRaises(cdms2.CDMSError):
            u.getValue()

        with self.assertRaises(cdms2.CDMSError):
            u[0:1]

        with self.assertRaises(cdms2.CDMSError):
            u[0, 0, 0] = -99.9

        with self.assertRaises(cdms2.CDMSError):
            u[0:1] = -99.9


if __name__ == "__main__":
    basetest.run()
