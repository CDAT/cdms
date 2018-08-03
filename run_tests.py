import os
import sys
import cdat_info
import tempfile

class CDMSTestRunner(cdat_info.TestRunnerBase):
    def run(self, workdir, tests=None):

        os.chdir(workdir)
        test_names = super(CDMSTestRunner, self)._get_tests(workdir, self.args.tests)

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
