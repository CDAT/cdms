Regridding Data
---------------


Overview
^^^^^^^^

CDMS provides several methods for interpolating gridded data:

-  From one rectangular, lat-lon grid to another (CDMS regridder)
-  Between any two lat-lon grids (SCRIP regridder)
-  From one set of pressure levels to another
-  From one vertical (lat/level) cross-section to another vertical
   cross-section.

CDMS Horizontal Regrider
^^^^^^^^^^^^^^^^^^^^^^^^
.. highlight:: python
   :linenothreshold: 3

.. testsetup:: *

   import requests
   fnames = [ 'clt.nc', 'geos-sample', 'xieArkin-T42.nc', 'remap_grid_POP43.nc', 'remap_grid_T42.nc', 'rmp_POP43_to_T42_conserv.n', 'rmp_T42_to_POP43_conserv.nc', 'ta_ncep_87-6-88-4.nc', 'rmp_T42_to_C02562_conserv.nc' ]
   for file in fnames:
       url = 'http://cdat.llnl.gov/cdat/sample_data/'+file
       r = requests.get(url)
       open(file, 'wb').write(r.content)

.. testcleanup:: *

    import os
    fnames = [ 'clt.nc', 'geos-sample', 'xieArkin-T42.nc', 'remap_grid_POP43.nc', 'remap_grid_T42.nc', 'rmp_POP43_to_T42_conserv.n', 'rmp_T42_to_POP43_conserv.nc', 'ta_ncep_87-6-88-4.nc', 'rmp_T42_to_C02562_conserv.nc' ]
    for file in fnames:
       os.remove(file)

The simplest method to regrid a variable from one rectangular, lat/lon
grid to another is to use the regrid function defined for variables.
This function takes the target grid as an argument, and returns the
variable regridded to the target grid:

::

    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/clt.nc"
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/geos5-sample.nc"
    >>> import cdms2
    >>> import cdat_info
    >>> f1=cdms2.open("clt.nc")
    >>> f2=cdms2.open("geos5-sample.nc")
    >>> clt=f1('clt')  # Read the data
    >>> clt.shape
    (120, 46, 72)
    >>> ozone=f2['ozone']  # Get the file variable (no data read)
    >>> outgrid = ozone.getGrid() # Get the target grid
    >>> cltnew = clt.regrid(outgrid)
    >>> cltnew.shape
    (120, 181, 360)
    >>> outgrid.shape
    (181, 360)


A somewhat more efficient method is to create a regridder function. This
has the advantage that the mapping is created only once and can be used
for multiple arrays. Also, this method can be used with data in the form
of an MV2.MaskedArray. The steps in this process are:

#. Given an input grid and output grid, generate a regridder function.
#. Call the regridder function on a Numpy array, resulting in an array
   defined on the output grid. The regridder function can be called with
   any array or variable defined on the input grid.

The following example illustrates this process. The regridder function
is generated at line 9, and the regridding is performed at line 10:

::

    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/clt.nc"
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/geos5-sample.nc"
    >>> import cdms2
    >>> from regrid2 import Regridder
    >>> f = cdms2.open("clt.nc")
    >>> cltf = f['clt']
    >>> ingrid = cltf.getGrid()
    >>> g = cdms2.open('geos5-sample.nc')
    >>> outgrid = g['ozone'].getGrid()
    >>> regridfunc = Regridder(ingrid, outgrid)
    >>> cltnew = regridfunc(cltf)
    >>> f.close()
    >>> g.close()


Notes
~~~~~

**Line #3** Makes the CDMS module available.

**Line #4** Makes the Regridder class available from the regrid module.

**Line #5** Opens the input dataset.

**Line #6** Gets the variable object named ‘clt’. No data is read.

**Line #7** Gets the input grid.

**Line #8** Opens a dataset to retrieve the output grid.

**Line #9** The output grid is the grid associated with the variable named ‘ozone’ in dataset g. Just the grid is retrieved, not the data.

**Line #10** Generates a regridder function regridfunc.

**Line #11** Reads all data for variable cltf, and calls the regridder
function on that data, resulting in a transient variable cltnew.

SCRIP Horizontal Regridder
^^^^^^^^^^^^^^^^^^^^^^^^^^

To interpolate between grids where one or both grids is non-rectangular,
CDMS provides an interface to the SCRIP regridder package developed at
Los Alamos National Laboratory (https://oceans11.lanl.gov/trac/SCRIP). 

Figure 3 illustrates the process:

#. Obtain or generate the source and target grids in SCRIP netCDF
   format. A CDMS grid can be written to a netCDF file, in SCRIP format,
   using the write-ScripGrid method.
#. Edit the input namelist file scrip\_in to reference the grids and
   select the method of interpolation, either conservative, bilinear,
   bicubic, or distance-weighted. See the SCRIP documentation for
   detailed instructions.
#. Run the scrip executable to generate a remapping file containing the
   transformation coefficients.
#. CDMS, open the remapping file and create a regridder function with
   the readRegridder method.
#. Call the regridder function on the input variable, defined on the
   source grid. The return value is the variable interpolated to the new
   grid. Note that the variable may have more than two dimensions. Also
   note that the input arguments to the regridder function depend on the
   type of regridder. For example, the bicubic interpolation has
   additional arguments for the gradients of the variable.


Regridding Data with SCRIP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Example:**

Regrid data from a T42 to POP4/3 grid, using the first-order,
conservative interpolator.

In this example:

-  The input grid is defined in remap_grid_T42.nc.
-  The output grid is defined in remap_grid_POP43.nc.
-  The input data is variable src_array in file sampleT42Grid.nc.
-  The file scrip_in has contents:


::

    >>> &remap_inputs
    >>> num_maps = 1
    >>> 
    >>> grid1_file = 'remap_grid_T42.nc'
    >>> grid2_file = 'remap_grid_POP43.nc'
    >>> interp_file1 = 'rmp_T42_to_POP43_conserv.nc'
    >>> interp_file2 = 'rmp_POP43_to_T42_conserv.nc'
    >>> map1_name = 'T42 to POP43 Conservative Mapping'           
    >>> map2_name = 'POP43 to T42 Conservative Mapping'
    >>> map_method = 'conservative'
    >>> normalize_opt = 'frac'
    >>> output_opt = 'scrip'
    >>> restrict_type = 'latitude'
    >>> num_srch_bins = 90
    >>> luse_grid1_area = .false.
    >>> luse_grid2_area = .false.


``num_maps`` specifies the number of mappings generated, either 1 or 2.
For a single mapping, ``grid1_file`` and ``grid2_file`` are the source
and target grid definitions, respectively. The ``map_method`` specifies
the type of interpolation, either ‘conservative’, ‘bilinear’, ‘bicubic’,
or ‘distwgt’ (distanceweighted). The remaining parameters are described
in the SCRIP documentation.

Once the grids and input file are defined, run the scrip executable to
generate the remapping file ‘rmp\_T42\_to\_POP43\_conserv.nc’


::

    >>> % scrip
    >>> Using latitude bins to restrict search.
    >>>  Computing remappings between:
    >>> T42 Gaussian Grid
    >>>                                      and
    >>> POP 4/3 Displaced-Pole T grid
    >>> grid1 sweep
    >>> grid2 sweep
    >>> Total number of links = 63112


Next, run CDAT and create the regridder:

::

    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/remap_grid_POP43.nc"
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/remap_grid_T42.nc"
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/rmp_POP43_to_T42_conserv.nc"
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/rmp_T42_to_POP43_conserv.nc"
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/xieArkin-T42.nc"
    >>> # Import regrid package for regridder functions
    >>> import regrid2, cdms2
    >>> # Read the regridder from the remapper file
    >>> remapf = cdms2.open('rmp_T42_to_POP43_conserv.nc')
    >>> regridf = regrid2.readRegridder(remapf)
    >>> remapf.close()

Then read the input data and regrid:

::

    >>> # Get the source variable
    >>> f = cdms2.open('xieArkin-T42.nc')
    >>> t42prc = f('prc')
    >>> f.close()
    >>> # Regrid the source variable
    >>> popdat = regridf(t42prc)

Note that ``t42dat`` can have rank greater than 2. The trailing
dimensions must match the input grid shape. For example, if ``t42dat``
has shape (12, 64, 128), then the input grid must have shape (64,128).
Similarly if the variable had a generic grid with shape (8092,), the
last dimension of the variable would have length 8092.

Pressure-Level Regridder
^^^^^^^^^^^^^^^^^^^^^^^^

To regrid a variable which is a function of latitude, longitude,
pressure level, and (optionally) time to a new set of pressure levels,
use the ``pressureRegrid`` function defined for variables. This function
takes an axis representing the target set of pressure levels, and
returns a new variable ``d`` regridded to that dimension.

::

    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/ta_ncep_87-6-88-4.nc"
    >>> f=cdms2.open("ta_ncep_87-6-88-4.nc")
    >>> ta=f('ta')
    >>> ta.shape
    (11, 17, 73, 144)
    >>> ta.getAxisIds()
    ['time', 'level', 'latitude', 'longitude']
    >>> result = ta.pressureRegrid(cdms2.createAxis([1000.0]))
    >>> result.shape
    (11, 1, 73, 144)

Cross-Section Regridder
^^^^^^^^^^^^^^^^^^^^^^^

To regrid a variable which is a function of latitude, height, and
(optionally) time to a new latitude/height cross-section, use the
``crossSectionRegridder`` defined for variables. This function takes as
arguments the new latitudes and heights, and returns the variable
regridded to those axes.

::

    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/ta_ncep_87-6-88-4.nc"
    >>> f=cdms2.open("ta_ncep_87-6-88-4.nc")
    >>> ta=f('ta')
    >>> ta.shape
    (11, 17, 73, 144)
    >>> levOut=cdms2.createAxis([1000.0,950.])
    >>> levOut.designateLevel()
    >>> latOut=cdms2.createAxis(ta.getLatitude()[10:20])
    >>> latOut.designateLatitude()
    >>> ta0 = ta[0,:]
    >>> ta0.getAxisIds()
    ['level', 'latitude', 'longitude']
    >>> taout = ta0.crossSectionRegrid(levOut, latOut)
    >>> taout.shape
    (2, 10, 144)


Regrid Module
^^^^^^^^^^^^^

The ``regrid`` module implements the CDMS regridding functionality as
well as the SCRIP interface. Although this module is not strictly a part
of CDMS, it is designed to work with CDMS objects.

CDMS Horizontal Regridder
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    from regrid2 import Regridder

Makes the CDMS Regridder class available within a Python program. An
instance of Regridder is a function which regrids data from rectangular
input to output grids.

CDMS Regridder Constructor
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: 
   :header:  "Constructor", "Description"
   :widths:  50, 90
   :align: left

   "``regridFunction = Regridder(inputGrid, outputGrid)``", "Create a regridder function which interpolates a data array from input to output grid.
       * `CDMS regridder functions`_ describes the calling sequence of this function. 
       * ``inputGrid`` and ``outputGrid`` are CDMS grid objects.
       **Note:** To set the mask associated with inputGrid or outputGrid, use the grid setMask function."

SCRIP Regridder
^^^^^^^^^^^^^^^

SCRIP regridder functions are created with the ``regrid.readRegridder``
function:

SCRIP Regridder Constructor
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: 
   :header:  "Constructor", "Description"
   :widths:  80, 90
   :align: left

   "``regridFunction = regrid.readRegridder(fileobj, mapMethod=None, checkGrid=1)``", "Read a regridder from an open CDMS file object.
      * ``fileobj`` is a CDMS file object, as returned from ``cdms.open``.
      * ``mapMethod`` is one of:
           * ``'conservative'``: conservative remapper, suitable where area-integrated fields such as water or heat fluxes must be conserved.
           * ``'bilinear'``: bilinear interpolation
           * ``'bicubic'``: bicubic interpolation
           * ``'distwgt'``: distance-weighted interpolation.
      * It is only necessary to specify the map method if it is not defined in the file.
      * If ``checkGrid`` is 1 (default), the grid cells are checked for convexity, and 'repaired' if necessary.
      * Grid cells may appear to be nonconvex if they cross a ``0 / 2pi`` boundary. 
      * The repair consists of shifting the cell vertices to the same side modulo 360 degrees."

Regridder Functions
^^^^^^^^^^^^^^^^^^^

It is only necessary to specify the map method if it is not defined in
the file.

If ``checkGrid`` is 1 (default), the grid cells are checked for
convexity, and ‘repaired’ if necessary. Grid cells may appear to be
nonconvex if they cross a ``0 / 2pi`` boundary. The repair consists of
shifting the cell vertices to the same side modulo 360 degrees.

CDMS Regridder Functions
^^^^^^^^^^^^^^^^^^^^^^^^

A CDMS regridder function is an instance of the CDMS ``Regridder``
class. The function is associated with rectangular input and output
grids. Typically its use is straightforward:
  * The function is passed an input array and returns the regridded array.
    However, when the array has missing data, or the input and/or output 
    grids are masked, the logic becomes more complicated.

Step 1
~~~~~~

The regridder function first forms an input mask. This mask is either
two-dimensional or n-dimensional, depending on the rank of the
user-supplied mask. If no mask or missing value is specified, the mask
is obtained from the data array mask if present.

**Two-dimensional case:**

-  Let mask\_1 be the two-dimensional user mask supplied via the mask
   argument, or the mask of the input grid if no user mask is specified.
-  If a missing-data value is specified via the missing argument, let
   the implicit\_mask be the two-dimensional mask defined as 0 where the
   first horizontal slice of the input array is missing, 1 elsewhere.
-  The input mask is the logical AND(mask\_1, implicit\_mask)

**N-dimensional case:**

-  If the user mask is 3 or 4-dimensional with the same shape as the
   input array, it is used as the input mask.

Step 2
~~~~~~

The data is then regridded. In the two-dimensional case, the input mask
is ‘broadcast’ across the other dimensions of the array. In other words,
it assumes that all horizontal slices of the array have the same mask.
The result is a new array, defined on the output grid. Optionally, the
regridder function can also return an array having the same shape as the
output array, defining the fractional area of the output array which
overlaps a non-missing input grid cell. This is useful for calculating
area-weighted means of masked data.

Step 3
~~~~~~

Finally, if the output grid has a mask, it is applied to the result
array. Where the output mask is 0, data values are set to the missing
data value, or 1.0e20 if undefined. The result array or transient
variable will have a mask value of 1 (invalid value) for those output
grid cells which completely overlap input grid cells with missing values

CDMS Regridder Function
~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: 
   :header:  "Type", "Function", "Description"
   :widths:  40, 40, 80
   :align: left

   "Array or Transient-Variable", "``regridFunction(array, missing=None, order=None, mask=None)``", "Interpolate a gridded data array to a new grid.
     The interpolation preserves the area-weighted mean on each horizontal slice. If array is a Variable, a TransientVariable of  the same rank as the input array is returned, otherwise a masked array is returned.
       * ``array`` is a Variable, masked array, or Numpy array of rank 2, 3, or 4.
       *  For example, the string 'tzyx' indicates that the dimension order of ``array`` is (time, level, latitude, longitude).
       * If unspecified, the function assumes that the last two dimensions of ``array`` match the input grid.
       * ``missing`` is a Float specifying the missing data value. The default is 1.0e20.
       * ``order`` is a string indicating the order of dimensions of the array.  It has the form returned from ``variable.getOrder().``
       * ``mask`` is a Numpy array, of datatype Integer or Float, consisting of a fractional number between 0 and 1.
       * A value of 1 or 1.0 indicates that the corresponding data value is to be ignored for purposes of regridding.
       * A value of 0 or 0.0 indicates that the corresponding data value is valid. This is consistent with the convention for masks used by the MV2 module. 
       * A fractional value between 0.0 and 1.0 indicates the fraction of the data value (e.g., the corresponding cell) to be ignored when regridding. This is useful if a variable is regridded first to grid A and then to another grid B; the mask when regridding from A to B would be (1.0 - f) where f is the maskArray returned from the initial grid operation using the ``returnTuple`` argument.
       * If ``mask`` is two-dimensional of the same shape as the input grid, it overrides the mask of the input grid.  
       * If the ``mask`` has more than two dimensions, it must have the same shape as ``array``. In this case, the ``missing`` data value is also ignored. Such an ndimensional mask is useful if the pattern of missing data varies with level (e.g., ocean data) or time. 
       **Note:** If neither ``missing`` or ``mask`` is set, the default mask is obtained from the mask of the array if any."
   "Array, Array",  "``regridFunction(ar, missing=None, order=None, mask=None, returnTuple=1)``", "If called with the optional ``returnTuple`` argument equal to 1, the function returns a tuple ``dataArray``, ``maskArray``).
       * ``dataArray`` is the result data array.
       * ``maskArray`` is a Float32 array of the same shape as ``dataArray``, such that ``maskArray[i,j]`` is fraction of the output grid cell [i,j] overlapping a non-missing cell of the grid."

SCRIP Regridder Functions
^^^^^^^^^^^^^^^^^^^^^^^^^

A SCRIP regridder function is an instance of the ScripRegridder class.
Such a function is created by calling the regrid.readRegridder method.
Typical usage is straightforward:

::

    >>> import cdms2
    >>> import regrid2
    >>> remapf = cdms2.open('rmp_T42_to_POP43_conserv.nc')
    >>> regridf = regrid2.readRegridder(remapf)
    >>> f = cdms2.open('xieArkin-T42.nc')
    >>> t42prc = f('prc')
    >>> f.close()
    >>> # Regrid the source variable
    >>> popdat = regridf(t42prc)



The bicubic regridder takes four arguments:

::

    >>> # outdat = regridf(t42prc, gradlat, gradlon, gradlatlon)


A regridder function also has associated methods to retrieve the
following fields:

-  Input grid
-  Output grid
-  Source fraction: the fraction of each source (input) grid cell
   participating in the interpolation.
-  Destination fraction: the fraction of each destination (output) grid
   cell participating in the interpolation.

In addition, a conservative regridder has the associated grid cell areas
for source and target grids.

SCRIP Regridder Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: 
   :header:  "Return Type", "Method", "Description"
   :widths:  40, 40, 80
   :align: left

    "Array or Transient-Variable", "[conservative, bilinear, and distance-weighted regridders] ``regridFunction(array)``", "Interpolate a gridded data array to a new grid. 
    The return value is the regridded data variable. 
       * ``array`` is a Variable, MaskedArray, or Numpy array.
       * The rank of the array may be greater than the rank of the input grid, in which case the input grid shape must match a trailing portion of the array shape. 
       * For example, if the input grid is curvilinear with shape (64,128), the last two dimensions of the array must match. 
       * Similarly, if the input grid is generic with shape (2560,), the last dimension of the array must have that length."
    "Array or Transient-Variable", "[bicubic regridders] ``regridFunction(array, gradientLat, gradientLon, gradientLatLon)``", "Interpolate a gridded data array to a new grid, using a bicubic regridder. 
    The return value is the regridded data variable.
       * ``array`` is a Variable, MaskedArray, or Numpy array. 
       * The rank of the array may be greater than the rank of the input grid, in which case the input grid shape must match a trailing portion of the array shape. 
       * For example, if the input grid is curvilinear with shape (64,128), the last two dimensions of the array must match. 
       * Simiarly, if the input grid is generic with shape (2560,), the last dimension of the array must have that length.
       * ``gradientLat``: df/di (see the SCRIP documentation). Same shape as ``array``.
       * ``gradientLon``: df/dj. Same shape as ``array``.
       * ``gradientLatLon``: d(df)/(di)(dj). Same shape as array."
    "Numpy array", "``getDestinationArea()`` [conservative regridders only]", "Return the area of the destination (output) grid cell. 
       * The array is 1-D, with length equal to the number of cells in the output grid."
    "Numpy array", "``getDestinationFraction()``", "Return the area fraction of the destination (output) grid cell that participates in the regridding. 
       * The array is 1-D, with length equal to the number of cells in the output grid."
    "CurveGrid or Generic-Grid", "``getInputGrid()``", "Return the input grid, or None if no input grid is associated with the regridder."
    "CurveGrid or Generic-Grid", "``getOutputGrid()``", "Return the output grid."
    "Numpy array", "``getSourceFraction()``", "Return the area fraction of the source (input) grid cell that participates in the regridding. 
       * The array is 1-D, with length equal to the number of cells in the input grid"

Examples
^^^^^^^^

CDMS Regridder
~~~~~~~~~~~~~~

**Example:**

Regrid data to a uniform output grid.

::

    
    >>> import cdms2
    >>> from regrid2 import Regridder
    >>> f = cdms2.open('clt.nc')
    >>> cltf = f.variables['clt']
    >>> ingrid = cltf.getGrid()
    >>> outgrid = cdms2.createUniformGrid(90.0, 46, -4.0, 0.0, 72, 5.0)
    >>> regridFunc = Regridder(ingrid, outgrid)
    >>> newrls = regridFunc(cltf)
    >>> f.close()

Regridder Constructure
~~~~~~~~~~~~~~~~~~~~~~

.. csv-table::
   :header:  "Line", "Notes"
   :widths:  8, 45

   "3", "Open a netCDF file for input."
   "6", "Create a 4 x 5 degree output grid. Note that this grid is not associated with a file or dataset."
   "7", "Create the regridder function."
   "8", "Read all data and regrid. The missing data value is obtained from variable rlsf"

Return the area fraction of the source (input) grid cell that
participates in the regridding. The array is 1-D, with length equal to
the number of cells in the input grid.

**Example:**

Get a mask from a separate file, and set as the input grid mask.

::

    >>> # wget http://cdat.llnl.gov/cdat/sample_data/clt.nc
    >>> # wget http://cdat.llnl.gov/cdat/sample_data/geos5-sample.nc
    >>> import cdms2
    >>> from regrid2 import Regridder
    >>> #
    >>> f = cdms2.open('clt.nc')
    >>> cltf = f.variables['clt']
    >>> outgrid = cltf.getGrid()
    >>> g = cdms2.open('geos5-sample.nc')
    >>> ozoneg = g.variables['ozone']
    >>> ingrid = ozoneg.getGrid()
    >>> regridFunc = Regridder(ingrid,outgrid)
    >>> uwmaskvar = g.variables['uwnd']
    >>> uwmask = uwmaskvar[:]<0
    >>> outArray = regridFunc(ozoneg.subSlice(time=0),mask=uwmask)
    >>> f.close()
    >>> g.close()

.. csv-table::
   :header:  "Line", "Notes"
   :widths:  8, 45

   "7", "Get the input grid."
   "10", "Get the output grid."
   "11", "Create the regridder function."
   "14", "Get the mask."
   "15", "Regrid with a user mask. The subslice call returns a transient variable corresponding to variables of at time 0."


**Note:** Although it cannot be determined from the code, both mask and
the input arrays of are four-dimensional. This is the n-dimensional
case.


**Example:**

Generate an array of zonal mean values.


::

    >>> f = cdms.open(‘rls_ccc_per.nc’)
    >>> rlsf = f.variables[‘rls’]
    >>> ingrid = rlsf.getGrid()
    >>> outgrid = cdms.createZonalGrid(ingrid)
    >>> regridFunc = Regridder(ingrid,outgrid)
    >>> mean = regridFunc(rlsf)
    >>> f.close()


.. csv-table::
   :header:  "Line", "Notes"
   :widths:  8, 45

   "3", "Open a netCDF file for inputGet the input grid. Return the area fraction of the source (input) grid cell that participates in the regridding. The array is 1-D, with length equal to the number of cells in the input grid."
   "4", "Create a zonal grid. outgrid has the same latitudes as ingrid, and a singleton longitude dimension. createGlobalMeanGrid could be used here to generate a global mean array."
   "5", "Generate the regridder function."
   "6", "Generate the zonal mean array."

**Example:**

Regrid an array with missing data, and calculate the area-weighted mean
of the result.

:: 

   >>> import cdms2
   >>> from cdms2.MV2 import *
   >>> from regrid2 import Regridder
   >>> f = cdms2.open("ta_ncep_87-6-88-4.nc")
   >>> var = f('ta')
   >>> outgrid = cdms2.createUniformGrid(90.0, 46, -4.0, 0.0, 72, 5.0)
   >>> outlatw, outlonw = outgrid.getWeights()
   >>> outweights = outerproduct(outlatw, outlonw)
   >>> grid = var.getGrid()
   >>> sample = var[0,0]
   >>> latw, lonw = grid.getWeights()
   >>> weights = outerproduct(latw, lonw)
   >>> inmask = where(greater(absolute(sample),1.e15),0,1)
   >>> mean = add.reduce(ravel(inmask*weights*sample))/add.reduce(ravel(inmask*weights))
   >>> regridFunc = Regridder(grid, outgrid)
   >>> outsample, outmask = regridFunc(sample, mask=inmask, returnTuple=1)
   >>> outmean = add.reduce(ravel(outmask*outweights*outsample)) / add.reduce(ravel(outmask*outweights))


.. csv-table::
   :header:  "Line", "Notes"
   :widths:  8, 45

   "2", "Create a uniform target grid."
   "3", "Get the latitude and longitude weights."
   "4", "Generate a 2-D weights array."
   "5", "Get the input grid. ``var`` is a 4-D variable."
   "6", "Get the first horizontal slice from ``var``."
   "7-8", "Get the input weights, and generate a 2-D weights array."
   "9", "Set the 2-D input mask."
   "10", "Calculate the input array area-weighted mean."
   "11", "Create the regridder function."
   "12", "Regrid. Because returnTuple is set to 1, the result is a tuple (dataArray, maskArray)."
   "13", "Calculate the area-weighted mean of the regridded data. mean and outmean should be approximately equal."


SCRIP Regridder
~~~~~~~~~~~~~~~

**Example:**

Regrid from a curvilinear to a generic grid, using a conservative
remapping. Compute the area-weighted means on input and output for
comparison.

::

    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/remap_grid_T42.nc"
    >>> # wget http://cdat.llnl.gov/cdat/sample_data/rmp_T42_to_C02562_conserv.nc
    >>> # wget "http://cdat.llnl.gov/cdat/sample_data/xieArkin-T42.nc"
    >>> import cdms2, regrid2, MV2
    >>> # Open the SCRIP remapping file and data file
    >>> fremap = cdms2.open('rmp_T42_to_C02562_conserv.nc')
    >>> fdat = cdms2.open('xieArkin-T42.nc')
    >>> # Input data array
    >>> dat = fdat('prc')[0,:]
    >>> # Read the SCRIP regridder
    >>> regridf = regrid2.readRegridder(fremap)
    >>> # Regrid the variable
    >>> outdat = regridf(dat)
    >>> # Get the cell area and fraction arrays. Areas are computed only
    >>> # for conservative regridding.
    >>> srcfrac = regridf.getSourceFraction()
    >>> srcarea = regridf.getSourceArea()
    >>> dstfrac = regridf.getDestinationFraction()
    >>> dstarea = regridf.getDestinationArea()
    >>> # calculate area-weighted means
    >>> inmean = MV2.sum(srcfrac*srcarea*MV2.ravel(dat)) / MV2.sum(srcfrac*srcarea)
    >>> outmean = MV2.sum(dstfrac*dstarea*MV2.ravel(outdat)) / MV2.sum(dstfrac*dstarea)
    >>> print 'Input mean:', inmean
    Input mean: 2.60376502339
    >>> print 'Output mean:', outmean
    Output mean: 2.60376502339
    >>> fremap.close()
    >>> fdat.close()





