## Automatically adapted for numpy.oldnumeric Aug 01, 2007 by 

import numpy
import cdms2,os,sys
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
        f = self.getDataFile("u_2000.nc")
        self.other_u_file = f["u"]
        self.ones = MV2.ones(self.other_u_file.shape, numpy.float32, axes=self.other_u_file.getAxisList(), attributes=self.other_u_file.attributes, id=self.other_u_file.id)

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
        self.assertTrue(MV2.allequal(broadcast_mul[0] / self.u_file[0] / self.other_u_file, 2))
        scalar_right = 1 / self.u_file
        self.assertTrue(MV2.allclose(scalar_mul * scalar_right, 2))

    def testTypeCoercion(self):
        x9 = 3*self.u_file
        x15 = x9.astype(numpy.float32)
        self.assertTrue(x15.dtype.char==numpy.sctype2char(numpy.float32))

    def testArange(self):
        test_range = MV2.arange(16, axis=self.u_lat)
        self.assertEqual(len(test_range), 16)
        self.assertIsNotNone(test_range.getLatitude())

    def testMaskedArray(self):
        ## masked_array(a, mask=None, fill_value=None, axes=None, attributes=None, id=None) 
        ##   masked_array(a, mask=None) = 
        ##   array(a, mask=mask, copy=0, fill_value=fill_value)
        ##   Use fill_value(a) if None.
        xmarray = MV2.masked_array(self.u_file, mask=self.u_file > .01)
        self.assertEqual(len(xmarray.getAxisList()), len(self.u_file.getAxisList()))
        self.assertTrue(MV2.allequal(xmarray.mask, self.u_file > .01))

    def testAverage(self):
        xav = MV2.average(self.ones, axis=1)
        self.assertTrue(MV2.allequal(xav, 1))
        xav2 = MV2.average(self.u_file)
        xav3 = MV2.average(self.u_transient)
        xav4, wav4 = MV2.average(self.u_transient, weights=MV2.ones(self.u_transient.shape, numpy.float), returned=1)
        a = MV2.arange(5)
        b = 2 ** a
        av, wav = MV2.average(b, weights=a, returned=1)
        self.assertEqual(av, 9.8)
        self.assertEqual(wav, 10)

    def testArrayGeneration(self):
        xones = MV2.ones(self.other_u_file.shape, numpy.float32, axes=self.other_u_file.getAxisList(), attributes=self.other_u_file.attributes, id=self.other_u_file.id)
        self.assertTrue(MV2.allequal(xones, 1))
        self.assertEqual(xones.shape, self.other_u_file.shape)
        xzeros = MV2.zeros(self.u_file.shape, dtype=numpy.float, axes=self.u_file.getAxisList(), attributes=self.u_file.attributes, id=self.u_file.id)
        self.assertTrue(MV2.allequal(xzeros, 0))
        self.assertEqual(xzeros.shape, self.u_file.shape)

    def testChoose(self):
        ct1 = MV2.TransientVariable([1,1,2,0,1])
        ctr = MV2.choose(ct1, [numpy.ma.masked, 10,20,30,40])
        self.assertTrue(MV2.allclose(ctr, [10, 10, 20, 100, 10]))
        ctx = MV2.TransientVariable([1,2,3,150,4])
        cty = -MV2.TransientVariable([1,2,3,150,4])
        ctr = MV2.choose(MV2.greater(ctx,100), (ctx, 100))
        self.assertTrue(MV2.allclose(ctr, [1,2,3,100,4]))
        ctr = MV2.choose(MV2.greater(ctx,100), (ctx, cty))
        self.assertTrue(MV2.allclose(ctr, [1,2,3,-150,4]))

    def testConcatenate(self):
        xcon = MV2.concatenate((self.u_file, self.v_file))
        self.assertEqual(xcon.shape, (self.u_file.shape[0] + self.v_file.shape[0], self.u_file.shape[1], self.u_file.shape[2]))

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
        masked = MV2.masked_where(MV2.logical_or(MV2.greater(xouter, 3), MV2.less(xouter, 2)), xouter)
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

        t1 = MV2.TransientVariable([1.,2.])
        t2 = MV2.TransientVariable([1.,10.])
        t3 = MV2.minimum.outer(t1, t2)
        self.assertTrue(MV2.allequal(t3, [[1, 1], [1, 2]]))
        t3 = MV2.maximum.outer(t1, t2)
        self.assertTrue(MV2.allequal(t3, [[1, 10], [2, 10]]))

    def testMV2(self):
        return
        ## product(a, axis=0, fill_value=1) 
        ##   Product of elements along axis using fill_value for missing elements.
        xprod = MV2.product(self.u_file)

        ## power(a, b, third=None) 
        ##   a**b
        xpower = xprod**(1./3.)

        ## repeat(a, repeats, axis=0) 
        ##   repeat elements of a repeats times along axis
        ##   repeats is a sequence of length a.shape[axis]
        ##   telling how many times to repeat each element.
        xreshape = xarange.reshape(8,2)
        xrepeat = MV2.repeat(xreshape, repeats=2)
        xrepeat2 = MV2.repeat(xreshape, repeats=2, axis=1)

        ## reshape(a, newshape, axes=None, attributes=None, id=None) 
        ##   Copy of a with a new shape.
        xreshape = MV2.reshape(xarange, (8,2))

        ## resize(a, new_shape, axes=None, attributes=None, id=None) 
        ##   resize(a, new_shape) returns a new array with the specified shape.
        ##   The original array's total size can be any size.
        xresize = MV2.resize(xarange, (8,2))

        ## set_default_fill_value(value_type, value) 
        ##   Set the default fill value for value_type to value.
        ##   value_type is a string: 'real','complex','character','integer',or 'object'.
        ##   value should be a scalar or single-element array.

        ## sometrue(a, axis=None)
        ##   True iff some element is true
        xsome = MV2.zeros((3,4))
        xsome[1,2] = 1
        res = MV2.sometrue(xsome)
        res2 = MV2.sometrue(xsome, axis=1)

        ## sum(a, axis=0, fill_value=0) 
        ##   Sum of elements along a certain axis using fill_value for missing.
        xsum = MV2.sum(self.other_u_file, axis=1)
        xsum2 = MV2.sum(xones, axis=1)
        xsum3 = MV2.sum(xones)

        ## take(a, indices, axis=0) 
        ##   take(a, indices, axis=0) returns selection of items from a.
        xtake = MV2.take(xmasked, [0,2,4,6,8], 1)
        xtake2 = MV2.take(xmasked, [0,2,4,6,8])

        ## transpose(a, axes=None) 
        ##   transpose(a, axes=None) reorder dimensions per tuple axes
        xtr = MV2.transpose(self.u_file)
        xtr = numpy.arange(24)
        xtr.shape = (4,6)
        xtr1 = MV2.transpose(xtr)
        xtr2 = MV2.transpose(MV2.TransientVariable(xtr))
        self.assertTrue(xtr2.shape == (6,4))
        xtr3 = numpy.transpose(xtr)
        self.assertTrue(MV2.allclose(xtr1, xtr3))
        self.assertTrue(MV2.allclose(xtr2, xtr3))

        ## where(condition, x, y) 
        ##   where(condition, x, y) is x where condition is true, y otherwise
        xwhere = MV2.where(MV2.greater(xouter,200),xouter,MV2.masked)
        xwhere2 = MV2.where(MV2.greater(self.u_file,200),self.u_file,MV2.masked)
        xwhere3 = MV2.where(MV2.greater(self.other_u_file,200),self.other_u_file,MV2.masked)
        xwhere2 = MV2.choose(MV2.greater(xouter,200), (MV2.masked, xouter))
        self.assertTrue(MV2.allclose(xwhere,xwhere2))

        ## diagonal(x, k)
        xdiag = MV2.TransientVariable([[1,2,3],[4,5,6]])
        self.assertTrue(MV2.allclose(MV2.diagonal(xdiag, 1), [2,6]))
        # Broadcast
        v_transient2 = self.v_transient[0]
        vsum = self.u_transient - v_transient2

if __name__ == "__main__":
    basetest.run()

