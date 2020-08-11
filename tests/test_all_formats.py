import cdms2
import os
import sys
import cdat_info
import basetest
import platform
from shutil import copyfile


class TestFormats(basetest.CDMSBaseTest):
    def testPP(self):
        f = self.getDataFile("testpp.pp")
        data = f["ps"]
        self.assertEqual(data.missing_value, -1.07374182e09)

    def testHDF(self):
        if cdat_info.CDMS_INCLUDE_HDF == "yes":
            f = self.getDataFile("tdata.hdf")

    def testDRS(self):
        f = self.getDataFile("dvtest1.dic")
        data = f["a"]
        self.assertEqual(data.missing_value, 1e20)

    def dtestDAP(self):
        try:
            os.unlink(os.environ["HOME"] + "/.dodsrc")
        except:
            pass
        f = cdms2.open(
            "http://test.opendap.org/opendap/hyrax/data/nc/coads_climatology.nc"
        )
        data = f["SST"]
        self.assertEqual(data.missing_value, -1e34)
        f.close()

    def testGRIB2(self):
        f = self.getDataFile("testgrib2.ctl")
        data = f["wvhgtsfc"]
        self.assertEqual(data.missing_value, 9.999e20)

    # test disabled due to OSX issue
    def testESGF(self):
        ESGFINFO = {
            # "https://esg1.umr-cnrm.fr/thredds/dodsC/CMIP5_CNRM/output1/CNRM-CERFACS/CNRM-CM5/historical/day/atmos/day/r5i1p1/v20120703/huss/huss_day_CNRM-CM5_historical_r5i1p1_20050101-20051231.nc": "huss",
            # "https://esgf-node.cmcc.it/thredds/dodsC/esg_dataroot/cmip5/output1/CMCC/CMCC-CM/decadal1960/6hr/atmos/6hrPlev/r1i1p1/v20170725/psl/psl_6hrPlev_CMCC-CM_decadal1960_r1i1p1_1990120100-1990123118.nc": "psl",
            "https://aims3.llnl.gov/thredds/dodsC/cmip5_css01_data/cmip5/output1/BCC/bcc-csm1-1-m/1pctCO2/day/ocean/day/r1i1p1/v20120910/tos/tos_day_bcc-csm1-1-m_1pctCO2_r1i1p1_02800101-02891231.nc": "tos",
        }
        passed = False
        for site in ESGFINFO.keys():
            try:
                f = cdms2.open(site)
                var = ESGFINFO[site]
                print("SUCCESS: ", site)
            except:
                continue

            try:
                self.assertIn(var, f.listvariables())
            except:
                print("********************************************")
                print("**** ESGF sites errors can't access var  ***")
                print("********************************************")
                for site in ESGFINFO.keys():
                    print("Failed to open:", site)
                print("********************************************")
                print("**** ESGF sites errors can't access var  ***")
                print("********************************************")

            if f is not None:
                data = f[var]
                passed = True
                try:
                    reading = data[0, 0, :]
                    break
                except:
                    print("********************************************")
                    print("open file " + str(f) + "sucessfully")
                    print("**** can open file, but can't read data ***")
                    print("********************************************")
                    continue
        if passed:
            print("ESGF read success")
        else:
            print("********************************************")
            print("ESGF read FAILED")
            print("********************************************")
            raise Exception("ESGF Failed")


if __name__ == "__main__":
    basetest.run()
