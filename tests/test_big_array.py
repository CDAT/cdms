import os
import unittest
import cdms2
import numpy as np
import functools

class TestBigData(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('large_array.nc'):
            data = np.random.randint(10, size=(66000,128,256), dtype=np.int8)
            step = 180.0/128.0
            lat = cdms2.createAxis(np.arange(-90+(step/2), 90, step), id='lat')
            print(lat.shape)
            step = 360.0/256.0
            lon = cdms2.createAxis(np.arange(0+(step/2), 360, step), id='lon')
            time = cdms2.createAxis(np.arange(0, 66000), id='time')
            time.units = 'days since 1990'

            var = cdms2.createVariable(data, axes=[time, lat, lon], id='fake')

            with cdms2.open('large_array.nc', 'w') as f:
                f.write(var)

    def test_read_large_slice(self):
        with cdms2.open('large_array.nc') as f:
            data = f('fake', time=slice(0, 65000))

        nitems = functools.reduce(lambda x, y: x * y, data.shape)

        self.assertTrue(nitems < 2147483647)
        self.assertFalse(np.all(data == 0))

        del data

        with cdms2.open('large_array.nc') as f:
            data = f('fake')

        nitems = functools.reduce(lambda x, y: x * y, data.shape)

        self.assertTrue(nitems > 2147483647)
        self.assertFalse(np.all(data == 0))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBigData)
    unittest.TextTestRunner(verbosity=2).run(suite)
