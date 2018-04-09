Plotting CDMS data in Python
----------------------------

Overview
~~~~~~~~

Data read via the CDMS Python interface can be plotted using the ``vcs``
module. This module, part of the Climate Data
Analysis Tool (CDAT) is documented in the CDAT reference manual.
The ``vcs`` module provides access to the functionality of the VCS
visualization program.

Examples of plotting data accessed from CDMS are given below, as well as
documentation for the plot routine keywords.

Examples
~~~~~~~~

In the following examples, it is assumed that variable ``psl`` is
dimensioned (time, latitude, longitude). ``psl`` is contained in the
dataset named ``'sample.xml'``.

Plotting a Gridded Variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^
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



.. doctest:: Example: plotting a gridded variable

    >>> import cdms2, vcs 
    >>> f = cdms2.open("clt.nc") 
    >>> clt = f.variables['clt'] 
    >>> sample = clt[0,:] 
    >>> w=vcs.init() 
    >>> w.plot(sample) 
    <vcs.displayplot.Dp object ...>
    >>> f.close() 

**Notes:**

.. csv-table::  
   :header:  "Line", "Notes"
   :widths:  10, 90

   "3","Get a horizontal slice, for the first time point."
   "4","Create a VCS Canvas ``w``."   
   "5", "Plot the data.  Because sample is a transient variable, it encapsulates all the time, latitude, longitude, and attribute information."
   "7", "Close the file.  This must be done after the reference to the persistent variable ``ps l``."

Thats it! The axis coordinates, variable name, description, units, etc.
are obtained from variable sample.

What if the units are not explicitly defined for ``clt``, or a different
description is desired? ``plot`` has a number of other keywords which
fill in the extra plot information.

Using A Plot Keywords
^^^^^^^^^^^^^^^^^^^^^

.. doctest::

    >>> import cdms2, vcs 
    >>> f = cdms2.open("clt.nc") 
    >>> clt = f.variables['clt'] 
    >>> sample = clt[0,:] 
    >>> w=vcs.init() 
    >>> w.plot(sample, units='percent', file_comment='', long_name="Total Cloud", comment1="Example plot", hms="00:00:00", ymd="1979/01/01") 
    <vcs.displayplot.Dp object ...>
    >>> f.close() 


**Note:** Keyword arguments can be listed in any order.

Plotting a Time-Latitude Slice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming that variable ``clt`` has domain ``(time,latitude,longitude)``,
this example selects and plots a time-latitude slice:

.. doctest::

    >>> import cdms2, vcs 
    >>> f = cdms2.open("clt.nc") 
    >>> clt = f.variables['clt'] 
    >>> samp = clt[:,:,0] 
    >>> w = vcs.init() 
    >>> w.plot(samp, name='Total Cloudiness') 
    <vcs.displayplot.Dp object ...>


.. csv-table:: 
  :header:  "Line", "Notes"
  :widths:  10, 90

  "4", "``samp`` is a slice of ``clt``, at index ``0`` of the last dimension.  Since ``samp`` was obtained from the slice operator, it is a transient variable, which includes the latitude and time information."
  "6", "The ``name`` keyword defines the identifier, default is the name found in the file."

Plotting Subsetted Data
^^^^^^^^^^^^^^^^^^^^^^^

Calling the variable ``clt`` as a function reads a subset of the
variable. The result variable ``samp`` can be plotted directly:

.. doctest::

    >>> import cdms2, vcs 
    >>> f = cdms2.open("clt.nc")
    >>> clt = f.variables['clt']
    >>> samp = clt(time = (0.0,100.0), longitude = 180.0, squeeze=1)
    >>> w = vcs.init()
    >>> w.plot(samp)
    <vcs.displayplot.Dp object ...>
    >>> f.close()


Plot Method
~~~~~~~~~~~

The ``plot`` method is documented in the CDAT Reference Manual. This
section augments the documentation with a description of the optional
keyword arguments. The general form of the plot command is:

``canvas.plot(array [, args] [,key=value [, key=value [, ...] ] ])``

where:

-  canvas is a VCS Canvas object, created with the vcs.init method.

-  array is a variable, masked array, or Numpy array having between
   two and five dimensions. The last dimensions of the array is termed
   the 'x' dimension, the next-to-last the 'y' dimension, then 'z', 't',
   and 'w'. For example, if array is three-dimensional, the axes are
   (z,y,x), and if array is four-dimensional, the axes are (t,z,y,x).
   (Note that the t dimension need have no connection with time; any
   spatial axis can be mapped to any plot dimension. For a graphics
   method which is two-dimensional, such as boxfill, the y-axis is
   plotted on the horizontal, and the x-axis on the vertical.

   If array is a gridded variable on a rectangular grid, the plot
   function uses a box-fill graphics method. If it is non-rectangular,
   the meshfill graphics method is used.

   Note that some plot keywords apply only to rectangular grids only.

-  args are optional positional arguments:

   ``args`` := template\_name, graphics\_method, graphics\_name

   ``template_name``: the name of the VCS template (e.g., 'AMIP')

   ``graphics_method``: the VCS graphics method (boxfill)

   ``graphics_name``: the name of the specific graphics method
   ('default')

   See the CDAT Reference Manual and VCS Reference Manual for a
   detailed description of these arguments.

-  ``key=value``, ... are optional keyword/value pairs, listed in any
   order. These are defined in the table below.

Table Plot Keywords
^^^^^^^^^^^^^^^^^^^

.. csv-table::
    :header: "Key", "Type", "Value"
    :widths: 20, 20, 80

    "``comment1``", "string", "Comment plotted above ``file_comment``"
    "``comment2``", "string", "Comment plotted above ``comment1``"
    "``comment3``", "string", "Comment plotted above ``comment2``"
    "``continents``", "0 or 1", "if ``1``, plot continental outlines (default:plot if ``xaxis`` is longitude, ``yaxis`` is latitude -or- ``xname`` is 'longitude' and ``yname`` is 'latitude'"
    "``file_comment``", "string", "Comment, defaults to ``variable.parent.comment``"
    "``grid``", "CDMS grid object", "Grid associated with the data. Defaults to ``variable.getGrid()``"
    "``hms``", "string", "Hour, minute, second"
    "``long_name``", "string", "Descriptive variable name, defaults to ``variable.long_name``."
    "``missing_value``", "same type as array", "Missing data value, defaults to ``variable.getMissing()``"
    "``name``", "string", "Variable name, defaults to ``variable.id``"
    "``time``", "cdtime relative or absolute", "Time associated with the data."
    ,,"Example:"
    ,,"- ``cdtime.reltime(30.0, 'days since 1978-1-1').``"
    "``units``", "string",  "Data units. Defaults to ``variable.units``"
    "``variable``", "CDMS variable object", "Variable associated with the data. The variable grid must have the same shape as the data array."
    "``xarray`` (``[y|z|t|w]array``)", "1-D Numpy array", "*Rectangular grids only*. Array of coordinate values, having the same length as the corresponding dimension. Defaults to ``xaxis[:\] (y|z|t|waxis[:])``"
    "``xaxis`` (``[y|z|t|w]axis``)", "CDMS axis object", "*Rectangular grids only*. Axis object. ``xaxis`` defaults to ``grid.getAxis(0)``, ``yaxis`` defaults to ``grid.getAxis(1)``"
    "``xbounds`` (``ybounds``)", "2-D Numpy array",  "*Rectangular grids only*. Boundary array of shape ``(n,2)`` where ``n`` is the axis length. Defaults to ``xaxis.getBounds()``, or ``xaxis.genGenericBounds()`` if ``None``, similarly for ``ybounds``."

    "``xname`` (``[y|z|t|w]name``)", "string", "*Rectangular grids only*. Axis name. Defaults to ``xaxis.id`` (``[y|z|t|w]axis.id``)"
    "``xrev`` (``yrev``)", "0 or 1", "If ``xrev`` (``yrev``) is 1, reverse the direction of the ``x-axis (y-axis)``. Defaults to 0, with the following exceptions:"
    ,,"- If the ``y-axis`` is latitude, and has decreasing values, ``yrev`` defaults to 1"
    ,,"- If the ``y-axis`` is a vertical level, and has increasing pressure levels, ``yrev`` defaults to 1."

    "``xunits`` (``[y|z|t|w]units``)", "string", "*Rectangular grids only*. Axis units. Defaults to ``xaxis.units`` (``[y|z|t|w]axis.units``)."




b
