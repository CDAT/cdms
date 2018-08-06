import os
import sys
import cdat_info
from testsrunner.Util import run_command
import tempfile

SUCCESS = 0

class CDMSTestRunner(cdat_info.TestRunnerBase):

    def __setup_cdms(self):
        home = os.environ["HOME"]
        os.mkdir("{h}/.esg".format(h=home))

        esgf_pwd = os.environ["ESGF_PWD"]
        esgf_user = os.environ["ESGF_USER"]
        cmd = "echo {p} | myproxyclient logon -s esgf-node.llnl.gov -p 7512 -t 12 -S -b -l {u} -o {h}/.esg/esgf.cert".format(p=esgf_pwd, u=esgf_user, h=home)
        ret_code, out = run_command(cmd)
        if ret_code != 0:
            return ret_code

        cookies = "-c {h}/.esg/.dods_cookies".format(h=home)
        cert_opt = "--cert {h}/.esg/esgf.cert".format(h=home)
        key_opt = "--key {h}/.esg/esgf.cert".format(h=home)
        dds = "https://aims3.llnl.gov/thredds/dodsC/cmip5_css02_data/cmip5/output1/CMCC/CMCC-CM/decadal2005/mon/atmos/Amon/r1i1p1/cct/1/cct_Amon_CMCC-CM_decadal2005_r1i1p1_202601-203512.nc.dds"
        cmd = "curl -L -v {cookies} {cert} {key} {dds}".format(cookies=cookies,
                                                               cert=cert_opt,
                                                               key=key_opt,
                                                               dds=dds)
        ret_code, out = run_command(cmd)
        if ret_code != SUCCESS:
            return ret_code
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


test_suite_name = 'cdms'

workdir = os.getcwd()
runner = CDMSTestRunner(test_suite_name, options=["--subdir"],
                        options_files=["tests/cdms_runtests.json"],
                        get_sample_data=True,
                        test_data_files_info="share/test_data_files.txt")
ret_code = runner.run(workdir)

sys.exit(ret_code)
