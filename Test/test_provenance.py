import numpy
import cdms2.provenance
import cdms2.provenance.operations.arrays as prov_arrays
import cdms2.provenance.operations.geo as prov_geo
import cdms2.provenance.operations.nc as prov_nc
import basetest


def compute_binary(func, first, second, outer=False):
    a = {
        "func": func,
        "first": first,
        "second": second,
        "outer": outer
    }
    return prov_arrays.binary_compute(a)


def compute_unary(func, arg):
    a = {
        "func": func,
        "arg": arg
    }
    return prov_arrays.unary_compute(a)


def compute_unary(func, arg, axis, mode=False):
    a = {
        "func": func,
        "arg": arg,
        "axis": axis,
        "mode": mode
    }
    return prov_arrays.unary_compute(a)


class TestProvenanceArrayComputations(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceArrayComputations, self).setUp()
        self.ones = numpy.ones((5, 5))
        self.zeros = numpy.zeros((5, 5))

    def testArrayArithmetic(self):
        # add, subtract, remainder, multiply, divide, power
        twos = self.ones + 1
        self.assertArraysEqual(compute_binary("add", self.ones, 1), twos)
        self.assertArraysEqual(compute_binary("subtract", twos, self.ones), self.ones)
        self.assertArraysEqual(compute_binary("multiply", twos, twos), self.ones * 4)
        self.assertArraysEqual(compute_binary("divide", twos, twos), self.ones)
        self.assertArraysEqual(compute_binary("power", twos, self.ones), twos)
        self.assertArraysEqual(compute_binary("remainder", self.ones, twos), self.ones)

    def testArrayHypoteneuse(self):
        threes = self.ones + 2
        fours = self.ones + 3
        fives = self.ones + 4
        self.assertArraysEqual(compute_binary("hypot", threes, fours), fives)

    def testArrayArctan2(self):
        threes = self.ones + 2
        pis = numpy.full(self.ones.shape, numpy.pi)
        self.assertArraysEqual(compute_binary("arctan2", -threes, -threes), -3 * pis / 4)

    def testArrayOuterproduct(self):
        arr1 = numpy.array(range(2))
        arr2 = numpy.array(range(2))
        arr_answer = numpy.array(
            [
                [0, 0],
                [0, 1]
            ]
        )
        self.assertArraysEqual(compute_binary("outerproduct", arr1, arr2), arr_answer)

    def testArrayFmod(self):
        twos = self.ones + 1
        threes = self.ones + 2.5
        self.assertArraysEqual(compute_binary("fmod", threes, twos), self.ones + .5)

    def testArrayLogicFunctions(self):
        logic_arr1 = numpy.array([
            [0, 1],
            [1, 0]
        ])
        logic_arr2 = numpy.array([
            [0, 1],
            [1, 1]
        ])

        and_answer = logic_arr1
        or_answer = logic_arr2
        xor_answer = numpy.array([
            [0, 0],
            [0, 1]
        ])

        self.assertArraysEqual(compute_binary("logical_and", logic_arr1, logic_arr2), and_answer)
        self.assertArraysEqual(compute_binary("logical_or", logic_arr1, logic_arr2), or_answer)
        self.assertArraysEqual(compute_binary("logical_xor", logic_arr1, logic_arr2), xor_answer)

    def testArrayBitwise(self):
        bit_arr1 = numpy.array(range(3), dtype="int")
        bit_arr2 = numpy.ones((3,), dtype="int")

        bit_and = [0, 1, 0]
        bit_or = [1, 1, 3]
        bit_xor = [1, 0, 3]

        self.assertArraysEqual(compute_binary("bitwise_and", bit_arr1, bit_arr2), bit_and)
        self.assertArraysEqual(compute_binary("bitwise_or", bit_arr1, bit_arr2), bit_or)
        self.assertArraysEqual(compute_binary("bitwise_xor", bit_arr1, bit_arr2), bit_xor)

    def testArrayComparisons(self):
        ranged = numpy.arange(3, dtype="int")
        ones = numpy.ones((3,), dtype="int")
        self.assertArraysEqual(compute_binary("not_equal", ranged, ones), [1, 0, 1])
        self.assertArraysEqual(compute_binary("equal", ranged, ones), [0, 1, 0])
        self.assertArraysEqual(compute_binary("less", ranged, ones), [1, 0, 0])
        self.assertArraysEqual(compute_binary("less_equal", ranged, ones), [1, 1, 0])
        self.assertArraysEqual(compute_binary("greater", ranged, ones), [0, 0, 1])
        self.assertArraysEqual(compute_binary("greater_equal", ranged, ones), [0, 1, 1])
