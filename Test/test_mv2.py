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

    def testMV2(self):
        ## arrayrange(start, stop=None, step=1, typecode=None, axis=None, attributes=None, id=None) 
        ##   Just like range() except it returns a variable whose type can be specfied
        ##   by the keyword argument typecode. The axis of the result variable may be specified.
        xarange = MV2.arange(16., axis=self.u_lat)

        ## masked_object(data, value, copy=1, savespace=0) 
        ##   Create array masked where exactly data equal to value

        ## masked_values(data, value, rtol=1.0000000000000001e-05, atol=1e-08, copy=1, savespace=0, axes=None,
        ## attributes=None, id=None) 
        ##   masked_values(data, value, rtol=1.e-5, atol=1.e-8)
        ##   Create a masked array; mask is None if possible.
        ##   May share data values with original array, but not recommended.
        ##   Masked where abs(data-value)<= atol + rtol * abs(value)

        ## ones(shape, typecode='l', savespace=0, axes=None, attributes=None, id=None) 
        ##   ones(n, typecode=Int, savespace=0, axes=None, attributes=None, id=None) = 
        ##   an array of all ones of the given length or shape.
        xones = MV2.ones(self.other_u_file.shape, numpy.float32, axes=self.other_u_file.getAxisList(), attributes=self.other_u_file.attributes, id=self.other_u_file.id)
        self.assertTrue(xones[0,0,0]==1.0)

        ## zeros(shape, typecode='l', savespace=0, axes=None, attributes=None, id=None) 
        ##   zeros(n, typecode=Int, savespace=0, axes=None, attributes=None, id=None) = 
        ##   an array of all zeros of the given length or shape.
        xzeros = MV2.zeros(self.u_file.shape, dtype=numpy.float, axes=self.u_file.getAxisList(), attributes=self.u_file.attributes, id=self.u_file.id)
        xmasked = MV2.as_masked(xzeros)

        ## argsort(x, axis=-1, fill_value=None) 
        ##   Treating masked values as if they have the value fill_value,
        ##   return sort indices for sorting along given axis.
        ##   if fill_value is None, use fill_value(x)

        ## choose(indices, t) 
        ##   Shaped like indices, values t[i] where at indices[i]
        ##   If t[j] is masked, special treatment to preserve type.
        ct1 = MV2.TransientVariable([1,1,2,0,1])
        ctr = MV2.choose(ct1, [numpy.ma.masked, 10,20,30,40])
        self.assertTrue(MV2.allclose(ctr, [10, 10, 20, 100, 10]))
        ctx = MV2.TransientVariable([1,2,3,150,4])
        cty = -MV2.TransientVariable([1,2,3,150,4])
        ctr = MV2.choose(MV2.greater(ctx,100), (ctx, 100))
        self.assertTrue(MV2.allclose(ctr, [1,2,3,100,4]))
        ctr = MV2.choose(MV2.greater(ctx,100), (ctx, cty))
        self.assertTrue(MV2.allclose(ctr, [1,2,3,-150,4]))

        ## concatenate(arrays, axis=0, axisid=None, axisattributes=None) 
        ##   Concatenate the arrays along the given axis. Give the extended axis the id and
        ##   attributes provided - by default, those of the first array.

        try:
            xcon = MV2.concatenate((self.u_file, self.v_file))
        except:
            markError('Concatenate error')

        ## isMaskedVariable(x) 
        ##   Is x a masked variable, that is, an instance of AbstractVariable?
        im1 = MV2.isMaskedVariable(xones)
        im2 = MV2.isMaskedVariable(xmasked)

        ## outerproduct(a, b) 
        ##   outerproduct(a,b) = {a[i]*b[j]}, has shape (len(a),len(b))
        xouter = MV2.outerproduct(MV2.arange(16.),MV2.arange(32.))
        lat = self.other_u_file.getLatitude()
        lon = self.other_u_file.getLongitude()
        xouter.setAxis(0,lat)
        xouter.setAxis(1,lon)
        xouter.setAxisList([lat,lon])           # Equivalent

        ## masked_equal(x, value) 
        ##   masked_equal(x, value) = x masked where x == value
        ##   For floating point consider masked_values(x, value) instead.

        ## masked_greater(x, value) 
        ##   masked_greater(x, value) = x masked where x > value

        ## masked_greater_equal(x, value) 
        ##   masked_greater_equal(x, value) = x masked where x >= value
        xge = MV2.masked_greater_equal(xouter, 120)

        ## masked_less(x, value) 
        ##   masked_less(x, value) = x masked where x < value
        xl = MV2.masked_less(xouter, 160)

        ## masked_less_equal(x, value) 
        ##   masked_less_equal(x, value) = x masked where x <= value

        ## masked_not_equal(x, value) 
        ##   masked_not_equal(x, value) = x masked where x != value

        ## masked_outside(x, v1, v2) 
        ##   x with mask of all values of x that are outside [v1,v2]
        xmo = MV2.masked_outside(xouter, 120, 160)

        ## count(a, axis=None) 
        ##   Count of the non-masked elements in a, or along a certain axis.
        xcount = MV2.count(xmo,0)
        xcount2 = MV2.count(xmo,1)

        ## masked_where(condition, x, copy=1) 
        ##   Return x as an array masked where condition is true. 
        ##   Also masked where x or condition masked.
        xmwhere = MV2.masked_where(MV2.logical_and(MV2.greater(xouter,120),MV2.less(xouter,160)),xouter)

        ## maximum(a, b=None) 
        ##   returns maximum element of a single array, or elementwise
        maxval = MV2.maximum(xouter)
        xmax = MV2.maximum(self.u_file,self.v_file)
        xmax = MV2.maximum.reduce(self.u_file)
        xmax = MV2.maximum.reduce(self.v_file)
        xmax2 = numpy.ma.maximum.reduce(self.v_file.subSlice(),axis=0)
        self.assertTrue(MV2.allclose(xmax, xmax2))

        ## minimum(a, b=None) 
        ##   returns minimum element of a single array, or elementwise
        minval = MV2.minimum(xouter)
        xmin = MV2.minimum(self.u_file,self.v_file)
        xmin = MV2.minimum.reduce(self.u_file)
        xmin = MV2.minimum.reduce(self.v_file)
        xmin2 = numpy.ma.minimum.reduce(self.v_file.subSlice(),axis=0)
        self.assertTrue(MV2.allclose(xmin, xmin2))
        t1 = MV2.TransientVariable([1.,2.,3.])
        t2 = MV2.TransientVariable([1.,10.])
        t3 = MV2.add.outer(t1,t2)
        t3 = MV2.minimum.outer(t1,t2)
        t3 = MV2.maximum.outer(t1,t2)
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

