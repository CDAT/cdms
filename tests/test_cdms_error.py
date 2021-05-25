import unittest
import cdms2


class TestFlake8(unittest.TestCase):
    def test_cduniferror(self):
        with self.assertRaises(cdms2.CDMSError):
            raise cdms2.CDMSError()

        with self.assertRaises(cdms2.CdunifError):
            raise cdms2.CdunifError()

        try:
            raise cdms2.CdunifError()
        except cdms2.CDMSError as e:
            self.assertTrue(isinstance(e, cdms2.CdunifError))
            self.assertTrue(isinstance(e, cdms2.CDMSError))
        else:
            self.assertTrue(False)
