

#!/usr/bin/env python

# Can't write a _FillValue attribute to a Variable
# J-Y Peterschmitt - LSCE - 07/2015
import cdms2,numpy,cdtime,os,sys
import numpy as np
import basetest

class TestFillValueWrite(basetest.CDMSBaseTest):
    def testWriteFillValue(self):

        data = np.random.random((10, 10))
        data = np.ma.array(data,fill_value=1234.0)
        data = np.ma.masked_less(data, 0.5)
        dummy_grid = cdms2.createUniformGrid(10, 10, 1, 0, 10, 1)
        dummy_var = cdms2.createVariable(data, axes=[dummy_grid.getLatitude(), dummy_grid.getLongitude()], id='my_var')

        if dummy_var.fill_value != 1234.0:   markError("createVariable fill_value failed")

        # Test if all fillvalue related attributes are changed
        dummy_var.fill_value= 2.e+20
        self.assertTrue(all([v == 2.e20 for v in (dummy_var.fill_value, dummy_var._FillValue, dummy_var.missing_value)]))

        dummy_var._FillValue = 1.33
        self.assertTrue(all([v == 1.33 for v in (dummy_var.fill_value, dummy_var._FillValue, dummy_var.missing_value)]))

        dummy_var.dummy_att = 'Dummy att'
        dummy_var._dummy_att = 'Dummy att starting with _'
        dummy_var.units = '10e3 dummy'

        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevelFlag(0)

        # Test 1 passing fill_value
        var_att = dummy_var.attributes
        f = self.getTempFile('dummy1.nc', 'w')
        f.write(dummy_var, fill_value=999.999)
        f.close()

        f = self.getTempFile('dummy1.nc')
        m = f("my_var")
        self.assertTrue(all([v == 999.999 for v in (m.fill_value, m._FillValue, m.missing_value)]))

        # Test 2 Copy dummy_var attributes
        var_att = dummy_var.attributes
        var_att['another_att'] = 'New att'
        var_att['_another_att'] = 'New att starting with _'

        f = self.getTempFile('dummy2.nc', 'w')
        f.write(dummy_var, attributes=var_att)
        f.close()

        f = self.getTempFile('dummy2.nc')
        m = f("my_var")
        self.assertTrue(all([v == 1.33 for v in (m.fill_value, m._FillValue, m.missing_value)]))

        # Test 3 pass variable as is
        dummy_var = cdms2.createVariable(data, axes=[dummy_grid.getLatitude(), dummy_grid.getLongitude()], id='dummy3_var')

        f = self.getTempFile('dummy3.nc', 'w')
        f.write(dummy_var)
        f.close()

        f = self.getTempFile('dummy3.nc')
        m = f("dummy3_var")
        self.assertTrue(all([v == 1234.0 for v in (m.fill_value, m._FillValue, m.missing_value)]))

if __name__ == "__main__":
    basetest.run()
