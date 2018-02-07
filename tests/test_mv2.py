# Automatically adapted for numpy.oldnumeric Aug 01, 2007 by

import numpy
import cdms2
import os
import sys
from cdms2.tvariable import TransientVariable as TV
import MV2
import basetest


class TestMV2(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestMV2, self).setUp()
        self.file = self.getDataFile("test.xml")
        self.u_file = self.file["u"]
        self.u_transient = self.file("u")
        self.v_file = self.file["v"]
        self.v_transient = self.file('v')
        self.u_lat = self.u_file.getLatitude()
        self.f = self.getDataFile("u_2000.nc")
        self.other_u_file = self.f["u"]
        self.ones = MV2.ones(
            self.other_u_file.shape,
            numpy.float32,
            axes=self.other_u_file.getAxisList(),
            attributes=self.other_u_file.attributes,
            id=self.other_u_file.id)

    def testKwargs(self):
        # This test makes sure that kwargs are passed through in each of the
        # types of operation
        arr = numpy.full((3, 3), .65) * [range(i, i + 3) for i in range(3)]
        # Test var_unary_operation
        v = MV2.around(arr, decimals=1)
        valid = numpy.array([
            [0.0, 0.6, 1.3],
            [0.6, 1.3, 2.0],
            [1.3, 2.0, 2.6]
        ])
        self.assertTrue(MV2.allequal(v, valid))
        xs = [1, -1, -1, 1]
        ys = [1, 1, -1, -1]
        angles = [numpy.pi / 4, 3 * numpy.pi /
                  4, -3 * numpy.pi / 4, -numpy.pi / 4]
        test_arr = numpy.zeros(4)
        # Test var_binary_operation
        MV2.arctan2(ys, xs, out=test_arr)
        self.assertFalse(MV2.allclose(test_arr, 0))
        self.assertTrue(MV2.allequal(test_arr, angles))
        # Test var_unary_operation_with_axis
        values = numpy.tile(numpy.arange(2), 3)
        self.assertEqual(
            len(MV2.sometrue(values, axis=0, keepdims=True).shape), len(values.shape))

    def testPowAndSqrt(self):
        vel = MV2.sqrt(self.u_file ** 2 + self.v_file ** 2)
        vel.id = 'velocity'
        vel2 = MV2.sqrt(self.u_transient ** 2 + self.v_transient ** 2)
        vel2.id = 'velocity'
        vel2.units = self.u_file.units
        self.assertTrue(MV2.allequal(vel, vel2))

    def testAdditionSubtraction(self):
        x1 = self.other_u_file + 1.0
        x2 = 1.0 - self.u_file
        self.assertTrue(MV2.allequal(x1 + x2[0], 2.0))

    def testNegAbs(self):
        x11 = -self.other_u_file
        x12 = MV2.absolute(self.u_file)
        self.assertTrue(MV2.allequal(x11 + x12[0], 0))

    def testMulDiv(self):
        scalar_mul = self.u_file * 2
        broadcast_mul = scalar_mul * self.other_u_file
        self.assertTrue(
            MV2.allequal(
                broadcast_mul[0] /
                self.u_file[0] /
                self.other_u_file,
                2))
        scalar_right = 1 / self.u_file[:]
        self.assertTrue(MV2.allclose(scalar_mul * scalar_right, 2))

    def testTypeCoercion(self):
        x9 = 3 * self.u_file[:]
        x15 = x9.astype(numpy.float32)
        self.assertTrue(x15.dtype.char == numpy.sctype2char(numpy.float32))

    def testArange(self):
        test_range = MV2.arange(16, axis=self.u_lat)
        self.assertEqual(len(test_range), 16)
        self.assertIsNotNone(test_range.getLatitude())

    def testMaskedArray(self):
        xmarray = MV2.masked_array(self.u_file, mask=self.u_file > .01)
        self.assertEqual(len(xmarray.getAxisList()),
                         len(self.u_file.getAxisList()))
        self.assertTrue(MV2.allequal(xmarray.mask, self.u_file > .01))

    def testAverage(self):
        xav = MV2.average(self.ones, axis=1)
        self.assertTrue(MV2.allequal(xav, 1))
        xav2 = MV2.average(self.u_file)
        xav3 = MV2.average(self.u_transient)
        xav4, wav4 = MV2.average(
            self.u_transient, weights=MV2.ones(
                self.u_transient.shape, numpy.float), returned=1)
        a = MV2.arange(5)
        b = 2 ** a
        av, wav = MV2.average(b, weights=a, returned=1)
        self.assertEqual(av, 9.8)
        self.assertEqual(wav, 10)

    def testArrayGeneration(self):
        xones = MV2.ones(
            self.other_u_file.shape,
            numpy.float32,
            axes=self.other_u_file.getAxisList(),
            attributes=self.other_u_file.attributes,
            id=self.other_u_file.id)
        self.assertTrue(MV2.allequal(xones, 1))
        self.assertEqual(xones.shape, self.other_u_file.shape)
        xzeros = MV2.zeros(
            self.u_file.shape,
            dtype=numpy.float,
            axes=self.u_file.getAxisList(),
            attributes=self.u_file.attributes,
            id=self.u_file.id)
        self.assertTrue(MV2.allequal(xzeros, 0))
        self.assertEqual(xzeros.shape, self.u_file.shape)

    def testChoose(self):
        ct1 = MV2.TransientVariable([1, 1, 2, 0, 1])
        ctr = MV2.choose(ct1, [numpy.ma.masked, 10, 20, 30, 40])
        self.assertTrue(MV2.allclose(ctr, [10, 10, 20, 100, 10]))
        ctx = MV2.TransientVariable([1, 2, 3, 150, 4])
        cty = -MV2.TransientVariable([1, 2, 3, 150, 4])
        ctr = MV2.choose(MV2.greater(ctx, 100), (ctx, 100))
        self.assertTrue(MV2.allclose(ctr, [1, 2, 3, 100, 4]))
        ctr = MV2.choose(MV2.greater(ctx, 100), (ctx, cty))
        self.assertTrue(MV2.allclose(ctr, [1, 2, 3, -150, 4]))

    def testConcatenate(self):
        xcon = MV2.concatenate((self.u_file, self.v_file))
        self.assertEqual(
            xcon.shape,
            (self.u_file.shape[0] +
             self.v_file.shape[0],
             self.u_file.shape[1],
             self.u_file.shape[2]))

    def testIsMasked(self):
        self.assertFalse(MV2.isMaskedVariable(numpy.ones(self.ones.shape)))
        self.assertTrue(MV2.isMaskedVariable(self.ones))

    def testOuterproduct(self):
        xouter = MV2.outerproduct(MV2.arange(3.), MV2.arange(5.))
        self.assertEqual(xouter.shape, (3, 5))
        for i in range(3):
            self.assertTrue(MV2.allequal(xouter[i], i * xouter[1]))

    def testMaskingFunctions(self):
        xouter = MV2.outerproduct(MV2.arange(5.), [1] * 10)
        masked = MV2.masked_greater(xouter, 1)
        self.assertTrue(MV2.allequal(masked.mask[2:], True))
        self.assertTrue(MV2.allequal(masked.mask[:2], False))
        masked = MV2.masked_greater_equal(xouter, 1)
        self.assertTrue(MV2.allequal(masked.mask[1:], True))
        self.assertTrue(MV2.allequal(masked.mask[:1], False))
        masked = MV2.masked_less(xouter, 1)
        self.assertTrue(MV2.allequal(masked.mask[:1], True))
        self.assertTrue(MV2.allequal(masked.mask[1:], False))
        masked = MV2.masked_less_equal(xouter, 1)
        self.assertTrue(MV2.allequal(masked.mask[:2], True))
        self.assertTrue(MV2.allequal(masked.mask[2:], False))
        masked = MV2.masked_not_equal(xouter, 1)
        self.assertTrue(MV2.allequal(masked.mask[1], False))
        self.assertTrue(MV2.allequal(masked.mask[0], True))
        self.assertTrue(MV2.allequal(masked.mask[2:], True))
        masked = MV2.masked_equal(xouter, 1)
        self.assertTrue(MV2.allequal(masked.mask[1], True))
        self.assertTrue(MV2.allequal(masked.mask[0], False))
        self.assertTrue(MV2.allequal(masked.mask[2:], False))
        masked = MV2.masked_outside(xouter, 1, 3)
        self.assertTrue(MV2.allequal(masked.mask[0:1], True))
        self.assertTrue(MV2.allequal(masked.mask[1:4], False))
        self.assertTrue(MV2.allequal(masked.mask[4:], True))
        masked = MV2.masked_where(
            MV2.logical_or(
                MV2.greater(
                    xouter, 3), MV2.less(
                    xouter, 2)), xouter)
        self.assertTrue(MV2.allequal(masked.mask[0:2], True))
        self.assertTrue(MV2.allequal(masked.mask[2:4], False))
        self.assertTrue(MV2.allequal(masked.mask[4:], True))

    def testCount(self):
        xouter = MV2.outerproduct(MV2.arange(5.), [1] * 10)
        masked = MV2.masked_outside(xouter, 1, 3)
        self.assertEqual(MV2.count(masked), 30)
        self.assertTrue(MV2.allequal(MV2.count(masked, 0), 3))
        self.assertTrue((MV2.count(masked, 1) == [0, 10, 10, 10, 0]).all())

    def testMinMax(self):

        # Scalar
        xouter = MV2.outerproduct(MV2.arange(10), MV2.arange(10))
        maxval = MV2.maximum(xouter)
        minval = MV2.minimum(xouter)
        self.assertEqual(maxval, 81)
        self.assertEqual(minval, 0)

        # Do an elementwise maximum
        xmax = MV2.maximum(self.u_file, self.v_file)
        xmin = MV2.minimum(self.u_file, self.v_file)
        self.assertTrue(((xmax - self.u_file) >= 0).all())
        self.assertTrue(((xmax - self.v_file) >= 0).all())
        self.assertTrue(((xmin - self.u_file) <= 0).all())
        self.assertTrue(((xmin - self.v_file) <= 0).all())

        # Reduce along axes
        slicer = [Ellipsis for i in range(len(self.u_file.shape))]
        for axis_index, axis_length in enumerate(self.u_file.shape):
            amax = MV2.maximum.reduce(self.u_file, axis=axis_index)
            amin = MV2.minimum.reduce(self.u_file, axis=axis_index)
            s = list(slicer)
            for i in range(axis_length):
                s[axis_index] = i
                ind_slice = self.u_file.subSlice(*s, squeeze=True)
                self.assertTrue(((ind_slice - amax) <= 0).all())
                self.assertTrue(((ind_slice - amin) >= 0).all())

        t1 = MV2.TransientVariable([1., 2.])
        t2 = MV2.TransientVariable([1., 10.])
        t3 = MV2.minimum.outer(t1, t2)
        self.assertTrue(MV2.allequal(t3, [[1, 1], [1, 2]]))
        t3 = MV2.maximum.outer(t1, t2)
        self.assertTrue(MV2.allequal(t3, [[1, 10], [2, 10]]))

    def testProduct(self):
        xprod = MV2.product(self.u_file)
        partial_prod = MV2.product(self.u_file[1:])
        self.assertTrue(MV2.allequal(xprod / partial_prod, self.u_file[0]))

    def testArrayManipulation(self):
        # Concat
        arr1 = MV2.ones((1, 2, 3))
        arr2 = MV2.ones((1, 2, 3))
        arr3 = MV2.concatenate([arr1, arr2])
        self.assertEqual(arr3.shape, (2, 2, 3))
        # Repeat
        arr4 = MV2.repeat(arr3, 5, axis=2)
        self.assertEqual(arr4.shape, (2, 2, 15))
        # Reshape
        arr5 = MV2.reshape(arr4, (4, 15))
        self.assertEqual(arr5.shape, (4, 15))
        # Resize
        arr6 = MV2.resize(arr5, (4, 4))
        self.assertEqual(arr6.shape, (4, 4))

    def testSomeTrue(self):
        xsome = MV2.zeros((3, 4))
        xsome[1, 2] = 1
        self.assertFalse(MV2.sometrue(xsome[0]))
        self.assertTrue(MV2.sometrue(xsome[1]))

    def testSum(self):
        ones = MV2.ones((1, 2, 3))
        self.assertEqual(MV2.sum(ones), 6)
        self.assertTrue(MV2.allequal(MV2.sum(ones, axis=2), 3))

    def testTake(self):
        t = MV2.take(self.u_file, [2, 4, 6], axis=2)
        self.assertTrue(MV2.allequal(t[:, :, 0], self.u_file[:, :, 2]))
        self.assertTrue(MV2.allequal(t[:, :, 1], self.u_file[:, :, 4]))
        self.assertTrue(MV2.allequal(t[:, :, 2], self.u_file[:, :, 6]))

    def testTranspose(self):
        ## transpose(a, axes=None)
        # transpose(a, axes=None) reorder dimensions per tuple axes
        xtr = MV2.transpose(self.u_file)
        xtr = numpy.arange(24)
        xtr.shape = (4, 6)
        xtr1 = MV2.transpose(xtr)
        xtr2 = MV2.transpose(MV2.TransientVariable(xtr))
        self.assertTrue(xtr2.shape == (6, 4))
        xtr3 = numpy.transpose(xtr)
        self.assertTrue(MV2.allclose(xtr1, xtr3))
        self.assertTrue(MV2.allclose(xtr2, xtr3))

    def testWhere(self):
        xouter = MV2.outerproduct(MV2.arange(3), MV2.arange(3))
        xwhere = MV2.where(MV2.greater(xouter, 3), xouter, -123)
        self.assertEqual(xwhere[-1, -1], 4)
        xwhere.mask = xwhere == 4
        self.assertTrue(MV2.allequal(xwhere, -123))

    def testDiagnoal(self):
        xdiag = MV2.TransientVariable([[1, 2, 3], [4, 5, 6]])
        self.assertTrue(MV2.allclose(MV2.diagonal(xdiag, 1), [2, 6]))

    def testCopy(self):
        mycopy = self.f('u').copy()
        self.assertEqual(
            mycopy.getAxisIds(), [
                'time', 'latitude', 'longitude'])

    def testIndex(self):
        u = self.f('u')
        listindex = [3, 4, 5]
        npindex = numpy.array([[0, 0, 0], [5, 4, 5], [5, 6, 7]])
        self.assertTrue(numpy.array_equal(
            u[listindex], numpy.array([[3., 4., 5.]])))
        self.assertTrue(numpy.array_equal(u[npindex], numpy.array(
            [[[0., 0., 0.], [5., 4., 5.], [5., 6., 7.]]])))

    def testBroadcasting(self):
        # Broadcast
        v_transient2 = self.v_transient[0]
        broadcasted = self.u_transient - v_transient2
        self.assertTrue(
            MV2.allequal(
                self.u_transient[2],
                broadcasted[2] +
                v_transient2))

    def testMean(self):
        a = MV2.ones((13, 14))
        b = a.mean()
        self.assertEqual(b, 1.0)

    def testCrosSectionRegrid(self):
        fmod = self.getDataFile(
            "20160520.A_WCYCL1850.ne30_oEC.edison.alpha6_01_ANN_climo_Q.nc")
        fobs = self.getDataFile("MERRA_ANN_climo_SHUM.nc")
        var1 = fmod('Q')
        var2 = fobs('SHUM')

        mv1 = MV2.average(var1, axis=-1)
        mv2 = MV2.average(var2, axis=-1)
        mv1_reg = mv1
        lev_out = mv1.getLevel()
        lat_out = mv1.getLatitude()
        mv2_reg = mv2.crossSectionRegrid(lev_out, lat_out)
        self.assertTrue(numpy.ma.is_masked(mv2_reg[:, :, -1].all()))


if __name__ == "__main__":
    basetest.run()
