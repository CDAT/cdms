import numpy
import cdms2.provenance
import cdms2.provenance.operations.geospatial as geo_arrays
import basetest


def compute_geo(func, array, **kwargs):
    a = {
        "func": func,
        "array": array,
        "args": kwargs
    }
    return geo_arrays.compute_geo(a)


class TestProvenanceGeospatialComputations(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceGeospatialComputations, self).setUp()
        self.readOnly = self.getDataFile("readonly.nc")
        self.u = self.readOnly["u"]
        self.u_masked = self.readOnly["umasked"]

    def testSubset(self):
        self.assertEqual(compute_geo("subset", self.u, latitude=(-50, 50), longitude=(-20, 20)).shape, (1, 8, 3))

    def testAxisRetrieval(self):
        self.assertEqual(len(compute_geo("time", self.u)), 1)
        self.assertEqual(len(compute_geo("axis", self.u, index=0)), 1)
        self.assertEqual(len(compute_geo("lat", self.u)), 16)
        self.assertEqual(len(compute_geo("axis", self.u, index=1)), 16)
        self.assertEqual(len(compute_geo("lon", self.u)), 32)
        self.assertEqual(len(compute_geo("axis", self.u, index=2)), 32)
        # Should also test "lev" and axis for fetching lev, but we don't have any 4D testdata
