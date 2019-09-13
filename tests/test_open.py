import basetest
import cdms2

class TestOpenFile(basetest.CDMSBaseTest):
    def test_write_to_file(self):
        f = cdms2.open("bad.nc", "w")

if __name__ == "__main__":
    basetest.run()
