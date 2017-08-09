import cdms2
import numpy
import unittest

class cdmsCrossSection(unittest.TestCase):
    def setUp(self):
        self.data = numpy.arange(25,dtype=numpy.float32)
        self.data = cdms2.MV2.reshape(self.data,(5,5))

        lat = cdms2.createAxis(numpy.arange(-5,5,2))
        lat.designateLatitude()
        print lat[:]

        lev = cdms2.createAxis(numpy.arange(1000,500,-100))
        lev.designateLevel()
        lev.units='hPa'
        print lev[:]

        self.data.setAxis(0,lev)
        self.data.setAxis(1,lat)

    def assertAllClose(self,test,good):
        self.assertTrue(numpy.allclose(test,good))

    def toCross(self,targetLat):
        print targetLat
        print targetLat[:]
        out = self.data.crossSectionRegrid(self.data.getLevel(),targetLat)
        print out.tolist()
        return out

    def restUniform(self):
        # Target has less lat
        lat = cdms2.createAxis(numpy.arange(-5,6,2.5))
        good = [[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0], [10.0, 11.0, 11.999999046325684, 13.0, 14.0], [14.999999046325684, 16.0, 17.0, 18.0, 19.0], [20.0, 21.0, 22.0, 23.0, 24.0]]
        out = self.toCross(lat)
        self.assertAllClose(out,good)
        # Target has more lat
        lat = cdms2.createAxis(numpy.arange(-5,6,0.5))
        out = self.toCross(lat)
        good = [[0.0, 0.0, 0.0, 0.8921453356742859, 1.0, 1.0, 1.0, 1.0, 1.6319929361343384, 2.0, 2.0, 2.0, 2.0, 2.368007183074951, 3.0, 3.0, 3.0, 3.0, 3.1078546047210693, 4.0, 4.0, 4.0], [5.0, 5.0, 5.0, 5.892145156860352, 6.0, 6.0, 6.0, 6.0, 6.631992816925049, 7.000000476837158, 7.0, 7.0, 7.000000476837158, 7.368007183074951, 8.0, 8.0, 8.0, 8.0, 8.107854843139648, 9.0, 9.0, 9.0], [10.0, 10.0, 10.0, 10.892145156860352, 11.0, 11.0, 11.0, 11.0, 11.631993293762207, 12.0, 12.0, 12.0, 12.0, 12.36800765991211, 13.0, 13.0, 12.999999046325684, 13.0, 13.107854843139648, 13.999999046325684, 14.0, 14.0], [15.0, 15.0, 15.0, 15.892145156860352, 16.0, 16.0, 16.0, 16.0, 16.63199234008789, 17.0, 17.0, 17.0, 17.0, 17.36800765991211, 18.0, 18.0, 18.0, 18.0, 18.10785484313965, 19.0, 19.0, 19.0], [20.0, 20.0, 20.0, 20.89214515686035, 21.0, 20.999998092651367, 21.0, 21.0, 21.631994247436523, 22.0, 22.0, 22.0, 22.0, 22.36800765991211, 23.0, 23.0, 23.0, 23.0, 23.10785484313965, 24.0, 24.0, 24.0]]
        self.assertAllClose(out,good)

    def testGaussian(self):
        lat = cdms2.createGaussianAxis(3)
        out = self.toCross(lat)
        good = [[3.2598915100097656, 2.0, 0.7401084899902344], [8.259891510009766, 7.0, 5.740108489990234], [13.259891510009766, 12.0, 10.740108489990234], [18.259891510009766, 17.0, 15.740108489990234], [23.259891510009766, 22.0, 20.740108489990234]]
        self.assertAllClose(out,good)
        lat = cdms2.createGaussianAxis(7)
        out = self.toCross(lat)

    def restEqualArea(self):
        lat = cdms2.createEqualAreaAxis(3)
        out = self.toCross(lat)
        good = [[3.2598915100097656, 2.0, 0.7401084899902344], [8.259891510009766, 7.0, 5.740108489990234], [13.259891510009766, 12.0, 10.740108489990234], [18.259891510009766, 17.0, 15.740108489990234], [23.259891510009766, 22.0, 20.740108489990234]]
        self.assertAllClose(out,good)
        lat = cdms2.createEqualAreaAxis(7)
        out = self.toCross(lat)
        good = [[3.2664215564727783, 3.0, 2.1606080532073975, 2.0, 1.8393919467926025, 1.0, 0.7335784435272217], [8.2664213180542, 8.0, 7.160607814788818, 6.999999523162842, 6.839391708374023, 6.0, 5.733578681945801], [13.2664213180542, 13.0, 12.16060733795166, 12.0, 11.839391708374023, 11.0, 10.733577728271484], [18.266422271728516, 18.0, 17.160608291625977, 17.0, 16.839391708374023, 16.0, 15.7335786819458], [23.266422271728516, 23.0, 22.160608291625977, 22.0, 21.839391708374023, 21.0, 20.733577728271484]]
        self.assertAllClose(out,good)

    def restGeneric(self):
        # Less latitudes
        lat = cdms2.createAxis([-5,0,1])
        lat.designateLatitude()
        lat.setBounds(None)
        out = self.toCross(lat)
        good = [[2.0, 2.0, 2.0], [7.0, 7.0, 7.0], [12.000000953674316, 11.999999046325684, 12.0], [17.0, 17.0, 17.0], [22.0, 22.0, 22.0]]
        self.assertAllClose(out,good)

        # More latitudes
        lat = cdms2.createAxis([-5,-4,-1,6,21,23,45,56,78])
        lat.designateLatitude()
        lat.setBounds(None)
        out = self.toCross(lat)
        good = [[2.0, 2.0, 2.0, 2.0, 2.0, 2.9562435150146484, 3.0, 3.0, 3.9574670791625977], [7.0, 7.0, 7.0, 7.0, 7.0, 7.956243515014648, 8.0, 8.0, 8.957467079162598], [12.0, 12.0, 12.0, 11.999999046325684, 12.0, 12.956244468688965, 13.0, 13.0, 13.957467079162598], [17.0, 17.0, 17.0, 17.0, 17.0, 17.95624351501465, 18.0, 18.0, 18.95746612548828], [22.0, 22.0, 22.0, 22.0, 22.0, 22.95624351501465, 23.0, 23.0, 23.95746612548828]]
        self.assertAllClose(out,good)
