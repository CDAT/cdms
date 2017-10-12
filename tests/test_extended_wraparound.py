#!/usr/bin/env python

# Test extended wraparound

import cdms2
import os
import sys
import basetest


class TestExtendedWraparound(basetest.CDMSBaseTest):
    def assertWrapsCorrectly(self, axis, coord, index):
        ci = (coord[0], coord[1])
        if len(coord) == 2:
            indic = 'ccn'
        else:
            indic = coord[2]
        inter = axis.mapIntervalExt(ci, indic)
        if inter is not None:
            if inter[2] == -1:
                result = inter
            else:
                result = (inter[0], inter[1])
        else:
            result = inter
        self.assertEqual(result, index)

    def testWraparound(self):
        f = self.getDataFile('test.xml')
        lon = f['longitude']
        lat = f['latitude']
        rlat_nounits = cdms2.createAxis(lat[::-1], id='latitude')
        rlat = cdms2.createAxis(lat[::-1], id='latitude')
        rlat.units = 'degrees_north'
        rlat.setBounds(None)
        time = f['time']
        time0 = time.subAxis(0, 1)
        lev = cdms2.createAxis([0.05035, 0.10089999, ], id='level')

        self.assertWrapsCorrectly(lon, (-90, 90, 'ccn'), (-8, 9))
        self.assertWrapsCorrectly(lon, (-90, 0, 'ccn'), (-8, 1))
        self.assertWrapsCorrectly(lon, (-6, 5, 'ccb'), (-1, 1))
        self.assertWrapsCorrectly(lon, (-17, -5, 'ccb'), (-2, 1))
        self.assertWrapsCorrectly(lon, (353, 365, 'ccb'), (31, 33))
        self.assertWrapsCorrectly(lon, (-6, 1, 'ccn'), (0, 1))
        self.assertWrapsCorrectly(lon, (0, 348.75), (0, 32))
        self.assertWrapsCorrectly(lon, (1, 348.76), (1, 32))
        self.assertWrapsCorrectly(lon, (0, 348.749999), (0, 32))
        self.assertWrapsCorrectly(lon, (0, 348.74), (0, 31))
        self.assertWrapsCorrectly(lon, (0, 360, 'co'), (0, 32))
        self.assertWrapsCorrectly(lon, (0, 360, 'cc'), (0, 33))
        self.assertWrapsCorrectly(lon, (0, 360, 'oc'), (1, 33))
        self.assertWrapsCorrectly(lon, (5, 17, 'ccs'), (1, 2))
        self.assertWrapsCorrectly(lon, (5, 17, 'ccb'), (0, 3))
        self.assertWrapsCorrectly(lon, (-180, 180), (-16, 17))
        self.assertWrapsCorrectly(lon, (-180, 180, 'co'), (-16, 16))
        self.assertWrapsCorrectly(lon, (-5, 16.875, 'cob'), (0, 2))
        self.assertWrapsCorrectly(lon, (-5, 16.875, 'ccb'), (0, 3))
        self.assertWrapsCorrectly(lon, (1, 2), None)
        self.assertWrapsCorrectly(lon, (1, 2, 'ccb'), (0, 1))

        self.assertWrapsCorrectly(lat, (-90, 90, 'co'), (0, 15))
        self.assertWrapsCorrectly(lat, (90, -90), (15, None, -1))
        self.assertWrapsCorrectly(lat, (-45, 45), (4, 12))
        self.assertWrapsCorrectly(lat, (45, -45), (11, 3, -1))
        self.assertWrapsCorrectly(lat, (180, -180), (15, None, -1))
        self.assertWrapsCorrectly(lat, (89, 89, 'ccb'), (15, 16))
        self.assertWrapsCorrectly(lat, (83, 83, 'ccb'), (14, 15))
        self.assertWrapsCorrectly(lat, (89, 89, 'ccn'), None)
        self.assertWrapsCorrectly(lat, (0, 0, 'ccb'), (7, 9))
        self.assertWrapsCorrectly(lat, (91, 91, 'ccb'), None)
        self.assertWrapsCorrectly(lat, (90.0001, 90.0001, 'ccn'), (15, 16))
        self.assertWrapsCorrectly(lat, (-90.0001, -90.0001, 'ccn'), (0, 1))

        self.assertWrapsCorrectly(rlat, (-90, 90, 'cc'), (15, None, -1))
        self.assertWrapsCorrectly(rlat, (-90, 90, 'co'), (15, 0, -1))
        self.assertWrapsCorrectly(rlat, (90, -90, 'cc'), (0, 16))
        self.assertWrapsCorrectly(rlat, (90, -90, 'co'), (0, 15))
        self.assertWrapsCorrectly(rlat, (45, -45), (4, 12))
        self.assertWrapsCorrectly(rlat, (-45, 45), (11, 3, -1))
        self.assertWrapsCorrectly(rlat, (180, -180), (0, 16))
        self.assertWrapsCorrectly(rlat, (89, 89, 'ccb'), (0, None, -1))
        self.assertWrapsCorrectly(rlat, (83, 83, 'ccb'), (1, 0, -1))
        self.assertWrapsCorrectly(rlat, (89, 89, 'ccn'), None)
        self.assertWrapsCorrectly(rlat, (0, 0, 'ccb'), (8, 6, -1))
        self.assertWrapsCorrectly(rlat, (91, 91, 'ccb'), None)
        self.assertWrapsCorrectly(rlat, (54, -54), (3, 13))
        self.assertWrapsCorrectly(
            rlat, (90.0001, 90.0001, 'ccn'), (0, None, -1))
        self.assertWrapsCorrectly(
            rlat, (-90.0001, -90.0001, 'ccn'), (15, 14, -1))

        self.assertWrapsCorrectly(
            rlat_nounits, (-90, 90, 'cc'), (15, None, -1))
        self.assertWrapsCorrectly(rlat_nounits, (-90, 90, 'co'), (15, 0, -1))
        self.assertWrapsCorrectly(rlat_nounits, (90, -90, 'cc'), (0, 16))
        self.assertWrapsCorrectly(rlat_nounits, (90, -90, 'co'), (0, 15))
        self.assertWrapsCorrectly(rlat_nounits, (45, -45), (4, 12))
        self.assertWrapsCorrectly(rlat_nounits, (-45, 45), (11, 3, -1))
        self.assertWrapsCorrectly(rlat_nounits, (180, -180), (0, 16))
        self.assertWrapsCorrectly(rlat_nounits, (89, 89, 'ccb'), (0, None, -1))
        self.assertWrapsCorrectly(rlat_nounits, (83, 83, 'ccb'), (1, 0, -1))
        self.assertWrapsCorrectly(rlat_nounits, (89, 89, 'ccn'), None)
        self.assertWrapsCorrectly(rlat_nounits, (0, 0, 'ccb'), (8, 6, -1))
        self.assertWrapsCorrectly(rlat_nounits, (91, 91, 'ccb'), (0, None, -1))
        self.assertWrapsCorrectly(rlat_nounits, (54, -54), (3, 13))
        self.assertWrapsCorrectly(
            rlat_nounits, (90.0001, 90.0001, 'ccn'), (0, None, -1))
        self.assertWrapsCorrectly(
            rlat_nounits, (-90.0001, -90.0001, 'ccn'), (15, 14, -1))

        self.assertWrapsCorrectly(time, ('2000', '2001'), (0, 2))
        self.assertWrapsCorrectly(time, ('2000', '2000'), (0, 1))
        self.assertWrapsCorrectly(time, ('2002', '2000'), (2, None, -1))
        self.assertWrapsCorrectly(
            time, ('1999-12-1', '1999-12-10', 'cob'), (0, 1))

        self.assertWrapsCorrectly(time0, (0.0, 0.0, 'ccb'), (0, 1))

        self.assertWrapsCorrectly(lev, (0.05035, 0.05035), (0, 1))
        self.assertWrapsCorrectly(lev, (0.1009, 0.1009), (1, 2))


if __name__ == "__main__":
    basetest.run()
