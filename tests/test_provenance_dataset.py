import numpy
import cdms2.provenance
import cdms2.provenance.operations.dataset as dataset
import basetest


def compute_dataset(uri, func, objid=None, **kwargs):
    a = {
        "uri": uri,
        "objtype": func,
        "objid": objid
    }
    a.update(kwargs)
    return dataset.compute_dataset(a)


class TestProvenanceDatasetRetrieval(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceDatasetRetrieval, self).setUp()
        pth = self.getDataFilePath("tas_mo_clim.nc")
        self.uri = "file://" + pth
        self.df = self.getDataFile("tas_mo_clim.nc")

    def testVariable(self):
        func = "variable"
        objid = "climseas"
        var = compute_dataset(self.uri, func, objid)
        self.assertEqual(var.id, objid)
        tas = self.df("climseas")
        self.assertArraysEqual(var, tas)

    def testAxis(self):
        func = "axis"
        objid = "latitude"
        axis = compute_dataset(self.uri, func, objid)
        self.assertEqual(axis.id, objid)
        lat = self.df.getAxis("latitude")
        self.assertArraysEqual(lat, axis)

    def testGrid(self):
        func = "grid"
        objid = "grid_45x72"
        grid = compute_dataset(self.uri, func, objid)
        self.assertEqual(objid, grid.id)
        tasgrid = self.df.getGrid(objid)
        self.assertEqual(tasgrid.shape, grid.shape)
        for i in range(len(tasgrid.shape)):
            self.assertArraysEqual(grid.getAxis(i), tasgrid.getAxis(i))

    def testAttributes(self):
        attrs = compute_dataset(self.uri, "attributes")
        self.assertEqual(len(attrs), len(self.df.attributes))
        for a in attrs:
            self.assertEqual(compute_dataset(self.uri, "attribute", a), self.df.attributes[a])
