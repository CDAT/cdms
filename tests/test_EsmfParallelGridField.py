"""

$Id: testEsmfParallelGridField.py 2394 2012-07-26 17:23:11Z dkindig $

Test the order of grid and field creation relative to GridAddCoord such that all grids and
fields are decomposed.
"""


import ESMF
import numpy
try:
    from mpi4py import MPI
    has_mpi = True
except BaseException:
    has_mpi = False

rootPe = 0
if has_mpi:
    pe = MPI.COMM_WORLD.Get_rank()
else:
    pe = 0

COORDSYS = ESMF.CoordSys.CART
CENTER = ESMF.StaggerLoc.CENTER
CORNER = ESMF.StaggerLoc.CORNER
R4 = ESMF.TypeKind.R4

ESMF.Manager(debug=True)


def makeGrid2D(ny, nx):

    x = numpy.linspace(1, 4, nx, numpy.float32)
    y = numpy.linspace(0, 3, ny, numpy.float32)

    xx = numpy.outer(numpy.ones(ny), x)
    yy = numpy.outer(y, numpy.ones(nx))

    xd, yd = abs(x[0] - x[1]) / 2., abs(y[0] - y[1]) / 2.
    xs, xe = x[0] - xd, x[-1] + xd
    ys, ye = y[0] - yd, y[-1] + yd
    xb = numpy.linspace(xs, xe, nx + 1, numpy.float32)
    yb = numpy.linspace(ys, ye, ny + 1, numpy.float32)

    xxb = numpy.outer(numpy.ones(ny + 1), xb)
    yyb = numpy.outer(yb, numpy.ones(nx + 1))

    return (yy, xx), (xxb, yyb)


def makeGrid3D(nx, ny, nz):
    dims = (nz, ny, nx)
    dimb = (nz + 1, ny + 1, nx + 1)
    xbot, xtop, ybot, ytop, zbot, ztop = 1, 4, 1, 5, .5, 6
    xbob, xtob, ybob, ytob, zbob, ztob = .5, 4.5, .5, 5.5, 0, 6.5
    x = numpy.linspace(xbot, xtop, nx)
    y = numpy.linspace(ybot, ytop, ny)
    z = numpy.linspace(zbot, ztop, nz)

    xb = numpy.linspace(xbob, xtob, nx + 1)
    yb = numpy.linspace(ybob, ytob, ny + 1)
    zb = numpy.linspace(zbob, ztob, nz + 1)

    xx = numpy.outer(numpy.ones(ny), x)
    yy = numpy.outer(y, numpy.ones(nx))
    ones = numpy.outer(numpy.ones(ny), numpy.ones(nx))
    xxx = numpy.outer(numpy.ones(nz), xx).reshape(dims)
    yyy = numpy.outer(numpy.ones(nz), yy).reshape(dims)
    zzz = numpy.outer(z, ones).reshape(dims)

    xxb = numpy.outer(numpy.ones(ny + 1), xb)
    yyb = numpy.outer(yb, numpy.ones(nx + 1))
    ones = numpy.outer(numpy.ones(ny + 1), numpy.ones(nx + 1))
    xxxb = numpy.outer(numpy.ones(nz + 1), xxb).reshape(dimb)
    yyyb = numpy.outer(numpy.ones(nz + 1), yyb).reshape(dimb)
    zzzb = numpy.outer(zb, ones).reshape(dimb)

    theVolume = [xxx, yyy, zzz]
    theBounds = [xxxb, yyyb, zzzb]

    theData = xxx * yyy + zzz

    return dims, theVolume, theData, theBounds


class createGridAndField:
    def __init__(self, maxIndex):

        self.grid = ESMF.Grid(
            maxIndex,
            num_peri_dims=0,
            coord_sys=COORDSYS,
            staggerloc=[CENTER])
        self.field = ESMF.Field(
            self.grid,
            name='srcField1',
            staggerloc=CENTER,
            typekind=R4)

    def getCoordPointer(self):
        return self.grid.get_coords(coord_dim=0, staggerloc=CENTER)

    def getDataPointer(self):
        return self.field.data


sDims, srcCrds, srcData, srcBnds = makeGrid3D(6, 12, 24)
dDims, dstCrds, dstData, dstBnds = makeGrid3D(6, 12, 24)

maxIndex = numpy.array(srcCrds[0].shape[::-1], numpy.int32)

srcGrid1 = ESMF.Grid(maxIndex, coord_sys=ESMF.CoordSys.CART)
dstGrid1 = ESMF.Grid(maxIndex, coord_sys=ESMF.CoordSys.CART)

srcFeld1 = ESMF.Field(srcGrid1, name='srcFeld1', staggerloc=CENTER,
                      typekind=R4)
dstFeld1 = ESMF.Field(srcGrid1, name='dstFeld1', staggerloc=CENTER,
                      typekind=R4)

srcPtr = srcFeld1.data
if pe == rootPe:
    print('1. Create Grid, Field then GridAddCoord()')
if pe == rootPe:
    print('2. GridCreate, GridAddCoord, FieldCreate')
if pe == rootPe:
    print('3. Use a class to create the grid addCoords then the field')
print(('1. ', srcPtr.size, srcCrds[0].size))

srcPtr = srcFeld1.data
print(('1. ', srcPtr.size, srcCrds[0].size))

srcGrid2 = ESMF.Grid(maxIndex, num_peri_dims=0, coord_sys=COORDSYS)
dstGrid2 = ESMF.Grid(maxIndex, num_peri_dims=0, coord_sys=COORDSYS)

srcFeld2 = ESMF.Field(srcGrid2, name='srcFeld2', staggerloc=CENTER,
                      typekind=R4)
dstFeld2 = ESMF.Field(dstGrid2, name='dstFeld2', staggerloc=CENTER,
                      typekind=R4)

srcPtr = srcFeld2.data
print(('2. ', srcPtr.size, srcCrds[0].size))

srcStuff = createGridAndField(maxIndex)

aa = srcStuff.getDataPointer()
bb = srcStuff.getCoordPointer()
print(('3. ', aa.size, bb.size))
