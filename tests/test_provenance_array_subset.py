import numpy
import cdms2.provenance
import cdms2.provenance.operations.arrays as prov_arrays
import basetest


def compute_subset(arr, ind1, ind2=None, step=None):
    a = {
        "array": arr,
        "ind1": ind1,
        "ind2": ind2,
        "step": step
    }
    return prov_arrays.subset_compute(a)


class TestProvenanceArraySubsetComputations(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceArraySubsetComputations, self).setUp()
        self.ones = numpy.ones((5, 5))
        self.zeros = numpy.zeros((5, 5))
        self.vector_1 = numpy.arange(3)
        self.vector_2 = numpy.ones((3,))

    def testGetItem(self):
        sub = compute_subset(self.vector_1, 1)
        self.assertEqual(sub, 1)

    def testRangeRetrieval(self):
        sub = compute_subset(self.vector_1, 1, 3)
        self.assertArraysEqual(sub, [1, 2])

    def testSliceRetrieval(self):
        sub = compute_subset(self.vector_1, 0, 3, 2)
        self.assertArraysEqual(sub, [0, 2])
