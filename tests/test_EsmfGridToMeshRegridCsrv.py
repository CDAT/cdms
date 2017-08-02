#!/usr/bin/env python
#
# $Id: ESMP_GridToMeshRegridCsrv.py,v 1.5 2012/04/23 23:00:14 rokuingh Exp $
#=========================================================================
#             ESMP/examples/ESMP_GridToMeshRegrid.py
#=========================================================================

"""
ESMP_GridToMeshRegridCsrv.py

Two ESMP_Field objects are created, one on a Grid and the other on a Mesh.  The
source Field is set to an analytic function, and a conservative regridding
operation is performed from the source to the destination Field.  After
the regridding is completed, the destination Field is compared to the
exact solution over that domain.
"""

import cdms2
import ESMF
import numpy as np
import unittest


def compare_fields_grid(field1, field2, itrp_tol, csrv_tol, parallel=False,
                        dstfracfield=None, mass1=None, mass2=None,
                        regrid_method=ESMF.RegridMethod.CONSERVE, mask_values=[0]):
    '''
    PRECONDITIONS: Two Fields have been created and a comparison of the
                   the values is desired between 'field1' and
                   'field2'.  The fields should be the same size on have
                   rank=2 or 3.
    POSTCONDITIONS: The values on 'field1' and 'field2' are
                    compared against the each other.
    '''
    import numpy.ma as ma

    correct = False
    # verify that the fields are the same size
    assert field1.data.shape == field2.data.shape, 'compare_fields: Fields must be the same size!'

    # deal with default values for fracfield
    if dstfracfield is None:
        dstfracfield = ma.ones(field1.data.shape)

    # compute pointwise error measures
    totalErr = 0.0
    max_error = 0.0
    min_error = 1000000.0
    num_nodes = 0

    # allow fields of all dimensions
    field1_flat = np.ravel(field1.data)
    field2_flat = np.ravel(field2.data)
    dstfracfield_flat = np.ravel(dstfracfield.data)
    # TODO:  test for evaluating field2mask into an array of True/False values
    # based on field2.grid.mask
    if field2.grid.mask[field2.staggerloc] is not None:
        field2mask_flat = [
            True if x in mask_values else False for x in field2.grid.mask[field2.staggerloc].flatten().tolist()]
    else:
        field2mask_flat = np.ravel(np.zeros_like(field2.data))

    # TODO: would be nice to add a condition to ignore where original value is
    # unchanged
    for i in range(field2_flat.size):
        if ((not field2mask_flat[i]) and
            (regrid_method != ESMF.RegridMethod.CONSERVE or
             dstfracfield_flat[i] >= 0.999) and
                field2_flat[i] != 0.0):

            err = abs(field1_flat[i] / dstfracfield_flat[i] -
                      field2_flat[i]) / abs(field2_flat[i])

            num_nodes += 1
            totalErr += err
            if (err > max_error):
                max_error = err
            if (err < min_error):
                min_error = err

    # gather error on processor 0 or set global variables in serial case
    mass1_global = 0
    mass2_global = 0
    csrv_error_global = 0
    if parallel:
        # use mpi4py to collect values
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        total_error_global = comm.reduce(totalErr, op=MPI.SUM)
        num_nodes_global = comm.reduce(num_nodes, op=MPI.SUM)
        max_error_global = comm.reduce(max_error, op=MPI.MAX)
        min_error_global = comm.reduce(min_error, op=MPI.MIN)
        if (mass1 and mass2):
            mass1_global = comm.reduce(mass1, op=MPI.SUM)
            mass2_global = comm.reduce(mass2, op=MPI.SUM)
    else:
        total_error_global = totalErr
        num_nodes_global = num_nodes
        max_error_global = max_error
        min_error_global = min_error
        if (mass1 and mass2):
            mass1_global = mass1
            mass2_global = mass2

    # compute relative error measures and compare against tolerance values
    itrp = False
    csrv = False
    if ESMF.local_pet() == 0:
        if mass1_global == 0:
            csrv_error_global = abs(mass2_global - mass1_global)
        else:
            csrv_error_global = abs(
                mass2_global - mass1_global) / abs(mass1_global)

        # compute mean relative error
        if num_nodes != 0:
            total_error_global = total_error_global / num_nodes_global

        # determine if interpolation and conservation are up to spec
        if (total_error_global < itrp_tol):
            itrp = True
        if (csrv_error_global < csrv_tol):
            csrv = True

        # print out diagnostic information
        print(("  Mean relative error = " + str(total_error_global)))
        print(("  Max  relative error = " + str(max_error_global)))
        print(("  Conservation  error = " + str(csrv_error_global)))
        # print "  Min error   = "+str(min_error_global)
        # print "  srcmass     = "+str(mass1_global)
        # print "  dstmass     = "+str(mass2_global)

    # broadcast in parallel case
    if parallel:
        itrp, csrv = MPI.COMM_WORLD.bcast([itrp, csrv], 0)
        total_error_global, csrv_error_global = \
            MPI.COMM_WORLD.bcast([total_error_global, csrv_error_global], 0)

    # print pass or fail
    assert (itrp and csrv)
    if (itrp and csrv):
        print(("PET{0} - PASS".format(ESMF.local_pet())))
        correct = True
    else:
        print(("PET{0} - FAIL".format(ESMF.local_pet())))

    return total_error_global, csrv_error_global


def initialize_field_grid(field, domask=False, doarea=False):
    '''
    PRECONDITIONS: A Field has been created.
    POSTCONDITIONS: The 'field' has been initialized to an analytic
                    field.
    RETURN VALUES: \n Field :: field \n
    '''
    if domask:
        mask = field.grid.get_item(ESMF.GridItem.MASK)

    # get the coordinate pointers and set the coordinates
    [x, y] = [0, 1]
    gridXCoord = field.grid.get_coords(0, ESMF.StaggerLoc.CENTER)
    gridYCoord = field.grid.get_coords(1, ESMF.StaggerLoc.CENTER)

    field.data[:] = 20.0 + gridXCoord**2 + \
        gridXCoord * gridYCoord + gridYCoord**2

    if domask:
        field.data[mask == 0] = 0

    return field


def initialize_field_mesh(field, nodeCoord, nodeOwner, elemType, elemConn,
                          domask=False, elemMask=None):
    '''
    PRECONDITIONS: A Field has been created on the elements of a Mesh.
    POSTCONDITIONS: The Field has been initialized to an analytic
                    field.
    RETURN VALUES: \n Field :: field \n
    '''

    [node, element] = [0, 1]

    if field.staggerloc == element:
        offset = 0
        for i in range(field.grid.size_owned[element]):
            if (elemType[i] == ESMF.MeshElemType.TRI):
                x1 = nodeCoord[(elemConn[offset]) * 2]
                x2 = nodeCoord[(elemConn[offset + 1]) * 2]
                x3 = nodeCoord[(elemConn[offset + 2]) * 2]
                y1 = nodeCoord[(elemConn[offset]) * 2 + 1]
                y2 = nodeCoord[(elemConn[offset + 1]) * 2 + 1]
                y3 = nodeCoord[(elemConn[offset + 2]) * 2 + 1]
                x = (x1 + x2 + x3) / 3.0
                y = (y1 + y2 + y3) / 3.0
                offset = offset + 3
            elif (elemType[i] == ESMF.MeshElemType.QUAD):
                x1 = nodeCoord[(elemConn[offset]) * 2]
                x2 = nodeCoord[(elemConn[offset + 1]) * 2]
                y1 = nodeCoord[(elemConn[offset + 1]) * 2 + 1]
                y2 = nodeCoord[(elemConn[offset + 3]) * 2 + 1]
                x = (x1 + x2) / 2.0
                y = (y1 + y2) / 2.0
                offset = offset + 4
            else:
                raise ValueError("Elem type is not supported.")

            # print '[{0},{1}] = {2}'.format(x,y,field.data[i])
            field.data[i] = 20.0 + x**2 + x * y + y**2

            if domask:
                # calculate field
                if (elemMask[i] == 0):
                    field.data[i] = 0

    elif field.staggerloc == node:
        ind = 0
        for i in range(field.grid.size[node]):
            x = nodeCoord[i * 2]
            y = nodeCoord[i * 2 + 1]

            if (nodeOwner[i] == ESMF.local_pet()):
                if ind > field.grid.size_owned:
                    raise ValueError("Overstepped the mesh bounds!")
                field.data[ind] = 20.0 + x**2 + x * y + y**2
                # print '[{0},{1}] = {2}'.format(x,y,field.data[ind])
                ind += 1

            if domask:
                # calculate field
                if (elemMask[i] == 0):
                    field.data[i] = 0

    else:
        raise ValueError("Field staggerloc is not supported")

    return field


def grid_create(xdom, ydom, nx, ny, corners=False,
                domask=False, doarea=False, ctk=ESMF.TypeKind.R8):
    """
    :param xdom: 2,1 list containing the x domain
    :param ydom: 2,1 list conatining the y domain
    :param nx: number of longitude values at cell centers
    :param ny: number of latitude values at cell centers
    :param corners: boolean to determine whether or not to add corner coordinates to this grid
    :param domask: boolean to determine whether to set an arbitrary mask or not
    :param doarea: boolean to determine whether to set an arbitrary area values or not
    :param ctk: the coordinate typekind
    :return: grid
    """
    [x, y] = [0, 1]

    # Create arrays of center and corner values to emulate what would be read from a standard CF-like file
    # +1 because corners have one more than center
    xs = np.linspace(xdom[0], xdom[1], nx + 1)
    xcorner = np.array([xs[0:-1], xs[1::]]).T
    xcenter = (xcorner[:, 1] + xcorner[:, 0]) / 2

    # +1 because corners have one more than center
    ys = np.linspace(ydom[0], ydom[1], ny + 1)
    ycorner = np.array([ys[0:-1], ys[1::]]).T
    ycenter = (ycorner[:, 1] + ycorner[:, 0]) / 2

    # create a grid given the number of grid cells in each dimension, the center stagger location is allocated, the
    # Cartesian coordinate system and type of the coordinates are specified
    max_index = np.array([nx, ny])
    grid = ESMF.Grid(
        max_index,
        staggerloc=[
            ESMF.StaggerLoc.CENTER],
        coord_sys=ESMF.CoordSys.CART,
        coord_typekind=ctk)

    # set the grid coordinates using numpy arrays, parallel case is handled
    # using grid bounds
    gridXCenter = grid.get_coords(x)
    x_par = xcenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER]
                    [x]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][x]]
    gridXCenter[...] = x_par.reshape((x_par.size, 1))

    gridYCenter = grid.get_coords(y)
    y_par = ycenter[grid.lower_bounds[ESMF.StaggerLoc.CENTER]
                    [y]:grid.upper_bounds[ESMF.StaggerLoc.CENTER][y]]
    gridYCenter[...] = y_par.reshape((1, y_par.size))

    # create grid corners in a slightly different manner to account for the
    # bounds format common in CF-like files
    if corners:
        grid.add_coords([ESMF.StaggerLoc.CORNER])
        lbx = grid.lower_bounds[ESMF.StaggerLoc.CORNER][x]
        ubx = grid.upper_bounds[ESMF.StaggerLoc.CORNER][x]
        lby = grid.lower_bounds[ESMF.StaggerLoc.CORNER][y]
        uby = grid.upper_bounds[ESMF.StaggerLoc.CORNER][y]

        gridXCorner = grid.get_coords(x, staggerloc=ESMF.StaggerLoc.CORNER)
        for i0 in range(ubx - lbx - 1):
            gridXCorner[i0, :] = xcorner[i0 + lbx, 0]
        gridXCorner[i0 + 1, :] = xcorner[i0 + lbx, 1]

        gridYCorner = grid.get_coords(y, staggerloc=ESMF.StaggerLoc.CORNER)
        for i1 in range(uby - lby - 1):
            gridYCorner[:, i1] = ycorner[i1 + lby, 0]
        gridYCorner[:, i1 + 1] = ycorner[i1 + lby, 1]

    # add an arbitrary mask
    if domask:
        mask = grid.add_item(ESMF.GridItem.MASK)
        mask[:] = 1
        mask[np.where((1.75 <= gridXCenter.data < 2.25) &
                      (1.75 <= gridYCenter.data < 2.25))] = 0

    # add arbitrary areas values
    if doarea:
        area = grid.add_item(ESMF.GridItem.AREA)
        area[:] = 5.0

    return grid


def compute_mass_grid(valuefield, dofrac=False, fracfield=None,
                      uninitval=422397696.):
    '''
    PRECONDITIONS: 'fracfield' contains the fractions of each cell
                   which contributed to a regridding operation involving
                   'valuefield.  'dofrac' is a boolean value that gives
                   the option to not use the 'fracfield'.\n
    POSTCONDITIONS: The mass of the data field is computed.\n
    RETURN VALUES: float :: mass \n
    '''
    mass = 0.0
    areafield = ESMF.Field(valuefield.grid, name='areafield')
    areafield.get_area()

    ind = np.where(valuefield.data != uninitval)

    if dofrac:
        mass = np.sum(
            areafield.data[ind] *
            valuefield.data[ind] *
            fracfield.data[ind])
    else:
        mass = np.sum(areafield.data[ind] * valuefield.data[ind])

    return mass


def compute_mass_mesh(valuefield, dofrac=False, fracfield=None,
                      uninitval=422397696.):
    '''
    PRECONDITIONS: 'fracfield' contains the fractions of each cell
                   which contributed to a regridding operation involving
                   'valuefield.  'dofrac' is a boolean value that gives
                   the option to not use the 'fracfield'.\n
    POSTCONDITIONS: The mass of the data field is computed.\n
    RETURN VALUES: float :: mass \n
    '''
    mass = 0.0
    # mesh area field must be built on elements
    areafield = ESMF.Field(valuefield.grid, name='areafield',
                           meshloc=ESMF.MeshLoc.ELEMENT)
    areafield.get_area()

    ind = np.where(valuefield.data != uninitval)
    if dofrac:
        mass = np.sum(areafield.data[ind[0]] *
                      valuefield.data[ind[0]] *
                      fracfield.data[ind[0]])
    else:
        mass = np.sum(areafield.data[ind[0]] * valuefield.data[ind[0]])

    return mass


def mesh_create_50(domask=False, doarea=False):
    '''
    PRECONDITIONS: None
    POSTCONDITIONS: A 50 element Mesh has been created.
    RETURN VALUES: \n Mesh :: mesh \n

      3.75  81 ------ 82 ----- 83 ------ 84 ------ 85 ------ 86 ------ 87 ------ 88
            |         |        |         |         |         |         |  77 /   |
            |    71   |   72   |    73   |    74   |   75    |    76   |    /    |
            |         |        |         |         |         |         |  /  78  |
      3.25  71 ------ 72 ----- 73 ------ 74 ------ 75 ------ 76 ------ 77 ------ 78
            |         |        |         |         |         |         |         |
            |    61   |   62   |    63   |    64   |    65   |    66   |   67    |
            |         |        |         |         |         |         |         |
      2.75  61 ------ 62 ----- 63 ------ 64 ------ 65 ------ 66 ------ 67 ------ 68
            |         |        |         |         |         |         |         |
            |    51   |   52   |    53   |    54   |    55   |    56   |   57    |
            |         |        |         |         |         |         |         |
      2.25  51 ------ 52 ----- 53 ------ 54 ------ 55 ------ 56 ------ 57 ------ 58
            |         |        |         |         |         |         |         |
            |    41   |   42   |    43   |    44   |    45   |    46   |   47    |
            |         |        |         |         |         |         |         |
      1.75  41 ------ 42 ----- 43 ------ 44 ------ 45 ------ 46 ------ 47 ------ 48
            |         |        |         |         |         |         |         |
            |    31   |   32   |    33   |    34   |    35   |    36   |   37    |
            |         |        |         |         |         |         |         |
      1.25  31 ------ 32 ----- 33 ------ 34 ------ 35 ------ 36 ------ 37 ------ 38
            |         |        |         |         |         |         |         |
            |    21   |   22   |    23   |    24   |    25   |    26   |   27    |
            |         |        |         |         |         |         |         |
      0.75  21 ------ 22 ----- 23 ------ 24 ------ 25 ------ 26 ------ 27 ------ 28
            |         |        |         |         |         |         |         |
            |    11   |   12   |    13   |    14   |    15   |    16   |   17    |
            |         |        |         |         |         |         |         |
      0.25  11 ------ 12 ----- 13 ------ 14 ------ 15 ------ 16 ------ 17 ------ 18

           0.25      0.75     1.25      1.75      2.25      2.75      3.25      3.75

          Node Ids at corners
          Element Ids in centers

    Note: This mesh is not parallel, it can only be used in serial
    '''
    # Two parametric dimensions, and two spatial dimensions
    mesh = ESMF.Mesh(parametric_dim=2, spatial_dim=2)

    num_node = 64
    num_elem = 50
    nodeId = np.array([11, 12, 13, 14, 15, 16, 17, 18,
                       21, 22, 23, 24, 25, 26, 27, 28,
                       31, 32, 33, 34, 35, 36, 37, 38,
                       41, 42, 43, 44, 45, 46, 47, 48,
                       51, 52, 53, 54, 55, 56, 57, 58,
                       61, 62, 63, 64, 65, 66, 67, 68,
                       71, 72, 73, 74, 75, 76, 77, 78,
                       81, 82, 83, 84, 85, 86, 87, 88])
    nodeCoord = np.array([0.25, 0.25, 0.25, 0.75, 0.25, 1.25, 0.25, 1.75, 0.25, 2.25, 0.25, 2.75, 0.25, 3.25, 0.25, 3.75,
                          0.75, 0.25, 0.75, 0.75, 0.75, 1.25, 0.75, 1.75, 0.75, 2.25, 0.75, 2.75, 0.75, 3.25, 0.75, 3.75,
                          1.25, 0.25, 1.25, 0.75, 1.25, 1.25, 1.25, 1.75, 1.25, 2.25, 1.25, 2.75, 1.25, 3.25, 1.25, 3.75,
                          1.75, 0.25, 1.75, 0.75, 1.75, 1.25, 1.75, 1.75, 1.75, 2.25, 1.75, 2.75, 1.75, 3.25, 1.75, 3.75,
                          2.25, 0.25, 2.25, 0.75, 2.25, 1.25, 2.25, 1.75, 2.25, 2.25, 2.25, 2.75, 2.25, 3.25, 2.25, 3.75,
                          2.75, 0.25, 2.75, 0.75, 2.75, 1.25, 2.75, 1.75, 2.75, 2.25, 2.75, 2.75, 2.75, 3.25, 2.75, 3.75,
                          3.25, 0.25, 3.25, 0.75, 3.25, 1.25, 3.25, 1.75, 3.25, 2.25, 3.25, 2.75, 3.25, 3.25, 3.25, 3.75,
                          3.75, 0.25, 3.75, 0.75, 3.75, 1.25, 3.75, 1.75, 3.75, 2.25, 3.75, 2.75, 3.75, 3.25, 3.75, 3.75])
    nodeOwner = np.zeros(num_node)
    elemId = np.array([11, 12, 13, 14, 15, 16, 17,
                       21, 22, 23, 24, 25, 26, 27,
                       31, 32, 33, 34, 35, 36, 37,
                       41, 42, 43, 44, 45, 46, 47,
                       51, 52, 53, 54, 55, 56, 57,
                       61, 62, 63, 64, 65, 66, 67,
                       71, 72, 73, 74, 75, 76, 77, 78])
    elemType = np.ones(num_elem - 2) * ESMF.MeshElemType.QUAD
    elemType = np.append(
        elemType, [
            ESMF.MeshElemType.TRI, ESMF.MeshElemType.TRI])
    elemConn = np.array([11, 12, 22, 21, 12, 13, 23, 22, 13, 14, 24, 23, 14, 15, 25, 24, 15, 16, 26, 25, 16, 17, 27, 26, 17, 18, 28, 27,
                         21, 22, 32, 31, 22, 23, 33, 32, 23, 24, 34, 33, 24, 25, 35, 34, 25, 26, 36, 35, 26, 27, 37, 36, 27, 28, 38, 37,
                         31, 32, 42, 41, 32, 33, 43, 42, 33, 34, 44, 43, 34, 35, 45, 44, 35, 36, 46, 45, 36, 37, 47, 46, 37, 38, 48, 47,
                         41, 42, 52, 51, 42, 43, 53, 52, 43, 44, 54, 53, 44, 45, 55, 54, 45, 46, 56, 55, 46, 47, 57, 56, 47, 48, 58, 57,
                         51, 52, 62, 61, 52, 53, 63, 62, 53, 54, 64, 63, 54, 55, 65, 64, 55, 56, 66, 65, 56, 57, 67, 66, 57, 58, 68, 67,
                         61, 62, 72, 71, 62, 63, 73, 72, 63, 64, 74, 73, 64, 65, 75, 74, 65, 66, 76, 75, 66, 67, 77, 76, 67, 68, 78, 77,
                         71, 72, 82, 81, 72, 73, 83, 82, 73, 74, 84, 83, 74, 75, 85, 84, 75, 76, 86, 85, 76, 77, 87, 86,
                         77, 88, 87,
                         77, 78, 88])
    elemConn = np.array([np.where(a == nodeId) for a in elemConn]).flatten()
    elemCoord = np.array(
        [0.5, 0.5, 1.0, 0.5, 1.5, 0.5, 2.0, 0.5, 2.5, 0.5, 3.0, 0.5, 3.5, 0.5,
         0.5, 1.0, 1.0, 1.0, 1.5, 1.0, 2.0, 1.0, 2.5, 1.0, 3.0, 1.0, 3.5, 1.0,
         0.5, 1.5, 1.0, 1.5, 1.5, 1.5, 2.0, 1.5, 2.5, 1.5, 3.0, 1.5, 3.5, 1.5,
         0.5, 2.0, 1.0, 2.0, 1.5, 2.0, 2.0, 2.0, 2.5, 2.0, 3.0, 2.0, 3.5, 2.0,
         0.5, 2.5, 1.0, 2.5, 1.5, 2.5, 2.0, 2.5, 2.5, 2.5, 3.0, 2.5, 3.5, 2.5,
         0.5, 3.0, 1.0, 3.0, 1.5, 3.0, 2.0, 3.0, 2.5, 3.0, 3.0, 3.0, 3.5, 3.0,
         0.5, 3.5, 1.0, 3.5, 1.5, 3.5, 2.0, 3.5, 2.5, 3.5, 3.0, 3.5, 3.375, 3.625, 3.625, 3.375])
    elemMask = None
    if domask:
        elemMask = np.ones(50)
        elemMask[1] = 0
    elemArea = None
    if doarea:
        elemArea = np.ones(48) * 5
        elemArea = np.append(elemArea, [2.5, 2.5])

    mesh.add_nodes(num_node, nodeId, nodeCoord, nodeOwner)

    mesh.add_elements(num_elem, elemId, elemType, elemConn,
                      element_mask=elemMask, element_area=elemArea, element_coords=elemCoord)

    # TODO: clean this up!
    if domask and doarea:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemMask, elemArea
    elif domask and not doarea:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemMask
    elif not domask and doarea:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemArea
    else:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemCoord


def mesh_create_50_parallel(domask=False, doarea=False):
    '''
    PRECONDITIONS: None
    POSTCONDITIONS: A 50 element Mesh has been created in parallel.
    RETURN VALUES: \n Mesh :: mesh \n

      3.75  81 ------ 82 ----- 83 ------ 84   [84] ----- 85 ------ 86 ------ 87 ------ 88
            |         |        |         |     |         |         |         |  77 /   |
            |    71   |   72   |    73   |     |    74   |   75    |    76   |    /    |
            |         |        |         |     |         |         |         |  /  78  |
      3.25  71 ------ 72 ----- 73 ------ 74   [74] ----- 75 ------ 76 ------ 77 ------ 78
            |         |        |         |     |         |         |         |         |
            |    61   |   62   |    63   |     |    64   |    65   |    66   |   67    |
            |         |        |         |     |         |         |         |         |
      2.75  61 ------ 62 ----- 63 ------ 64   [64] ----- 65 ------ 66 ------ 67 ------ 68
            |         |        |         |     |         |         |         |         |
            |    51   |   52   |    53   |     |    54   |    55   |    56   |   57    |
            |         |        |         |     |         |         |         |         |
      2.25  51 ------ 52 ----- 53 ------ 54   [54] ----- 55 ------ 56 ------ 57 ------ 58
            |         |        |         |     |         |         |         |         |
            |    41   |   42   |    43   |     |    44   |    45   |    46   |   47    |
            |         |        |         |     |         |         |         |         |
      1.75 [41] ---- [42] --- [43] ---- [44]  [44] ---- [45] ---- [46] ---- [47] ---- [48]

                        PET 2                                     PET 3


      1.75  41 ------ 42 ----- 43 ------ 44   [44] ----- 45 ------ 46 ------ 47 ------ 48
            |         |        |         |     |         |         |         |         |
            |    31   |   32   |    33   |     |    34   |    35   |    36   |   37    |
            |         |        |         |     |         |         |         |         |
      1.25  31 ------ 32 ----- 33 ------ 34   [34] ----- 35 ------ 36 ------ 37 ------ 38
            |         |        |         |     |         |         |         |         |
            |    21   |   22   |    23   |     |    24   |    25   |    26   |   27    |
            |         |        |         |     |         |         |         |         |
      0.75  21 ------ 22 ----- 23 ------ 24   [24] ----- 25 ------ 26 ------ 27 ------ 28
            |         |        |         |     |         |         |         |         |
            |    11   |   12   |    13   |     |    14   |    15   |    16   |   17    |
            |         |        |         |     |         |         |         |         |
      0.25  11 ------ 12 ----- 13 ------ 14   [14] ----- 15 ------ 16 ------ 17 ------ 18

           0.25      0.75     1.25      1.75  1.75      2.25      2.75      3.25      3.75

                        PET 0                                     PET 1

          Node Ids at corners
          Element Ids in centers
    '''
    if ESMF.pet_count() > 1:
        if ESMF.pet_count() != 4:
            raise NameError('MPI rank must be 4 to build this mesh!')

    # Two parametric dimensions, and two spatial dimensions
    mesh = ESMF.Mesh(parametric_dim=2, spatial_dim=2)

    if ESMF.local_pet() == 0:
        num_node = 16
        num_elem = 9
        nodeId = np.array([11, 12, 13, 14,
                           21, 22, 23, 24,
                           31, 32, 33, 34,
                           41, 42, 43, 44])
        nodeCoord = np.array([0.25, 0.25, 0.25, 0.75, 0.25, 1.25, 0.25, 1.75,
                              0.75, 0.25, 0.75, 0.75, 0.75, 1.25, 0.75, 1.75,
                              1.25, 0.25, 1.25, 0.75, 1.25, 1.25, 1.25, 1.75,
                              1.75, 0.25, 1.75, 0.75, 1.75, 1.25, 1.75, 1.75])
        nodeOwner = np.zeros(num_node)
        elemId = np.array([11, 12, 13,
                           21, 22, 23,
                           31, 32, 33])
        elemType = np.ones(num_elem) * ESMF.MeshElemType.QUAD
        elemConn = np.array([11, 12, 22, 21, 12, 13, 23, 22, 13, 14, 24, 23,
                             21, 22, 32, 31, 22, 23, 33, 32, 23, 24, 34, 33,
                             31, 32, 42, 41, 32, 33, 43, 42, 33, 34, 44, 43])
        elemConn = np.array([np.where(a == nodeId)
                             for a in elemConn]).flatten()
        elemMask = None
        if domask:
            elemMask = np.ones(num_elem)
            elemMask[1] = 0
        elemArea = None
        if doarea:
            elemArea = np.ones(num_elem) * 5

    elif ESMF.local_pet() == 1:
        num_node = 20
        num_elem = 12
        nodeId = np.array([14, 15, 16, 17, 18,
                           24, 25, 26, 27, 28,
                           34, 35, 36, 37, 38,
                           44, 45, 46, 47, 48])
        nodeCoord = np.array([0.25, 1.75, 0.25, 2.25, 0.25, 2.75, 0.25, 3.25, 0.25, 3.75,
                              0.75, 1.75, 0.75, 2.25, 0.75, 2.75, 0.75, 3.25, 0.75, 3.75,
                              1.25, 1.75, 1.25, 2.25, 1.25, 2.75, 1.25, 3.25, 1.25, 3.75,
                              1.75, 1.75, 1.75, 2.25, 1.75, 2.75, 1.75, 3.25, 1.75, 3.75])
        nodeOwner = np.array(
            [0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1])
        elemId = np.array([14, 15, 16, 17,
                           24, 25, 26, 27,
                           34, 35, 36, 37])
        elemType = np.ones(num_elem) * ESMF.MeshElemType.QUAD
        elemConn = np.array([14, 15, 25, 24, 15, 16, 26, 25, 16, 17, 27, 26, 17, 18, 28, 27,
                             24, 25, 35, 34, 25, 26, 36, 35, 26, 27, 37, 36, 27, 28, 38, 37,
                             34, 35, 45, 44, 35, 36, 46, 45, 36, 37, 47, 46, 37, 38, 48, 47])
        elemConn = np.array([np.where(a == nodeId)
                             for a in elemConn]).flatten()
        elemMask = None
        if domask:
            elemMask = np.ones(num_elem)
        elemArea = None
        if doarea:
            elemArea = np.ones(num_elem) * 5

    elif ESMF.local_pet() == 2:
        num_node = 20
        num_elem = 12
        nodeId = np.array([41, 42, 43, 44,
                           51, 52, 53, 54,
                           61, 62, 63, 64,
                           71, 72, 73, 74,
                           81, 82, 83, 84])
        nodeCoord = np.array([1.75, 0.25, 1.75, 0.75, 1.75, 1.25, 1.75, 1.75,
                              2.25, 0.25, 2.25, 0.75, 2.25, 1.25, 2.25, 1.75,
                              2.75, 0.25, 2.75, 0.75, 2.75, 1.25, 2.75, 1.75,
                              3.25, 0.25, 3.25, 0.75, 3.25, 1.25, 3.25, 1.75,
                              3.75, 0.25, 3.75, 0.75, 3.75, 1.25, 3.75, 1.75])
        nodeOwner = np.array(
            [0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
        elemId = np.array([41, 42, 43,
                           51, 52, 53,
                           61, 62, 63,
                           71, 72, 73])
        elemType = np.ones(num_elem) * ESMF.MeshElemType.QUAD
        elemConn = np.array([41, 42, 52, 51, 42, 43, 53, 52, 43, 44, 54, 53,
                             51, 52, 62, 61, 52, 53, 63, 62, 53, 54, 64, 63,
                             61, 62, 72, 71, 62, 63, 73, 72, 63, 64, 74, 73,
                             71, 72, 82, 81, 72, 73, 83, 82, 73, 74, 84, 83])
        elemConn = np.array([np.where(a == nodeId)
                             for a in elemConn]).flatten()
        elemMask = None
        if domask:
            elemMask = np.ones(num_elem)
        elemArea = None
        if doarea:
            elemArea = np.ones(num_elem) * 5

    elif ESMF.local_pet() == 3:
        num_node = 25
        num_elem = 17
        nodeId = np.array([44, 45, 46, 47, 48,
                           54, 55, 56, 57, 58,
                           64, 65, 66, 67, 68,
                           74, 75, 76, 77, 78,
                           84, 85, 86, 87, 88])
        nodeCoord = np.array([1.75, 1.75, 1.75, 2.25, 1.75, 2.75, 1.75, 3.25, 1.75, 3.75,
                              2.25, 1.75, 2.25, 2.25, 2.25, 2.75, 2.25, 3.25, 2.25, 3.75,
                              2.75, 1.75, 2.75, 2.25, 2.75, 2.75, 2.75, 3.25, 2.75, 3.75,
                              3.25, 1.75, 3.25, 2.25, 3.25, 2.75, 3.25, 3.25, 3.25, 3.75,
                              3.75, 1.75, 3.75, 2.25, 3.75, 2.75, 3.75, 3.25, 3.75, 3.75])
        nodeOwner = np.array(
            [0, 1, 1, 1, 1, 2, 3, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 3, 3, 3])
        elemId = np.array([44, 45, 46, 47,
                           54, 55, 56, 57,
                           64, 65, 66, 67,
                           74, 75, 76, 77, 78])
        elemType = np.ones(num_elem - 2) * ESMF.MeshElemType.QUAD
        elemType = np.append(
            elemType, [
                ESMF.MeshElemType.TRI, ESMF.MeshElemType.TRI])
        elemConn = np.array([44, 45, 55, 54, 45, 46, 56, 55, 46, 47, 57, 56, 47, 48, 58, 57,
                             54, 55, 65, 64, 55, 56, 66, 65, 56, 57, 67, 66, 57, 58, 68, 67,
                             64, 65, 75, 74, 65, 66, 76, 75, 66, 67, 77, 76, 67, 68, 78, 77,
                             74, 75, 85, 84, 75, 76, 86, 85, 76, 77, 87, 86,
                             77, 88, 87,
                             77, 78, 88])
        elemConn = np.array([np.where(a == nodeId)
                             for a in elemConn]).flatten()
        elemMask = None
        if domask:
            elemMask = np.ones(num_elem)
        elemArea = None
        if doarea:
            elemArea = np.ones(num_elem - 2) * 5
            elemArea = np.append(elemArea, [2.5, 2.5])

    mesh.add_nodes(num_node, nodeId, nodeCoord, nodeOwner)

    mesh.add_elements(num_elem, elemId, elemType, elemConn,
                      element_mask=elemMask, element_area=elemArea)

    if domask and doarea:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemMask, elemArea
    elif domask and not doarea:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemMask
    elif not domask and doarea:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn, elemArea
    else:
        return mesh, nodeCoord, nodeOwner, elemType, elemConn


class TestESMP_GridToMeshRegridCsrv(unittest.TestCase):

    def setUp(self):
        pass

    def test_test1(self):
        parallel = False
        if ESMF.pet_count() > 1:
            if ESMF.pet_count() != 4:
                raise NameError('MPI rank must be 4 in parallel mode!')
            parallel = True

        # create a Mesh
        if parallel:
            mesh, nodeCoord, nodeOwner, elemType, elemConn = \
                mesh_create_50_parallel()
        else:
            mesh, nodeCoord, nodeOwner, elemType, elemConn, _ = \
                mesh_create_50()

        # create a grid
        grid = grid_create([0, 4], [0, 4], 8, 8, corners=True)

        # create Fields
        srcfield = ESMF.Field(
            mesh,
            name='srcfield',
            meshloc=ESMF.MeshLoc.ELEMENT)
        srcfracfield = ESMF.Field(
            mesh,
            name='srcfracfield',
            meshloc=ESMF.MeshLoc.ELEMENT)
        dstfield = ESMF.Field(grid, name='dstfield')
        dstfracfield = ESMF.Field(grid, name='dstfracfield')
        exactfield = ESMF.Field(grid, name='exactfield')

        # initialize the Fields to an analytic function
        srcfield = initialize_field_mesh(
            srcfield, nodeCoord, nodeOwner, elemType, elemConn)
        exactfield = initialize_field_grid(exactfield)

        # run the ESMF regridding
        regridSrc2Dst = ESMF.Regrid(srcfield, dstfield,
                                    regrid_method=ESMF.RegridMethod.CONSERVE,
                                    norm_type=ESMF.NormType.FRACAREA,
                                    unmapped_action=ESMF.UnmappedAction.ERROR,
                                    src_frac_field=srcfracfield,
                                    dst_frac_field=dstfracfield)
        dstfield = regridSrc2Dst(srcfield, dstfield)

        # compute the mass
        srcmass = compute_mass_mesh(srcfield,
                                    dofrac=True, fracfield=srcfracfield)
        dstmass = compute_mass_grid(dstfield,
                                    dofrac=True, fracfield=dstfracfield)

        # compare results and output PASS or FAIL
        meanrel, csrvrel = compare_fields_grid(dstfield, exactfield, 50E-1, 10E-16, parallel=parallel,
                                               dstfracfield=dstfracfield, mass1=srcmass, mass2=dstmass)

        self.assertAlmostEqual(meanrel, 0.037733241800767432)
        self.assertAlmostEqual(csrvrel, 0.0)


if __name__ == '__main__':

    ESMF.Manager(debug=True)
    print("")  # Spacer
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMP_GridToMeshRegridCsrv)
    unittest.TextTestRunner(verbosity=1).run(suite)
