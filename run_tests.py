import os
import sys
import shutil
import cdat_info
import socket

from testsrunner.Util import run_command
import tempfile

SUCCESS = 0

class CDMSTestRunner(cdat_info.TestRunnerBase):

    def __setup_cdms(self):
        home = os.environ["HOME"]
        esg_dir = "{h}/.esg".format(h=home)
        if os.path.isdir(esg_dir):
            shutil.rmtree(esg_dir)
        os.mkdir(esg_dir)

        # check if we are running tests from within the lab.
        hostname = socket.gethostname()
        cacert_pem = ""
        if hostname.endswith('.llnl.gov'):
            cmd = "curl https://access.llnl.gov/cspca.cer -o {h}/cspca.cer".format(h=home)
            ret_code, out = run_command(cmd)
            if ret_code != SUCCESS:
                return ret_code

            python_ver = "python{a}.{i}".format(a=sys.version_info.major,
                                                i=sys.version_info.minor)
            coverage_opts = ""
            dest = os.path.join(sys.prefix, 'lib', python_ver, 'site-packages', 'certifi', 'cacert.pem')
            cmd = "cat {h}/cspca.cer >> {dest}".format(h=home, dest=dest)
            cacert_pem = "--cacert {cacert}".format(cacert=dest)

        esgf_pwd = os.environ["ESGF_PWD"]
        esgf_user = os.environ["ESGF_USER"]

        cookies = "-c {h}/.esg/.dods_cookies".format(h=home)
        cert_opt = "--cert {h}/.esg/esgf.cert".format(h=home)
        key_opt = "--key {h}/.esg/esgf.cert".format(h=home)
        ESGFINFO = {"https://aims3.llnl.gov/thredds/dodsC/cmip5_css01_data/cmip5/output1/BCC/bcc-csm1-1-m/1pctCO2/day/ocean/day/r1i1p1/v20120910/tos/tos_day_bcc-csm1-1-m_1pctCO2_r1i1p1_02800101-02891231.nc": "esgf-node.llnl.gov",
        "https://esg1.umr-cnrm.fr/thredds/dodsC/CMIP5_CNRM/output1/CNRM-CERFACS/CNRM-CM5/historical/day/atmos/day/r5i1p1/v20120703/huss/huss_day_CNRM-CM5_historical_r5i1p1_20050101-20051231.nc": "esg1.umr-cnrm.fr", 
        "https://esgf-node.cmcc.it/thredds/dodsC/esg_dataroot/cmip5/output1/CMCC/CMCC-CM/decadal1960/6hr/atmos/6hrPlev/r1i1p1/v20170725/psl/psl_6hrPlev_CMCC-CM_decadal1960_r1i1p1_1990120100-1990123118.nc": "esgf-node.cmcc.it"}
        
        passed = False
        for file in ESGFINFO.keys():
            site = ESGFINFO[file]
            cmd = "echo {p} | myproxyclient logon -s {s} -p 7512 -t 12 -S -b -l {u} -o {h}/.esg/esgf.cert".format(s=site, p=esgf_pwd, u=esgf_user, h=home)
            rc = os.system(cmd)
            if rc != 0:
               continue
            dds = file + ".dds"
            cmd = "curl -L -v {cacert} {cookies} {cert} {key} \"{dds}\"".format(cacert=cacert_pem,
                                                                                cookies=cookies,
                                                                                cert=cert_opt,
                                                                                key=key_opt,
                                                                                dds=dds)
            print("CMD: {cmd}".format(cmd=cmd))
            rc = os.system(cmd)
            if rc == 0:
                passed = True
                break

        if passed == False:
            raise Exception("Can't get certificates from any ESGF sites")
        if sys.platform == 'darwin':
            cmd = "cp tests/dodsrccircleciDarwin {h}/.dodsrc".format(h=home)
        else:
            cmd = "cp tests/dodsrccircleciLinux {h}/.dodsrc".format(h=home)
        ret_code, out = run_command(cmd)
        return ret_code

    def run(self, workdir, tests=None):

        os.chdir(workdir)
        test_names = super(CDMSTestRunner, self)._get_tests(workdir, self.args.tests)

        ret_code = self.__setup_cdms()
        if ret_code != SUCCESS:
            return(ret_code)

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
