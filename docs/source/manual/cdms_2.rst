CHAPTER 2 CDMS Python Application Programming Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2.1 Overview
^^^^^^^^^^^^

This chapter describes the CDMS Python application programming interface
(API). Python is a popular public-domain, object-oriented language. Its
features include support for object-oriented development, a rich set of
programming constructs, and an extensible architecture. CDMS itself is
implemented in a mixture of C and Python. In this chapter the assumption
is made that the reader is familiar with the basic features of the
Python language.

Python supports the notion of a module, which groups together associated
classes and methods. The import command makes the module accessible to
an application. This chapter documents the cdms, cdtime, and regrid
modules.

The chapter sections correspond to the CDMS classes. Each section
contains tables base. If no parent, the datapath is absolute.describing
the class internal (non-persistent) attributes, constructors (functions
for creating an object), and class methods (functions). A method can
return an instance of a CDMS class, or one of the Python types:

Table 2.1 Python types used in CDMS
                                   

+-------+--------------+
| Type  | Description  |
+=======+==============+
| Array | Numeric or   |
|       | masked       |
|       | multidimensi |
|       | onal         |
|       | data array.  |
|       | All elements |
|       | of the array |
|       | are of the   |
|       | same type.   |
|       | Defined in   |
|       | the Numeric  |
|       | and MA       |
|       | modules.     |
+-------+--------------+
| Compt | Absolute     |
| ime   | time value,  |
|       | a time with  |
|       | representati |
|       | on           |
|       | (year,       |
|       | month, day,  |
|       | hour,        |
|       | minute,      |
|       | second).     |
|       | Defined in   |
|       | the cdtime   |
|       | module. cf.  |
|       | reltime      |
+-------+--------------+
| Dicti | An unordered |
| onary | 2,3collectio |
|       | n            |
|       | of objects,  |
|       | indexed by   |
|       | key. All     |
|       | dictionaries |
|       | in CDMS are  |
|       | indexed by   |
|       | strings,     |
|       | e.g.:        |
|       | ``axes['time |
|       | ']``         |
+-------+--------------+
| Float | Floating-poi |
|       | nt           |
|       | value.       |
+-------+--------------+
| Integ | Integer      |
| er    | value.       |
+-------+--------------+
| List  | An ordered   |
|       | sequence of  |
|       | objects,     |
|       | which need   |
|       | not be of    |
|       | the same     |
|       | type. New    |
|       | members can  |
|       | be inserted  |
|       | or appended. |
|       | Lists are    |
|       | denoted with |
|       | square       |
|       | brackets,    |
|       | e.g.,        |
|       | ``[1, 2.0, ' |
|       | x', 'y']``   |
+-------+--------------+
| None  | No value     |
|       | returned.    |
+-------+--------------+
| Relti | Relative     |
| me    | time value,  |
|       | a time with  |
|       | representati |
|       | on           |
|       | (value,      |
|       | units since  |
|       | basetime).   |
|       | Defined in   |
|       | the cdtime   |
|       | module. cf.  |
|       | comptime     |
+-------+--------------+
| Tuple | An ordered   |
|       | sequence of  |
|       | objects,     |
|       | which need   |
|       | not be of    |
|       | the same     |
|       | type. Unlike |
|       | lists,       |
|       | tuples       |
|       | elements     |
|       | cannot be    |
|       | inserted or  |
|       | appended.    |
|       | Tuples are   |
|       | denoted with |
|       | parentheses, |
|       | e.g.,        |
|       | ``(1, 2.0, ' |
|       | x', 'y')``   |
+-------+--------------+

2.2 A first example
^^^^^^^^^^^^^^^^^^^

The following Python script reads January and July monthly temperature
data from an input dataset, averages over time, and writes the results
to an output file. The input temperature data is ordered (time,
latitude, longitude).

{% highlight python %} 1 #!/usr/bin/env python 2 import cdms 3 from cdms
import MV 4 jones = cdms.open('/pcmdi/cdms/obs/jones\_mo.nc') 5 tasvar =
jones['tas'] 6 jans = tasvar[0::12] 7 julys = tasvar[6::12] 8 janavg =
MV.average(jans) 9 janavg.id = "tas\_jan" 10 janavg.long\_name = "mean
January surface temperature" 11 julyavg = MV.average(julys) 12
julyavg.id = "tas\_jul" 13 julyavg.long\_name = "mean July surface
temperature" 14 out = cdms.open('janjuly.nc','w') 15 out.write(janavg)
16 out.write(julyavg) 17 out.comment = "Average January/July from Jones
dataset" 18 jones.close() 19 out.close() {% endhighlight %}

+-------+--------+
| Line  | Notes  |
+=======+========+
| 2,3   | Makes  |
|       | the    |
|       | CDMS   |
|       | and MV |
|       | module |
|       | s      |
|       | availa |
|       | ble.   |
|       | MV     |
|       | define |
|       | s      |
|       | arithm |
|       | etic   |
|       | functi |
|       | ons.   |
+-------+--------+
| 4     | Opens  |
|       | a      |
|       | netCDF |
|       | file   |
|       | read-o |
|       | nly.   |
|       | The    |
|       | result |
|       | jones  |
|       | is a   |
|       | datase |
|       | t      |
|       | object |
|       | .      |
+-------+--------+
| 5     | Gets   |
|       | the    |
|       | surfac |
|       | e      |
|       | air    |
|       | temper |
|       | ature  |
|       | variab |
|       | le.    |
|       | 'tas'  |
|       | is the |
|       | name   |
|       | of the |
|       | variab |
|       | le     |
|       | in the |
|       | input  |
|       | datase |
|       | t.     |
|       | This   |
|       | does   |
|       | not    |
|       | actual |
|       | ly     |
|       | read   |
|       | the    |
|       | data.  |
+-------+--------+
| 6     | Read   |
|       | all    |
|       | Januar |
|       | y      |
|       | monthl |
|       | y      |
|       | mean   |
|       | data   |
|       | into a |
|       | variab |
|       | le     |
|       | jans.  |
|       | Variab |
|       | les    |
|       | can be |
|       | sliced |
|       | like   |
|       | arrays |
|       | .      |
|       | The    |
|       | slice  |
|       | operat |
|       | or     |
|       | [0::12 |
|       | ]      |
|       | means  |
|       | take   |
|       | every  |
|       | 12th   |
|       | slice  |
|       | from   |
|       | dimens |
|       | ion    |
|       | 0,     |
|       | starti |
|       | ng     |
|       | at     |
|       | index  |
|       | 0 and  |
|       | ending |
|       | at the |
|       | last   |
|       | index. |
|       | If the |
|       | stride |
|       | 12     |
|       | were   |
|       | omitte |
|       | d,     |
|       | it     |
|       | would  |
|       | defaul |
|       | t      |
|       | to 1.  |
|       | Note   |
|       | that   |
|       | the    |
|       | variab |
|       | le     |
|       | is     |
|       | actual |
|       | ly     |
|       | 3-dime |
|       | nsiona |
|       | l.     |
|       | Since  |
|       | no     |
|       | slice  |
|       | is     |
|       | specif |
|       | ied    |
|       | for    |
|       | the    |
|       | second |
|       | or     |
|       | third  |
|       | dimens |
|       | ions,  |
|       | all    |
|       | values |
|       | of     |
|       | those  |
|       | 2,3    |
|       | dimens |
|       | ions   |
|       | are    |
|       | retrie |
|       | ved.   |
|       | The    |
|       | slice  |
|       | operat |
|       | ion    |
|       | could  |
|       | also   |
|       | have   |
|       | been   |
|       | writte |
|       | n      |
|       | [0::12 |
|       | ,      |
|       | : ,    |
|       | :].    |
|       | Also   |
|       | note   |
|       | that   |
|       | the    |
|       | same   |
|       | script |
|       | works  |
|       | for    |
|       | multi- |
|       | file   |
|       | datase |
|       | ts.    |
|       | CDMS   |
|       | opens  |
|       | the    |
|       | needed |
|       | data   |
|       | files, |
|       | extrac |
|       | ts     |
|       | the    |
|       | approp |
|       | riate  |
|       | slices |
|       | ,      |
|       | and    |
|       | concat |
|       | enates |
|       | them   |
|       | into   |
|       | the    |
|       | result |
|       | array. |
+-------+--------+
| 7     | Reads  |
|       | all    |
|       | July   |
|       | data   |
|       | into a |
|       | masked |
|       | array  |
|       | julys. |
+-------+--------+
| 8     | Calcul |
|       | ate    |
|       | the    |
|       | averag |
|       | e      |
|       | Januar |
|       | y      |
|       | value  |
|       | for    |
|       | each   |
|       | grid   |
|       | zone.  |
|       | Any    |
|       | missin |
|       | g      |
|       | data   |
|       | is     |
|       | handle |
|       | d      |
|       | automa |
|       | ticall |
|       | y.     |
+-------+--------+
| 9,10  | Set    |
|       | the    |
|       | variab |
|       | le     |
|       | id and |
|       | long\_ |
|       | name   |
|       | attrib |
|       | utes.  |
|       | The id |
|       | is     |
|       | used   |
|       | as the |
|       | name   |
|       | of the |
|       | variab |
|       | le     |
|       | when   |
|       | plotte |
|       | d      |
|       | or     |
|       | writte |
|       | n      |
|       | to a   |
|       | file.  |
+-------+--------+
| 14    | Create |
|       | a new  |
|       | netCDF |
|       | output |
|       | file   |
|       | named  |
|       | 'janju |
|       | ly.nc' |
|       | to     |
|       | hold   |
|       | the    |
|       | result |
|       | s.     |
+-------+--------+
| 15    | Write  |
|       | the    |
|       | Januar |
|       | y      |
|       | averag |
|       | e      |
|       | values |
|       | to the |
|       | output |
|       | file.  |
|       | The    |
|       | variab |
|       | le     |
|       | will   |
|       | have   |
|       | id     |
|       | "tas\_ |
|       | jan"   |
|       | in the |
|       | file.  |
|       | ``writ |
|       | e``    |
|       | is a   |
|       | utilit |
|       | y      |
|       | functi |
|       | on     |
|       | which  |
|       | create |
|       | s      |
|       | the    |
|       | variab |
|       | le     |
|       | in the |
|       | file,  |
|       | then   |
|       | writes |
|       | data   |
|       | to the |
|       | variab |
|       | le.    |
|       | A more |
|       | genera |
|       | l      |
|       | method |
|       | of     |
|       | data   |
|       | output |
|       | is     |
|       | first  |
|       | to     |
|       | create |
|       | a      |
|       | variab |
|       | le,    |
|       | then   |
|       | set a  |
|       | slice  |
|       | of the |
|       | variab |
|       | le.    |
|       | Note   |
|       | that   |
|       | janavg |
|       | and    |
|       | julavg |
|       | have   |
|       | the    |
|       | same   |
|       | latitu |
|       | de     |
|       | and    |
|       | longit |
|       | ude    |
|       | inform |
|       | ation  |
|       | as     |
|       | tasvar |
|       | .      |
|       | It is  |
|       | carrie |
|       | d      |
|       | along  |
|       | with   |
|       | the    |
|       | comput |
|       | ations |
|       | .      |
+-------+--------+
| 17    | Set    |
|       | the    |
|       | global |
|       | attrib |
|       | ute    |
|       | 'comme |
|       | nt'.   |
+-------+--------+
| 18    | Close  |
|       | the    |
|       | output |
|       | file.  |
+-------+--------+

2.3 cdms module
^^^^^^^^^^^^^^^

The cdms module is the Python interface to CDMS. The objects and methods
in this chapter are made accessible with the command:

{% highlight python %} import cdms {% endhighlight %}

The functions described in this section are not associated with a class.
Rather, they are called as module functions, e.g.,

{% highlight python %} file = cdms.open('sample.nc') {% endhighlight %}

Table 2.2 cdms module functions
                               

.. raw:: html

   <table class="table">

.. raw:: html

   <tr>

::

    <th>Type</th>

    <th>Definition</th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Variable

.. raw:: html

   </td>

.. raw:: html

   <td>

asVariable(s): Transform s into a transient variable. s is a masked
array, Numeric array, or Variable. If s is already a transient variable,
s is returned. See also: isVariable.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Axis

.. raw:: html

   </td>

.. raw:: html

   <td>

createAxis(data, bounds=None): Create a one-dimensional coordinate Axis,
which is not associated with a file or dataset. This is useful for
creating a grid which is not contained in a file or dataset. data is a
one-dimensional, monotonic Numeric array. bounds is an array of shape
(len(data),2), such that for all i, data[i] is in the range
[bounds[i,0],bounds[i,1] ]. If bounds is not specified, the default
boundaries are generated at the midpoints between the consecutive data
values, provided that the autobounds mode is 'on' (the default). See
setAutoBounds. Also see: CdmsFile.createAxis

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Axis

.. raw:: html

   </td>

.. raw:: html

   <td>

createEqualAreaAxis(nlat): Create an equal-area latitude axis. The
latitude values range from north to south, and for all axis values x[i],
sin(x[i])sin(x[i+1]) is constant. nlat is the axis length. The axis is
not associated with a file or dataset.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Axis

.. raw:: html

   </td>

.. raw:: html

   <td>

createGaussianAxis(nlat): Create a Gaussian latitude axis. Axis values
range from north to south. nlat is the axis length. The axis is not
associated with a file or dataset.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

RectGrid

.. raw:: html

   </td>

.. raw:: html

   <td>

createGaussianGrid(nlats, xorigin=0.0, order="yx"): Create a Gaussian
grid, with shape (nlats, 2\*nlats). nlats is the number of latitudes.
xorigin is the origin of the longitude axis. order is either "yx"
(lat-lon, default) or "xy" (lon-lat)

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

RectGrid

.. raw:: html

   </td>

.. raw:: html

   <td>

createGenericGrid(latArray, lonArray, latBounds=None, lonBounds=None,
order="yx", mask=None): Create a generic grid, that is, a grid which is
not typed as Gaussian, uniform, or equal-area. The grid is not
associated with a file or dataset. latArray is a NumPy array of latitude
values. lonArray is a NumPy array of longitude values. latBounds is a
NumPy array having shape (len(latArray),2), of latitude boundaries.
lonBounds is a NumPy array having shape (len(lonArray),2), of longitude
boundaries. order is a string specifying the order of the axes, either
"yx" for (latitude, longitude), or "xy" for the reverse. mask (optional)
is an integer-valued NumPy mask array, having the same shape and
ordering as the grid.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

RectGrid

.. raw:: html

   </td>

.. raw:: html

   <td>

createGlobalMeanGrid(grid): Generate a grid for calculating the global
mean via a regridding operation. The return grid is a single zone
covering the range of the input grid. grid is a RectGrid.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

RectGrid

.. raw:: html

   </td>

.. raw:: html

   <td>

createRectGrid(lat, lon, order, type="generic", mask=None): Create a
rectilinear grid, not associated with a file or dataset. This might be
used as the target grid for a regridding operation. lat is a latitude
axis, created by cdms.createAxis. lon is a longitude axis, created by
cdms.createAxis. order is a string with value "yx" (the first grid
dimension is latitude) or "xy" (the first grid dimension is longitude).
type is one of 'gaussian','uniform','equalarea',or 'generic'. If
specified, mask is a two-dimensional, logical Numeric array (all values
are zero or one) with the same shape as the grid.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

RectGrid

.. raw:: html

   </td>

.. raw:: html

   <td>

createUniformGrid(startLat, nlat, deltaLat, start-Lon, nlon, deltaLon,
order="yx", mask=None): Create a uniform rectilinear grid. The grid is
not associated with a file or dataset. The grid boundaries are at the
midpoints of the axis values. startLat is the starting latitude value.
nlat is the number of latitudes. If nlat is 1, the grid latitude
boundaries will be startLat +/- deltaLat/2. deltaLat is the increment
between latitudes. startLon is the starting longitude value. nlon is the
number of longitudes. If nlon is 1, the grid longitude boundaries will
be startLon +/- deltaLon/2. deltaLon is the increment between
longitudes. order is a string with value "yx" (the first grid dimension
is latitude) or "xy" (the first grid dimension is longitude). If
specified, mask is a two-dimensional, logical Numeric array (all values
are zero or one) with the same shape as the grid.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Axis

.. raw:: html

   </td>

.. raw:: html

   <td>

createUniformLatitudeAxis(startLat, nlat, deltaLat): Create a uniform
latitude axis. The axis boundaries are at the midpoints of the axis
values. The axis is designated as a circular latitude axis. startLat is
the starting latitude value. nlat is the number of latitudes. deltaLat
is the increment between latitudes.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

RectGrid

.. raw:: html

   </td>

.. raw:: html

   <td>

createZonalGrid(grid): Create a zonal grid. The output grid has the same
latitude as the input grid, and a single longitude. This may be used to
calculate zonal averages via a regridding operation. grid is a RectGrid.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Axis

.. raw:: html

   </td>

.. raw:: html

   <td>

createUniformLongitudeAxis(startLon, nlon, delta-Lon): Create a uniform
longitude axis. The axis boundaries are at the midpoints of the axis
values. The axis is designated as a circular longitude axis. startLon is
the starting longitude value. nlon is the number of longitudes. deltaLon
is the increment between longitudes.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Variable

.. raw:: html

   </td>

.. raw:: html

   <td>

createVariable(array, typecode=None, copy=0, savespace=0, mask=None,
fill\_value=None, grid=None, axes=None, attributes=None, id=None): This
function is documented in Table 2.34 on page 90.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Integer

.. raw:: html

   </td>

.. raw:: html

   <td>

getAutoBounds(): Get the current autobounds mode. Returns 0, 1, or 2.
See setAutoBounds.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Integer

.. raw:: html

   </td>

.. raw:: html

   <td>

isVariable(s): Return 1 if s is a variable, 0 otherwise. See also:
asVariable.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Dataset or CdmsFile

.. raw:: html

   </td>

.. raw:: html

   <td>

open(url,mode='r'): Open or create a Dataset or CdmsFile. url is a
Uniform Resource Locator, referring to a cdunif or XML file. If the URL
has the extension '.xml' or '.cdml', a Dataset is returned, otherwise a
CdmsFile is returned. If the URL protocol is 'http', the file must be a
'.xml' or '.cdml' file, and the mode must be 'r'. If the protocol is
'file' or is omitted, a local file or dataset is opened. mode is the
open mode. See Table 2.24 on page 70.

.. raw:: html

   <p>

Example: Open an existing dataset:

f = cdms.open("sampleset.xml")

.. raw:: html

   </p>

.. raw:: html

   <p>

Example: Create a netCDF file:

f = cdms.open("newfile.nc",'w')

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

List

.. raw:: html

   </td>

.. raw:: html

   <td>

order2index (axes, orderstring): Find the index permutation of axes to
match order. Return a list of indices. axes is a list of axis objects.
orderstring is defined as in orderparse.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

List

.. raw:: html

   </td>

.. raw:: html

   <td>

orderparse(orderstring): Parse an order string. Returns a list of axes
specifiers. orderstring consists of:

.. raw:: html

   <ul>

::

    <li> Letters t, x, y, z meaning time, longitude, latitude, level</li>

    <li> Numbers 0-9 representing position in axes</li>

    <li> Dash (-) meaning insert the next available axis here.</li>

    <li> The ellipsis ... meaning fill these positions with any remaining axes.</li>

    <li> (name) meaning an axis whose id is name</li>

.. raw:: html

   </ul>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

None

.. raw:: html

   </td>

.. raw:: html

   <td>

setAutoBounds(mode): Set autobounds mode. In some circumstances CDMS can
generate boundaries for 1-D axes and rectilinear grids, when the bounds
are not explicitly defined. The autobounds mode determines how this is
done: If mode is 'grid' or 2 (the default), the getBounds method will
automatically generate boundary information for an axis or grid if the
axis is designated as a latitude or longitude axis, and the boundaries
are not explicitly defined. If mode is 'on' or 1, the getBounds method
will automatically generate boundary information for an axis or grid, if
the boundaries are not explicitly defined. If mode is 'off' or 0, and no
boundary data is explicitly defined, the bounds will NOT be generated;
the getBounds method will return None for the boundaries. Note: In
versions of CDMS prior to V4.0, the default mode was 'on'.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

None

.. raw:: html

   </td>

.. raw:: html

   <td>

setClassifyGrids(mode): Set the grid classification mode. This affects
how grid type is determined, for the purpose of generating grid
boundaries. If mode is 'on' (the default), grid type is determined by a
grid classification method, regardless of the value of grid.get-Type().
If mode is 'off', the value of grid.getType() determines the grid type

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

None

.. raw:: html

   </td>

.. raw:: html

   <td>

writeScripGrid(path, grid, gridTitle=None): Write a grid to a SCRIP grid
file. path is a string, the path of the SCRIP file to be created. grid
is a CDMS grid object. It may be rectangular. gridTitle is a string ID
for the grid.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>

Table 2.3 Class Tags
                    

+--------------+---------------------+
| Tag          | Class               |
+==============+=====================+
| 'axis'       | Axis                |
+--------------+---------------------+
| 'database'   | Database            |
+--------------+---------------------+
| 'dataset'    | Dataset, CdmsFile   |
+--------------+---------------------+
| 'grid'       | RectGrid            |
+--------------+---------------------+
| 'variable'   | Variable            |
+--------------+---------------------+
| 'xlink'      | Xlink               |
+--------------+---------------------+

2.4 CdmsObj
^^^^^^^^^^^

A CdmsObj is the base class for all CDMS database objects. At the
application level, CdmsObj objects are never created and used directly.
Rather the subclasses of CdmsObj (Dataset, Variable, Axis, etc.) are the
basis of user application programming.

All objects derived from CdmsObj have a special attribute .attributes.
This is a Python dictionary, which contains all the external
(persistent) attributes associated with the object. This is in contrast
to the internal, non-persistent attributes of an object, which are
built-in and predefined. When a CDMS object is written to a file, the
external attributes are written, but not the internal attributes.

**Example**: get a list of all external attributes of obj.

{% highlight python %} extatts = obj.attributes.keys() {% endhighlight
%}

Table 2.4 Attributes common to all CDMS objects
                                               

+--------------+--------------+--------------------------------------------------+
| Type         | Name         | Definition                                       |
+==============+==============+==================================================+
| Dictionary   | attributes   | External attribute dictionary for this object.   |
+--------------+--------------+--------------------------------------------------+

Table 2.5 Getting and setting attributes
                                        

.. raw:: html

   <table class="table">

.. raw:: html

   <tr>

::

    <th>Type</th>

    <th>Definition</th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

various

.. raw:: html

   </td>

.. raw:: html

   <td>

value = obj.attname

.. raw:: html

   <p>

Get an internal or external attribute value. If the attribute is
external, it is read from the database. If the attribute is not already
in the database, it is created as an external attribute. Internal
attributes cannot be created, only referenced.

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

various

.. raw:: html

   </td>

.. raw:: html

   <td>

obj.attname = value

.. raw:: html

   <p>

Set an internal or external attribute value. If the attribute is
external, it is written to the database.

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>

2.5 CoordinateAxis
^^^^^^^^^^^^^^^^^^

A CoordinateAxis is a variable that represents coordinate information.
It may be contained in a file or dataset, or may be transient
(memoryresident). Setting a slice of a file CoordinateAxis writes to the
file, and referencing a file CoordinateAxis slice reads data from the
file. Axis objects are also used to define the domain of a Variable.

CDMS defines several different types of CoordinateAxis objects. Table
2.9 on page 45 documents methods that are common to all CoordinateAxis
types. Table 2.10 on page 48 specifies methods that are unique to 1D
Axis objects.

Table 2.6 CoordinateAxis types
                              

+----------+-------------+
| Type     | Definition  |
+==========+=============+
| ``Coordi | A variable  |
| nateAxis | that        |
| ``       | represents  |
|          | coordinate  |
|          | information |
|          | .           |
|          | Has         |
|          | subtypes    |
|          | ``Axis2D``  |
|          | and         |
|          | ``AuxAxis1D |
|          | ``.         |
+----------+-------------+
| ``Axis`` | A           |
|          | one-dimensi |
|          | onal        |
|          | coordinate  |
|          | axis whose  |
|          | values are  |
|          | strictly    |
|          | monotonic.  |
|          | Has         |
|          | subtypes    |
|          | ``DatasetAx |
|          | is``,       |
|          | ``FileAxis` |
|          | `,          |
|          | and         |
|          | ``Transient |
|          | Axis``.     |
|          | May be an   |
|          | index axis, |
|          | mapping a   |
|          | range of    |
|          | integers to |
|          | the         |
|          | equivalent  |
|          | floating    |
|          | point       |
|          | value. If a |
|          | latitude or |
|          | longitude   |
|          | axis, may   |
|          | be          |
|          | associated  |
|          | with a      |
|          | ``RectGrid` |
|          | `.          |
+----------+-------------+
| ``Axis2D | A           |
| ``       | two-dimensi |
|          | onal        |
|          | coordinate  |
|          | axis,       |
|          | typically a |
|          | latitude or |
|          | longitude   |
|          | axis        |
|          | related to  |
|          | a           |
|          | ``Curviline |
|          | arGrid``.   |
|          | Has         |
|          | subtypes    |
|          | ``DatasetAx |
|          | is2D``,     |
|          | ``FileAxis2 |
|          | D``,        |
|          | and         |
|          | ``Transient |
|          | Axis2D``.   |
+----------+-------------+
| ``AuxAxi | A           |
| s1D``    | one-dimensi |
|          | onal        |
|          | coordinate  |
|          | axis whose  |
|          | values need |
|          | not be      |
|          | monotonic.  |
|          | Typically a |
|          | latitude or |
|          | longitude   |
|          | axis        |
|          | associated  |
|          | with a      |
|          | ``GenericGr |
|          | id``.       |
|          | Has         |
|          | subtypes    |
|          | ``DatasetAu |
|          | xAxis1D``,  |
|          | ``FileAuxAx |
|          | is1D``,     |
|          | and         |
|          | ``Transient |
|          | AuxAxis1D`` |
|          | .           |
|          | An axis in  |
|          | a           |
|          | ``CdmsFile` |
|          | `           |
|          | may be      |
|          | designated  |
|          | the         |
|          | unlimited   |
|          | axis,       |
|          | meaning     |
|          | that it can |
|          | be extended |
|          | in length   |
|          | after the   |
|          | initial     |
|          | definition. |
|          | There can   |
|          | be at most  |
|          | one         |
|          | unlimited   |
|          | axis        |
|          | associated  |
|          | with a      |
|          | ``CdmsFile` |
|          | `.          |
+----------+-------------+

Table 2.7 CoordinateAxis Internal Attributes
                                            

+------------------+------------------+--------------------------------------------+
| Type             | Name             | Definition                                 |
+==================+==================+============================================+
| ``Dictionary``   | ``attributes``   | External attribute dictionary.             |
+------------------+------------------+--------------------------------------------+
| ``String``       | ``id``           | CoordinateAxis identifer.                  |
+------------------+------------------+--------------------------------------------+
| ``Dataset``      | ``parent``       | The dataset which contains the variable.   |
+------------------+------------------+--------------------------------------------+
| ``Tuple``        | ``shape``        | The length of each axis.                   |
+------------------+------------------+--------------------------------------------+

Table 2.8 Axis Constructors
                           

+---------------+---------------+
| Constructor   | Description   |
+===============+===============+
| ``cdms.create | Create an     |
| Axis(data, bo | axis which is |
| unds=None)``  | not           |
|               | associated    |
|               | with a        |
|               | dataset or    |
|               | file. See     |
|               | Table 2.2 on  |
|               | page 33.      |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+
| ``Dataset.cre | Create an     |
| ateAxis(name, | ``Axis`` in a |
| ar)``         | ``Dataset``.  |
|               | (This         |
|               | function is   |
|               | not yet       |
|               | implemented.  |
|               | )             |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+
| ``CdmsFile.cr | Create an     |
| eateAxis(name | Axis in a     |
| ,ar,unlimited | ``CdmsFile``. |
| =0)``         | ``name`` is   |
|               | the string    |
|               | ``name`` of   |
|               | the ``Axis``. |
|               | ``ar`` is a   |
|               | 1-D data      |
|               | array which   |
|               | defines the   |
|               | ``Axis``      |
|               | values. It    |
|               | may have the  |
|               | value         |
|               | ``None`` if   |
|               | an unlimited  |
|               | axis is being |
|               | defined. At   |
|               | most one      |
|               | ``Axis`` in a |
|               | ``CdmsFile``  |
|               | may be        |
|               | designated as |
|               | being         |
|               | unlimited,    |
|               | meaning that  |
|               | it may be     |
|               | extended in   |
|               | length. To    |
|               | define an     |
|               | axis as       |
|               | unlimited,    |
|               | either:       |
+---------------+---------------+
|               | A) set ``ar`` |
|               | to ``None``,  |
|               | and leave     |
|               | ``unlimited`` |
|               | undefined, or |
+---------------+---------------+
|               | B) set ``ar`` |
|               | to the        |
|               | initial 1-D   |
|               | array, and    |
|               | set           |
|               | ``unlimited`` |
|               | to            |
|               | ``cdms.Unlimi |
|               | ted``         |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+
| ``cdms.create | See Table 2.2 |
| EqualAreaAxis | on page 33.   |
| (nlat)``      |               |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+
| ``cdms.create | See Table 2.2 |
| GaussianAxis( | on page 18.   |
| nlat)``       |               |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+
| ``cdms.create | See Table 2.2 |
| UniformLatitu | on page 18.   |
| deAxis(startl |               |
| at, nlat, del |               |
| talat)``      |               |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+
| ``cdms.create | See Table 2.2 |
| UniformLongit | on page 18.   |
| udeAxis(start |               |
| lon, nlon, de |               |
| ltalon)``     |               |
+---------------+---------------+
| -----------   | ------------  |
+---------------+---------------+

Table 2.9 CoordinateAxis Methods
                                

+-------+-------+-------+
| Type  | Metho | Defin |
|       | d     | ition |
+=======+=======+=======+
| ``Arr | ``arr | Read  |
| ay``  | ay =  | a     |
|       | axis[ | slice |
|       | i:j]` | of    |
|       | `     | data  |
|       |       | from  |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file  |
|       |       | or    |
|       |       | datas |
|       |       | et.   |
|       |       | Data  |
|       |       | is    |
|       |       | retur |
|       |       | ned   |
|       |       | in    |
|       |       | the   |
|       |       | physi |
|       |       | cal   |
|       |       | order |
|       |       | ing   |
|       |       | defin |
|       |       | ed    |
|       |       | in    |
|       |       | the   |
|       |       | datas |
|       |       | et.   |
|       |       | See   |
|       |       | Table |
|       |       | 2.11  |
|       |       | on    |
|       |       | page  |
|       |       | 51    |
|       |       | for a |
|       |       | descr |
|       |       | iptio |
|       |       | n     |
|       |       | of    |
|       |       | slice |
|       |       | opera |
|       |       | tors. |
+-------+-------+-------+
| ``Non | ``axi | Write |
| e``   | s[i:j | a     |
|       | ] = a | slice |
|       | rray` | of    |
|       | `     | data  |
|       |       | to    |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file. |
|       |       | Datas |
|       |       | et    |
|       |       | axes  |
|       |       | are   |
|       |       | read- |
|       |       | only. |
+-------+-------+-------+
| ``Non | ``ass | Set   |
| e``   | ignVa | the   |
|       | lue(a | entir |
|       | rray) | e     |
|       | ``    | value |
|       |       | of    |
|       |       | the   |
|       |       | axis. |
|       |       | ``arr |
|       |       | ay``  |
|       |       | is a  |
|       |       | Numer |
|       |       | ic    |
|       |       | array |
|       |       | ,     |
|       |       | of    |
|       |       | the   |
|       |       | same  |
|       |       | dimen |
|       |       | siona |
|       |       | lity  |
|       |       | as    |
|       |       | the   |
|       |       | axis. |
+-------+-------+-------+
| ``Axi | ``clo | Retur |
| s``   | ne(co | n     |
|       | pyDat | a     |
|       | a=1)` | copy  |
|       | `     | of    |
|       |       | the   |
|       |       | axis, |
|       |       | as a  |
|       |       | trans |
|       |       | ient  |
|       |       | axis. |
|       |       | If    |
|       |       | copyD |
|       |       | ata   |
|       |       | is 1  |
|       |       | (the  |
|       |       | defau |
|       |       | lt)   |
|       |       | the   |
|       |       | data  |
|       |       | itsel |
|       |       | f     |
|       |       | is    |
|       |       | copie |
|       |       | d.    |
+-------+-------+-------+
| ``Non | ``des | Desig |
| e``   | ignat | nate  |
|       | eLati | the   |
|       | tude( | axis  |
|       | persi | to be |
|       | stent | a     |
|       | =0)`` | latit |
|       |       | ude   |
|       |       | axis. |
|       |       | If    |
|       |       | persi |
|       |       | stent |
|       |       | is    |
|       |       | true, |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file  |
|       |       | or    |
|       |       | datas |
|       |       | et    |
|       |       | (if   |
|       |       | any)  |
|       |       | is    |
|       |       | modif |
|       |       | ied.  |
|       |       | By    |
|       |       | defau |
|       |       | lt,   |
|       |       | the   |
|       |       | desig |
|       |       | natio |
|       |       | n     |
|       |       | is    |
|       |       | tempo |
|       |       | rary. |
+-------+-------+-------+
| ``Non | ``des | Desig |
| e``   | ignat | nate  |
|       | eLeve | the   |
|       | l(per | axis  |
|       | siste | to be |
|       | nt=0) | a     |
|       | ``    | verti |
|       |       | cal   |
|       |       | level |
|       |       | axis. |
|       |       | If    |
|       |       | persi |
|       |       | stent |
|       |       | is    |
|       |       | true, |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file  |
|       |       | or    |
|       |       | datas |
|       |       | et    |
|       |       | (if   |
|       |       | any)  |
|       |       | is    |
|       |       | modif |
|       |       | ied.  |
|       |       | By    |
|       |       | defau |
|       |       | lt,   |
|       |       | the   |
|       |       | desig |
|       |       | natio |
|       |       | n     |
|       |       | is    |
|       |       | tempo |
|       |       | rary. |
+-------+-------+-------+
| ``Non | ``des | Desig |
| e``   | ignat | nate  |
|       | eLong | the   |
|       | itude | axis  |
|       | (pers | to be |
|       | isten | a     |
|       | t=0,  | longi |
|       | modul | tude  |
|       | o=360 | axis. |
|       | .0)`` | ``mod |
|       |       | ulo`` |
|       |       | is    |
|       |       | the   |
|       |       | modul |
|       |       | us    |
|       |       | value |
|       |       | .     |
|       |       | Any   |
|       |       | given |
|       |       | axis  |
|       |       | value |
|       |       | ``x`` |
|       |       | is    |
|       |       | treat |
|       |       | ed    |
|       |       | as    |
|       |       | equiv |
|       |       | alent |
|       |       | to    |
|       |       | ``x + |
|       |       |  modu |
|       |       | lus`` |
|       |       | .     |
|       |       | If    |
|       |       | ``per |
|       |       | siste |
|       |       | nt``  |
|       |       | is    |
|       |       | true, |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file  |
|       |       | or    |
|       |       | datas |
|       |       | et    |
|       |       | (if   |
|       |       | any)  |
|       |       | is    |
|       |       | modif |
|       |       | ied.  |
|       |       | By    |
|       |       | defau |
|       |       | lt,   |
|       |       | the   |
|       |       | desig |
|       |       | natio |
|       |       | n     |
|       |       | is    |
|       |       | tempo |
|       |       | rary. |
+-------+-------+-------+
| ``Non | ``des | Desig |
| e``   | ignat | nate  |
|       | eTime | the   |
|       | (pers | axis  |
|       | isten | to be |
|       | t=0,  | a     |
|       | calen | time  |
|       | dar = | axis. |
|       |  cdti | If    |
|       | me.Mi | ``per |
|       | xedCa | siste |
|       | lenda | nt``  |
|       | r)``  | is    |
|       |       | true, |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file  |
|       |       | or    |
|       |       | datas |
|       |       | et    |
|       |       | (if   |
|       |       | any)  |
|       |       | is    |
|       |       | modif |
|       |       | ied.  |
|       |       | By    |
|       |       | defau |
|       |       | lt,   |
|       |       | the   |
|       |       | desig |
|       |       | natio |
|       |       | n     |
|       |       | is    |
|       |       | tempo |
|       |       | rary. |
|       |       | ``cal |
|       |       | endar |
|       |       | ``    |
|       |       | is    |
|       |       | defin |
|       |       | ed    |
|       |       | as in |
|       |       | ``get |
|       |       | Calen |
|       |       | dar() |
|       |       | ``.   |
+-------+-------+-------+
| ``Arr | ``get | Get   |
| ay``  | Bound | the   |
|       | s()`` | assoc |
|       |       | iated |
|       |       | bound |
|       |       | ary   |
|       |       | array |
|       |       | .     |
|       |       | The   |
|       |       | shape |
|       |       | of    |
|       |       | the   |
|       |       | retur |
|       |       | n     |
|       |       | array |
|       |       | depen |
|       |       | ds    |
|       |       | on    |
|       |       | the   |
|       |       | type  |
|       |       | of    |
|       |       | axis: |
+-------+-------+-------+
|       | ``Axi |
|       | s``:  |
|       | ``(n, |
|       | 2)``  |
+-------+-------+-------+
|       | ``Axi |
|       | s2D`` |
|       | :     |
|       | ``(i, |
|       | j,4)` |
|       | `     |
+-------+-------+-------+
|       | ``Aux |
|       | Axis1 |
|       | D``:  |
|       | ``(nc |
|       | ell,  |
|       | nvert |
|       | )``   |
|       | where |
|       | nvert |
|       | is    |
|       | the   |
|       | maxim |
|       | um    |
|       | numbe |
|       | r     |
|       | of    |
|       | verti |
|       | ces   |
|       | of a  |
|       | cell. |
+-------+-------+-------+
|       | If    |
|       | the   |
|       | bound |
|       | ary   |
|       | array |
|       | of a  |
|       | latit |
|       | ude   |
|       | or    |
|       | longi |
|       | tude  |
|       | ``Axi |
|       | s``   |
|       | is    |
|       | not   |
|       | expli |
|       | citly |
|       | defin |
|       | ed,   |
|       | and   |
|       | ``aut |
|       | oBoun |
|       | ds``  |
|       | mode  |
|       | is    |
|       | on, a |
|       | defau |
|       | lt    |
|       | array |
|       | is    |
|       | gener |
|       | ated  |
|       | by    |
|       | calli |
|       | ng    |
|       | ``gen |
|       | Gener |
|       | icBou |
|       | nds`` |
|       | .     |
|       | Other |
|       | wise  |
|       | if    |
|       | auto- |
|       | Bound |
|       | s     |
|       | mode  |
|       | is    |
|       | off,  |
|       | the   |
|       | retur |
|       | n     |
|       | value |
|       | is    |
|       | ``Non |
|       | e``.  |
|       | See   |
|       | ``set |
|       | AutoB |
|       | ounds |
|       | ``.   |
+-------+-------+-------+
| ``Int | ``get | Retur |
| eger` | Calen | ns    |
| `     | dar() | the   |
|       | ``    | calen |
|       |       | dar   |
|       |       | assoc |
|       |       | iated |
|       |       | with  |
|       |       | the   |
|       |       | ``(ti |
|       |       | me)`` |
|       |       | \ axi |
|       |       | s.    |
|       |       | Possi |
|       |       | ble   |
|       |       | retur |
|       |       | n     |
|       |       | value |
|       |       | s,    |
|       |       | as    |
|       |       | defin |
|       |       | ed    |
|       |       | in    |
|       |       | the   |
|       |       | ``cdt |
|       |       | ime`` |
|       |       | modul |
|       |       | e,    |
|       |       | are:  |
+-------+-------+-------+
|       | ``cdt |
|       | ime.G |
|       | regor |
|       | ianCa |
|       | lenda |
|       | r``:  |
|       | the   |
|       | stand |
|       | ard   |
|       | Grego |
|       | rian  |
|       | calen |
|       | dar   |
+-------+-------+-------+
|       | ``cdt |
|       | ime.M |
|       | ixedC |
|       | alend |
|       | ar``: |
|       | mixed |
|       | Julia |
|       | n/Gre |
|       | goria |
|       | n     |
|       | calen |
|       | dar   |
+-------+-------+-------+
|       | ``cdt |
|       | ime.J |
|       | ulian |
|       | Calen |
|       | dar`` |
|       | :     |
|       | years |
|       | divis |
|       | ible  |
|       | by 4  |
|       | are   |
|       | leap  |
|       | years |
+-------+-------+-------+
|       | ``cdt |
|       | ime.N |
|       | oLeap |
|       | Calen |
|       | dar`` |
|       | :     |
|       | a     |
|       | year  |
|       | is    |
|       | 365   |
|       | days  |
+-------+-------+-------+
|       | ``cdt |
|       | ime.C |
|       | alend |
|       | ar360 |
|       | ``:   |
|       | a     |
|       | year  |
|       | is    |
|       | 360   |
|       | days  |
+-------+-------+-------+
|       | ``Non |
|       | e``:  |
|       | no    |
|       | calen |
|       | dar   |
|       | can   |
|       | be    |
|       | ident |
|       | ified |
+-------+-------+-------+
|       | Note: |
|       | If    |
|       | the   |
|       | axis  |
|       | is    |
|       | not a |
|       | time  |
|       | axis, |
|       | the   |
|       | globa |
|       | l,    |
|       | file- |
|       | relat |
|       | ed    |
|       | calen |
|       | dar   |
|       | is    |
|       | retur |
|       | ned.  |
+-------+-------+-------+
| ``Arr | ``get | Get   |
| ay``  | Value | the   |
|       | ()``  | entir |
|       |       | e     |
|       |       | axis  |
|       |       | vecto |
|       |       | r.    |
+-------+-------+-------+
| ``Int | ``isL | Retur |
| eger` | atitu | ns    |
| `     | de()` | true  |
|       | `     | iff   |
|       |       | the   |
|       |       | axis  |
|       |       | is a  |
|       |       | latit |
|       |       | ude   |
|       |       | axis. |
+-------+-------+-------+
| ``Int | ``isL | Retur |
| eger` | evel( | ns    |
| `     | )``   | true  |
|       |       | iff   |
|       |       | the   |
|       |       | axis  |
|       |       | is a  |
|       |       | level |
|       |       | axis. |
+-------+-------+-------+
| ``Int | ``isL | Retur |
| eger` | ongit | ns    |
| `     | ude() | true  |
|       | ``    | iff   |
|       |       | the   |
|       |       | axis  |
|       |       | is a  |
|       |       | longi |
|       |       | tude  |
|       |       | axis. |
+-------+-------+-------+
| ``Int | ``isT | Retur |
| eger` | ime() | ns    |
| `     | ``    | true  |
|       |       | iff   |
|       |       | the   |
|       |       | axis  |
|       |       | is a  |
|       |       | time  |
|       |       | axis. |
+-------+-------+-------+
| ``Int | ``len | The   |
| eger` | (axis | lengt |
| `     | )``   | h     |
|       |       | of    |
|       |       | the   |
|       |       | axis  |
|       |       | if    |
|       |       | one-d |
|       |       | imens |
|       |       | ional |
|       |       | .     |
|       |       | If    |
|       |       | multi |
|       |       | dimen |
|       |       | siona |
|       |       | l,    |
|       |       | the   |
|       |       | lengt |
|       |       | h     |
|       |       | of    |
|       |       | the   |
|       |       | first |
|       |       | dimen |
|       |       | sion. |
+-------+-------+-------+
| ``Int | ``siz | The   |
| eger` | e()`` | numbe |
| `     |       | r     |
|       |       | of    |
|       |       | eleme |
|       |       | nts   |
|       |       | in    |
|       |       | the   |
|       |       | axis. |
+-------+-------+-------+
| ``Str | ``typ | The   |
| ing`` | ecode | ``Num |
|       | ()``  | eric` |
|       |       | `     |
|       |       | datat |
|       |       | ype   |
|       |       | ident |
|       |       | ifier |
|       |       | .     |
+-------+-------+-------+

Table 2.10 Axis Methods, additional to CoordinateAxis methods
                                                             

+-------+-------+-------+
| Type  | Metho | Defin |
|       | d     | ition |
+=======+=======+=======+
| ``Lis | ``asC | ``Arr |
| t``   | ompon | ay``  |
| of    | entTi | versi |
| compo | me(ca | on    |
| nent  | lenda | of    |
| times | r=Non | ``cdt |
|       | e)``  | ime t |
|       |       | ocomp |
|       |       | ``.   |
|       |       | Retur |
|       |       | ns    |
|       |       | a     |
|       |       | ``Lis |
|       |       | t``   |
|       |       | of    |
|       |       | compo |
|       |       | nent  |
|       |       | times |
|       |       | .     |
+-------+-------+-------+
| ``Lis | ``asR | ``Arr |
| t``   | elati | ay``  |
| of    | veTim | versi |
| relat | e()`` | on    |
| ive   |       | of    |
| times |       | ``cdt |
|       |       | ime t |
|       |       | orel` |
|       |       | `.    |
|       |       | Retur |
|       |       | ns    |
|       |       | a     |
|       |       | ``Lis |
|       |       | t``   |
|       |       | of    |
|       |       | relat |
|       |       | ive   |
|       |       | times |
|       |       | .     |
+-------+-------+-------+
| ``Non | ``des | Desig |
| e``   | ignat | nate  |
|       | eCirc | the   |
|       | ular( | axis  |
|       | modul | to be |
|       | o, pe | circu |
|       | rsist | lar.  |
|       | ent=0 | ``mod |
|       | )``   | ulo`` |
|       |       | is    |
|       |       | the   |
|       |       | modul |
|       |       | us    |
|       |       | value |
|       |       | .     |
|       |       | Any   |
|       |       | given |
|       |       | axis  |
|       |       | value |
|       |       | ``x`` |
|       |       | is    |
|       |       | treat |
|       |       | ed    |
|       |       | as    |
|       |       | equiv |
|       |       | alent |
|       |       | to    |
|       |       | ``x + |
|       |       |  modu |
|       |       | lus`` |
|       |       | .     |
|       |       | If    |
|       |       | ``per |
|       |       | siste |
|       |       | nt``  |
|       |       | is    |
|       |       | ``Tru |
|       |       | e``,  |
|       |       | the   |
|       |       | exter |
|       |       | nal   |
|       |       | file  |
|       |       | or    |
|       |       | datas |
|       |       | et    |
|       |       | (if   |
|       |       | any)  |
|       |       | is    |
|       |       | modif |
|       |       | ied.  |
|       |       | By    |
|       |       | defau |
|       |       | lt,   |
|       |       | the   |
|       |       | desig |
|       |       | natio |
|       |       | n     |
|       |       | is    |
|       |       | tempo |
|       |       | rary. |
+-------+-------+-------+
| ``Int | ``isC | Retur |
| eger` | ircul | ns    |
| `     | ar()` | ``Tru |
|       | `     | e``   |
|       |       | if    |
|       |       | the   |
|       |       | axis  |
|       |       | has   |
|       |       | circu |
|       |       | lar   |
|       |       | topol |
|       |       | ogy.  |
|       |       | An    |
|       |       | axis  |
|       |       | is    |
|       |       | defin |
|       |       | ed    |
|       |       | as    |
|       |       | circu |
|       |       | lar   |
|       |       | if:   |
+-------+-------+-------+
|       | ``axi |
|       | s.top |
|       | ology |
|       |  == ' |
|       | circu |
|       | lar'` |
|       | `,    |
|       | or    |
+-------+-------+-------+
|       | ``axi |
|       | s.top |
|       | ology |
|       | ``    |
|       | is    |
|       | undef |
|       | ined, |
|       | and   |
|       | the   |
|       | axis  |
|       | is a  |
|       | longi |
|       | tude. |
|       | The   |
|       | defau |
|       | lt    |
|       | cycle |
|       | for   |
|       | circu |
|       | lar   |
|       | axes  |
|       | is    |
|       | 360.0 |
+-------+-------+-------+
| ``Int | ``isL | Retur |
| eger` | inear | ns    |
| `     | ()``  | ``Tru |
|       |       | e``   |
|       |       | if    |
|       |       | the   |
|       |       | axis  |
|       |       | has a |
|       |       | linea |
|       |       | r     |
|       |       | repre |
|       |       | senta |
|       |       | tion. |
+-------+-------+-------+
| ``Tup | ``map | Same  |
| le``  | Inter | as    |
|       | val(i | ``map |
|       | nterv | Inter |
|       | al)`` | valEx |
|       |       | t``,  |
|       |       | but   |
|       |       | retur |
|       |       | ns    |
|       |       | only  |
|       |       | the   |
|       |       | tuple |
|       |       | ``(i, |
|       |       | j)``, |
|       |       | and   |
|       |       | ``wra |
|       |       | parou |
|       |       | nd``  |
|       |       | is    |
|       |       | restr |
|       |       | icted |
|       |       | to    |
|       |       | one   |
|       |       | cycle |
|       |       | .     |
+-------+-------+-------+
| ``(i, | ``map | Map a |
| j,k)` | Inter | coord |
| `     | valEx | inate |
|       | t(int | inter |
|       | erval | val   |
|       | )``   | to an |
|       |       | index |
|       |       | ``int |
|       |       | erval |
|       |       | ``.   |
|       |       | ``int |
|       |       | erval |
|       |       | ``    |
|       |       | is a  |
|       |       | tuple |
|       |       | havin |
|       |       | g     |
|       |       | one   |
|       |       | of    |
|       |       | the   |
|       |       | forms |
|       |       | :     |
+-------+-------+-------+
|       | ``(x, |
|       | y)``  |
+-------+-------+-------+
|       | ``(x, |
|       | y,ind |
|       | icato |
|       | r)``  |
+-------+-------+-------+
|       | ``(x, |
|       | y,ind |
|       | icato |
|       | r,cyc |
|       | le)`` |
+-------+-------+-------+
|       | ``Non |
|       | e or  |
|       | ':'`` |
+-------+-------+-------+
|       | where |
|       | ``x`` |
|       | and   |
|       | ``y`` |
|       | are   |
|       | coord |
|       | inate |
|       | s     |
|       | indic |
|       | ating |
|       | the   |
|       | inter |
|       | val   |
|       | ``[x, |
|       | y)``, |
|       | and:  |
+-------+-------+-------+
|       | ``ind |
|       | icato |
|       | r``   |
|       | is a  |
|       | two   |
|       | or    |
|       | three |
|       | -char |
|       | acter |
|       | strin |
|       | g,    |
|       | where |
|       | the   |
|       | first |
|       | chara |
|       | cter  |
|       | is    |
|       | ``'c' |
|       | ``    |
|       | if    |
|       | the   |
|       | inter |
|       | val   |
|       | is    |
|       | close |
|       | d     |
|       | on    |
|       | the   |
|       | left, |
|       | ``'o' |
|       | ``    |
|       | if    |
|       | open, |
|       | and   |
|       | the   |
|       | secon |
|       | d     |
|       | chara |
|       | cter  |
|       | has   |
|       | the   |
|       | same  |
|       | meani |
|       | ng    |
|       | for   |
|       | the   |
|       | right |
|       | -hand |
|       | point |
|       | .     |
|       | If    |
|       | prese |
|       | nt,   |
|       | the   |
|       | third |
|       | chara |
|       | cter  |
|       | speci |
|       | fies  |
|       | how   |
|       | the   |
|       | inter |
|       | val   |
|       | shoul |
|       | d     |
|       | be    |
|       | inter |
|       | secte |
|       | d     |
|       | with  |
|       | the   |
|       | axis: |
+-------+-------+-------+
|       | ``'n' |
|       | ``    |
|       | -     |
|       | selec |
|       | t     |
|       | node  |
|       | value |
|       | s     |
|       | which |
|       | are   |
|       | conta |
|       | ined  |
|       | in    |
|       | the   |
|       | inter |
|       | val   |
+-------+-------+-------+
|       | ``'b' |
|       | ``    |
|       | -sele |
|       | ct    |
|       | axis  |
|       | eleme |
|       | nts   |
|       | for   |
|       | which |
|       | the   |
|       | corre |
|       | spond |
|       | ing   |
|       | cell  |
|       | bound |
|       | ary   |
|       | inter |
|       | sects |
|       | the   |
|       | inter |
|       | val   |
+-------+-------+-------+
|       | ``'e' |
|       | ``    |
|       | -     |
|       | same  |
|       | as n, |
|       | but   |
|       | inclu |
|       | de    |
|       | an    |
|       | extra |
|       | node  |
|       | on    |
|       | eithe |
|       | r     |
|       | side  |
+-------+-------+-------+
|       | ``'s' |
|       | ``    |
|       | -     |
|       | selec |
|       | t     |
|       | axis  |
|       | eleme |
|       | nts   |
|       | for   |
|       | which |
|       | the   |
|       | cell  |
|       | bound |
|       | ary   |
|       | is a  |
|       | subse |
|       | t     |
|       | of    |
|       | the   |
|       | inter |
|       | val   |
+-------+-------+-------+
|       | The   |
|       | defau |
|       | lt    |
|       | indic |
|       | ator  |
|       | is    |
|       | 'ccn' |
|       | ,     |
|       | that  |
|       | is,   |
|       | the   |
|       | inter |
|       | val   |
|       | is    |
|       | close |
|       | d,    |
|       | and   |
|       | nodes |
|       | in    |
|       | the   |
|       | inter |
|       | val   |
|       | are   |
|       | selec |
|       | ted.  |
+-------+-------+-------+
|       | If    |
|       | ``cyc |
|       | le``  |
|       | is    |
|       | speci |
|       | fied, |
|       | the   |
|       | axis  |
|       | is    |
|       | treat |
|       | ed    |
|       | as    |
|       | circu |
|       | lar   |
|       | with  |
|       | the   |
|       | given |
|       | cycle |
|       | value |
|       | .     |
|       | By    |
|       | defau |
|       | lt,   |
|       | if    |
|       | ``axi |
|       | s.isC |
|       | ircul |
|       | ar()` |
|       | `     |
|       | is    |
|       | true, |
|       | the   |
|       | axis  |
|       | is    |
|       | treat |
|       | ed    |
|       | as    |
|       | circu |
|       | lar   |
|       | with  |
|       | a     |
|       | defau |
|       | lt    |
|       | modul |
|       | us    |
|       | of    |
|       | ``360 |
|       | .0``. |
+-------+-------+-------+
|       | An    |
|       | inter |
|       | val   |
|       | of    |
|       | ``Non |
|       | e``   |
|       | or    |
|       | ``':' |
|       | ``    |
|       | retur |
|       | ns    |
|       | the   |
|       | full  |
|       | index |
|       | inter |
|       | val   |
|       | of    |
|       | the   |
|       | axis. |
+-------+-------+-------+
|       | The   |
|       | metho |
|       | d     |
|       | retur |
|       | ns    |
|       | the   |
|       | corre |
|       | spond |
|       | ing   |
|       | index |
|       | inter |
|       | val   |
|       | as a  |
|       | 3tupl |
|       | e     |
|       | ``(i, |
|       | j,k)` |
|       | `,    |
|       | where |
|       | ``k`` |
|       | is    |
|       | the   |
|       | integ |
|       | er    |
|       | strid |
|       | e,    |
|       | and   |
|       | ``[i. |
|       | j)``  |
|       | is    |
|       | the   |
|       | half- |
|       | open  |
|       | index |
|       | inter |
|       | val   |
|       | ``i < |
|       | = k < |
|       |  j``  |
|       | ``(i  |
|       | >= k  |
|       | > j i |
|       | f k < |
|       |  0)`` |
|       | ,     |
|       | or    |
|       | ``non |
|       | e``   |
|       | if    |
|       | the   |
|       | inter |
|       | secti |
|       | on    |
|       | is    |
|       | empty |
|       | .     |
+-------+-------+-------+
|       | for   |
|       | an    |
|       | axis  |
|       | which |
|       | is    |
|       | circu |
|       | lar   |
|       | (``ax |
|       | is.to |
|       | polog |
|       | y ==  |
|       | 'circ |
|       | ular' |
|       | ``),  |
|       | ``[i, |
|       | j)``  |
|       | is    |
|       | inter |
|       | prete |
|       | d     |
|       | as    |
|       | follo |
|       | ws,   |
|       | where |
|       | ``n = |
|       |  len( |
|       | axis) |
|       | ``    |
+-------+-------+-------+
|       | if    |
|       | ``0 < |
|       | = i < |
|       |  n``  |
|       | and   |
|       | ``0 < |
|       | = j < |
|       | = n`` |
|       | ,     |
|       | the   |
|       | inter |
|       | val   |
|       | does  |
|       | not   |
|       | wrap  |
|       | aroun |
|       | d     |
|       | the   |
|       | axis  |
|       | endpo |
|       | int.  |
+-------+-------+-------+
|       | other |
|       | wise  |
|       | the   |
|       | inter |
|       | val   |
|       | wraps |
|       | aroun |
|       | d     |
|       | the   |
|       | axis  |
|       | endpo |
|       | int.  |
+-------+-------+-------+
|       | see   |
|       | also: |
|       | ``map |
|       | inter |
|       | val`` |
|       | ,     |
|       | ``var |
|       | iable |
|       | .subr |
|       | egion |
|       | ()``  |
+-------+-------+-------+
| ``tra | ``sub | creat |
| nsien | axis( | e     |
| taxis | i,j,k | an    |
| ``    | =1)`` | axis  |
|       |       | assoc |
|       |       | iated |
|       |       | with  |
|       |       | the   |
|       |       | integ |
|       |       | er    |
|       |       | range |
|       |       | ``[i: |
|       |       | j:k]` |
|       |       | `.    |
|       |       | the   |
|       |       | strid |
|       |       | e     |
|       |       | ``k`` |
|       |       | can   |
|       |       | be    |
|       |       | posit |
|       |       | ive   |
|       |       | or    |
|       |       | negat |
|       |       | ive.  |
|       |       | wrapa |
|       |       | round |
|       |       | is    |
|       |       | suppo |
|       |       | rted  |
|       |       | for   |
|       |       | longi |
|       |       | tude  |
|       |       | dimen |
|       |       | sions |
|       |       | or    |
|       |       | those |
|       |       | with  |
|       |       | a     |
|       |       | modul |
|       |       | us    |
|       |       | attri |
|       |       | bute. |
+-------+-------+-------+

table 2.11 axis slice operators
                               

+---------------+-----------------------------------------------------------------------------+
| slice         | definition                                                                  |
+===============+=============================================================================+
| ``[i]``       | the ``ith`` element, starting with index ``0``                              |
+---------------+-----------------------------------------------------------------------------+
| ``[i:j]``     | the ``ith`` element through, but not including, element ``j``               |
+---------------+-----------------------------------------------------------------------------+
| ``[i:]``      | the ``ith`` element through and including the end                           |
+---------------+-----------------------------------------------------------------------------+
| ``[:j]``      | the beginning element through, but not including, element ``j``             |
+---------------+-----------------------------------------------------------------------------+
| ``[:]``       | the entire array                                                            |
+---------------+-----------------------------------------------------------------------------+
| ``[i:j:k]``   | every ``kth`` element, starting at ``i``, through but not including ``j``   |
+---------------+-----------------------------------------------------------------------------+
| ``[-i]``      | the ``ith`` element from the end. ``-1`` is the last element.               |
+---------------+-----------------------------------------------------------------------------+

**example:**

a longitude axis has value ``[0.0, 2.0, ..., 358.0]``, of length
``180``. map the coordinate interval ``-5.0 <= x < 5.0`` to index
interval(s), with wraparound. the result index interval ``-2 <= n < 3``
wraps around, since ``-2 < 0``, and has a stride of ``1``. this is
equivalent to the two contiguous index intervals ``2 <= n < 0`` and
``0 <= n < 3``

{% highlight python %} >>> axis.isCircular() 1 >>>
axis.mapIntervalExt((-5.0,5.0,'co')) (-2,3,1) {% endhighlight %}

2.6 CdmsFile
^^^^^^^^^^^^

A ``CdmsFile`` is a physical file, accessible via the ``cdunif``
interface. netCDF files are accessible in read-write mode. All other
formats (DRS, HDF, GrADS/GRIB, POP, QL) are accessible read-only.

As of CDMS V3, the legacy cuDataset interface is also supported by
Cdms-Files. See "cu Module" on page 180.

Table 2.12 CdmsFile Internal Attributes
                                       

+------------------+------------------+---------------------------------------+
| Type             | Name             | Definition                            |
+==================+==================+=======================================+
| ``Dictionary``   | ``attributes``   | Global, external file attributes      |
+------------------+------------------+---------------------------------------+
| ``Dictionary``   | ``axes``         | Axis objects contained in the file.   |
+------------------+------------------+---------------------------------------+
| ``Dictionary``   | ``grids``        | Grids contained in the file.          |
+------------------+------------------+---------------------------------------+
| ``String``       | ``id``           | File pathname.                        |
+------------------+------------------+---------------------------------------+
| ``Dictionary``   | ``variables``    | Variables contained in the file.      |
+------------------+------------------+---------------------------------------+

Table 2.13 CdmsFile Constructors
                                

+------+------+
| Cons | Desc |
| truc | ript |
| tor  | ion  |
+======+======+
| ``fi | Open |
| leob | the  |
| j =  | file |
| cdms | spec |
| .ope | ifie |
| n(pa | d    |
| th,  | by   |
| mode | path |
| )``  | retu |
|      | rnin |
|      | g    |
|      | a    |
|      | Cdms |
|      | File |
|      | obje |
|      | ct.  |
|      | ``pa |
|      | th`` |
|      | is   |
|      | the  |
|      | file |
|      | path |
|      | name |
|      | ,    |
|      | a    |
|      | stri |
|      | ng.  |
|      | ``mo |
|      | de`` |
|      | is   |
|      | the  |
|      | open |
|      | mode |
|      | indi |
|      | cato |
|      | r,   |
|      | as   |
|      | list |
|      | ed   |
|      | in   |
|      | Tabl |
|      | e    |
|      | 2.24 |
|      | on   |
|      | page |
|      | 70.  |
+------+------+
| ``fi | Crea |
| leob | te   |
| j =  | the  |
| cdms | file |
| .cre | spec |
| ateD | ifie |
| atas | d    |
| et(p | by   |
| ath) | path |
| ``   | ,    |
|      | a    |
|      | stri |
|      | ng.  |
+------+------+

Table 2.14 CdmsFile Methods
                           

.. raw:: html

   <table class="table">

.. raw:: html

   <thead>

::

    <tr>
      <th style="text-align: left">Type</th>
      <th style="text-align: left">Method</th>
      <th style="text-align: left">Definition</th>
    </tr>

.. raw:: html

   </thead>

.. raw:: html

   <tbody>

::

    <tr>
      <td style="text-align: left"><code>Transient-Variable</code></td>
      <td style="text-align: left"><code>fileobj(varname, selector)</code></td>
      <td style="text-align: left"><p>Calling a <code>CdmsFile</code> object as a function reads the region of data specified by the <code>selector</code>. The result is a transient variable, unless <code>raw = 1</code> is specified. See "Selectors" on page 103.</p><p><strong>Example:</strong> The following reads data for variable 'prc', year 1980:</p><pre style="word-break:normal;">f = cdms.open('test.nc')

x = f('prc', time=('1980-1','1981-1'))

.. raw:: html

   </pre>

.. raw:: html

   </td>

::

    </tr>
    <tr>
      <td style="text-align: left"><p><code>Variable</code>, <code>Axis</code>, or <code>Grid</code></p></td>
      <td style="text-align: left"><p><code>fileobj['id']</code></p></td>
      <td style="text-align: left"><p>Get the persistent variable, axis or grid object having the string identifier. This does not read the data for a variable.</p><p><strong>Example:</strong> The following gets the persistent variable <code>v</code>, equivalent to <code>v = f.variables['prc']</code>.</p>
      <pre style="word-break:normal;">f = cdms.open('sample.nc')

v = f['prc']

.. raw:: html

   </pre>

.. raw:: html

   <p>

Example: The following gets the axis named time, equivalent to t =
f.axes['time'].

.. raw:: html

   </p>

::

      <p><code>t = f['time']</code></p></td>
    </tr>
    <tr>
      <td style="text-align: left"><code>None</code></td>
      <td style="text-align: left"><code>close()</code></td>
      <td style="text-align: left">Close the file.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>Axis</code></td>
      <td style="text-align: left"><code>copyAxis(axis, newname=None)</code></td>
      <td style="text-align: left">Copy <code>axis</code> values and attributes to a new axis in the file. The returned object is persistent: it can be used to write axis data to or read axis data from the file. If an axis already exists in the file, having the same name and coordinate values, it is returned. It is an error if an axis of the same name exists, but with different coordinate values. <code>axis</code> is the axis object to be copied. <code>newname</code>, if specified, is the string identifier of the new axis object. If not specified, the identifier of the input axis is used.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>Grid</code></td>
      <td style="text-align: left"><code>copyGrid(grid, newname=None)</code></td>
      <td style="text-align: left">Copy grid values and attributes to a new grid in the file. The returned grid is persistent. If a grid already exists in the file, having the same name and axes, it is returned. An error is raised if a grid of the same name exists, having different axes. <code>grid</code> is the grid object to be copied. <code>newname</code>, if specified is the string identifier of the new grid object. If unspecified, the identifier of the input grid is used.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>Axis</code></td>
      <td style="text-align: left"><code>createAxis(id, ar, unlimited=0)</code></td>
      <td style="text-align: left">Create a new <code>Axis</code>. This is a persistent object which can be used to read or write axis data to the file. <code>id</code> is an alphanumeric string identifier, containing no blanks. <code>ar</code> is the one-dimensional axis array. Set <code>unlimited</code> to <code>cdms.Unlimited</code> to indicate that the axis is extensible.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>RectGrid</code></td>
      <td style="text-align: left"><code>createRectGrid(id, lat, lon, order, type="generic", mask=None)</code></td>
      <td style="text-align: left">Create a <code>RectGrid</code> in the file. This is not a persistent object: the order, type, and mask are not written to the file. However, the grid may be used for regridding operations. <code>lat</code> is a latitude axis in the file. <code>lon</code> is a longitude axis in the file. <code>order</code> is a string with value <code>"yx"</code> (the first grid dimension is latitude) or <code>"xy"</code> (the first grid dimension is longitude). <code>type</code> is one of <code>'gaussian'</code>,<code>'uniform'</code>,<code>'equalarea'</code>, or <code>'generic'</code>. If specified, <code>mask</code> is a two-dimensional, logical Numeric array (all values are zero or one) with the same shape as the grid.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>Variable</code></td>
      <td style="text-align: left"><code>createVariable(String id, String datatype,List axes, fill_value=None)</code></td>
      <td style="text-align: left">Create a new Variable. This is a persistent object which can be used to read or write variable data to the file. <code>id</code> is a String name which is unique with respect to all other objects in the file. <code>datatype</code> is an <code>MA</code> typecode, e.g., <code>MA.Float</code>, <code>MA.Int</code>. <code>axes</code> is a list of Axis and/or Grid objects. <code>fill_value</code> is the missing value (optional).</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>Variable</code></td>
      <td style="text-align: left"><code>createVariableCopy(var, newname=None)</code></td>
      <td style="text-align: left"><p>Create a new <code>Variable</code>, with the same name, axes, and attributes as the input variable. An error is raised if a variable of the same name exists in the file. <code>var</code> is the <code>Variable</code> to be copied. <code>newname</code>, if specified is the name of the new variable. If unspecified, the returned variable has the same name as <code>var</code>.</p><p><strong>Note:</strong> Unlike copyAxis, the actual data is not copied to the new variable.</p></td>
    </tr>
    <tr>
      <td style="text-align: left"><code>CurveGrid</code> or <code>Generic-Grid</code></td>
      <td style="text-align: left"><code>readScripGrid(self, whichGrid='destination', check-Grid=1)</code></td>
      <td style="text-align: left">Read a curvilinear or generic grid from a SCRIP netCDF file. The file can be a SCRIP grid file or remapping file. If a mapping file, <code>whichGrid</code> chooses the grid to read, either <code>"source"</code> or <code>"destination"</code>. If <code>checkGrid</code> is <code>1</code> (default), the grid cells are checked for convexity, and 'repaired' if necessary. Grid cells may appear to be nonconvex if they cross a <code>0 / 2pi</code> boundary. The repair consists of shifting the cell vertices to the same side modulo 360 degrees.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>None</code></td>
      <td style="text-align: left"><code>sync()</code></td>
      <td style="text-align: left">Writes any pending changes to the file.</td>
    </tr>
    <tr>
      <td style="text-align: left"><code>Variable</code></td>
      <td style="text-align: left"><pre style="word-break:normal;">write(var, attributes=None, axes=None, extbounds=None, id=None, extend=None, fill_value=None, index=None, typecode=None)</pre></td>
      <td style="text-align: left"><p>Write a variable or array to the file. The return value is the associated file variable.</p><p>If the variable does not exist in the file, it is first defined and  all attributes written, then the data is written. By default, the time dimension of the variable is defined as the unlimited dimension of the file. If the data is already defined, then data is extended or overwritten depending on the value of keywords <code>extend</code> and <code>index</code>, and the unlimited dimension values associated with <code>var</code>.</p><p><code>var</code> is a Variable, masked array, or Numeric array. <code>attributes</code> is the attribute dictionary for the variable. The default is <code>var.attributes</code>. <code>axes</code> is the list of file axes comprising the domain of the variable. The default is to copy <code>var.getAxisList()</code>. <code>extbounds</code> is the unlimited dimension bounds. Defaults to <code>var.getAxis(0).getBounds()</code>. <code>id</code> is the variable name in the file. Default is <code>var.id</code>. <code>extend = 1</code> causes the first dimension to be unlimited: iteratively writeable. The default is <code>None</code>, in which case the first dimension is extensible if it is <code>time.Set</code> to <code>0</code> to turn off this behaviour. <code>fill_value</code> is the missing value flag. <code>index</code> is the extended dimension index to write to. The default index is determined by lookup relative to the existing extended dimension.</p>
      <p><strong>Note:</strong> data can also be written by setting a slice of a file variable, and attributes can be written by setting an attribute of a file variable.</p>
      </td>
    </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

Table 2.15 CDMS Datatypes
                         

+-----------------+-----------------------------------+
| CDMS Datatype   | Definition                        |
+=================+===================================+
| ``CdChar``      | character                         |
+-----------------+-----------------------------------+
| ``CdDouble``    | double-precision floating-point   |
+-----------------+-----------------------------------+
| ``CdFloat``     | floating-point                    |
+-----------------+-----------------------------------+
| ``CdInt``       | integer                           |
+-----------------+-----------------------------------+
| ``CdLong``      | long integer                      |
+-----------------+-----------------------------------+
| ``CdShort``     | short integer                     |
+-----------------+-----------------------------------+

2.7 Database
^^^^^^^^^^^^

A Database is a collection of datasets and other CDMS objects. It
consists of a hierarchical collection of objects, with the database
being at the root, or top of the hierarchy. A database is used to:

-  search for metadata
-  access data
-  provide authentication and access control for data and metadata

The figure below illustrates several important points:

-  Each object in the database has a relative name of the form tag=id.
   The id of an object is unique with respect to all objects contained
   in the parent.

-  The name of the object consists of its relative name followed by the
   relative name(s) of its antecedent objects, up to and including the
   database name. In the figure below, one of the variables has name
   ``"variable=ua,dataset=ncep_reanalysis_mo,database=CDMS"``.

-  Subordinate objects are thought of as being contained in the parent.
   In this example, the database 'CDMS' contains two datasets, each of
   which contain several variables.

.. figure:: /images/diagram1.jpg
   :alt: Diagram 1

   Diagram 1

Figure 1
        

2.7.1 Overview
''''''''''''''

To access a database:

.. raw:: html

   <ol>

.. raw:: html

   <li>

Open a connection. The connect method opens a database connection.
connect takes a database URI and returns a database object: db =
cdms.connect("ldap://dbhost.llnl.gov/database=CDMS,ou=PCMDI,o=LLNL,c=US")

.. raw:: html

   </li>

.. raw:: html

   <li>

.. raw:: html

   <p>

Search the database, locating one or more datasets, variables, and/or
other objects.

.. raw:: html

   </p>

.. raw:: html

   <p>

The database searchFilter method searches the database. A single
database connection may be used for an arbitrary number of searches.

.. raw:: html

   </p>

.. raw:: html

   <p>

Example: Find all observed datasets

.. raw:: html

   </p>

.. raw:: html

   <p>

result = db.searchFilter(category="observed",tag="dataset")

.. raw:: html

   </p>

.. raw:: html

   <p>

Searches can be restricted to a subhierarchy of the database.

.. raw:: html

   </p>

.. raw:: html

   <p>

Example: Search just the dataset 'ncep\_reanalysis\_mo':

.. raw:: html

   </p>

.. raw:: html

   <p>

result = db.searchFilter(relbase="dataset=ncep\_reanalysis")

.. raw:: html

   </p>

.. raw:: html

   </li>

.. raw:: html

   <li>

Refine the search results if necessary. The result of a search can be
narrowed with the searchPredicate method.

.. raw:: html

   </li>

.. raw:: html

   <li>

.. raw:: html

   <p>

Process the results. A search result consists of a sequence of entries.
Each entry has a name, the name of the CDMS object, and an attribute
dictionary, consisting of the attributes located by the search:

.. raw:: html

   </p>

.. raw:: html

   <p>

 for entry in result: print entry.name, entry.attributes

.. raw:: html

   </p>

.. raw:: html

   </li>

.. raw:: html

   <li>

.. raw:: html

   <p>

Access the data. The CDMS object associated with an entry is obtained
from the getObject method:

.. raw:: html

   </p>

.. raw:: html

   <p>

obj = entry.getObject()

.. raw:: html

   </p>

.. raw:: html

   <p>

If the id of a dataset is known, the dataset can be opened directly with
the open method:

.. raw:: html

   </p>

.. raw:: html

   <p>

dset = db.open("ncep\_reanalysis\_mo")

.. raw:: html

   </p>

.. raw:: html

   </li>

.. raw:: html

   <li>

.. raw:: html

   <p>

Close the database connection:

.. raw:: html

   </p>

.. raw:: html

   <p>

db.close()

.. raw:: html

   </p>

.. raw:: html

   </li>

.. raw:: html

   </ol>

Table 2.16 Database Internal Attributes
                                       

+------------------+------------------+----------------------------------------+
| Type             | Name             | Summary                                |
+==================+==================+========================================+
| ``Dictionary``   | ``attributes``   | Database attribute dictionary          |
+------------------+------------------+----------------------------------------+
| ``LDAP``         | ``db``           | (LDAP only) LDAP database object       |
+------------------+------------------+----------------------------------------+
| ``String``       | ``netloc``       | Hostname, for server-based databases   |
+------------------+------------------+----------------------------------------+
| ``String``       | ``path``         | path name                              |
+------------------+------------------+----------------------------------------+
| ``String``       | ``uri``          | Uniform Resource Identifier            |
+------------------+------------------+----------------------------------------+

Table 2.17 Database Constructors
                                

+------+------+
| Cons | Desc |
| truc | ript |
| tor  | ion  |
+======+======+
| ``db | Conn |
|  = c | ect  |
| dms. | to   |
| conn | the  |
| ect( | data |
| uri= | base |
| None | .    |
| , us | ``ur |
| er=" | i``  |
| ", p | is   |
| assw | the  |
| ord= | Univ |
| "")` | ersa |
| `    | l    |
|      | Reso |
|      | urce |
|      | Inde |
|      | ntif |
|      | ier  |
|      | of   |
|      | the  |
|      | data |
|      | base |
|      | .    |
|      | The  |
|      | form |
|      | of   |
|      | the  |
|      | URI  |
|      | depe |
|      | nds  |
|      | on   |
|      | the  |
|      | impl |
|      | emen |
|      | tati |
|      | on   |
|      | of   |
|      | the  |
|      | data |
|      | base |
|      | .    |
|      | For  |
|      | a    |
|      | Ligh |
|      | twei |
|      | ght  |
|      | Dire |
|      | ctor |
|      | y    |
|      | Acce |
|      | ss   |
|      | Prot |
|      | ocol |
|      | (LDA |
|      | P)   |
|      | data |
|      | base |
|      | ,    |
|      | the  |
|      | form |
|      | is:  |
|      | ``ld |
|      | ap:/ |
|      | /hos |
|      | t[:p |
|      | ort] |
|      | /dbn |
|      | ame` |
|      | `.   |
|      | For  |
|      | exam |
|      | ple, |
|      | if   |
|      | the  |
|      | data |
|      | base |
|      | is   |
|      | loca |
|      | ted  |
|      | on   |
|      | host |
|      | dbho |
|      | st.l |
|      | lnl. |
|      | gov, |
|      | and  |
|      | is   |
|      | name |
|      | d    |
|      | ``'d |
|      | atab |
|      | ase= |
|      | CDMS |
|      | ,ou= |
|      | PCMD |
|      | I,o= |
|      | LLNL |
|      | ,c=U |
|      | S'`` |
|      | ,    |
|      | the  |
|      | URI  |
|      | is:  |
|      | ``ld |
|      | ap:/ |
|      | /dbh |
|      | ost. |
|      | llnl |
|      | .gov |
|      | /dat |
|      | abas |
|      | e=CD |
|      | MS,o |
|      | u=PC |
|      | MDI, |
|      | o=LL |
|      | NL,c |
|      | =US` |
|      | `.   |
|      | If   |
|      | unsp |
|      | ecif |
|      | ied, |
|      | the  |
|      | URI  |
|      | defa |
|      | ults |
|      | to   |
|      | the  |
|      | valu |
|      | e    |
|      | of   |
|      | envi |
|      | ronm |
|      | ent  |
|      | vari |
|      | able |
|      | CDMS |
|      | ROOT |
|      | .    |
|      | ``us |
|      | er`` |
|      | is   |
|      | the  |
|      | user |
|      | ID.  |
|      | If   |
|      | unsp |
|      | ecif |
|      | ied, |
|      | an   |
|      | anon |
|      | ymou |
|      | s    |
|      | conn |
|      | ecti |
|      | on   |
|      | is   |
|      | made |
|      | .    |
|      | ``pa |
|      | sswo |
|      | rd`` |
|      | is   |
|      | the  |
|      | user |
|      | pass |
|      | word |
|      | .    |
|      | A    |
|      | pass |
|      | word |
|      | is   |
|      | not  |
|      | requ |
|      | ired |
|      | for  |
|      | an   |
|      | anon |
|      | ymou |
|      | s    |
|      | conn |
|      | ecti |
|      | on   |
+------+------+

Table 2.18 Database Methods
                           

.. raw:: html

   <table class="table">

.. raw:: html

   <tr>

.. raw:: html

   <th>

Type

.. raw:: html

   </th>

.. raw:: html

   <th>

Method

.. raw:: html

   </th>

.. raw:: html

   <th>

Definition

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

None

.. raw:: html

   </td>

.. raw:: html

   <td>

close()

.. raw:: html

   </td>

.. raw:: html

   <td>

Close a database connection.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

List

.. raw:: html

   </td>

.. raw:: html

   <td>

listDatasets()

.. raw:: html

   </td>

.. raw:: html

   <td>

Return a list of the dataset IDs in this database. A dataset ID can be
passed to the open command.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Dataset

.. raw:: html

   </td>

.. raw:: html

   <td>

open(dsetid, mode='r')

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Open a dataset.

.. raw:: html

   </p>

.. raw:: html

   <p>

dsetid is the string dataset identifier

.. raw:: html

   </p>

.. raw:: html

   <p>

mode is the open mode, 'r' - read-only, 'r+' - read-write, 'w' - create.

.. raw:: html

   </p>

.. raw:: html

   <p>

openDataset is a synonym for open.

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

SearchResult

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <pre style="word-break: normal;">
   searchFilter(filter=None, tag=None, relbase=None, scope=Subtree, attnames=None, timeout=None)
     </pre>

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Search a CDMS database.

.. raw:: html

   </p>

.. raw:: html

   <p>

filter is the string search filter. Simple filters have the form "tag =
value". Simple filters can be combined using logical operators '&',
'\|', '!' in prefix notation.

.. raw:: html

   </p>

.. raw:: html

   <p>

Example:

.. raw:: html

   </p>

.. raw:: html

   <p>

The filter '(&(objec)(id=cli))' finds all variables named "cli".

.. raw:: html

   </p>

.. raw:: html

   <p>

A formal definition of search filters is provided in the following
section.

.. raw:: html

   </p>

.. raw:: html

   <p>

tag restricts the search to objects with that tag ("dataset" \|
"variable" \| "database" \| "axis" \| "grid").

.. raw:: html

   </p>

.. raw:: html

   <p>

relbase is the relative name of the base object of the search. The
search is restricted to the base object and all objects below it in the
hierarchy.

.. raw:: html

   </p>

.. raw:: html

   <p>

Example:

.. raw:: html

   </p>

.. raw:: html

   <p>

To search only dataset 'ncep\_reanalysis\_mo', specify:

.. raw:: html

   </p>

.. raw:: html

   <p>

relbase="dataset=ncep\_reanalysis\_mo"

.. raw:: html

   </p>

.. raw:: html

   <p>

To search only variable 'ua' in 'ncep\_reanalysis\_mo', use:

.. raw:: html

   </p>

.. raw:: html

   <p>

relbase="variable=ua,dataset=ncep\_reanalysis\_mo"

.. raw:: html

   </p>

.. raw:: html

   <p>

If no base is specified, the entire database is searched. See the scope
argument also.

.. raw:: html

   </p>

.. raw:: html

   <p>

scope is the search scope (Subtree \| Onelevel \| Base).

.. raw:: html

   </p>

.. raw:: html

   <ul>

::

    <li><b>Subtree</b> searches the base object and its descendants.</li>
    <li><b>Onelevel</b> searches the base object and its immediate descendants.</li>
    <li><b>Base</b>searches the base object alone.</li>

.. raw:: html

   </ul>

.. raw:: html

   <p>

The default is Subtree.

.. raw:: html

   </p>

.. raw:: html

   <p>

attnames: list of attribute names. Restricts the attributes returned. If
None, all attributes are returned. Attributes 'id' and 'objectclass' are
always included in the list.

.. raw:: html

   </p>

.. raw:: html

   <p>

timeout: integer number of seconds before timeout. The default is no
timeout.

.. raw:: html

   </p>

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>

2.7.2 Searching a database
''''''''''''''''''''''''''

The ``searchFilter`` method is used to search a database. The result is
called a search result, and consists of a sequence of result entries.

In its simplest form, ``searchFilter`` takes an argument consisting of a
string filter. The search returns a sequence of entries, corresponding
to those objects having an attribute which matches the filter. Simple
filters have the form (tag = value), where value can contain wildcards.
For example:

{% highlight text %} (id = ncep\*) (project = AMIP2) {% endhighlight %}

Simple filters can be combined with the logical operators '&', '\|',
'!'. For example,

{% highlight text %} (&(id = bmrc\*)(project = AMIP2)) {% endhighlight
%}

matches all objects with id starting with bmrc, and a project attribute
with value 'AMIP2'.

Formally, search filters are strings defined as follows:

{% highlight text %} filter ::= "(" filtercomp ")"

filtercomp ::= "&" filterlist \| # and "\|" filterlist \| # or "!"
filterlist \| # not simple

filterlist ::= filter \| filter filterlist simple ::= tag op value op
::= "=" \| # equality

"~=" \| # approximate equality "<=" \| # lexicographically less than or
equal to ">=" # lexicographically greater than or equal to

tag ::= string attribute name value ::= string attribute value, may
include '\*' as a wild card {% endhighlight %}

Attribute names are defined in the chapter on "Climate Data Markup
Language (CDML)" on page 149. In addition, some special attributes are
defined for convenience:

-  ``category`` is either "experimental" or "observed"
-  ``parentid`` is the ID of the parent dataset
-  ``project`` is a project identifier, e.g., "AMIP2"
-  ``objectclass`` is the list of tags associated with the object.

The set of objects searched is called the search scope. The top object
in the hierarchy is the base object. By default, all objects in the
database are searched, that is, the database is the base object. If the
database is very large, this may result in an unnecessarily slow or
inefficient search. To remedy this the search scope can be limited in
several ways:

-  The base object can be changed.
-  The scope can be limited to the base object and one level below, or
   to just the base object.
-  The search can be restricted to objects of a given class (dataset,
   variable, etc.)
-  The search can be restricted to return only a subset of the object
   attributes
-  The search can be restricted to the result of a previous search.
-  A search result is accessed sequentially within a for loop:

{% highlight python %} result =
db.searchFilter('(&(category=obs\ *)(id=ncep*))') for entry in result:
print entry.name {% endhighlight %}

Search results can be narrowed using ``searchPredicate``. In the
following example, the result of one search is itself searched for all
variables defined on a 94x192 grid:

{% highlight python %} >>> result =
db.searchFilter('parentid=ncep\*',tag="variable") >>> len(result) 65 >>>
result2 = result.searchPredicate(lambda x:

x.getGrid().shape==(94,192)) >>> len(result2) 3 >>> for entry in
result2: print entry.name
variable=rluscs,dataset=ncep\_reanalysis\_mo,database=CDMS,ou=PCMDI,

::

      o=LLNL, c=US

variable=rlds,dataset=ncep\_reanalysis\_mo,database=CDMS,ou=PCMDI,

::

      o=LLNL, c=US

variable=rlus,dataset=ncep\_reanalysis\_mo,database=CDMS,ou=PCMDI,

::

      o=LLNL, c=US

{% endhighlight %}

Table 2.19 SearchResult Methods
                               

+------+------+------+
| Type | Meth | Defi |
|      | od   | niti |
|      |      | on   |
+======+======+======+
| Resu | ``[i | Retu |
| ltEn | ]``  | rn   |
| try  |      | the  |
|      |      | i-th |
|      |      | sear |
|      |      | ch   |
|      |      | resu |
|      |      | lt.  |
|      |      | Resu |
|      |      | lts  |
|      |      | can  |
|      |      | also |
|      |      | be   |
|      |      | retu |
|      |      | rned |
|      |      | in a |
|      |      | for  |
|      |      | loop |
|      |      | :    |
|      |      | ``fo |
|      |      | r en |
|      |      | try  |
|      |      | in d |
|      |      | b.se |
|      |      | arch |
|      |      | Resu |
|      |      | lt(t |
|      |      | ag=" |
|      |      | data |
|      |      | set" |
|      |      | ):`` |
+------+------+------+
| Inte | ``le | Numb |
| ger  | n()` | er   |
|      | `    | of   |
|      |      | entr |
|      |      | ies  |
|      |      | in   |
|      |      | the  |
|      |      | resu |
|      |      | lt.  |
+------+------+------+
| Sear | ``se | Refi |
| chRe | arch | ne   |
| sult | Pred | a    |
|      | icat | sear |
|      | e(pr | ch   |
|      | edic | resu |
|      | ate, | lt,  |
|      |  tag | with |
|      | =Non | a    |
|      | e)`` | pred |
|      |      | icat |
|      |      | e    |
|      |      | sear |
|      |      | ch.  |
|      |      | ``pr |
|      |      | edic |
|      |      | ate` |
|      |      | `    |
|      |      | is a |
|      |      | func |
|      |      | tion |
|      |      | whic |
|      |      | h    |
|      |      | take |
|      |      | s    |
|      |      | a    |
|      |      | sing |
|      |      | le   |
|      |      | CDMS |
|      |      | obje |
|      |      | ct   |
|      |      | and  |
|      |      | retu |
|      |      | rns  |
|      |      | true |
|      |      | (1)  |
|      |      | if   |
|      |      | the  |
|      |      | obje |
|      |      | ct   |
|      |      | sati |
|      |      | sfie |
|      |      | s    |
|      |      | the  |
|      |      | pred |
|      |      | icat |
|      |      | e,   |
|      |      | 0 if |
|      |      | not. |
|      |      | ``ta |
|      |      | g``  |
|      |      | rest |
|      |      | rict |
|      |      | s    |
|      |      | the  |
|      |      | sear |
|      |      | ch   |
|      |      | to   |
|      |      | obje |
|      |      | cts  |
|      |      | of   |
|      |      | the  |
|      |      | clas |
|      |      | s    |
|      |      | deno |
|      |      | ted  |
|      |      | by   |
|      |      | the  |
|      |      | tag. |
|      |      | **No |
|      |      | te** |
|      |      | :    |
|      |      | In   |
|      |      | the  |
|      |      | curr |
|      |      | ent  |
|      |      | impl |
|      |      | emen |
|      |      | tati |
|      |      | on,  |
|      |      | ``se |
|      |      | arch |
|      |      | Pred |
|      |      | icat |
|      |      | e``\ |
|      |      |  is  |
|      |      | much |
|      |      | less |
|      |      | effi |
|      |      | cien |
|      |      | t    |
|      |      | than |
|      |      | ``se |
|      |      | arch |
|      |      | Filt |
|      |      | er`` |
|      |      | .    |
|      |      | For  |
|      |      | best |
|      |      | perf |
|      |      | orma |
|      |      | nce, |
|      |      | use  |
|      |      | ``se |
|      |      | arch |
|      |      | Filt |
|      |      | er`` |
|      |      | to   |
|      |      | narr |
|      |      | ow   |
|      |      | the  |
|      |      | scop |
|      |      | e    |
|      |      | of   |
|      |      | the  |
|      |      | sear |
|      |      | ch,  |
|      |      | then |
|      |      | use  |
|      |      | ``se |
|      |      | arch |
|      |      | Pred |
|      |      | icat |
|      |      | e``  |
|      |      | for  |
|      |      | more |
|      |      | gene |
|      |      | ral  |
|      |      | sear |
|      |      | ches |
|      |      | .    |
+------+------+------+

A search result is a sequence of result entries. Each entry has a string
name, the name of the object in the database hierarchy, and an attribute
dictionary. An entry corresponds to an object found by the search, but
differs from the object, in that only the attributes requested are
associated with the entry. In general, there will be much more
information defined for the associated CDMS object, which is retrieved
with the ``getObject`` method.

Table 2.20 ResultEntry Attributes
                                 

+------+------+------+
| Type | Name | Desc |
|      |      | ript |
|      |      | ion  |
+======+======+======+
| Stri | ``na | The  |
| ng   | me`` | name |
|      |      | of   |
|      |      | this |
|      |      | entr |
|      |      | y    |
|      |      | in   |
|      |      | the  |
|      |      | data |
|      |      | base |
|      |      | .    |
+------+------+------+
| Dict | ``at | The  |
| iona | trib | attr |
| ry   | utes | ibut |
|      | ``   | es   |
|      |      | retu |
|      |      | rned |
|      |      | from |
|      |      | the  |
|      |      | sear |
|      |      | ch.  |
|      |      | ``at |
|      |      | trib |
|      |      | utes |
|      |      | [key |
|      |      | ]``  |
|      |      | is a |
|      |      | list |
|      |      | of   |
|      |      | all  |
|      |      | stri |
|      |      | ng   |
|      |      | valu |
|      |      | es   |
|      |      | asso |
|      |      | ciat |
|      |      | ed   |
|      |      | with |
|      |      | the  |
|      |      | key  |
+------+------+------+

Table 2.21 ResultEntry Methods
                              

+------+------+------+
| Type | Meth | Defi |
|      | od   | niti |
|      |      | on   |
+======+======+======+
| ``Cd | ``ge | Retu |
| msOb | tObj | rn   |
| j``  | ect( | the  |
|      | )``  | CDMS |
|      |      | obje |
|      |      | ct   |
|      |      | asso |
|      |      | ciat |
|      |      | ed   |
|      |      | with |
|      |      | this |
|      |      | entr |
|      |      | y.   |
|      |      | **No |
|      |      | te:* |
|      |      | *    |
|      |      | For  |
|      |      | many |
|      |      | sear |
|      |      | ch   |
|      |      | appl |
|      |      | icat |
|      |      | ions |
|      |      | it   |
|      |      | is   |
|      |      | unne |
|      |      | cess |
|      |      | ary  |
|      |      | to   |
|      |      | acce |
|      |      | ss   |
|      |      | the  |
|      |      | asso |
|      |      | ciat |
|      |      | ed   |
|      |      | CDMS |
|      |      | obje |
|      |      | ct.  |
|      |      | For  |
|      |      | best |
|      |      | perf |
|      |      | orma |
|      |      | nce  |
|      |      | this |
|      |      | func |
|      |      | tion |
|      |      | shou |
|      |      | ld   |
|      |      | be   |
|      |      | used |
|      |      | only |
|      |      | when |
|      |      | nece |
|      |      | ssar |
|      |      | y,   |
|      |      | for  |
|      |      | exam |
|      |      | ple, |
|      |      | to   |
|      |      | retr |
|      |      | ieve |
|      |      | data |
|      |      | asso |
|      |      | ciat |
|      |      | ed   |
|      |      | with |
|      |      | a    |
|      |      | vari |
|      |      | able |
|      |      | .    |
+------+------+------+

2.7.3 Accessing data
''''''''''''''''''''

To access data via CDMS:

1. Locate the dataset ID. This may involve searching the metadata.
2. Open the dataset, using the open method.
3. Reference the portion of the variable to be read.

In the next example, a portion of variable 'ua' is read from dataset
'ncep\_reanalysis\_mo':

{% highlight python %} dset = db.open('ncep\_reanalysis\_mo') ua =
dset.variables['ua'] data = ua[0,0] {% endhighlight %}

2.7.4 Examples of database searches
'''''''''''''''''''''''''''''''''''

In the following examples, db is the database opened with

{% highlight python %} db = cdms.connect() {% endhighlight %}

This defaults to the database defined in environment variable
``CDMSROOT``.

**Example:** List all variables in dataset 'ncep\_reanalysis\_mo':

{% highlight python %} for entry in db.searchFilter(filter =
"parentid=ncep\_reanalysis\_mo", tag = "variable"): print entry.name {%
endhighlight %}

**Example:** Find all axes with bounds defined:

{% highlight python %} for entry in
db.searchFilter(filter="bounds=\*",tag="axis"): print entry.name {%
endhighlight %}

**Example:** Locate all GDT datasets:

{% highlight python %} for entry in
db.searchFilter(filter="Conventions=GDT\*",tag="dataset"): print
entry.name {% endhighlight %}

**Example:** Find all variables with missing time values, in observed
datasets:

{% highlight python %} def missingTime(obj): time = obj.getTime() return
time.length != time.partition\_length

result = db.searchFilter(filter="category=observed") for entry in
result.searchPredicate(missingTime): print entry.name {% endhighlight %}

**Example:** Find all CMIP2 datasets having a variable with id "hfss":

{% highlight python %} for entry in db.searchFilter(filter =
"(&(project=CMIP2)(id=hfss))", tag = "variable"): print
entry.getObject().parent.id {% endhighlight %}

**Example:** Find all observed variables on 73x144 grids:

{% highlight python %} result = db.searchFilter(category='obs\*') for
entry in result.searchPredicate(lambda x:
x.getGrid().shape==(73,144),tag="variable"): print entry.name {%
endhighlight %}

**Example:** Find all observed variables with more than 1000 timepoints:

{% highlight python %} result = db.searchFilter(category='obs\*') for
entry in result.searchPredicate(lambda x: len(x.getTime())>1000, tag =
"variable"): print entry.name, len(entry.getObject().getTime()) {%
endhighlight %}

**Example:** Find the total number of each type of object in the
database

{% highlight python %} print
len(db.searchFilter(tag="database")),"database" print
len(db.searchFilter(tag="dataset")),"datasets" print
len(db.searchFilter(tag="variable")),"variables" print
len(db.searchFilter(tag="axis")),"axes" {% endhighlight %}

2.8 Dataset
^^^^^^^^^^^

A Dataset is a virtual file. It consists of a metafile, in CDML/XML
representation, and one or more data files.

As of CDMS V3, the legacy cuDataset interface is supported by Datasets.
See "cu Module" on page 180.

Table 2.22 Dataset Internal Attributes
                                      

+------+------+------+
| Type | Name | Desc |
|      |      | ript |
|      |      | ion  |
+======+======+======+
| Dict | ``at | Data |
| iona | trib | set  |
| ry   | utes | exte |
|      | ``   | rnal |
|      |      | attr |
|      |      | ibut |
|      |      | es.  |
+------+------+------+
| Dict | ``ax | Axes |
| iona | es`` | cont |
| ry   |      | aine |
|      |      | d    |
|      |      | in   |
|      |      | the  |
|      |      | data |
|      |      | set. |
+------+------+------+
| Stri | ``da | Path |
| ng   | tapa | of   |
|      | th`` | data |
|      |      | file |
|      |      | s,   |
|      |      | rela |
|      |      | tive |
|      |      | to   |
|      |      | the  |
|      |      | pare |
|      |      | nt   |
|      |      | data |
|      |      | base |
|      |      | .    |
|      |      | If   |
|      |      | no   |
|      |      | pare |
|      |      | nt,  |
|      |      | the  |
|      |      | data |
|      |      | path |
|      |      | is   |
|      |      | abso |
|      |      | lute |
|      |      | .    |
+------+------+------+
| Dict | ``gr | Grid |
| iona | ids` | s    |
| ry   | `    | cont |
|      |      | aine |
|      |      | d    |
|      |      | in   |
|      |      | the  |
|      |      | data |
|      |      | set. |
+------+------+------+
| Stri | ``mo | Open |
| ng   | de`` | mode |
|      |      | .    |
+------+------+------+
| Data | ``pa | Data |
| base | rent | base |
|      | ``   | whic |
|      |      | h    |
|      |      | cont |
|      |      | ains |
|      |      | this |
|      |      | data |
|      |      | set. |
|      |      | If   |
|      |      | the  |
|      |      | data |
|      |      | set  |
|      |      | is   |
|      |      | not  |
|      |      | part |
|      |      | of a |
|      |      | data |
|      |      | base |
|      |      | ,    |
|      |      | the  |
|      |      | valu |
|      |      | e    |
|      |      | is   |
|      |      | ``No |
|      |      | ne`` |
|      |      | .    |
+------+------+------+
| Stri | ``ur | Unif |
| ng   | i``  | orm  |
|      |      | Reso |
|      |      | urce |
|      |      | Iden |
|      |      | tifi |
|      |      | er   |
|      |      | of   |
|      |      | this |
|      |      | data |
|      |      | set. |
+------+------+------+
| Dict | ``va | Vari |
| iona | riab | able |
| ry   | les` | s    |
|      | `    | cont |
|      |      | aine |
|      |      | d    |
|      |      | in   |
|      |      | the  |
|      |      | data |
|      |      | set. |
+------+------+------+
| Dict | ``xl | Exte |
| iona | inks | rnal |
| ry   | ``   | link |
|      |      | s    |
|      |      | cont |
|      |      | aine |
|      |      | d    |
|      |      | in   |
|      |      | the  |
|      |      | data |
|      |      | set. |
+------+------+------+

Table 2.23 Dataset Constructors
                               

+------+------+
| Cons | Desc |
| truc | ript |
| tor  | ion  |
+======+======+
| ``da | Open |
| tase | the  |
| tobj | data |
|  = c | set  |
| dms. | spec |
| open | ifie |
| (Str | d    |
| ing  | by   |
| uri, | the  |
|  Str | Univ |
| ing  | ersa |
| mode | l    |
| ='r' | Reso |
| )``  | urce |
|      | Indi |
|      | cato |
|      | r,   |
|      | a    |
|      | CDML |
|      | file |
|      | .    |
|      | Retu |
|      | rns  |
|      | a    |
|      | Data |
|      | set  |
|      | obje |
|      | ct.  |
|      | mode |
|      | is   |
|      | one  |
|      | of   |
|      | the  |
|      | indi |
|      | cato |
|      | rs   |
|      | list |
|      | ed   |
|      | in   |
|      | Tabl |
|      | e    |
|      | 2.24 |
|      | on   |
|      | page |
|      | 70.  |
|      | ``op |
|      | enDa |
|      | tase |
|      | t``  |
|      | is a |
|      | syno |
|      | nym  |
|      | for  |
|      | ``op |
|      | en`` |
+------+------+

Table 2.24 Open Modes
                     

+--------+-----------------------------------------------------------------------+
| Mode   | Definition                                                            |
+========+=======================================================================+
| 'r'    | read-only                                                             |
+--------+-----------------------------------------------------------------------+
| 'r+'   | read-write                                                            |
+--------+-----------------------------------------------------------------------+
| 'a'    | read-write. Open the file if it exists, otherwise create a new file   |
+--------+-----------------------------------------------------------------------+
| 'w'    | Create a new file, read-write                                         |
+--------+-----------------------------------------------------------------------+

Table 2.25 Dataset Methods
                          

.. raw:: html

   <table class="table">

::

    <tbody>
      <tr>
        <th>Type</th>

        <th>Method</th>

        <th>Definition</th>
      </tr>

      <tr>
        <td>Transient-Variable</td>

        <td><code>datasetobj(varname, selector)</code></td>

        <td>
          Calling a Dataset object as a function reads the region of data defined by the
          selector. The result is a transient variable, unless <code>raw = 1</code> is
          specified. See "Selectors" on page 103.

          <p><b>Example:</b> The following reads data for variable 'prc', year 1980:</p>
          <pre style="word-break:normal;">

f = cdms.open('test.xml') x = f('prc', time=('1980-1','1981-1'))

.. raw:: html

   </pre>

::

        </td>
      </tr>

      <tr>
        <td>Variable, Axis, or Grid</td>

        <td><code>datasetobj['id']</code></td>

        <td>
          <p>The square bracket operator applied to a dataset gets the persistent
          variable, axis or grid object having the string identifier. This does not read
          the data for a variable. Returns <code>None</code> if not found.</p>

          <p><b>Example:</b></p>
          <pre style="word-break:normal;">

f = cdms.open('sample.xml') v = f['prc']

.. raw:: html

   </pre>

::

          <p>gets the persistent variable v, equivalent to <code>v =
          f.variables['prc']</code>.</p>

          <p><b>Example:</b></p>

          <p><code>t = f['time']</code><br />
          gets the axis named 'time', equivalent to <code>t = f.axes['time']</code></p>
        </td>
      </tr>

      <tr>
        <td><code>None</code><br />
        <br /></td>

        <td><code>close()</code></td>

        <td>Close the dataset.</td>
      </tr>

      <tr>
        <td>
          <p><code>RectGrid</code></p>
        </td>

        <td>
          <p><code>createRectGrid(id, lat, lon, order, type="generic",
          mask=None)</code></p>
        </td>

        <td>
          <p>Create a RectGrid in the dataset. This is not a persistent object: the
          order, type, and mask are not written to the dataset. However, the grid may be
          used for regridding operations.</p>

          <p><code>lat</code> is a latitude axis in the dataset.</p>

          <p><code>lon</code> is a longitude axis in the dataset.</p>

          <p><code>order</code> is a string with value "yx" (the first grid dimension is
          latitude) or "xy" (the first grid dimension is longitude).</p>

          <p><code>type</code> is one of 'gaussian','uniform','equalarea',or
          'generic'</p>

          <p>If specified, <code>mask</code> is a two-dimensional, logical Numeric array
          (all values are zero or one) with the same shape as the grid.</p>
        </td>
      </tr>

      <tr>
        <td>
          <p>Axis</p>
        </td>

        <td>
          <p><code>getAxis(id)</code></p>
        </td>

        <td>
          <p>Get an axis object from the file or dataset.</p>

          <p><code>id</code> is the string axis identifier.</p>
        </td>
      </tr>

      <tr>
        <td>
          <p>Grid</p>
        </td>

        <td>
          <p><code>getGrid(id)</code></p>
        </td>

        <td>
          <p>Get a grid object from a file or dataset.</p>

          <p><code>id</code> is the string grid identifier.</p>
        </td>
      </tr>

      <tr>
        <td>
          <p>List</p>
        </td>

        <td>
          <p><code>getPaths()</code></p>
        </td>

        <td>
          <p>Get a sorted list of pathnames of datafiles which comprise the dataset. This
          does not include the XML metafile path, which is stored in the .uri
          attribute.</p>
        </td>
      </tr>

      <tr>
        <td>
          <p>Variable</p>
        </td>

        <td>
          <p><code>getVariable(id)</code></p>
        </td>

        <td>
          <p>Get a variable object from a file or dataset.</p>

          <p><code>id</code> is the string variable identifier.</p>
        </td>
      </tr>

    <tr>
      <td>CurveGrid or GenericGrid</td>

      <td><code>readScripGrid(self, whichGrid='destination', check-or Generic-Grid=1)</code></td>

      <td>
        <p>Read a curvilinear or generic grid from a SCRIP dataset. The dataset can be a SCRIP grid file or remapping file.</p>

        <p>If a mapping file, <code>whichGrid</code> chooses the grid to read, either <code>"source"</code> or <code>"destination"</code>.</p>

        <p>If <code>checkGrid</code> is 1 (default), the grid cells are checked for convexity, and 'repaired' if necessary. Grid cells may appear to be nonconvex if they cross a <code>0 / 2pi</code> boundary. The repair consists of shifting the cell vertices to the same side modulo 360 degrees.</p>
      </td>
    </tr>

    <tr>
      <td>None<br /><br /></td>
      <td><code>sync()</code></td>
      <td>Write any pending changes to the dataset.</td>
    </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

2.9 MV module
^^^^^^^^^^^^^

The fundamental CDMS data object is the variable. A variable is
comprised of:

-  a masked data array, as defined in the NumPy MA module.
-  a domain: an ordered list of axes and/or grids.
-  an attribute dictionary.

The MV module is a work-alike replacement for the MA module, that
carries along the domain and attribute information where appropriate. MV
provides the same set of functions as MA. However, MV functions generate
transient variables as results. Often this simplifies scripts that
perform computation. MA is part of the Python Numeric package,
documented at http://www.numpy.org.

MV can be imported with the command:

{% highlight text %} import MV {% endhighlight %}

The command

{% highlight text %} from MV import \* {% endhighlight %}

allows use of MV commands without any prefix.

Table 2.26 on page 75 lists the constructors in MV. All functions return
a transient variable. In most cases the keywords axes, attributes, and
id are available. axes is a list of axis objects which specifies the
domain of the variable. attributes is a dictionary. id is a special
attribute string that serves as the identifier of the variable, and
should not contain blanks or non-printing characters. It is used when
the variable is plotted or written to a file. Since the id is just an
attribute, it can also be set like any attribute:

{% highlight text %} var.id = 'temperature' {% endhighlight %}

For completeness MV provides access to all the MA functions. The
functions not listed in the following tables are identical to the
corresponding MA function: ``allclose``, ``allequal``,
``common_fill_value``, ``compress``, ``create_mask``, ``dot``, ``e``,
``fill_value``, ``filled``, ``get_print_limit``, ``getmask``,
``getmaskarray``, ``identity``, ``indices``, ``innerproduct``, ``isMA``,
``isMaskedArray``, ``is_mask``, ``isarray``, ``make_mask``,
``make_mask_none``, ``mask_or``, ``masked``, ``pi``, ``put``,
``putmask``, ``rank``, ``ravel``, ``set_fill_value``,
``set_print_limit``, ``shape``, ``size``. See the documentation at
http://numpy.sourceforge.net for a description of these functions.

Table 2.26 Variable Constructors in module MV
                                             

+------+------+
| Cons | Desc |
| truc | ript |
| tor  | ion  |
+======+======+
| ``ar | Just |
| rayr | like |
| ange | ``MA |
| (sta | .ara |
| rt,  | nge( |
| stop | )``  |
| =Non | exce |
| e, s | pt   |
| tep= | it   |
| 1, t | retu |
| ypec | rns  |
| ode= | a    |
| None | vari |
| , ax | able |
| is=N | whos |
| one, | e    |
|  att | type |
| ribu | can  |
| tes= | be   |
| None | spec |
| , id | fied |
| =Non | by   |
| e)`` | the  |
|      | keyw |
|      | ord  |
|      | argu |
|      | ment |
|      | type |
|      | code |
|      | .    |
|      | The  |
|      | axis |
|      | ,    |
|      | attr |
|      | ibut |
|      | e    |
|      | dict |
|      | iona |
|      | ry,  |
|      | and  |
|      | stri |
|      | ng   |
|      | iden |
|      | tifi |
|      | er   |
|      | of   |
|      | the  |
|      | resu |
|      | lt   |
|      | vari |
|      | able |
|      | may  |
|      | be   |
|      | spec |
|      | ifie |
|      | d.   |
|      | *Syn |
|      | onym |
|      | :*   |
|      | ``ar |
|      | ange |
|      | ``   |
+------+------+
| ``ma | Same |
| sked | as   |
| _arr | MA.m |
| ay(a | aske |
| , ma | d\_a |
| sk=N | rray |
| one, | but  |
|  fil | crea |
| l_va | tes  |
| lue= | a    |
| None | vari |
| , ax | able |
| es=N | inst |
| one, | ead. |
|  att | If   |
| ribu | no   |
| tes= | axes |
| None | are  |
| , id | spec |
| =Non | ifie |
| e)`` | d,   |
|      | the  |
|      | resu |
|      | lt   |
|      | has  |
|      | defa |
|      | ult  |
|      | axes |
|      | ,    |
|      | othe |
|      | rwis |
|      | e    |
|      | axes |
|      | is a |
|      | list |
|      | of   |
|      | axis |
|      | obje |
|      | cts  |
|      | matc |
|      | hing |
|      | a.sh |
|      | ape. |
+------+------+
| ``ma | Crea |
| sked | te   |
| _obj | vari |
| ect( | able |
| data | mask |
| , va | ed   |
| lue, | wher |
|  cop | e    |
| y=1, | exac |
|  sav | tly  |
| espa | data |
| ce=0 | equa |
| , ax | l    |
| es=N | to   |
| one, | valu |
|  att | e.   |
| ribu | Crea |
| tes= | te   |
| None | the  |
| , id | vari |
| =Non | able |
| e)`` | with |
|      | the  |
|      | give |
|      | n    |
|      | list |
|      | of   |
|      | axis |
|      | obje |
|      | cts, |
|      | attr |
|      | ibut |
|      | e    |
|      | dict |
|      | iona |
|      | ry,  |
|      | and  |
|      | stri |
|      | ng   |
|      | id.  |
+------+------+
| ``ma | Cons |
| sked | truc |
| _val | ts   |
| ues( | a    |
| data | vari |
| , va | able |
| lue, | with |
|  rto | the  |
| l=1e | give |
| -05, | n    |
|  ato | list |
| l=1e | of   |
| -08, | axes |
|  cop | and  |
| y=1, | attr |
|  sav | ibut |
| espa | e    |
| ce=0 | dict |
| , ax | iona |
| es=N | ry,  |
| one, | whos |
|  att | e    |
| ribu | mask |
| tes= | is   |
| None | set  |
| , id | at   |
| =Non | thos |
| e)`` | e    |
|      | plac |
|      | es   |
|      | wher |
|      | e    |
|      | ``ab |
|      | s(da |
|      | ta - |
|      |  val |
|      | ue)  |
|      | &lt; |
|      |  ato |
|      | l +  |
|      | rtol |
|      |  * a |
|      | bs(d |
|      | ata) |
|      | ``.  |
|      | This |
|      | is a |
|      | care |
|      | ful  |
|      | way  |
|      | of   |
|      | sayi |
|      | ng   |
|      | that |
|      | thos |
|      | e    |
|      | elem |
|      | ents |
|      | of   |
|      | the  |
|      | data |
|      | that |
|      | have |
|      | valu |
|      | e    |
|      | =    |
|      | valu |
|      | e    |
|      | (to  |
|      | with |
|      | in   |
|      | a    |
|      | tole |
|      | ranc |
|      | e)   |
|      | are  |
|      | to   |
|      | be   |
|      | trea |
|      | ted  |
|      | as   |
|      | inva |
|      | lid. |
|      | If   |
|      | data |
|      | is   |
|      | not  |
|      | of a |
|      | floa |
|      | ting |
|      | poin |
|      | t    |
|      | type |
|      | ,    |
|      | call |
|      | s    |
|      | mask |
|      | ed\_ |
|      | obje |
|      | ct   |
|      | inst |
|      | ead. |
+------+------+
| ``on | retu |
| es(s | rn   |
| hape | an   |
| , ty | arra |
| peco | y    |
| de=' | of   |
| l',  | all  |
| save | ones |
| spac | of   |
| e=0, | the  |
|  axe | give |
| s=no | n    |
| ne,  | leng |
| attr | th   |
| ibut | or   |
| es=n | shap |
| one, | e.   |
|  id= |      |
| none |      |
| )``  |      |
+------+------+
| ``re | copy |
| shap | of a |
| e(a, | with |
|  new | a    |
| shap | new  |
| e, a | shap |
| xes= | e.   |
| none |      |
| , at |      |
| trib |      |
| utes |      |
| =non |      |
| e, i |      |
| d=no |      |
| ne)` |      |
| `    |      |
+------+------+
| ``re | retu |
| size | rn   |
| (a,  | a    |
| new_ | new  |
| shap | arra |
| e, a | y    |
| xes= | with |
| none | the  |
| , at | spec |
| trib | ifie |
| utes | d    |
| =non | shap |
| e, i | e.   |
| d=no | the  |
| ne)` | orig |
| `    | inal |
|      | arra |
|      | ys   |
|      | tota |
|      | l    |
|      | size |
|      | can  |
|      | be   |
|      | any  |
|      | size |
|      | .    |
+------+------+
| ``ze | an   |
| ros( | arra |
| shap | y    |
| e, t | of   |
| ypec | all  |
| ode= | zero |
| 'l', | s    |
|  sav | of   |
| espa | the  |
| ce=0 | give |
| , ax | n    |
| es=n | leng |
| one, | th   |
|  att | or   |
| ribu | shap |
| tes= | e    |
| none |      |
| , id |      |
| =non |      |
| e)`` |      |
+------+------+

The following table describes the MV non-constructor functions. with the
exception of argsort, all functions return a transient variable.

Table 2.27 MV functions
                       

+------+------+
| Func | Desc |
| tion | ript |
|      | ion  |
+======+======+
| ``ar | Retu |
| gsor | rn   |
| t(x, | a    |
|  axi | Nume |
| s=-1 | ric  |
| , fi | arra |
| ll_v | y    |
| alue | of   |
| =Non | indi |
| e)`` | ces  |
|      | for  |
|      | sort |
|      | ing  |
|      | alon |
|      | g    |
|      | a    |
|      | give |
|      | n    |
|      | axis |
|      | .    |
+------+------+
| ``as | Same |
| arra | as   |
| y(da | ``cd |
| ta,  | ms.c |
| type | reat |
| code | eVar |
| =Non | iabl |
| e)`` | e(da |
|      | ta,  |
|      | type |
|      | code |
|      | , co |
|      | py=0 |
|      | )``. |
|      | This |
|      | is a |
|      | shor |
|      | t    |
|      | way  |
|      | of   |
|      | ensu |
|      | ring |
|      | that |
|      | some |
|      | thin |
|      | g    |
|      | is   |
|      | an   |
|      | inst |
|      | ance |
|      | of a |
|      | vari |
|      | able |
|      | of a |
|      | give |
|      | n    |
|      | type |
|      | befo |
|      | re   |
|      | proc |
|      | eedi |
|      | ng,  |
|      | as   |
|      | in   |
|      | ``da |
|      | ta = |
|      |  asa |
|      | rray |
|      | (dat |
|      | a)`` |
|      | .    |
|      | Also |
|      | see  |
|      | the  |
|      | vari |
|      | able |
|      | ``as |
|      | type |
|      | ()`` |
|      | func |
|      | tion |
|      | .    |
+------+------+
| ``av | Comp |
| erag | utes |
| e(a, | the  |
|  axi | aver |
| s=0, | age  |
|  wei | valu |
| ghts | e    |
| =Non | of   |
| e)`` | the  |
|      | non- |
|      | mask |
|      | ed   |
|      | elem |
|      | ents |
|      | of x |
|      | alon |
|      | g    |
|      | the  |
|      | sele |
|      | cted |
|      | axis |
|      | .    |
|      | If   |
|      | weig |
|      | hts  |
|      | is   |
|      | give |
|      | n,   |
|      | it   |
|      | must |
|      | matc |
|      | h    |
|      | the  |
|      | size |
|      | and  |
|      | shap |
|      | e    |
|      | of   |
|      | x,   |
|      | and  |
|      | the  |
|      | valu |
|      | e    |
|      | retu |
|      | rned |
|      | is:  |
|      | ``su |
|      | m(a* |
|      | weig |
|      | hts) |
|      | /sum |
|      | (wei |
|      | ghts |
|      | )``  |
|      | In   |
|      | comp |
|      | utin |
|      | g    |
|      | thes |
|      | e    |
|      | sums |
|      | ,    |
|      | elem |
|      | ents |
|      | that |
|      | corr |
|      | espo |
|      | nd   |
|      | to   |
|      | thos |
|      | e    |
|      | that |
|      | are  |
|      | mask |
|      | ed   |
|      | in x |
|      | or   |
|      | weig |
|      | hts  |
|      | are  |
|      | igno |
|      | red. |
+------+------+
| ``ch | Has  |
| oose | a    |
| (con | resu |
| diti | lt   |
| on,  | shap |
| t)`` | ed   |
|      | like |
|      | arra |
|      | y    |
|      | cond |
|      | itio |
|      | n.   |
|      | ``t` |
|      | `    |
|      | must |
|      | be a |
|      | tupl |
|      | e    |
|      | of   |
|      | two  |
|      | arra |
|      | ys   |
|      | ``t1 |
|      | ``   |
|      | and  |
|      | ``t2 |
|      | ``.  |
|      | Each |
|      | elem |
|      | ent  |
|      | of   |
|      | the  |
|      | resu |
|      | lt   |
|      | is   |
|      | the  |
|      | corr |
|      | espo |
|      | ndin |
|      | g    |
|      | elem |
|      | ent  |
|      | of   |
|      | ``t1 |
|      | ``\  |
|      | wher |
|      | e    |
|      | ``co |
|      | ndit |
|      | ion` |
|      | `    |
|      | is   |
|      | true |
|      | ,    |
|      | and  |
|      | the  |
|      | corr |
|      | espo |
|      | ndin |
|      | g    |
|      | elem |
|      | ent  |
|      | of   |
|      | ``t2 |
|      | ``   |
|      | wher |
|      | e    |
|      | ``co |
|      | ndit |
|      | ion` |
|      | `    |
|      | is   |
|      | fals |
|      | e.   |
|      | The  |
|      | resu |
|      | lt   |
|      | is   |
|      | mask |
|      | ed   |
|      | wher |
|      | e    |
|      | ``co |
|      | ndit |
|      | ion` |
|      | `    |
|      | is   |
|      | mask |
|      | ed   |
|      | or   |
|      | wher |
|      | e    |
|      | the  |
|      | sele |
|      | cted |
|      | elem |
|      | ent  |
|      | is   |
|      | mask |
|      | ed.  |
+------+------+
| ``co | Conc |
| ncat | aten |
| enat | ate  |
| e(ar | the  |
| rays | arra |
| , ax | ys   |
| is=0 | alon |
| , ax | g    |
| isid | the  |
| =Non | give |
| e, a | n    |
| xisa | axis |
| ttri | .    |
| bute | Give |
| s=No | the  |
| ne)` | exte |
| `    | nded |
|      | axis |
|      | the  |
|      | id   |
|      | and  |
|      | attr |
|      | ibut |
|      | es   |
|      | prov |
|      | ided |
|      | - by |
|      | defa |
|      | ult, |
|      | thos |
|      | e    |
|      | of   |
|      | the  |
|      | firs |
|      | t    |
|      | arra |
|      | y.   |
+------+------+
| ``co | Coun |
| unt( | t    |
| a, a | of   |
| xis= | the  |
| None | non- |
| )``  | mask |
|      | ed   |
|      | elem |
|      | ents |
|      | in   |
|      | ``a` |
|      | `,   |
|      | or   |
|      | alon |
|      | g    |
|      | a    |
|      | cert |
|      | ain  |
|      | axis |
|      | .    |
+------+------+
| ``is | Retu |
| Mask | rn   |
| edVa | true |
| riab | if   |
| le(x | ``x` |
| )``  | `    |
|      | is   |
|      | an   |
|      | inst |
|      | ance |
|      | of a |
|      | vari |
|      | able |
|      | .    |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _equ | mask |
| al(x | ed   |
| , va | wher |
| lue) | e    |
| ``   | ``x` |
|      | `    |
|      | equa |
|      | ls   |
|      | the  |
|      | scal |
|      | ar   |
|      | valu |
|      | e.   |
|      | For  |
|      | floa |
|      | ting |
|      | poin |
|      | t    |
|      | valu |
|      | es   |
|      | cons |
|      | ider |
|      | ``ma |
|      | sked |
|      | _val |
|      | ues( |
|      | x, v |
|      | alue |
|      | )``  |
|      | inst |
|      | ead. |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _gre | mask |
| ater | ed   |
| (x,  | wher |
| valu | e    |
| e)`` | ``x  |
|      | > va |
|      | lue` |
|      | `    |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _gre | mask |
| ater | ed   |
| _equ | wher |
| al(x | e    |
| , va | ``x  |
| lue) | >= v |
| ``   | alue |
|      | ``   |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _les | mask |
| s(x, | ed   |
|  val | wher |
| ue)` | e    |
| `    | ``x  |
|      | &lt; |
|      |  val |
|      | ue`` |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _les | mask |
| s_eq | ed   |
| ual( | wher |
| x, v | e    |
| alue | ``x  |
| )``  | &le; |
|      |  val |
|      | ue`` |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _not | mask |
| _equ | ed   |
| al(x | wher |
| , va | e    |
| lue) | ``x  |
| ``   | != v |
|      | alue |
|      | ``   |
+------+------+
| ``ma | ``x` |
| sked | `    |
| _out | with |
| side | mask |
| (x,  | of   |
| v1,  | all  |
| v2)` | valu |
| `    | es   |
|      | of   |
|      | ``x` |
|      | `    |
|      | that |
|      | are  |
|      | outs |
|      | ide  |
|      | ``[v |
|      | 1,v2 |
|      | ]``  |
+------+------+
| ``ma | Retu |
| sked | rn   |
| _whe | ``x` |
| re(c | `    |
| ondi | as a |
| tion | vari |
| , x, | able |
|  cop | mask |
| y=1) | ed   |
| ``   | wher |
|      | e    |
|      | cond |
|      | itio |
|      | n    |
|      | is   |
|      | true |
|      | .    |
|      | Also |
|      | mask |
|      | ed   |
|      | wher |
|      | e    |
|      | ``x` |
|      | `    |
|      | or   |
|      | ``co |
|      | ndit |
|      | ion` |
|      | `    |
|      | mask |
|      | ed.  |
|      | ``co |
|      | ndit |
|      | ion` |
|      | `    |
|      | is a |
|      | mask |
|      | ed   |
|      | arra |
|      | y    |
|      | havi |
|      | ng   |
|      | the  |
|      | same |
|      | shap |
|      | e    |
|      | as   |
|      | ``x` |
|      | `.   |
+------+------+
| ``ma | Comp |
| ximu | ute  |
| m(a, | the  |
|  b=N | maxi |
| one) | mum  |
| ``   | vali |
|      | d    |
|      | valu |
|      | es   |
|      | of   |
|      | ``x` |
|      | `    |
|      | if   |
|      | ``y` |
|      | `    |
|      | is   |
|      | ``No |
|      | ne`` |
|      | ;    |
|      | with |
|      | two  |
|      | argu |
|      | ment |
|      | s,   |
|      | retu |
|      | rn   |
|      | the  |
|      | elem |
|      | ent- |
|      | wise |
|      | larg |
|      | er   |
|      | of   |
|      | vali |
|      | d    |
|      | valu |
|      | es,  |
|      | and  |
|      | mask |
|      | the  |
|      | resu |
|      | lt   |
|      | wher |
|      | e    |
|      | eith |
|      | er   |
|      | ``x` |
|      | `    |
|      | or   |
|      | ``y` |
|      | `    |
|      | is   |
|      | mask |
|      | ed.  |
+------+------+
| ``mi | Comp |
| nimu | ute  |
| m(a, | the  |
|  b=N | mini |
| one) | mum  |
| ``   | vali |
|      | d    |
|      | valu |
|      | es   |
|      | of   |
|      | ``x` |
|      | `    |
|      | if   |
|      | ``y` |
|      | `    |
|      | is   |
|      | None |
|      | ;    |
|      | with |
|      | two  |
|      | argu |
|      | ment |
|      | s,   |
|      | retu |
|      | rn   |
|      | the  |
|      | elem |
|      | ent- |
|      | wise |
|      | smal |
|      | ler  |
|      | of   |
|      | vali |
|      | d    |
|      | valu |
|      | es,  |
|      | and  |
|      | mask |
|      | the  |
|      | resu |
|      | lt   |
|      | wher |
|      | e    |
|      | eith |
|      | er   |
|      | ``x` |
|      | `    |
|      | or   |
|      | ``y` |
|      | `    |
|      | is   |
|      | mask |
|      | ed.  |
+------+------+
| ``ou | Retu |
| terp | rn   |
| rodu | a    |
| ct(a | vari |
| , b) | able |
| ``   | such |
|      | that |
|      | ``re |
|      | sult |
|      | [i,  |
|      | j] = |
|      |  a[i |
|      | ] *  |
|      | b[j] |
|      | ``.  |
|      | The  |
|      | resu |
|      | lt   |
|      | will |
|      | be   |
|      | mask |
|      | ed   |
|      | wher |
|      | e    |
|      | ``a[ |
|      | i]`` |
|      | or   |
|      | ``b[ |
|      | j]`` |
|      | is   |
|      | mask |
|      | ed.  |
+------+------+
| ``po | ``a* |
| wer( | *b`` |
| a, b |      |
| )``  |      |
+------+------+
| ``pr | Prod |
| oduc | uct  |
| t(a, | of   |
|  axi | elem |
| s=0, | ents |
|  fil | alon |
| l_va | g    |
| lue= | axis |
| 1)`` | usin |
|      | g    |
|      | ``fi |
|      | ll_v |
|      | alue |
|      | ``   |
|      | for  |
|      | miss |
|      | ing  |
|      | elem |
|      | ents |
|      | .    |
+------+------+
| ``re | Retu |
| peat | rn   |
| (ar, | ``ar |
|  rep | ``   |
| eats | repe |
| , ax | ated |
| is=0 | ``re |
| )``  | peat |
|      | s``  |
|      | time |
|      | s    |
|      | alon |
|      | g    |
|      | ``ax |
|      | is`` |
|      | .    |
|      | ``re |
|      | peat |
|      | s``  |
|      | is a |
|      | sequ |
|      | ence |
|      | of   |
|      | leng |
|      | th   |
|      | ``ar |
|      | .sha |
|      | pe[a |
|      | xis] |
|      | ``   |
|      | tell |
|      | ing  |
|      | how  |
|      | many |
|      | time |
|      | s    |
|      | to   |
|      | repe |
|      | at   |
|      | each |
|      | elem |
|      | ent. |
+------+------+
| ``se | Set  |
| t_de | the  |
| faul | defa |
| t_fi | ult  |
| ll_v | fill |
| alue | valu |
| (val | e    |
| ue_t | for  |
| ype, | ``va |
|  val | lue_ |
| ue)` | type |
| `    | ``   |
|      | to   |
|      | ``va |
|      | lue` |
|      | `.   |
|      | ``va |
|      | lue_ |
|      | type |
|      | ``   |
|      | is a |
|      | stri |
|      | ng:  |
|      | 'rea |
|      | l',' |
|      | comp |
|      | lex' |
|      | ,'ch |
|      | arac |
|      | ter' |
|      | ,'in |
|      | tege |
|      | r',o |
|      | r    |
|      | 'obj |
|      | ect' |
|      | .    |
|      | ``va |
|      | lue` |
|      | `    |
|      | shou |
|      | ld   |
|      | be a |
|      | scal |
|      | ar   |
|      | or   |
|      | sing |
|      | le-e |
|      | leme |
|      | nt   |
|      | arra |
|      | y.   |
+------+------+
| ``so | Sort |
| rt(a | arra |
| r, a | y    |
| xis= | ``ar |
| -1)` | ``   |
| `    | elem |
|      | entw |
|      | ise  |
|      | alon |
|      | g    |
|      | the  |
|      | spec |
|      | ifie |
|      | d    |
|      | axis |
|      | .    |
|      | The  |
|      | corr |
|      | espo |
|      | ndin |
|      | g    |
|      | axis |
|      | in   |
|      | the  |
|      | resu |
|      | lt   |
|      | has  |
|      | dumm |
|      | y    |
|      | valu |
|      | es.  |
+------+------+
| ``su | Sum  |
| m(a, | of   |
|  axi | elem |
| s=0, | ents |
|  fil | alon |
| l_va | g    |
| lue= | a    |
| 0)`` | cert |
|      | ain  |
|      | axis |
|      | usin |
|      | g    |
|      | ``fi |
|      | ll_v |
|      | alue |
|      | ``   |
|      | for  |
|      | miss |
|      | ing. |
+------+------+
| ``ta | Retu |
| ke(a | rn   |
| , in | a    |
| dice | sele |
| s, a | ctio |
| xis= | n    |
| 0)`` | of   |
|      | item |
|      | s    |
|      | from |
|      | ``a` |
|      | `.   |
|      | See  |
|      | the  |
|      | docu |
|      | ment |
|      | atio |
|      | n    |
|      | in   |
|      | the  |
|      | Nume |
|      | ric  |
|      | manu |
|      | al.  |
+------+------+
| ``tr | Perf |
| ansp | orm  |
| ose( | a    |
| ar,  | reor |
| axes | deri |
| =Non | ng   |
| e)`` | of   |
|      | the  |
|      | axes |
|      | of   |
|      | arra |
|      | y    |
|      | ar   |
|      | depe |
|      | ndin |
|      | g    |
|      | on   |
|      | the  |
|      | tupl |
|      | e    |
|      | of   |
|      | indi |
|      | ces  |
|      | axes |
|      | ;    |
|      | the  |
|      | defa |
|      | ult  |
|      | is   |
|      | to   |
|      | reve |
|      | rse  |
|      | the  |
|      | orde |
|      | r    |
|      | of   |
|      | the  |
|      | axes |
|      | .    |
+------+------+
| ``wh | ``x` |
| ere( | `    |
| cond | wher |
| itio | e    |
| n, x | ``co |
| , y) | ndit |
| ``   | ion` |
|      | `    |
|      | is   |
|      | true |
|      | ,    |
|      | ``y` |
|      | `    |
|      | othe |
|      | rwis |
|      | e    |
+------+------+

2.10 HorizontalGrid
^^^^^^^^^^^^^^^^^^^

A HorizontalGrid represents a latitude-longitude coordinate system. In
addition, it optionally describes how lat-lon space is partitioned into
cells. Specifically, a HorizontalGrid:

-  consists of a latitude and longitude coordinate axis.
-  may have associated boundary arrays describing the grid cell
   boundaries,
-  may optionally have an associated logical mask.

CDMS supports several types of HorizontalGrids:

Table 2.28
          

+------+------+
| Grid | Defi |
| Type | niti |
|      | on   |
+======+======+
| ``Re | Asso |
| ctGr | ciat |
| id`` | ed   |
|      | lati |
|      | tude |
|      | an   |
|      | long |
|      | itud |
|      | e    |
|      | are  |
|      | 1-D  |
|      | axes |
|      | ,    |
|      | with |
|      | stri |
|      | ctly |
|      | mono |
|      | toni |
|      | c    |
|      | valu |
|      | es.  |
+------+------+
| ``Cu | Lati |
| rveG | tude |
| rid` | and  |
| `    | long |
|      | itud |
|      | e    |
|      | are  |
|      | 2-D  |
|      | coor |
|      | dina |
|      | te   |
|      | axes |
|      | (Axi |
|      | s2D) |
|      | .    |
+------+------+
| ``Ge | Lati |
| neri | tude |
| cGri | and  |
| d``  | long |
|      | itud |
|      | e    |
|      | are  |
|      | 1-D  |
|      | auxi |
|      | liar |
|      | y    |
|      | coor |
|      | dina |
|      | te   |
|      | axis |
|      | (Aux |
|      | Axis |
|      | 1D)  |
+------+------+

Table 2.29 HorizontalGrid Internal Attribute
                                            

+-----------------------+------------------+------------------------------------------------+
| Type                  | Name             | Definition                                     |
+=======================+==================+================================================+
| Dictionary            | ``attributes``   | External attribute dictionary.                 |
+-----------------------+------------------+------------------------------------------------+
| String                | ``id``           | The grid identifier.                           |
+-----------------------+------------------+------------------------------------------------+
| Dataset or CdmsFile   | ``parent``       | The dataset or file which contains the grid.   |
+-----------------------+------------------+------------------------------------------------+
| Tuple                 | ``shape``        | The shape of the grid, a 2-tuple               |
+-----------------------+------------------+------------------------------------------------+

Table 2.31 on page 82 describes the methods that apply to all types of
HorizontalGrids. Table 2.32 on page 86 describes the additional methods
that are unique to RectGrids.

Table 2.30 RectGrid Constructors
                                

+------+------+
| Cons | Desc |
| truc | ript |
| tor  | ion  |
+======+======+
| ``cd | Crea |
| ms.c | te   |
| reat | a    |
| eRec | grid |
| tGri | not  |
| d(la | asso |
| t, l | ciat |
| on,  | ed   |
| orde | with |
| r, t | a    |
| ype= | file |
| "gen | or   |
| eric | data |
| ", m | set. |
| ask= | See  |
| None | Tabl |
| )``  | e    |
|      | 2.2  |
|      | on   |
|      | page |
|      | 33.  |
+------+------+
| ``Cd | Crea |
| msFi | te   |
| le.c | a    |
| reat | grid |
| eRec | asso |
| tGri | ciat |
| d(id | ed   |
| , la | with |
| t, l | a    |
| on,  | file |
| orde | .    |
| r, t | See  |
| ype= | Tabl |
| "gen | e    |
| eric | 2.14 |
| ", m | on   |
| ask= | page |
| None | 53.  |
| )``  |      |
+------+------+
| ``Da | Crea |
| tase | te   |
| t.cr | a    |
| eate | grid |
| Rect | asso |
| Grid | ciat |
| (id, | ed   |
|  lat | with |
| , lo | a    |
| n, o | data |
| rder | set. |
| , ty | See  |
| pe=" | Tabl |
| gene | e    |
| ric" | 2.25 |
| , ma | on   |
| sk=N | page |
| one) | 71.  |
| ``   |      |
+------+------+
| ``cd | See  |
| ms.c | Tabl |
| reat | e    |
| eGau | 2.2  |
| ssia | on   |
| nGri | page |
| d(nl | 33.  |
| ats, |      |
|  xor |      |
| igin |      |
| =0.0 |      |
| , or |      |
| der= |      |
| "yx" |      |
| )``  |      |
+------+------+
| ``cd | See  |
| ms.c | Tabl |
| reat | e    |
| eGen | 2.2  |
| eric | on   |
| Grid | page |
| (lat | 18.  |
| Arra |      |
| y, l |      |
| onAr |      |
| ray, |      |
|  lat |      |
| Boun |      |
| ds=N |      |
| one, |      |
|  lon |      |
| Boun |      |
| ds=N |      |
| one, |      |
|  ord |      |
| er=" |      |
| yx", |      |
|  mas |      |
| k=No |      |
| ne)` |      |
| `    |      |
+------+------+
| ``cd | See  |
| ms.c | Tabl |
| reat | e    |
| eGlo | 2.2  |
| balM | on   |
| eanG | page |
| rid( | 18.  |
| grid |      |
| )``  |      |
+------+------+
| ``cd | See  |
| ms.c | Tabl |
| reat | e    |
| eRec | 2.2  |
| tGri | on   |
| d(la | page |
| t, l | 18.  |
| on,  |      |
| orde |      |
| r, t |      |
| ype= |      |
| "gen |      |
| eric |      |
| ", m |      |
| ask= |      |
| None |      |
| )``  |      |
+------+------+
| ``cd | See  |
| ms.c | Tabl |
| reat | e    |
| eUni | 2.2  |
| form | on   |
| Grid | page |
| (sta | 18.  |
| rtLa |      |
| t, n |      |
| lat, |      |
|  del |      |
| taLa |      |
| t, s |      |
| tart |      |
| Lon, |      |
|  nlo |      |
| n, d |      |
| elta |      |
| Lon, |      |
|  ord |      |
| er=" |      |
| yx", |      |
|  mas |      |
| k=No |      |
| ne)` |      |
| `    |      |
+------+------+
| ``cd | See  |
| ms.c | Tabl |
| reat | e    |
| eZon | 2.2  |
| alGr | on   |
| id(g | page |
| rid) | 18   |
| ``   |      |
+------+------+

Table 2.31 HorizontalGrid Methods
                                 

.. raw:: html

   <table class="table">

.. raw:: html

   <tbody>

::

    <tr>
      <th>Type</th>

      <th>Method</th>

      <th>Description</th>
    </tr>

    <tr>
      <td>
        <p><span>Horizontal-Grid</span></p>
      </td>

      <td><code>clone()</code></td>

      <td>
        <p>Return a transient copy of the grid.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getAxis(Integer n)</code></td>

      <td>
        <p>Get the n-th axis.n is either 0 or 1.</p>
      </td>
    </tr>

    <tr>
      <td>Tuple</td>

      <td><code>getBounds()</code></td>

      <td>
        <p>Get the grid boundary arrays.</p>

        <p>Returns a tuple <code>(latitudeArray, longitudeArray)</code>, where
        latitudeArray is a Numeric array of latitude bounds, and similarly for
        longitudeArray.The shape of latitudeArray and longitudeArray depend on the type
        of grid:</p>

        <ul>
          <li>for rectangular grids with shape (nlat, nlon), the boundary arrays have
          shape (nlat,2) and (nlon,2).</li>

          <li>for curvilinear grids with shape (nx, ny), the boundary arrays each have
          shape (nx, ny, 4).</li>

          <li>for generic grids with shape (ncell,), the boundary arrays each have
          shape (ncell, nvert) where nvert is the maximum number of vertices per
          cell.</li>
        </ul>

        <p>For rectilinear grids: If no boundary arrays are explicitly defined (in the
        file or dataset), the result depends on the auto- Bounds mode (see
        <code>cdms.setAutoBounds</code>) and the grid classification mode (see
        <code>cdms.setClassifyGrids</code>). By default, autoBounds mode is enabled, in
        which case the boundary arrays are generated based on the type of grid. If
        disabled, the return value is (None,None).For rectilinear grids: The grid
        classification mode specifies how the grid type is to be determined. By
        default, the grid type (Gaussian, uniform, etc.) is determined by calling
        <span>grid.classifyInFamily</span>. If the mode is 'off'
        <span>grid.getType</span> is used instead.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getLatitude()</code></td>

      <td>
        <p>Get the latitude axis of this grid.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getLongitude()</code></td>

      <td>
        <p>Get the latitude axis of this grid.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getMask()</code></td>

      <td>
        <p>Get the mask array of this grid, if any.Returns a 2-D Numeric array, having
        the same shape as the grid. If the mask is not explicitly defined, the return
        value is <code>None</code>.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getMesh(self, transpose=None)</code></td>

      <td>
        <p>Generate a mesh array for the meshfill graphics method.If transpose is
        defined to a tuple, say (1,0), first transpose latbounds and lonbounds
        according to the tuple, in this case (1,0,2).</p>
      </td>
    </tr>

    <tr>
      <td>None</td>

      <td><code>setBounds(latBounds, lonBounds, persistent=0)</code></td>

      <td>
        <p>Set the grid boundaries.<code>latBounds</code> is a NumPy array of shape
        (n,2), such that the boundaries of the kth axis value are
        <code>[latBounds[k,0],latBounds[k,1] ]</code>. <code>lonBounds</code> is
        defined similarly for the longitude array. <b>Note:</b> By default, the
        boundaries are not written to the file or dataset containing the grid (if any).
        This allows bounds to be set on read-only files, for regridding. If the
        optional argument <code>persistent</code> is set to 1, the boundary array is
        written to the file.</p>
      </td>
    </tr>

    <tr>
      <td>None</td>

      <td><code>setMask(mask, persistent=0)</code></td>

      <td>
        <p>Set the grid mask. If <code>persistent == 1</code>, the mask values are
        written to the associated file, if any. Otherwise, the mask is associated with
        the grid, but no I/O is generated. <code>mask</code> is a two-dimensional,
        Boolean-valued Numeric array, having the same shape as the grid.</p>
      </td>
    </tr>

    <tr>
      <td>Horizontal-Grid</td>

      <td><code>subGridRegion(latInterval, lonInterval)</code></td>

      <td>
        <p>Create a new grid corresponding to the coordinate region defined by
        <code>latInterval, lonInterval.</code></p>

        <p><code>latInterval</code> and <code>lonInterval</code> are the coordinate
        intervals for latitude and longitude, respectively.</p>

        <p>Each interval is a tuple having one of the forms:</p>

        <ul>
          <li><code>(x,y)</code></li>

          <li><code>(x,y,indicator)</code></li>

          <li><code>(x,y,indicator,cycle)</code></li>

          <li><code>None</code></li>
        </ul>

        <p>where <code>x</code> and <code>y</code> are coordinates indicating the
        interval <code>[x,y)</code>, and:</p>

        <p><code><span>indicator</span></code> is a two-character string, where the
        first character is 'c' if the interval is closed on the left, 'o' if open, and
        the second character has the same meaning for the right-hand point. (Default:
        'co').</p>

        <p><span>If <code>cycle</code> is specified, the axis is treated as circular
        with the given cycle value. By default, if <code>grid.isCircular()</code> is
        true, the axis is treated as circular with a default value of 360.0.</span></p>

        <p>An interval of <code>None</code> returns the full index interval of the
        axis.</p>

        <p>If a mask is defined, the subgrid also has a mask corresponding to the index
        ranges.Note: The result grid is not associated with any file or dataset.</p>
      </td>
    </tr>

    <tr>
      <td>
        <p>Transient-CurveGrid</p>
      </td>

      <td><code>toCurveGrid(gridid=None)</code></td>

      <td>
        <p>Convert to a curvilinear grid. If the grid is already curvilinear, a copy of
        the grid object is returned. <code>gridid</code> is the string identifier of
        the resulting curvilinear grid object. If unspecified, the grid ID is copied.
        <b>Note:</b> This method does not apply to generic grids.</p>
      </td>
    </tr>

    <tr>
      <td>
        <p>Transient-GenericGrid</p>
      </td>

      <td><code>toGenericGrid(gridid=None)</code></td>

      <td>
        <p>Convert to a generic grid. If the grid is already generic, a copy of the
        grid is returned. <code>gridid</code> is the string identifier of the resulting
        curvilinear grid object. If unspecified, the grid ID is copied.</p>
      </td>
    </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

Table 2.32 RectGrid Methods, additional to HorizontalGrid Methods
                                                                 

.. raw:: html

   <table class="table">

.. raw:: html

   <tr>

::

    <th>Type</th>

    <th>Method</th>

    <th>Description</th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <td>String</td>

    <td><code>getOrder()</code></td>

    <td>Get the grid ordering, either "yx" if latitude is the first axis, or "xy" if
    longitude is the first axis.</td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <td>String</td>

    <td><code>getType()</code></td>

    <td>Get the grid type, either "gaussian", "uniform", "equalarea", or
    "generic".</td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <td>(Array,Array)</td>

    <td><code>getWeights()</code></td>

    <td>
      <p>Get the normalized area weight arrays, as a tuple <code>(latWeights,
      lonWeights)</code>. It is assumed that the latitude and longitude axes are
      defined in degrees.</p>

      <p>The latitude weights are defined as:</p>

      <p><code>latWeights[i] = 0.5 * abs(sin(latBounds[i+1]) -
      sin(latBounds[i]))</code></p>

      <p>The longitude weights are defined as:</p>

      <p><code>lonWeights[i] = abs(lonBounds[i+1] - lonBounds[i])/360.0</code></p>

      <p>For a global grid, the weight arrays are normalized such that the sum of the
      weights is 1.0</p>

      <p><b>Example:</b></p>

      <p>Generate the 2-D weights array, such that <code>weights[i.j]</code> is the
      fractional area of grid zone <code>[i,j]</code>.</p>
      <pre style="word-break:normal;">

from cdms import MV latwts, lonwts = grid.getWeights() weights =
MV.outerproduct(latwts, lonwts)

.. raw:: html

   </pre>

::

      <p>Also see the function <code>area_weights</code> in module
      <code>pcmdi.weighting</code>.</p>
    </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <td>None</td>

    <td><code>setType(gridtype)</code></td>

    <td>Set the grid type. <code>gridtype</code> is one of "gaussian", "uniform",
    "equalarea", or "generic".</td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <td>RectGrid</td>

    <td><code>subGrid((latStart,latStop),(lonStart,lonStop))</code></td>

    <td>
      <p>Create a new grid, with latitude index range [latStart : latStop] and
      longitude index range [lonStart : lonStop]. Either index range can also be
      specified as None, indicating that the entire range of the latitude or longitude
      is used.</p>

      <p><b>Example:</b></p>

      <p>This creates newgrid corresponding to all latitudes and index range
      [lonStart:lonStop] of oldgrid.</p>

      <p><code>newgrid = oldgrid.subGrid(None, (lonStart, lonStop))</code></p>

      <p>If a mask is defined, the subgrid also has a mask corresponding to the index
      ranges.</p>

      <p><b>Note:</b> The result grid is not associated with any file or dataset.</p>
    </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

::

    <td>RectGrid</td>

    <td><code>transpose()</code></td>

    <td>
      <p>Create a new grid, with axis order reversed. The grid mask is also
      transposed.</p>

      <p><b>Note:</b> The result grid is not associated with any file or dataset.</p>
    </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>

2.11 Variable
^^^^^^^^^^^^^

A Variable is a multidimensional data object, consisting of:

-  a multidimensional data array, possibly masked,
-  a collection of attributes
-  a domain, an ordered tuple of CoordinateAxis objects.

A Variable which is contained in a Dataset or CdmsFile is called a
persistent variable. Setting a slice of a persistent Variable writes
data to the Dataset or file, and referencing a Variable slice reads data
from the Dataset. Variables may also be transient, not associated with a
Dataset or CdmsFile.

Variables support arithmetic operations, including the basic Python
operators (+,,\*,/,\*\*, abs, and sqrt), as well as the operations
defined in the MV module. The result of an arithmetic operation is a
transient variable, that is, the axis information is transferred to the
result.

The methods subRegion and subSlice return transient variables. In
addition, a transient variable may be created with the
cdms.createVariable method. The vcs and regrid module methods take
advantage of the attribute, domain, and mask information in a transient
variable.

Table 2.33 Variable Internal Attributes
                                       

+------+------+------+
| Type | Name | Defi |
|      |      | niti |
|      |      | on   |
+======+======+======+
| Dict | ``at | Exte |
| iona | trib | rnal |
| ry   | utes | attr |
|      | ``   | ibut |
|      |      | e    |
|      |      | dict |
|      |      | iona |
|      |      | ry.  |
+------+------+------+
| Stri | ``id | Vari |
| ng   | ``   | able |
|      |      | iden |
|      |      | tifi |
|      |      | er.  |
+------+------+------+
| Stri | ``na | The  |
| ng   | me\_ | name |
|      | in\_ | of   |
|      | file | the  |
|      | ``   | vari |
|      |      | able |
|      |      | in   |
|      |      | the  |
|      |      | file |
|      |      | or   |
|      |      | file |
|      |      | s    |
|      |      | whic |
|      |      | h    |
|      |      | repr |
|      |      | esen |
|      |      | t    |
|      |      | the  |
|      |      | data |
|      |      | set. |
|      |      | If   |
|      |      | diff |
|      |      | eren |
|      |      | t    |
|      |      | from |
|      |      | id,  |
|      |      | the  |
|      |      | vari |
|      |      | able |
|      |      | is   |
|      |      | alia |
|      |      | sed. |
+------+------+------+
| Data | ``pa | The  |
| set  | rent | data |
| or   | ``   | set  |
| Cdms |      | or   |
| File |      | file |
|      |      | whic |
|      |      | h    |
|      |      | cont |
|      |      | ains |
|      |      | the  |
|      |      | vari |
|      |      | able |
|      |      | .    |
+------+------+------+
| Tupl | ``sh | The  |
| e    | ape` | leng |
|      | `    | th   |
|      |      | of   |
|      |      | each |
|      |      | axis |
|      |      | of   |
|      |      | the  |
|      |      | vari |
|      |      | able |
+------+------+------+

Table 2.34 Variable Constructors
                                

.. raw:: html

   <table class="table">

::

    <tr>
      <th>Constructor</th>

      <th>Description</th>
    </tr>

    <tr>
      <td><code>Dataset.createVariable(String id, String datatype, List axes)</code></td>

      <td>Create a Variable in a Dataset. This function is not yet implemented.</td>
    </tr>

    <tr>
      <td><code>CdmsFile.createVariable(String id, String datatype, List
      axesOr-Grids)</code></td>

      <td>Create a Variable in a CdmsFile. <code>id</code> is the name of the variable.
      <code>datatype</code> is the MA or Numeric typecode, for example, MA.Float.
      <code>axesOrGrids</code> is a list of Axis and/or Grid objects, on which the
      variable is defined. Specifying a rectilinear grid is equivalent to listing the
      grid latitude and longitude axes, in the order defined for the grid. **Note:** this
      argument can either be a list or a tuple. If the tuple form is used, and there is
      only one element, it must have a following comma, e.g.:
      <code>(axisobj,)</code>.</td>
    </tr>

    <tr>
      <td><pre style="word-break:normal;">cdms.createVariable(array, typecode=None, copy=0, savespace=0,mask=None, fill_value=None, grid=None, axes=None,attributes=None, id=None)</pre></td>

      <td>Create a transient variable, not associated with a file or dataset.
      <code>array</code> is the data values: a Variable, masked array, or Numeric array.
      <code>typecode</code> is the MA typecode of the array. Defaults to the typecode of
      array. <code>copy</code> is an integer flag: if 1, the variable is created with a
      copy of the array, if 0 the variable data is shared with array.
      <code>savespace</code> is an integer flag: if set to 1, internal Numeric operations
      will attempt to avoid silent upcasting. <code>mask</code> is an array of integers
      with value 0 or 1, having the same shape as array. array elements with a
      corresponding mask value of 1 are considered invalid, and are not used for
      subsequent Numeric operations. The default mask is obtained from array if present,
      otherwise is None. <code>fill_value</code> is the missing value flag. The default
      is obtained from array if possible, otherwise is set to 1.0e20 for floating point
      variables, 0 for integer-valued variables. <code>grid</code> is a rectilinear grid
      object. <code>axes</code> is a tuple of axis objects. By default the axes are
      obtained from array if present. Otherwise for a dimension of length n, the default
      axis has values [0., 1., ..., double(n)]. <code>attributes</code> is a dictionary
      of attribute values. The dictionary keys must be strings. By default the dictionary
      is obtained from array if present, otherwise is empty. <code>id</code> is the
      string identifier of the variable. By default the id is obtained from array if
      possible, otherwise is set to 'variable_n' for some integer n.</td>
    </tr>

.. raw:: html

   </table>

Table 2.35 Variable Methods
                           

.. raw:: html

   <table class="table">

::

    <tr>
      <th>Type</th>

      <th>Method</th>

      <th>Definition</th>
    </tr>

    <tr>
      <td>Variable</td>

      <td><code>tvar = var[ i:j, m:n]</code></td>

      <td>Read a slice of data from the file or dataset, resulting in a transient
      variable. Singleton dimensions are 'squeezed' out. Data is returned in the physical
      ordering defined in the dataset. The forms of the slice operator are listed in
      Table 2.36 on page 102.</td>
    </tr>

    <tr>
      <td>None</td>

      <td><code>var[ i:j, m:n] = array</code></td>

      <td>Write a slice of data to the external dataset. The forms of the slice operator
      are listed in Table 2.21 on page 32. (Variables in CdmsFiles only)</td>
    </tr>

    <tr>
      <td>Variable</td>

      <td><code>tvar = var(selector)</code></td>

      <td>Calling a variable as a function reads the region of data defined by the
      selector. The result is a transient variable, unless raw=1 keyword is specified.
      See "Selectors" on page 103.</td>
    </tr>

    <tr>
      <td>None</td>

      <td><code>assignValue(Array ar)</code></td>

      <td>Write the entire data array. Equivalent to <code>var[:] = ar</code>. (Variables
      in CdmsFiles only).</td>
    </tr>

    <tr>
      <td>Variable</td>

      <td><code>astype(typecode)</code></td>

      <td>Cast the variable to a new datatype. Typecodes are as for MV, MA, and Numeric
      modules.</td>
    </tr>

    <tr>
      <td>Variable</td>

      <td><code>clone(copyData=1)</code></td>

      <td>
        <p>Return a copy of a transient variable.</p>

        <p>If copyData is 1 (the default) the variable data is copied as well. If
        copyData is 0, the result transient variable shares the original transient
        variables data array.</p>
      </td>
    </tr>

    <tr>
      <td>Transient Variable</td>

      <td><pre style="word-break:normal;">crossSectionRegrid(newLevel, newLatitude, method="log", missing=None, order=None)</pre></td>

      <td>
        <p>Return a lat/level vertical cross-section regridded to a new set of latitudes
        newLatitude and levels newLevel. The variable should be a function of latitude,
        level, and (optionally) time.</p>

        <p><code>newLevel</code> is an axis of the result pressure levels.</p>

        <p><code>newLatitude</code> is an axis of the result latitudes.</p>

        <p><code>method</code> is optional, either "log" to interpolate in the log of
        pressure (default), or "linear" for linear interpolation.</p>

        <p><code>missing</code> is a missing data value. The default is
        <code>var.getMissing()</code></p>

        <p><code>order</code> is an order string such as "tzy" or "zy". The default is
        <code>var.getOrder()</code>.</p>

        <p><i>See also:</i> <code>regrid</code>, <code>pressureRegrid</code>.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getAxis(n)</code></td>

      <td>
        <p>Get the n-th axis.</p>

        <p><code>n</code> is an integer.</p>
      </td>
    </tr>

    <tr>
      <td>List</td>

      <td><code>getAxisIds()</code></td>

      <td>Get a list of axis identifiers.</td>
    </tr>

    <tr>
      <td>Integer</td>

      <td><code>getAxisIndex(axis_spec)</code></td>

      <td>
        <p>Return the index of the axis specificed by axis_spec. Return -1 if no
        match.</p>

        <p><code>axis_spec</code> is a specification as defined for getAxisList</p>
      </td>
    </tr>

    <tr>
      <td>List</td>

      <td><code>getAxisList(axes=None, omit=None, order=None)</code></td>

      <td>
        <p>Get an ordered list of axis objects in the domain of the variable.</p>

        <p>If <code>axes</code> is not <code>None</code>, include only certain axes.
        Otherwise axes is a list of specifications as described below. Axes are returned
        in the order specified unless the order keyword is given.</p>

        <p>If <code>omit</code> is not <code>None</code>, omit those specified by an
        integer dimension number. Otherwise omit is a list of specifications as described
        below.</p>

        <p><code>order</code> is an optional string determining the output order.</p>

        <p>Specifications for the axes or omit keywords are a list, each element having
        one of the following forms:</p>

        <ul>
          <li>an integer dimension index, starting at 0.</li>

          <li>a string representing an axis id or one of the strings 'time', 'latitude',
          'lat', 'longitude', 'lon', 'lev' or 'level'.</li>

          <li>a function that takes an axis as an argument and returns a value. If the
          value returned is true, the axis matches.</li>

          <li>an axis object; will match if it is the same object as axis.</li>
        </ul>

        <p><code>order</code> can be a string containing the characters t,x,y,z, or -. If
        a dash ('-') is given, any elements of the result not chosen otherwise are filled
        in from left to right with remaining candidates.</p>
      </td>
    </tr>

    <tr>
      <td>List</td>

      <td><code>getAxisListIndex(axes=None, omit=None, order=None)</code></td>

      <td>Return a list of indices of axis objects. Arguments are as for
      getAxisList.</td>
    </tr>

    <tr>
      <td>List</td>

      <td><code>getDomain()</code></td>

      <td>Get the domain. Each element of the list is itself a tuple of the form
      <code>(axis,start,length,true_length)</code> where axis is an axis object, start is
      the start index of the domain relative to the axis object, length is the length of
      the axis, and true_length is the actual number of (defined) points in the domain.
      <i>See also:</i> <code>getAxisList</code>.</td>
    </tr>

    <tr>
      <td>Horizontal-Grid</td>

      <td><code>getGrid()</code></td>

      <td>Return the associated grid, or <code>None</code> if the variable is not
      gridded.</td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getLatitude()</code></td>

      <td>Get the latitude axis, or <code>None</code> if not found.</td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getLevel()</code></td>

      <td>Get the vertical level axis, or <code>None</code> if not found.</td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getLongitude()</code></td>

      <td>Get the longitude axis, or <code>None</code> if not found.</td>
    </tr>

    <tr>
      <td>Various</td>

      <td><code>getMissing()</code></td>

      <td>Get the missing data value, or <code>None</code> if not found.</td>
    </tr>

    <tr>
      <td>String</td>

      <td><code>getOrder()</code></td>

      <td>
        <p>Get the order string of a spatio-temporal variable. The order string specifies
        the physical ordering of the data. It is a string of characters with length equal
        to the rank of the variable, indicating the order of the variable's time, level,
        latitude, and/or longitude axes. Each character is one of:</p>

        <ul>
          <li>'t': time</li>

          <li>'z': vertical level</li>

          <li>'y': latitude</li>

          <li>'x': longitude</li>

          <li>'-': the axis is not spatio-temporal.</li>
        </ul>

        <p><b>Example:</b></p>

        <p>A variable with ordering "tzyx" is 4-dimensional, where the ordering of axes
        is (time, level, latitude, longitude).</p>

        <p><b>Note:</b> The order string is of the form required for the order argument
        of a regridder function.</p>
      </td>
    </tr>

    <tr>
      <td>List</td>

      <td><code>getPaths(*intervals)</code></td>

      <td>
        <p>Get the file paths associated with the index region specified by
        intervals.</p>

        <p><code>intervals</code> is a list of scalars, 2-tuples representing [i,j),
        slices, and/or Ellipses. If no <code>argument(s)</code> are present, all file
        paths associated with the variable are returned.</p>

        <p>Returns a list of tuples of the form (path,slicetuple), where path is the path
        of a file, and slicetuple is itself a tuple of slices, of the same length as the
        rank of the variable, representing the portion of the variable in the file
        corresponding to intervals.</p>

        <p><b>Note:</b> This function is not defined for transient variables.</p>
      </td>
    </tr>

    <tr>
      <td>Axis</td>

      <td><code>getTime()</code></td>

      <td>Get the time axis, or <code>None</code> if not found.</td>
    </tr>

    <tr>
      <td>Integer</td>

      <td><code>len(var)</code></td>

      <td>
        <p>The length of the first dimension of the variable. If the variable is
        zero-dimensional (scalar), a length of 0 is returned.</p>

        <p><b>Note:</b> <code>size()</code> returns the total number of elements.</p>
      </td>
    </tr>

    <tr>
      <td>Transient Variable</td>

      <td><code>pressureRegrid (newLevel, method="log", missing=None,
      order=None)</code></td>

      <td>
        <p>Return the variable regridded to a new set of pressure levels newLevel. The
        variable must be a function of latitude, longitude, pressure level, and
        (optionally) time.</p>

        <p><code>newLevel</code> is an axis of the result pressure levels.</p>

        <p><code>method</code> is optional, either "log" to interpolate in the log of
        pressure (default), or "linear" for linear interpolation.</p>

        <p><code>missing</code> is a missing data value. The default is
        <code>var.getMissing()</code></p>

        <p><code>order</code> is an order string such as "tzyx" or "zyx". The default is
        <code>var.getOrder()</code></p>

        <p>See also: <code>regrid</code>, <code>crossSectionRegrid</code>.</p>
      </td>
    </tr>

    <tr>
      <td>Integer</td>

      <td><code>rank()</code></td>

      <td>The number of dimensions of the variable.</td>
    </tr>

    <tr>
      <td>Transient</td>

      <td>
        <pre style="word-break:normal;">

regrid (togrid, missing=None, order=None, Variable mask=None)

.. raw:: html

   </pre>

::

      </td>

      <td>
        <p>Return the variable regridded to the horizontal grid togrid.</p>

        <p><code>missing</code> is a Float specifying the missing data value. The default
        is 1.0e20.</p>

        <p><code>order</code> is a string indicating the order of dimensions of the
        array. It has the form returned from <code>variable.getOrder()</code>. For
        example, the string "tzyx" indicates that the dimension order of array is (time,
        level, latitude, longitude). If unspecified, the function assumes that the last
        two dimensions of array match the input grid.</p>

        <p><code>mask</code> is a Numeric array, of datatype Integer or Float, consisting
        of ones and zeros. A value of 0 or 0.0 indicates that the corresponding data
        value is to be ignored for purposes of regridding. If mask is two-dimensional of
        the same shape as the input grid, it overrides the mask of the input grid. If the
        mask has more than two dimensions, it must have the same shape as array. In this
        case, the missing data value is also ignored. Such an n-dimensional mask is
        useful if the pattern of missing data varies with level (e.g., ocean data) or
        time. Note: If neither missing or mask is set, the default mask is obtained from
        the mask of the array if any.</p>

        <p>See also: <code>crossSectionRegrid</code>, <code>pressureRegrid</code>.</p>
      </td>
    </tr>

    <tr>
      <td><code>None</code></td>

      <td><code>setAxis(n, axis)</code></td>

      <td>Set the n-th axis (0-origin index) of to a copy of axis.</td>
    </tr>

    <tr>
      <td><code>None</code></td>

      <td><code>setAxisList(axislist)</code></td>

      <td>Set all axes of the variable. axislist is a list of axis objects.</td>
    </tr>

    <tr>
      <td><code>None</code></td>

      <td><code>setMissing(value)</code></td>

      <td>Set the missing value.</td>
    </tr>

    <tr>
      <td>Integer</td>

      <td><code>size()</code></td>

      <td>Number of elements of the variable.</td>
    </tr>

    <tr>
      <td>Variable</td>

      <td>
        <pre style="word-break:normal;">

subRegion(\*region, time=None, level=None, latitude=None,
longitude=None, squeeze=0, raw=0)

.. raw:: html

   </pre>

::

      </td>

      <td>
        <p>Read a coordinate region of data, returning a transient variable. A region is
        a hyperrectangle in coordinate space.</p>

        <p><code>region</code> is an argument list, each item of which specifies an
        interval of a coordinate axis. The intervals are listed in the order of the
        variable axes. If trailing dimensions are omitted, all values of those dimensions
        are retrieved. If an axis is circular (axis.isCircular() is true) or cycle is
        specified (see below), then data will be read with wraparound in that dimension.
        Only one axis may be read with wraparound. A coordinate interval has one of the
        forms listed in Table 2.37 on page 102. Also see
        <code>axis.mapIntervalExt</code>.</p>

        <p>The optional keyword arguments <code>time</code>, <code>level</code>,
        <code>latitude</code>, and <code>longitude</code> may also be used to specify the
        dimension for which the interval applies. This is particularly useful if the
        order of dimensions is not known in advance. An exception is raised if a keyword
        argument conflicts with a positional region argument.</p>

        <p>The optional keyword argument <code>squeeze</code> determines whether or not
        the shape of the returned array contains dimensions whose length is 1; by default
        this argument is 0, and such dimensions are not 'squeezed out'.</p>

        <p>The optional keyword argument <code>raw</code> specifies whether the return
        object is a variable or a masked array. By default, a transient variable is
        returned, having the axes and attributes corresponding to2,3 the region read. If
        raw=1, an MA masked array is returned, equivalent to the transient variable
        without the axis and attribute information.</p>
      </td>
    </tr>

    <tr>
      <td>Variable</td>

      <td>
        <pre style="word-break:normal;">

subSlice(\*specs, time=None, level=None, latitude=None, longitude=None,
squeeze=0, raw=0)

.. raw:: html

   </pre>

::

      </td>

      <td>
        <p>Read a slice of data, returning a transient variable. This is a functional
        form of the slice operator [] with the squeeze option turned off.</p>

        <p><code>specs</code> is an argument list, each element of which specifies a
        slice of the corresponding dimension. There can be zero or more positional
        arguments, each of the form:</p>

        <ul>
          <li>a single integer n, meaning <code>slice(n, n+1)</code></li>

          <li>an instance of the slice class</li>

          <li>a tuple, which will be used as arguments to create a slice</li>

          <li>':', which means a slice covering that entire dimension</li>

          <li>Ellipsis (...), which means to fill the slice list with ':' leaving only
          enough room at the end for the remaining positional arguments</li>

          <li>a Python slice object, of the form <code>slice(i,j,k)</code></li>
        </ul>

        <p>If there are fewer slices than corresponding dimensions, all values of the
        trailing dimensions are read.</p>

        <p>The keyword arguments are defined as in subRegion.</p>

        <p>There must be no conflict between the positional arguments and the
        keywords.</p>

        <p>In <code>(a)-(c)</code> and (f), negative numbers are treated as offsets from
        the end of that dimension, as in normal Python indexing.</p>
      </td>
    </tr>

    <tr>
      <td>String</td>

      <td><code>typecode()</code></td>

      <td>The Numeric datatype identifier.</td>
    </tr>

.. raw:: html

   </table>

**Example:** Get a region of data.

Variable ta is a function of (time, latitude, longitude). Read data
corresponding to all times, latitudes -45.0 up to but not
including+45.0, longitudes 0.0 through and including longitude 180.0:

{% highlight python %} data = ta.subRegion(':', (-45.0,45.0,'co'), (0.0,
180.0)) {% endhighlight %}

or equivalently:

{% highlight python %} data = ta.subRegion(latitude=(-45.0,45.0,'co'),
longitude=(0.0, 180.0) {% endhighlight %}

Read all data for March, 1980:

{% highlight python %} data =
ta.subRegion(time=('1980-3','1980-4','co')) {% endhighlight %}

Table 2.36 Variable Slice Operators
                                   

+-------------------+---------------------------------------------------------------+
| Operator          | Description                                                   |
+===================+===============================================================+
| ``[i]``           | The ith element, zero-origin indexing.                        |
+-------------------+---------------------------------------------------------------+
| ``[i:j]``         | The ith element through, but not including, element j         |
+-------------------+---------------------------------------------------------------+
| ``[i:]``          | The ith element through the end                               |
+-------------------+---------------------------------------------------------------+
| ``[:j]``          | The beginning element through, but not including, element j   |
+-------------------+---------------------------------------------------------------+
| ``[:]``           | The entire array                                              |
+-------------------+---------------------------------------------------------------+
| ``[i:j:k]``       | Every kth element                                             |
+-------------------+---------------------------------------------------------------+
| ``[i:j, m:n]``    | Multidimensional slice                                        |
+-------------------+---------------------------------------------------------------+
| ``[i, ..., m]``   | (Ellipsis) All dimensions between those specified.            |
+-------------------+---------------------------------------------------------------+
| ``[-1]``          | Negative indices 'wrap around'. -1 is the last element        |
+-------------------+---------------------------------------------------------------+

Table 2.37 Index and Coordinate Intervals
                                         

+------+------+------+
| Inte | Exam | Exam |
| rval | ple  | ple  |
| Defi | Inte |      |
| niti | rval |      |
| on   | Defi |      |
|      | niti |      |
|      | on   |      |
+======+======+======+
| ``x` | sing | ``18 |
| `    | le   | 0.0` |
|      | poin | `\ \ |
|      | t,   |  ``c |
|      | such | dtim |
|      | that | e.re |
|      | axis | ltim |
|      | [i]= | e(48 |
|      | =x   | ,"ho |
|      | In   | ur s |
|      | gene |  sin |
|      | ral  | ce 1 |
|      | x is | 980- |
|      | a    | 1")` |
|      | scal | `\ \ |
|      | ar.  |  ``' |
|      | If   | 1980 |
|      | the  | -1-3 |
|      | axis | '``  |
|      | is a |      |
|      | time |      |
|      | axis |      |
|      | ,    |      |
|      | x    |      |
|      | may  |      |
|      | also |      |
|      | be a |      |
|      | cdti |      |
|      | me   |      |
|      | rela |      |
|      | tive |      |
|      | time |      |
|      | type |      |
|      | ,    |      |
|      | comp |      |
|      | onen |      |
|      | t    |      |
|      | time |      |
|      | type |      |
|      | ,    |      |
|      | or   |      |
|      | stri |      |
|      | ng   |      |
|      | of   |      |
|      | the  |      |
|      | form |      |
|      | 'yyy |      |
|      | y-mm |      |
|      | -dd  |      |
|      | hh:m |      |
|      | i:ss |      |
|      | '    |      |
|      | (whe |      |
|      | re   |      |
|      | trai |      |
|      | ling |      |
|      | fiel |      |
|      | ds   |      |
|      | of   |      |
|      | the  |      |
|      | stri |      |
|      | ng   |      |
|      | may  |      |
|      | be   |      |
|      | omit |      |
|      | ted. |      |
+------+------+------+
| ``(x | indi | ``(- |
| ,y)` | ces  | 180, |
| `    | i    | 180) |
|      | such | ``   |
|      | that |      |
|      | x ≤  |      |
|      | axis |      |
|      | [i]  |      |
|      | ≤ y  |      |
+------+------+------+
| ``(x | ``x  | ``(- |
| ,y,' | ≤ ax | 90,9 |
| co') | is[i | 0,'c |
| ``   | ] <  | c')` |
|      | y``. | `    |
|      | The  |      |
|      | thir |      |
|      | d    |      |
|      | item |      |
|      | is   |      |
|      | defi |      |
|      | ned  |      |
|      | as   |      |
|      | in   |      |
|      | mapI |      |
|      | nter |      |
|      | val. |      |
+------+------+------+
| ``(x | ``x  | ``(  |
| ,y,' | ≤ ax | 180, |
| co', | is[i |  180 |
| cycl | ]< y | , 'c |
| e)`` | ``,  | o',  |
|      | with | 360. |
|      | wrap | 0)`` |
|      | arou |      |
|      | nd   |      |
|      | **No |      |
|      | te:* |      |
|      | *    |      |
|      | It   |      |
|      | is   |      |
|      | not  |      |
|      | nece |      |
|      | sary |      |
|      | to   |      |
|      | spec |      |
|      | ify  |      |
|      | the  |      |
|      | cycl |      |
|      | e    |      |
|      | of a |      |
|      | circ |      |
|      | ular |      |
|      | long |      |
|      | itud |      |
|      | e    |      |
|      | axis |      |
|      | ,    |      |
|      | that |      |
|      | is,  |      |
|      | for  |      |
|      | whic |      |
|      | h    |      |
|      | ``ax |      |
|      | is.i |      |
|      | sCir |      |
|      | cula |      |
|      | r()` |      |
|      | `    |      |
|      | is   |      |
|      | true |      |
|      | .    |      |
+------+------+------+
| ``sl | slic | ``sl |
| ice( | e    | ice( |
| i,j, | obje | 1,10 |
| k)`` | ct,  | )``\ |
|      | equi |  \ ` |
|      | vale | `sli |
|      | nt   | ce(, |
|      | to   | ,-1) |
|      | i:j: | ``   |
|      | k    | reve |
|      | in a | rses |
|      | slic | the  |
|      | e    | dire |
|      | oper | ctio |
|      | ator | n    |
|      | .    | of   |
|      | Refe | the  |
|      | rs   | axis |
|      | to   | .    |
|      | the  |      |
|      | indi |      |
|      | ces  |      |
|      | i,   |      |
|      | i+k, |      |
|      | i+2k |      |
|      | ,    |      |
|      | ...  |      |
|      | up   |      |
|      | to   |      |
|      | but  |      |
|      | not  |      |
|      | incl |      |
|      | udin |      |
|      | g    |      |
|      | inde |      |
|      | x    |      |
|      | j.   |      |
|      | If i |      |
|      | is   |      |
|      | not  |      |
|      | spec |      |
|      | ifie |      |
|      | d    |      |
|      | or   |      |
|      | is   |      |
|      | None |      |
|      | it   |      |
|      | defa |      |
|      | ults |      |
|      | to   |      |
|      | 0.   |      |
|      | If j |      |
|      | is   |      |
|      | not  |      |
|      | spec |      |
|      | ifie |      |
|      | d    |      |
|      | or   |      |
|      | is   |      |
|      | None |      |
|      | it   |      |
|      | defa |      |
|      | ults |      |
|      | to   |      |
|      | the  |      |
|      | leng |      |
|      | th   |      |
|      | of   |      |
|      | the  |      |
|      | axis |      |
|      | .    |      |
|      | The  |      |
|      | stri |      |
|      | de   |      |
|      | k    |      |
|      | defa |      |
|      | ults |      |
|      | to   |      |
|      | 1. k |      |
|      | may  |      |
|      | be   |      |
|      | nega |      |
|      | tive |      |
|      | .    |      |
+------+------+------+
| ``': | all  |      |
| '``  | axis |      |
|      | valu |      |
|      | es   |      |
|      | of   |      |
|      | one  |      |
|      | dime |      |
|      | nsio |      |
|      | n    |      |
+------+------+------+
| ``El | all  |      |
| lips | valu |      |
| is`` | es   |      |
|      | of   |      |
|      | all  |      |
|      | inte |      |
|      | rmed |      |
|      | iate |      |
|      | axes |      |
+------+------+------+

2.11.1 Selectors
''''''''''''''''

A selector is a specification of a region of data to be selected from a
variable. For example, the statement

{% highlight python %} x = v(time='1979-1-1', level=(1000.0,100.0)) {%
endhighlight %}

means 'select the values of variable v for time '1979-1-1' and levels
1000.0 to 100.0 inclusive, setting x to the result.' Selectors are
generally used to represent regions of space and time.

The form for using a selector is

{% highlight python %} result = v(s) {% endhighlight %}

where v is a variable and s is the selector. An equivalent form is

{% highlight python %} result = f('varid', s) {% endhighlight %}

where f is a file or dataset, and 'varid' is the string ID of a
variable.

A selector consists of a list of selector components. For example, the
selector

{% highlight python %} time='1979-1-1', level=(1000.0,100.0) {%
endhighlight %}

has two components: time='1979-1-1', and level=(1000.0,100.0). This
illustrates that selector components can be defined with keywords, using
the form:

{% highlight python %} keyword=value {% endhighlight %}

Note that for the keywords time, level, latitude, and longitude, the
selector can be used with any variable. If the corresponding axis is not
found, the selector component is ignored. This is very useful for
writing general purpose scripts. The required keyword overrides this
behavior. These keywords take values that are coordinate ranges or index
ranges as defined in Table 2.37 on page 102.

The following keywords are available: Another form of selector
components is the positional form, where the component order corresponds
to the axis order of a variable. For example:

Table 2.38 Selector keywords
                            

+------+------+------+
| Keyw | Desc | Valu |
| ord  | ript | e    |
|      | ion  |      |
+======+======+======+
| ``ax | Rest | See  |
| isid | rict | Tabl |
| ``   | the  | e    |
|      | axis | 2.37 |
|      | with | on   |
|      | ID   | page |
|      | axis | 102  |
|      | id   |      |
|      | to a |      |
|      | valu |      |
|      | e    |      |
|      | or   |      |
|      | rang |      |
|      | e    |      |
|      | of   |      |
|      | valu |      |
|      | es.  |      |
+------+------+------+
| ``gr | Regr | Grid |
| id`` | id   | obje |
|      | the  | ct   |
|      | resu |      |
|      | lt   |      |
|      | to   |      |
|      | the  |      |
|      | grid |      |
|      | .    |      |
+------+------+------+
| ``la | Rest | See  |
| titu | rict | Tabl |
| de`` | lati | e    |
|      | tude | 2.37 |
|      | valu | on   |
|      | es   | page |
|      | to a | 102  |
|      | valu |      |
|      | e    |      |
|      | or   |      |
|      | rang |      |
|      | e.   |      |
|      | Shor |      |
|      | t    |      |
|      | form |      |
|      | :    |      |
|      | lat  |      |
+------+------+------+
| ``le | Rest | See  |
| vel` | rict | Tabl |
| `    | vert | e    |
|      | ical | 2.37 |
|      | leve | on   |
|      | ls   | page |
|      | to a | 102  |
|      | valu |      |
|      | e    |      |
|      | or   |      |
|      | rang |      |
|      | e.   |      |
|      | Shor |      |
|      | t    |      |
|      | form |      |
|      | :    |      |
|      | lev  |      |
+------+------+------+
| ``lo | Rest | See  |
| ngit | rict | Tabl |
| ude` | long | e    |
| `    | itud | 2.37 |
|      | e    | on   |
|      | valu | page |
|      | es   | 102  |
|      | to a |      |
|      | valu |      |
|      | e    |      |
|      | or   |      |
|      | rang |      |
|      | e.   |      |
|      | Shor |      |
|      | t    |      |
|      | form |      |
|      | :    |      |
|      | lon  |      |
+------+------+------+
| ``or | Reor | Orde |
| der` | der  | r    |
| `    | the  | stri |
|      | resu | ng,  |
|      | lt.  | e.g. |
|      |      | ,    |
|      |      | "tzy |
|      |      | x"   |
+------+------+------+
| ``ra | Retu | 0:   |
| w``  | rn   | retu |
|      | a    | rn   |
|      | mask | a    |
|      | ed   | tran |
|      | arra | sien |
|      | y    | t    |
|      | (MA. | vari |
|      | arra | able |
|      | y)   | (def |
|      | rath | ault |
|      | er   | );   |
|      | than | =1:  |
|      | a    | retu |
|      | tran | rn   |
|      | sien | a    |
|      | t    | mask |
|      | vari | ed   |
|      | able | arra |
|      | .    | y.   |
+------+------+------+
| ``re | Requ | List |
| quir | ire  | of   |
| ed`` | that | axis |
|      | the  | iden |
|      | axis | tifi |
|      | IDs  | ers. |
|      | be   |      |
|      | pres |      |
|      | ent. |      |
+------+------+------+
| ``sq | Remo | 0:   |
| ueez | ve   | leav |
| e``  | sing | e    |
|      | leto | sing |
|      | n    | leto |
|      | dime | n    |
|      | nsio | dime |
|      | ns   | nsio |
|      | from | ns   |
|      | the  | (def |
|      | resu | ault |
|      | lt.  | );   |
|      |      | 1:   |
|      |      | remo |
|      |      | ve   |
|      |      | sing |
|      |      | leto |
|      |      | n    |
|      |      | dime |
|      |      | nsio |
|      |      | ns.  |
+------+------+------+
| ``ti | Rest | See  |
| me`` | rict | Tabl |
|      | time | e    |
|      | valu | 2.37 |
|      | es   | on   |
|      | to a | page |
|      | valu | 10   |
|      | e    |      |
|      | or   |      |
|      | rang |      |
|      | e.   |      |
+------+------+------+

Another form of selector components is the positional form, where the
component order corresponds to the axis order of a variable. For
example:

{% highlight python %} x9 = hus(('1979-1-1','1979-2-1'),1000.0) {%
endhighlight %}

reads data for the range ('1979-1-1','1979-2-1') of the first axis, and
coordinate value 1000.0 of the second axis. Non-keyword arguments of the
form(s) listed in Table 2.37 on page 102 are treated as positional. Such
selectors are more concise, but not as general or flexible as the other
types described in this section.

Selectors are objects in their own right. This means that a selector can
be defined and reused, independent of a particular variable. Selectors
are constructed using the cdms.selectors.Selector class. The constructor
takes an argument list of selector components. For example:

{% highlight python %} from cdms.selectors import Selector sel =
Selector(time=('1979-1-1','1979-2-1'), level=1000.) x1 = v1(sel) x2 =
v2(sel) {% endhighlight %}

For convenience CDMS provides several predefined selectors, which can be
used directly or can be combined into more complex selectors. The
selectors time, level, latitude, longitude, and required are equivalent
to their keyword counterparts. For example:

{% highlight python %} from cdms import time, level x =
hus(time('1979-1-1','1979-2-1'), level(1000.)) {% endhighlight %}

and

{% highlight python %} x = hus(time=('1979-1-1','1979-2-1'),
level=1000.) {% endhighlight %}

are equivalent. Additionally, the predefined selectors
``latitudeslice``, ``longitudeslice``, ``levelslice``, and ``timeslice``
take arguments ``(startindex, stopindex[, stride])``:

{% highlight python %} from cdms import timeslice, levelslice x =
v(timeslice(0,2), levelslice(16,17)) {% endhighlight %}

Finally, a collection of selectors is defined in module cdutil.region:

{% highlight python %} from cdutil.region import \*
NH=NorthernHemisphere=domain(latitude=(0.,90.)
SH=SouthernHemisphere=domain(latitude=(-90.,0.))
Tropics=domain(latitude=(-23.4,23.4))
NPZ=AZ=ArcticZone=domain(latitude=(66.6,90.))
SPZ=AAZ=AntarcticZone=domain(latitude=(-90.,-66.6)) {% endhighlight %}

Selectors can be combined using the & operator, or by refining them in
the call:

{% highlight python %} from cdms.selectors import Selector from cdms
import level sel2 = Selector(time=('1979-1-1','1979-2-1')) sel3 = sel2 &
level(1000.0) x1 = hus(sel3) x2 = hus(sel2, level=1000.0) {%
endhighlight %}

2.11.2 Selector examples
''''''''''''''''''''''''

CDMS provides a variety of ways to select or slice data. In the
following examples, variable hus is contained in file sample.nc, and is
a function of (time, level, latitude, longitude). Time values are
monthly starting at 1979-1-1. There are 17 levels, the last level being
1000.0. The name of the vertical level axis is 'plev'. All the examples
select the first two times and the last level. The last two examples
remove the singleton level dimension from the result array.

{% highlight python %} import cdms f = cdms.open('sample.nc') hus =
f.variables['hus']

Keyword selection
=================

x = hus(time=('1979-1-1','1979-2-1'), level=1000.)

Interval indicator (see mapIntervalExt)
=======================================

x = hus(time=('1979-1-1','1979-3-1','co'), level=1000.)

Axis ID (plev) as a keyword
===========================

x = hus(time=('1979-1-1','1979-2-1'), plev=1000.)

Positional
==========

x9 = hus(('1979-1-1','1979-2-1'),1000.0)

Predefined selectors
====================

from cdms import time, level x = hus(time('1979-1-1','1979-2-1'),
level(1000.))

from cdms import timeslice, levelslice x = hus(timeslice(0,2),
levelslice(16,17))

Call file as a function
=======================

x = f('hus', time=('1979-1-1','1979-2-1'), level=1000.)

Python slices
=============

x = hus(time=slice(0,2), level=slice(16,17))

Selector objects
================

from cdms.selectors import Selector sel =
Selector(time=('1979-1-1','1979-2-1'), level=1000.) x = hus(sel)

sel2 = Selector(time=('1979-1-1','1979-2-1')) sel3 = sel2 &
level(1000.0) x = hus(sel3) x = hus(sel2, level=1000.0)

Squeeze singleton dimension (level)
===================================

x = hus[0:2,16] x = hus(time=('1979-1-1','1979-2-1'), level=1000.,
squeeze=1)

f.close() {% endhighlight %}

2.12 Examples
^^^^^^^^^^^^^

2.12.1 Example 1
''''''''''''''''

In this example, two datasets are opened, containing surface air
temperature ('tas') and upper-air temperature ('ta') respectively.
Surface air temperature is a function of (time, latitude, longitude).
Upper-air temperature is a function of (time, level, latitude,
longitude). Time is assumed to have a relative representation in the
datasets (e.g., with units 'months since basetime').

Data is extracted from both datasets for January of the first input year
through December of the second input year. For each time and level,
three quantities are calculated: slope, variance, and correlation. The
results are written to a netCDF file. For brevity, the functions
``corrCoefSlope`` and ``removeSeasonalCycle`` are omitted.

{% highlight python %} 1. import cdms import MV

::

    # Calculate variance, slope, and correlation of    
    # surface air temperature with upper air temperature
    # by level, and save to a netCDF file. 'pathTa' is the location of
    # the file containing 'ta', 'pathTas' is the file with contains 'tas'.
    # Data is extracted from January of year1 through December of year2.
    def ccSlopeVarianceBySeasonFiltNet(pathTa,pathTas,month1,month2):

        # Open the files for ta and tas
        fta = cdms.open(pathTa)
        ftas = cdms.open(pathTas)

2. ::

       #Get upper air temperature
       taObj = fta['ta']
       levs = taObj.getLevel()

       #Get the surface temperature for the closed interval [time1,time2]
       tas = ftas('tas', time=(month1,month2,'cc'))

       # Allocate result arrays
       newaxes = taObj.getAxisList(omit='time')
       newshape = tuple([len(a) for a in newaxes])
       cc = MV.zeros(newshape, typecode=MV.Float, axes=newaxes, id='correlation')
       b = MV.zeros(newshape, typecode=MV.Float, axes=newaxes, id='slope')
       v = MV.zeros(newshape, typecode=MV.Float, axes=newaxes, id='variance')

       # Remove seasonal cycle from surface air temperature
       tas = removeSeasonalCycle(tas)

       # For each level of air temperature, remove seasonal cycle
       # from upper air temperature, and calculate statistics

3. ::

       for ilev in range(len(levs)):

           ta = taObj(time=(month1,month2,'cc'), \
                      level=slice(ilev, ilev+1), squeeze=1)
           ta = removeSeasonalCycle(ta)   
           cc[ilev], b[ilev] = corrCoefSlope(tas ,ta)
           v[ilev] = MV.sum( ta**2 )/(1.0*ta.shape[0])

       # Write slope, correlation, and variance variables

4. ::

       f = cdms.open('CC_B_V_ALL.nc','w')
       f.title = filtered
       f.write(b)
       f.write(cc)
       f.write(v)
       f.close()

5. if **name**\ =='**main**': pathTa =
   '/pcmdi/cdms/sample/ccmSample\_ta.xml' pathTas =
   '/pcmdi/cdms/sample/ccmSample\_tas.xml'
   # Process Jan80 through Dec81
   ccSlopeVarianceBySeasonFiltNet(pathTa,pathTas,'80-1','81-12') {%
   endhighlight %}

**Notes:**

1. Two modules are imported, ``cdms``, and ``MV``. ``MV`` implements
   arithmetic functions.
2. ``taObj`` is a file (persistent) variable. At this point, no data has
   actually been read. This happens when the file variable is sliced, or
   when the subRegion function is called. levs is an axis.
3. Calling the file like a function reads data for the given variable
   and time range. Note that month1 and month2 are time strings.
4. In contrast to ``taObj``, the variables ``cc``, ``b``, and ``v`` are
   transient variables, not associated with a file. The assigned names
   are used when the variables are written.
5. Another way to read data is to call the variable as a function. The
   squeeze option removes singleton axes, in this case the level axis.
6. Write the data. Axis information is written automatically.
7. This is the main routine of the script. ``pathTa`` and ``pathTas``
   pathnames. Data is processed from January 1980 through December 1981.

2.12.2 Example 2
''''''''''''''''

In the next example, the pointwise variance of a variable over time is
calculated, for all times in a dataset. The name of the dataset and
variable are entered, then the variance is calculated and plotted via
the vcs module.

{% highlight python %} #!/usr/bin/env python # # Calculates gridpoint
total variance # from an array of interest #

::

        import cdms
        from MV import *

        # Wait for return in an interactive window

        def pause():
            print Hit return to continue: ,
            line = sys.stdin.readline()

1. ::

       # Calculate pointwise variance of variable over time
       # Returns the variance and the number of points
       # for which the data is defined, for each grid point
       def calcVar(x):
           # Check that the first axis is a time axis
           firstaxis = x.getAxis(0)
           if not firstaxis.isTime():
               raise 'First axis is not time, variable:', x.id

           n = count(x,0)
           sumxx = sum(x*x)
           sumx = sum(x)
           variance = (n*sumxx -(sumx * sumx))/(n * (n-1.))

           return variance, n

       if __name__=='__main__':
           import vcs, sys

           print 'Enter dataset path [/pcmdi/cdms/obs/erbs_mo.xml]: ',
           path = string.strip(sys.stdin.readline())
           if path=='': path='/pcmdi/cdms/obs/erbs_mo.xml'

2. ::

           # Open the dataset
           dataset = cdms.open(path)

           # Select a variable from the dataset
           print 'Variables in file:',path
           varnames = dataset.variables.keys()
           varnames.sort()
           for varname in varnames:

               var = dataset.variables[varname]
               if hasattr(var,'long_name'):
                   long_name = var.long_name
               elif hasattr(var,'title'):
                   long_name = var.title
               else:
                   long_name = '?'

           print '%-10s: %s'%(varname,long_name)
           print 'Select a variable: ',

3. ::

           varname = string.strip(sys.stdin.readline())
           var = dataset(varname)
           dataset.close()

           # Calculate variance, count, and set attributes
           variance,n = calcVar(var)
           variance.id = 'variance_%s'%var.id
           n.id = 'count_%s'%var.id
           if hasattr(var,'units'):
               variance.units = '(%s)^2'%var.units

           # Plot variance
           w=vcs.init()

4. ::

           w.plot(variance)
           pause()
           w.clear()
           w.plot(n)
           pause()
           w.clear()

   {% endhighlight %}

The result of running this script is as follows:

{% highlight pycon %} % calcVar.py Enter dataset path
[/pcmdi/cdms/sample/obs/erbs\_mo.xml]:

Variables in file: /pcmdi/cdms/sample/obs/erbs\_mo.xml albt : Albedo TOA
[%] albtcs : Albedo TOA clear sky [%] rlcrft : LW Cloud Radiation
Forcing TOA [W/m^2] rlut : LW radiation TOA (OLR) [W/m^2] rlutcs : LW
radiation upward TOA clear sky [W/m^2] rscrft : SW Cloud Radiation
Forcing TOA [W/m^2] rsdt : SW radiation downward TOA [W/m^2] rsut : SW
radiation upward TOA [W/m^2] rsutcs : SW radiation upward TOA clear sky
[W/m^2] Select a variable: albt

Hit return to continue:

 {% endhighlight %}

**Notes:**

1. n = count(x, 0) returns the pointwise number of valid values, summing
   across axis 0, the first axis. count is an MV function.
2. dataset is a Dataset or CdmsFile object, depending on whether a .xml
   or .nc pathname is entered. dataset.variables is a dictionary mapping
   variable name to file variable.
3. var is a transient variable.
4. Plot the variance and count variables. Spatial longitude and latitude
   information are carried with the computations, so the continents are
   plotted correctly.
