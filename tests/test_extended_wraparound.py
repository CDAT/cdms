#!/usr/bin/env python

# Test extended wraparound

import cdms2,os,sys
import basetest
def wrapsCorrectly(lon,coord,index):
    ci = (coord[0],coord[1])
    if len(coord)==2:
        indic = 'ccn'
    else:
        indic = coord[2]
    inter = lon.mapIntervalExt(ci,indic)
    if inter is not None:
        if inter[2]==-1:
            result = inter
        else:
            result = (inter[0],inter[1])
    else:
        result = inter
    return result == index


class TestExtendedWraparound(basetest.CDMSBaseTest):
    def testWraparound(self):
        f = self.getDataFile('test.xml')
        lon = f['longitude']
        lat = f['latitude']
        rlat = cdms2.createAxis(lat[::-1], id='latitude')
        rlat.units = 'degrees_north'
        time = f['time']
        time0 = time.subAxis(0,1)
        lev = cdms2.createAxis([0.05035, 0.10089999,], id='level')

        self.assertTrue(wrapsCorrectly(lon,(-90,90,'ccn'),(-8,9)))
        self.assertTrue(wrapsCorrectly(lon,(-90,0,'ccn'),(-8,1)))
        self.assertTrue(wrapsCorrectly(lon,(-6,5,'ccb'),(-1,1)))
        self.assertTrue(wrapsCorrectly(lon,(-17,-5,'ccb'),(-2,1)))
        self.assertTrue(wrapsCorrectly(lon,(353,365,'ccb'),(31,33)))
        self.assertTrue(wrapsCorrectly(lon,(-6,1,'ccn'),(0,1)))
        self.assertTrue(wrapsCorrectly(lon,(0,348.75),(0,32)))
        self.assertTrue(wrapsCorrectly(lon,(1,348.76),(1,32)))
        self.assertTrue(wrapsCorrectly(lon,(0,348.749999),(0,32)))
        self.assertTrue(wrapsCorrectly(lon,(0,348.74),(0,31)))
        self.assertTrue(wrapsCorrectly(lon,(0,360,'co'),(0,32)))
        self.assertTrue(wrapsCorrectly(lon,(0,360,'cc'),(0,33)))
        self.assertTrue(wrapsCorrectly(lon,(0,360,'oc'),(1,33)))
        self.assertTrue(wrapsCorrectly(lon,(5,17,'ccs'),(1,2)))
        self.assertTrue(wrapsCorrectly(lon,(5,17,'ccb'),(0,3)))
        self.assertTrue(wrapsCorrectly(lon,(-180,180),(-16,17)))
        self.assertTrue(wrapsCorrectly(lon,(-180,180,'co'),(-16,16)))
        self.assertTrue(wrapsCorrectly(lon,(-5,16.875,'cob'),(0,2)))
        self.assertTrue(wrapsCorrectly(lon,(-5,16.875,'ccb'),(0,3)))
        self.assertTrue(wrapsCorrectly(lon,(1,2),None))
        self.assertTrue(wrapsCorrectly(lon,(1,2,'ccb'),(0,1)))

        self.assertTrue(wrapsCorrectly(lat,(-90,90,'co'),(0,15)))
        self.assertTrue(wrapsCorrectly(lat,(90,-90),(15,None,-1)))
        self.assertTrue(wrapsCorrectly(lat,(-45,45),(4,12)))
        self.assertTrue(wrapsCorrectly(lat,(45,-45),(11,3,-1)))
        self.assertTrue(wrapsCorrectly(lat,(180,-180),(15,None,-1)))
        self.assertTrue(wrapsCorrectly(lat, (89,89,'ccb'),(15,16)))
        self.assertTrue(wrapsCorrectly(lat, (83,83,'ccb'),(14,15)))
        self.assertTrue(wrapsCorrectly(lat, (89,89,'ccn'),None))
        self.assertTrue(wrapsCorrectly(lat, (0,0,'ccb'),(7,9)))
        self.assertTrue(wrapsCorrectly(lat, (91,91,'ccb'),None))
        self.assertTrue(wrapsCorrectly(lat, (90.0001,90.0001,'ccn'),(15,16)))
        self.assertTrue(wrapsCorrectly(lat, (-90.0001,-90.0001,'ccn'),(0,1)))

        self.assertTrue(wrapsCorrectly(rlat,(-90,90,'cc'),(15,None,-1)))
        self.assertTrue(wrapsCorrectly(rlat,(-90,90,'co'),(15,0,-1)))
        self.assertTrue(wrapsCorrectly(rlat,(90,-90,'cc'),(0,16)))
        self.assertTrue(wrapsCorrectly(rlat,(90,-90,'co'),(0,15)))
        self.assertTrue(wrapsCorrectly(rlat,(45,-45),(4,12)))
        self.assertTrue(wrapsCorrectly(rlat,(-45,45),(11,3,-1)))
        self.assertTrue(wrapsCorrectly(rlat,(180,-180),(0,16)))
        self.assertTrue(wrapsCorrectly(rlat, (89,89,'ccb'),(0,None,-1)))
        self.assertTrue(wrapsCorrectly(rlat, (83,83,'ccb'),(1,0,-1)))
        self.assertTrue(wrapsCorrectly(rlat, (89,89,'ccn'),None))
        self.assertTrue(wrapsCorrectly(rlat, (0,0,'ccb'),(8,6,-1)))
        self.assertTrue(wrapsCorrectly(rlat, (91,91,'ccb'),None))
        self.assertTrue(wrapsCorrectly(rlat, (54,-54),(3,13)))
        self.assertTrue(wrapsCorrectly(rlat, (90.0001,90.0001,'ccn'),(0,None,-1)))
        self.assertTrue(wrapsCorrectly(rlat, (-90.0001,-90.0001,'ccn'),(15,14,-1)))

        self.assertTrue(wrapsCorrectly(time, ('2000','2001'),(0,2)))
        self.assertTrue(wrapsCorrectly(time, ('2000','2000'),(0,1)))
        self.assertTrue(wrapsCorrectly(time, ('2002','2000'),(2,None,-1)))
        self.assertTrue(wrapsCorrectly(time, ('1999-12-1','1999-12-10','cob'),(0,1)))

        self.assertTrue(wrapsCorrectly(time0, (0.0, 0.0,'ccb'), (0,1)))

        self.assertTrue(wrapsCorrectly(lev,(0.05035,0.05035),(0,1)))
        self.assertTrue(wrapsCorrectly(lev,(0.1009, 0.1009),(1,2)))


if __name__ == "__main__":
    basetest.run()
