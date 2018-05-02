#!/usr/bin/env python

"""
Write data to VTK file format using the structured grid format
Alex Pletzer, Tech-X Corp. (2011)
This code is provided with the hope that it will be useful.
No guarantee is provided whatsoever. Use at your own risk.
"""

from __future__ import print_function
import numpy
import time
from . import mvBaseWriter


class VTKSGWriter(mvBaseWriter.BaseWriter):

    def write(self, filename):
        """
        Write file

        Parameters
        ----------

             filename
                 file name
        """
        f = open(filename, 'w')
        print('# vtk DataFile Version 2.0', file=f)
        print('generated on %s' % time.asctime(), file=f)
        print('ASCII', file=f)
        print('DATASET STRUCTURED_GRID', file=f)
        shp = self.shape[:]
        shp.reverse()
        print('DIMENSIONS %d %d %d' % tuple(shp), file=f)
        npts = self.mesh.shape[0]
        print('POINTS %d float' % npts, file=f)
        for i in range(npts):
            print('%f %f %f' % tuple(self.mesh[i, :]), file=f)
        n0, n1, n2 = self.shape
        # nodal data
        print('POINT_DATA %d' % (n0 * n1 * n2), file=f)
        print('SCALARS %s float' % (self.var.id), file=f)
        print('LOOKUP_TABLE default', file=f)
        if n0 > 1:
            for k in range(n0):
                for j in range(n1):
                    for i in range(n2):
                        print('%f' % self.var[k, j, i], file=f)
        else:
            for j in range(n1):
                for i in range(n2):
                    print('%f' % self.var[j, i], file=f)
        f.close()


######################################################################

def test2DRect():
    import cdms2
    from numpy import pi, cos, sin
    nlat, nlon = 6, 10
    grid = cdms2.createUniformGrid(-0.0, nlat, 60. / (nlat - 1),
                                   0., nlon, 30. / nlon)
    lons = grid.getLongitude()
    lats = grid.getLatitude()
    data = numpy.outer(cos(3 * pi * lats[:] / 180.0),
                       sin(5 * pi * lons[:] / 180.0))
    var = cdms2.createVariable(data, id='fake_data_2d_rect',
                               axes=(lats, lons))
    vw = VTKSGWriter(var)
    vw.write('test2DRect_SG.vtk')


def test3D():
    import cdms2
    var = cdms2.open('sample_data/ta_ncep_87-6-88-4.nc', 'r')('ta')
    vw = VTKSGWriter(var[0, 0:10, 0:20, 0:30])
    vw.write('test3D_SG.vtk')


if __name__ == '__main__':
    test2DRect()
    test3D()
