
import basetest
from cdms2.cdscan import main as cdscan
import os, sys
import xml.etree.ElementTree as ET


def diffElements(el1, el2):
    if el1.tag != el2.tag:
        return el1.tag, el2.tag

    for k in el1.keys():
        # Note: this deliberately only checks the keys in the first element
        # This means that if there's a key in the second element that isn't in this one,
        # the test will pass. This is because the "History" attribute of the dataset
        # contains a datetime; obviously an issue. This just makes sure that the
        # new output is reasonably similar to the baseline.
        if k not in el2.keys():
            return k, "Not found"
        if el2.get(k) != el1.get(k):
            return el1.get(k), el2.get(k)

    el1_kids = el1.getchildren()
    el2_kids = el2.getchildren()
    if len(el1_kids) != len(el2_kids):
        return "%d children" % len(el1_kids), "%d children" % len(el2_kids)

    for c1, c2 in zip(el1_kids, el2_kids):
        r = diffElements(c1, c2)
        if r is not None:
            return r


class TestCDScan(basetest.CDMSBaseTest):
    def testScan(self):
        argv = 'cdscan -q -d test -x some_junk.xml cam3_5_01_climo.nc'.split()
        pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.chdir(pth)
        cdscan(argv)
        baseline = ET.parse("test.xml")
        new = ET.parse("some_junk.xml")
        b_root = baseline.getroot()
        new_root = new.getroot()
        results = diffElements(b_root, new_root)
        self.assertIsNone(results)
        os.unlink("some_junk.xml")

if __name__ == "__main__":
    basetest.run()
