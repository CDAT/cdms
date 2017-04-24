import basetest
import subprocess
import cdms2
import os

class TestMissingASCII(basetest.CDMSBaseTest):
    def testMissingASCII(self):
        nc_dump = """
        netcdf tmp_test {
        dimensions:
            axis_0 = 2 ;
            axis_1 = 2 ;
        variables:
            double axis_0(axis_0) ;
            double axis_1(axis_1) ;
            double var(axis_0, axis_1) ;
                var:missing_value = "N/A" ;

        // global attributes:
                :Conventions = "CF-1.0" ;
        data:

         axis_0 = 0, 1 ;

         axis_1 = 0, 1 ;

         var =
          1, 1,
          1, 1 ;
        }
        """

        f=open("tmp_test.asc","w")
        f.write(nc_dump)
        f.close()

        subprocess.call("ncgen -b tmp_test.asc".split())

        f=cdms2.open("tmp_test.nc")
        v=f("var")
        f.close()

        self.assertEqual(v.missing_value,1.e20)

        os.remove("tmp_test.asc")
        os.remove("tmp_test.nc")


if __name__ == "__main__":
    basetest.run()
