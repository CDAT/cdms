import cdms2, MV2
import basetest


class TestDelAttrs(basetest.CDMSBaseTest):
    def test_del_attrs(self):
        test_nm = 'CDMS_Test_del_attributes.nc'
        f = self.getTempFile(test_nm, "w")
        s = MV2.ones((20, 20))
        s.id = "test"
        s.test_attribute = "some variable attribute"
        f.test_attribute = "some file attribute"
        f.write(s)
        f.close()
        f = self.getTempFile(test_nm, "r+")
        delattr(f, 'test_attribute')
        s = f["test"]
        del(s.test_attribute)
        f.close()
        f = self.getTempFile(test_nm)

        self.assertFalse(hasattr(f, 'test_attribute'))
        s = f["test"]
        self.assertFalse(hasattr(s, 'test_attribute'))

if __name__ == "__main__":
    basetest.run()
