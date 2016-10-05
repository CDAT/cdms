import cdms2
import os
import cdat_info
import basetest


class TestCreateCopyLoseDtype(basetest.CDMSBaseTest):
    def testLoseDType(self):
        incat = self.getFile(os.path.join(cdat_info.get_sampledata_path(), "tas_ccsr-95a.xml"))
        invar = incat['tas']
        intype = invar.dtype 

        outfile = self.getTempFile('newfile.nc', 'w')
        outfile.createVariableCopy(invar)

        outvar = outfile['tas']
        outtype = outvar.dtype

        self.assertEqual(outtype, intype)

if __name__ == "__main__":
    basetest.run()
