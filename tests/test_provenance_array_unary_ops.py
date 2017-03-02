import numpy
import cdms2.provenance
import cdms2.provenance.operations.arrays as prov_arrays
import basetest


def compute_unary(func, arg, **kwargs):
    a = {
        "func": func,
        "arg": arg
    }
    a.update(kwargs)
    return prov_arrays.unary_compute(a)


class TestProvenanceArrayUnaryComputations(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceArrayUnaryComputations, self).setUp()
        self.ones = numpy.ones((5, 5))
        self.zeros = numpy.zeros((5, 5))
        self.vector_1 = numpy.arange(3)
        self.vector_2 = numpy.ones((3,))

    def testLogarithms(self):
        es = numpy.exp(self.ones)
        tens = self.ones * 10
        self.assertArraysEqual(compute_unary("log", es), self.ones)
        self.assertArraysEqual(compute_unary("log10", tens), self.ones)

    def testConjugate(self):
        imaginary = self.ones.astype("complex128") * 1j
        neg_imaginary = -imaginary
        self.assertArraysEqual(compute_unary("conjugate", imaginary), neg_imaginary)

    def testTrig(self):
        angles = numpy.array([0, numpy.pi / 2])
        sines = [0, 1]
        cosines = [1, 0]
        tan_angles = numpy.array([numpy.pi / 4, -numpy.pi / 4])
        tangents = [1, -1]

        self.assertArraysEqual(compute_unary("sin", angles), sines)
        self.assertArraysEqual(compute_unary("cos", angles), cosines)
        self.assertArraysEqual(compute_unary("tan", tan_angles), tangents)
        self.assertArraysEqual(compute_unary("arcsin", sines), angles)
        self.assertArraysEqual(compute_unary("arccos", cosines), angles)
        self.assertArraysEqual(compute_unary("arctan", tangents), tan_angles)
        # Someone who wants to validate that these more stringently, be my guess.
        # We're really just making sure that the functions get called correctly.
        self.assertArraysEqual(compute_unary("sinh", self.zeros), self.zeros)
        self.assertArraysEqual(compute_unary("cosh", self.zeros), self.ones)
        self.assertArraysEqual(compute_unary("tanh", self.zeros), self.zeros)

    def testFabs(self):
        self.assertArraysEqual(compute_unary("fabs", self.zeros - 1), self.ones)

    def testNonZero(self):
        self.assertEqual(compute_unary("nonzero", self.ones).shape, (2, 25))

    def testFloorCeil(self):
        self.assertArraysEqual(compute_unary("floor", self.ones / 2.), self.zeros)
        self.assertArraysEqual(compute_unary("ceil", self.ones / 2.), self.ones)

    def testSqrt(self):
        fours = self.ones * 4
        twos = self.ones * 2
        self.assertArraysEqual(compute_unary("sqrt", fours), twos)

    def testAbs(self):
        neg = self.ones - 2
        self.assertArraysEqual(compute_unary("absolute", neg), self.ones)

    def testDiagonal(self):
        arr = numpy.arange(4).reshape(2,2)
        self.assertArraysEqual(compute_unary("diagonal", arr, offset=1), [1])

    def testReshape(self):
        self.assertArraysEqual(compute_unary("reshape", self.ones, newshape=(25,)), [1] * 25)

    def testResize(self):
        self.assertArraysEqual(compute_unary("resize", self.vector_1, new_shape=(2, 3)), [[0, 1, 2]] * 2)

    def testAround(self):
        arr = numpy.array([.55, 1.5, 2.5])
        self.assertArraysEqual(compute_unary("around", arr), [1, 2, 2])
        self.assertArraysEqual(compute_unary("around", arr, decimals=1), [.6, 1.5, 2.5])
