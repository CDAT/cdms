import numpy
import cdms2.provenance
import cdms2.provenance.operations.arrays as prov_arrays
import basetest


def compute_binary(func, first, second, outer=False):
    a = {
        "func": func,
        "first": first,
        "second": second,
        "outer": outer
    }
    return prov_arrays.binary_compute(a)


class TestProvenanceArrayBinaryComputations(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestProvenanceArrayBinaryComputations, self).setUp()
        self.ones = numpy.ones((5, 5))
        self.zeros = numpy.zeros((5, 5))
        self.vector_1 = numpy.arange(3)
        self.vector_2 = numpy.ones((3,))

    def testArithmetic(self):
        # add, subtract, remainder, multiply, divide, power
        twos = self.ones + 1
        self.assertArraysEqual(compute_binary("add", self.ones, 1), twos)
        answer = [
            [1,1,1],
            [2,2,2],
            [3,3,3],
        ]
        self.assertArraysEqual(compute_binary("add", self.vector_1, self.vector_2, outer=True), answer)
        self.assertArraysEqual(compute_binary("subtract", twos, self.ones), self.ones)
        answer = [
            [-1,-1,-1],
            [0,0,0],
            [1,1,1],
        ]
        self.assertArraysEqual(compute_binary("subtract", self.vector_1, self.vector_2, outer=True), answer)
        self.assertArraysEqual(compute_binary("multiply", twos, twos), self.ones * 4)
        answer = [
            [0,0,0],
            [1,1,1],
            [2,2,2],
        ]
        self.assertArraysEqual(compute_binary("multiply", self.vector_1, self.vector_2, outer=True), answer)
        # These have no "outer" calculation in numpy.ma; if we change the backend we're testing, we should add
        # those.
        self.assertArraysEqual(compute_binary("power", twos, self.ones), twos)
        self.assertArraysEqual(compute_binary("divide", twos, twos), self.ones)
        self.assertArraysEqual(compute_binary("remainder", self.ones, twos), self.ones)

    def testHypoteneuse(self):
        threes = self.ones + 2
        fours = self.ones + 3
        fives = self.ones + 4
        self.assertArraysEqual(compute_binary("hypot", threes, fours), fives)
        self.assertArraysEqual(compute_binary("hypot", threes[0], fours[0], outer=True), fives)

    def testArctan2(self):
        threes = self.ones + 2
        pis = numpy.full(self.ones.shape, numpy.pi)
        self.assertArraysEqual(compute_binary("arctan2", -threes, -threes), -3 * pis / 4)
        self.assertArraysEqual(compute_binary("arctan2", -threes[0], -threes[0], outer=True), -3 * pis / 4)

    def testOuterproduct(self):
        arr1 = numpy.array(range(2))
        arr2 = numpy.array(range(2))
        arr_answer = numpy.array(
            [
                [0, 0],
                [0, 1]
            ]
        )
        self.assertArraysEqual(compute_binary("outerproduct", arr1, arr2), arr_answer)

    def testFmod(self):
        twos = self.ones + 1
        threes = self.ones + 2.5
        self.assertArraysEqual(compute_binary("fmod", threes, twos), self.ones + .5)

    def testLogicFunctions(self):
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
        answer = [
            [0, 0, 0],
            [1, 1, 1],
            [1, 1, 1]
        ]
        self.assertArraysEqual(compute_binary("logical_and", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ]
        self.assertArraysEqual(compute_binary("logical_or", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.assertArraysEqual(compute_binary("logical_xor", self.vector_1, self.vector_2, outer=True), answer)

    def testBitwise(self):
        bit_and = [0, 1, 0]
        bit_or = [1, 1, 3]
        bit_xor = [1, 0, 3]
        v1 = self.vector_1.astype("int")
        v2 = self.vector_2.astype("int")
        self.assertArraysEqual(compute_binary("bitwise_and", v1, v2), bit_and)
        self.assertArraysEqual(compute_binary("bitwise_or", v1, v2), bit_or)
        self.assertArraysEqual(compute_binary("bitwise_xor", v1, v2), bit_xor)
        answer = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
        self.assertArraysEqual(compute_binary("bitwise_and", v1, v2, outer=True), answer)
        answer = [
            [1, 1, 1],
            [1, 1, 1],
            [3, 3, 3]
        ]
        self.assertArraysEqual(compute_binary("bitwise_or", v1, v2, outer=True), answer)
        answer = [
            [1, 1, 1],
            [0, 0, 0],
            [3, 3, 3]
        ]
        self.assertArraysEqual(compute_binary("bitwise_xor", v1, v2, outer=True), answer)

    def testComparisons(self):
        self.assertArraysEqual(compute_binary("not_equal", self.vector_1, self.vector_2), [1, 0, 1])
        self.assertArraysEqual(compute_binary("equal", self.vector_1, self.vector_2), [0, 1, 0])
        self.assertArraysEqual(compute_binary("less", self.vector_1, self.vector_2), [1, 0, 0])
        self.assertArraysEqual(compute_binary("less_equal", self.vector_1, self.vector_2), [1, 1, 0])
        self.assertArraysEqual(compute_binary("greater", self.vector_1, self.vector_2), [0, 0, 1])
        self.assertArraysEqual(compute_binary("greater_equal", self.vector_1, self.vector_2), [0, 1, 1])
        answer = [
            [1,1,1],
            [0,0,0],
            [1,1,1]
        ]
        self.assertArraysEqual(compute_binary("not_equal", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [0,0,0],
            [1,1,1],
            [0,0,0]
        ]
        self.assertArraysEqual(compute_binary("equal", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [1,1,1],
            [0,0,0],
            [0,0,0]
        ]
        self.assertArraysEqual(compute_binary("less", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [1,1,1],
            [1,1,1],
            [0,0,0]
        ]
        self.assertArraysEqual(compute_binary("less_equal", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [0,0,0],
            [0,0,0],
            [1,1,1]
        ]
        self.assertArraysEqual(compute_binary("greater", self.vector_1, self.vector_2, outer=True), answer)
        answer = [
            [0,0,0],
            [1,1,1],
            [1,1,1]
        ]
        self.assertArraysEqual(compute_binary("greater_equal", self.vector_1, self.vector_2, outer=True), answer)
