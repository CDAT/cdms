import numpy
import cdms2.provenance
import cdms2.provenance.operations.metadata as metadata
import basetest


def compute_metadata(obj, attribute=None, value=None):
    a = {
        "obj": obj,
    }
    if attribute:
        a["attribute"] = attribute
    if value:
        a["value"] = value
    return metadata.compute_metadata(a)


class TestProvenanceMetadata(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceMetadata, self).setUp()
        self.df = self.getDataFile("tas_mo_clim.nc")
        self.var = self.df("climseas")
        self.axis = self.df.getAxis("latitude")
        self.grid = self.df.getGrid("grid_45x72")

    def testVariableMetadata(self):
        attrs = compute_metadata(self.var)
        for a in attrs:
            self.assertEqual(compute_metadata(self.var, a), self.var.attributes[a])
        o = compute_metadata(self.var, "units", "test")
        self.assertEqual(o.units, "test")
        self.assertNotEqual(o.units, self.var.units)

    def testAxisMetadata(self):
        attrs = compute_metadata(self.axis)
        for a in attrs:
            self.assertEqual(compute_metadata(self.axis, a), self.axis.attributes[a])
        o = compute_metadata(self.axis, "units", "test")
        self.assertEqual(o.units, "test")
        self.assertNotEqual(o.units, self.axis.units)

    def testGridMetadata(self):
        attrs = compute_metadata(self.grid)
        for a in attrs:
            self.assertEqual(compute_metadata(self.grid, a), self.grid.attributes[a])
        o = compute_metadata(self.grid, "my_awesome_attribute", "test")
        self.assertEqual(o.my_awesome_attribute, "test")
        self.assertFalse("my_awesome_attribute" in self.grid.attributes)
