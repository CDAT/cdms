import os
import sys
import shutil
import cdat_info
import socket

from testsrunner.Util import run_command
import tempfile

SUCCESS = 0
FAILURE = 1

class CDMSTestRunner(cdat_info.TestRunnerBase):

    def __setup_cdms(self):
        home = os.environ["HOME"]
        hostname = socket.gethostname()
        cacert_pem = ""
        if hostname.endswith('.llnl.gov'):
            cmd = "curl https://access.llnl.gov/cspca.cer -o {h}/cspca.cer".format(h=home)
            cmd = "curl -k https://www-csp.llnl.gov/content/assets/csoc/cspca.crt -o {h}/cspca.cer".format(h=home)
            ret_code, out = run_command(cmd)
            if ret_code != SUCCESS:
                return ret_code

            python_ver = "python{a}.{i}".format(a=sys.version_info.major,
                                                i=sys.version_info.minor)
            dest = os.path.join(sys.prefix, 'lib', python_ver, 'site-packages', 'certifi', 'cacert.pem')
            cmd = "cat {h}/cspca.cer >> {dest}".format(h=home, dest=dest)
            cacert_pem = "--cacert {cacert}".format(cacert=dest)

        ESGFINFO = {"https://aims3.llnl.gov/thredds/dodsC/cmip5_css01_data/cmip5/output1/BCC/bcc-csm1-1-m/1pctCO2/day/ocean/day/r1i1p1/v20120910/tos/tos_day_bcc-csm1-1-m_1pctCO2_r1i1p1_02800101-02891231.nc": "esgf-node.llnl.gov",
        "https://esg1.umr-cnrm.fr/thredds/dodsC/CMIP5_CNRM/output1/CNRM-CERFACS/CNRM-CM5/historical/day/atmos/day/r5i1p1/v20120703/huss/huss_day_CNRM-CM5_historical_r5i1p1_20050101-20051231.nc": "esg1.umr-cnrm.fr", 
        "https://esgf-node.cmcc.it/thredds/dodsC/esg_dataroot/cmip5/output1/CMCC/CMCC-CM/decadal1960/6hr/atmos/6hrPlev/r1i1p1/v20170725/psl/psl_6hrPlev_CMCC-CM_decadal1960_r1i1p1_1990120100-1990123118.nc": "esgf-node.cmcc.it"}
        rc = FAILURE
        for file in ESGFINFO.keys():
            site = ESGFINFO[file]
            dds = file + ".dds"
            fname = os.path.basename(file)
            cmd = "curl -L -v {cacert} {source} -o {dest}".format(cacert=cacert_pem,
                                                                  source=dds,
                                                                  dest=fname)
            print("CMD: {cmd}".format(cmd=cmd))
            rc = os.system(cmd)
            if rc == SUCCESS:
                break

        return(rc)

    def run(self, workdir, tests=None):

        os.chdir(workdir)
        test_names = super(CDMSTestRunner, self)._get_tests(workdir, self.args.tests)

        ret_code = self.__setup_cdms()
        if ret_code != SUCCESS:
            return(ret_code)
        #print("XXX after returning from __setup_cdms()")
        if self.args.checkout_baseline:
            ret_code = super(CDMSTestRunner, self)._get_baseline(workdir)
            if ret_code != SUCCESS:
                return(ret_code)

        if self.args.subdir:
            tmpdir = tempfile.mkdtemp()
            os.chdir(tmpdir)
            ret_code = super(CDMSTestRunner, self)._do_run_tests(workdir, test_names)
            os.chdir(workdir)

        if self.args.html or self.args.package:
            super(CDMSTestRunner, self)._generate_html(workdir)

        if self.args.package:
            super(CDMSTestRunner, self)._package_results(workdir)

        return ret_code

    def _prep_nose_options(self):
        opt = super(CDMSTestRunner, self)._prep_nose_options()
        if self.args.dask:
            opt += ["-A",  "cdms_dask"]
        else:
            opt += ["-A",  "not cdms_dask"]
        return opt


test_suite_name = 'cdms'

this_dir = os.path.abspath(os.path.dirname(__file__))
runner = CDMSTestRunner(test_suite_name, options=["--subdir", "--dask"],
                        options_files=["tests/cdms_runtests.json"],
                        get_sample_data=True,
                        test_data_files_info="share/test_data_files.txt")
ret_code = runner.run(this_dir)
sys.exit(ret_code)
