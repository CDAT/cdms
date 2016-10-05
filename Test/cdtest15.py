import MV2
import basetest


class TestReshapeMaskAvg(basetest.CDMSBaseTest):
    def testRMA(self):
        a = MV2.arange(100)
        a = MV2.reshape(a, (10, 10))
        print a
        self.assertEqual(a.shape, (10, 10))
        self.assertEqual(len(a.getAxisList()), 2)
        a = MV2.masked_greater(a, 23)
        b = MV2.average(a, axis=0)
        c = a - b

if __name__ == "__main__":
    basetest.run()
