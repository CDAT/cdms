## Automatically adapted for numpy.oldnumeric Aug 01, 2007 by 

#!/usr/bin/env python

import cdms2
import numpy
import cdtime
import os
import sys
from cdms2 import MV2 as MV
import basetest
import cdat_info

class TestVariableSubselection(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestVariableSubselection, self).setUp()
        self.file = self.getDataFile("test.xml")
        self.var = self.file["v"]
        self.vp = self.test_arr[1, 1:, 4:12, 8:24]
        self.wp = self.test_arr[1, 2, 4:12]
        self.xp = numpy.ma.concatenate((self.test_arr[1, 1:, 4:12, 8:self.NLON], self.test_arr[1, 1:, 4:12, 0:8]), axis=2)

    def testGetRegion(self):
        # Positional
        s = self.var.getRegion((366., 731., 'ccn'), (-42., 42., 'ccn'), (90., 270., 'con'))
        self.assertTrue(numpy.ma.allequal(self.vp, s))
        # Keyword
        s = self.var.getRegion(latitude=(-42.,42.,'ccn'),longitude=(90.,270.,'con'),time=(366.,731.,'ccn'))
        self.assertTrue(numpy.ma.allequal(self.vp,s))
        # Wraparound
        s = self.var.getRegion(time=(366.,731.,'ccn'),latitude=(-42.,42.,'ccn'),longitude=(90.,450.,'con'))
        self.assertTrue(numpy.ma.allequal(self.xp,s))

    def testGetSlice(self):
        # positional
        s = self.var.getSlice(2, (4, 12), Ellipsis, squeeze=0)
        self.assertTrue(numpy.ma.allequal(self.wp, s))

        # keyword
        s = self.var.getSlice(latitude=(4, 12), time=2)
        self.assertTrue(numpy.ma.allequal(self.wp, s))

    def testSubRegion(self):
        # positional
        s2 = self.var.subRegion((366., 731., 'ccn'), (-42., 42., 'ccn'), (90., 270., 'con'))
        self.assertTrue(numpy.ma.allequal(self.vp, s2))

        # squeeze
        s2 = self.var.subRegion((731., 731., 'ccn'), (-42., 42., 'ccn'), (90., 270., 'con'), squeeze=1)
        self.assertEqual(len(s2.shape), 2)

        # keyword
        s2 = self.var.subRegion(latitude=(-42.,42.,'ccn'),longitude=(90.,270.,'con'),time=(366.,731.,'ccn'))
        self.assertTrue(numpy.ma.allequal(self.vp,s2))

        # Wraparound
        u = self.file['u']
        u1 = u[:, :, 8:]
        u2 = u[:, :, :8]
        ucat = MV.concatenate((u1, u2), axis=2)
        su = u.subRegion(lon=(90, 450, 'co'))
        self.assertTrue(numpy.ma.allequal(ucat, su))

    def testNegativeStride(self):
        fw = self.getDataFile('ps.wrap.test.0E.nc')
        ps = fw.getVariable('ps')
        pth = cdat_info.get_sampledata_path()
        fc = cdms2.Cdunif.CdunifFile(os.path.join(pth, 'ps.wrap.test.0E.nc'))
        psc = fc.variables['ps']
        psb = psc[:]
        s3c = psb[0, ::-1]
        s4c = psb[0, ::-2]
        s3 = fw('ps', latitude=(90, -90))
        self.assertTrue(numpy.ma.allequal(s3, s3c))
        s4 = ps.getSlice(':', (None, None, -1))
        self.assertTrue(numpy.ma.allequal(s4, s3c))
        s4 = ps.subRegion(latitude=slice(None, None, -1))
        self.assertTrue(numpy.ma.allequal(s4, s3c))
        s5 = ps.getSlice(':', (None, None, -2))
        self.assertTrue(numpy.ma.allequal(s5, s4c))
        fc.close()

    def testWraparound(self):
        # Test wraparound
        fw = self.getDataFile('ps.wrap.test.0E.nc')
        ps = fw.getVariable('ps')
        ps1 = ps[:, :, 36:]
        ps2 = ps[:, :, :37]
        s2 = numpy.ma.concatenate((ps1, ps2), axis=2)
        s2w = fw('ps', longitude=(-180, 180, 'ccn'))
        self.assertTrue(numpy.ma.allequal(s2, s2w))

    def testOrder(self):
        al = self.var.getAxisList()
        result = cdms2.avariable.order2index(al, 'yxt')
        self.assertEqual(result, [1, 2, 0])
        result = cdms2.avariable.order2index(al, '...(longitude)t')
        self.assertEqual(result, [1, 2, 0])
        result = cdms2.avariable.order2index(al, '...20')
        self.assertEqual(result, [1, 2, 0])
        result = cdms2.avariable.order2index(al, '1...')
        self.assertEqual(result, [1, 0, 2])
        s3 = self.var(order='yxt', squeeze=1)
        self.assertEqual(s3.getOrder(), 'yxt')
        s2 = self.var.subRegion(latitude=(-42., 42., 'ccn'),longitude=(90.,270.,'con'),time=(366.,731.,'ccn'), order='yxt')
        self.assertEqual(s3.getOrder(), s2.getOrder())

    def testSubRegionTimes(self):
        # subRegion - time types
        s2 = self.var.subRegion(latitude=(-42.,42.,'ccn'),longitude=(90.,270.,'con'),time=('2001-1','2002-1','ccn'))
        self.assertTrue(numpy.ma.allequal(self.vp,s2))

        t1 = cdtime.comptime(2001)
        t2 = cdtime.comptime(2002)
        s2 = self.var.subRegion(latitude=(-42.,42.,'ccn'),longitude=(90.,270.,'con'),time=(t1,t2))
        self.assertTrue(numpy.ma.allequal(self.vp,s2))

        t1 = cdtime.comptime(2003)
        t2 = cdtime.comptime(2004)

        with self.assertRaises(cdms2.CDMSError):
            s2 = self.var.subRegion(latitude=(-42.,42.,'ccn'),longitude=(90.,270.,'con'),time=(t1,t2))

        t1 = cdtime.reltime(0, "years since 2001")
        t2 = cdtime.reltime(1, "year since 2001")
        s2 = self.var.subRegion(latitude=(-42.,42.,'ccn'),longitude=(90.,270.,'con'),time=(t1,t2,'ccn'))
        self.assertTrue(numpy.ma.allequal(self.vp,s2))
        xx = self.var.subRegion('2000')
        self.assertTrue(numpy.ma.allequal(xx, self.var(time="2000")))

    def testSubSlice(self):
        # subSlice - positional
        s3 = self.var.subSlice(2,(4,12),Ellipsis,squeeze=0)
        self.assertTrue(numpy.ma.allequal(self.wp,s3))

        # subSlice - keyword
        s3 = self.var.subSlice(latitude=(4,12),time=2)
        self.assertTrue(numpy.ma.allequal(self.wp,s3))

        s3 = self.var.subSlice(latitude=(4,12),time=2, squeeze=1)
        self.assertEqual(len(s3.shape), 2)

        """
        TODO: Add required back to CDMS
        """
        # required
        s3 = self.var.subSlice(required='time')
        s3 = self.var.subSlice(required=('time','latitude'))

        #with self.assertRaises(cdms2.CDMSError):
        #    s3 = self.var.subSlice(required='lumbarsupport')

        #with self.assertRaises(cdms2.SelectorError):
        #    s3 = self.var.subSlice(required='lumbarsupport')

    def testSpatial(self):
        varlist = self.file.getVariables(spatial=1)


class TestCDTime(basetest.CDMSBaseTest):
    # Time functions

    def isEqual(self, x,y):
        return (abs(y-x)< ((1.e-7)*max(abs(y),1.)))

    def cmpYear(self, c1,c2):
        return ((c1.year == c2.year) and (c1.month == c2.month) and (c1.day == c2.day)) or ((c1.year == c2.year == 1582) and (c1.month == c2.month == 10) and (c1.day in [5,15] and (c2.day in [5,15])))

    def doCalTest(self, a,b,c,d,e,f,g,cal=cdtime.MixedCalendar):
        x = cdtime.comptime(d,e,f)
        units = "days since %d-%d-%d"%(a,b,c)
        r = x.torel(units,cal)
        self.assertTrue(self.isEqual(r.value,g))

        r2 = cdtime.reltime(g, units)
        x2 = r2.tocomp(cal)
        self.assertTrue(self.cmpYear(x,x2))

        units2 = "days since %d-%d-%d"%(d,e,f)
        r3 = cdtime.reltime(10.0,units2)
        r4 = r3.torel(units)
        self.assertTrue(self.isEqual(r4.value,(10.0+g)))

        bb = cdtime.comptime(a,b,c)
        x2 = bb.add(g,cdtime.Day,cal)
        self.assertTrue(self.cmpYear(x,x2))

        x2 = x.sub(g,cdtime.Day,cal)
        self.assertTrue(self.cmpYear(bb,x2))
        r2 = cdtime.reltime(g, units)
        r3 = r2.add(1000.0,cdtime.Day,cal)
        self.assertTrue(self.isEqual(r3.value, g+1000.0))
        r3 = r2.sub(1000.0,cdtime.Day,cal)
        self.assertTrue(self.isEqual(r3.value, g-1000.0))

    def testCalendars(self):
        self.doCalTest(1,1,1,1582,1,1,577460.00)
        self.doCalTest(1,1,1,1582,1,1,577460.00,cdtime.JulianCalendar)
        self.doCalTest(1582,1,1,1,1,1,-577460.00)
        self.doCalTest(1,1,1,1970,1,1,719164.0)
        self.doCalTest(1970,1,1,1,1,1,-719164.0)
        self.doCalTest(1583,1,1,1970,1,1,141349.00)
        self.doCalTest(1970,1,1,1583,1,1,-141349.00)
        self.doCalTest(1970,1,1,1583,1,1,-141349.00,cdtime.GregorianCalendar)
        self.doCalTest(1582,10,4,1582,10,15,1.0)
        self.doCalTest(1582,10,15,1582,10,4,-1.0)

if __name__ == "__main__":
    basetest.run()
