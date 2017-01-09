import MV2
import basetest                                                                                                                                

class TestFormats(basetest.CDMSBaseTest):                                                                                                      
    def testMV2(self):
        a=MV2.ones((13,14))
        b=a.mean()
        self.assertEqual(b, 1.0)

if __name__ == "__main__":
    basetest.run()
