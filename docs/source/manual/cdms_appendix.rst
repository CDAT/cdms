APPENDIX A
----------

CDMS Classes
~~~~~~~~~~~~

Figure 1, "CDMS Classes", on page 175 illustrates the class inheritance
structure of CDMS. The classes may be categorized as abstract or
concrete. Only concrete classes are meant to be used directly. In
contrast an abstract class defines the common interface of its
subclasses. For example, the class AbstractAxis2D defines the common
interface for two-dimensional coordinate axes. It has concrete
subclasses DatasetAxis2D, FileAxis2D, and TransientAxis2D, which are
used in applications. Abstract classes are denoted in italics.

For many abstract classes there are three 'flavors' of subclass:
dataset, file, and transient. Dataset-related objects are thought of as
being contained in datasets in the sense that operations on those
objects result in I/O operations on the corresponding dataset. The same
is true of file-related objects. Objects in datasets and files are
examples of persistent objects, whose state persists after the
application exits. On the other hand, transient objects live in memory
and are not persistent.

In general the concrete subclasses closely mirror the interface of the
abstract parent class. For this reason this document defines the
interfaces of the abstract classes, and only discusses a concrete class
in the few cases where the interface has been extended. This allows
applications to treat the behavior of, say a dataset axis and file axis,
as identical.

.. figure:: /images/cdms_classes.jpg
   :alt: 

FIGURE 1. CDMS Classes
                      

APPENDIX B
----------

Version Notes
~~~~~~~~~~~~~

B.1 Version 4.0
^^^^^^^^^^^^^^^

CDMS version 4.0 adds support for nonrectangular grids:

-  The following grid classes were added: AbstractHorizontalGrid,
   AbstractCurve-Grid, AbstractGenericGrid, DatasetCurveGrid,
   FileCurveGrid, TransientCurve-Grid, DatasetGenericGrid,
   FileGenericGrid, and TransientGenericGrid.
-  The following axis classes were added: AbstractCoordinateAxis,
   AbstractAuxAxis1D, AbstractAxis2D, DatasetAuxAxis1D, FileAuxAxis1D,
   TransientAuxAxis1D, DatasetAxis2D, FileAxis2D, and TransientAxis2D.
-  The getMesh and clone methods were added for grids.
-  An interface to the SCRIP package was added.

B.2 Version 3.0 Overview
^^^^^^^^^^^^^^^^^^^^^^^^

CDMS version 3.0 is a significant enhancement of previous versions. The
major changes were:

-  UV-CDAT/CDMS was integrated with the Numerical Python masked array
   class MA.MaskedVariable. The MV submodule was added as a wrapper
   around MA.
-  Methods that read data, such as subRegion, subSlice, and the slice
   operations, return instances of class TransientVariable. The plot and
   regrid modules were modified to handle masked array input. The
   specifiers time=..., latitude=..., etc. were added to the I/O
   routines.
-  The class TransientVariable was added.
-  A number of new functions were added, notably subRegion and subSlice,
   which return instances of TransientVariable.
-  When a masked array is returned from a method, it is "squeezed":
   singleton dimensions are removed. In contrast, transient variables
   are not squeezed. I/O functions have a squeeze option. The method
   setAutoReshapeMode was removed.
-  Internal attributes are handled in the InternalAttributes class. This
   allows CDMS classes to be subclassed more readily.
-  The class Variable was renamed DatasetVariable.
-  The cu module was emulated in cdms. cu and cdms methods can be mixed.
-  The code was modularized, so that Python, CDMS, and Numerical Python
   can be built and installed separately. This significantly enhances
   the portability of the code.

B.3 V3.0 Details
^^^^^^^^^^^^^^^^

B.3.1 AbstractVariable
''''''''''''''''''''''

-  Functions getDomain, getSlice, rank, regrid, setMissing, size,
   subRegion, and subSlice were added.
-  The functions getRegion, getSlice, getValue, and the slice operators
   all return an instance of MA, a masked array. Singleton dimensions
   are squeezed.
-  The functions subRegion and subSlice return an instance of
   TransientVariable. Singleton dimensions are not squeezed.
-  The xxSlice and xxRegion functions have keywords time, level,
   latitude, and longitude.
-  The input functions have the keyword squeeze.
-  AbstractVariable inherits from class Slab. The following functions
   previously available in module cu are Slab methods: getattribute,
   setattribute, listdimattributes, getdimattribute, listall, and info.
-  AbstractVariable implements arithmetic functions, astype.
-  The write function was added.

B.3.2 AbstractAxis
''''''''''''''''''

-  The functions asComponentTime, asRelativeTime, clone, getAxisIds,
   getAxis-Index, getAxisList, getAxisListIndex, mapIntervalExt were
   added.
-  subaxis was renamed subAxis for consistency.
-  Generalized wraparound was implemented, to handle multiple cycles,
   reversing, and negative strides. By default, coordinate intervals are
   closed. The intersection options 'n','e','b',and 's' were added to
   the interval indicator - see mapIntervalExt.

B.3.3 AbstractDatabase
''''''''''''''''''''''

-  The function open is synonymous with openDataset.

B.3.4 Dataset
'''''''''''''

-  The function open is synonymous with openDataset.

B.3.5 cdms module
'''''''''''''''''

-  The functions asVariable, isVariable, and createVariable were added.
-  The function setAutoReshapeMode was removed. It is replaced by the
   squeeze option for all I/O functions.

B.3.6 CdmsFile
''''''''''''''

-  The function createVariable has a keyword fill\_value. The datatype
   may be a Numeric/MA typecode.
-  The function write was added.

B.3.7 CDMSError
'''''''''''''''

-  All errors are an instance of the class CDMSError.

B.3.8 AbstractRectGrid
''''''''''''''''''''''

-  The function createGaussianGrid was added.

B.3.9 InternalAttributes
''''''''''''''''''''''''

-  The class InternalAttributes was added. It has methods
   add\_internal\_attribute, is\_internal\_attribute, and
   replace\_external\_attributes.

B.3.10 TransientVariable
''''''''''''''''''''''''

-  The class TransientVariable was added. It inherits from both
   AbstractVariable and MA.
-  The cdms module function createVariable returns a transient variable.
-  This class does not implement the functions getPaths or getTemplate.

B.3.11 MV
'''''''''

-  The MV submodule of cdms was added.

APPENDIX C
----------

``cu`` Module
~~~~~~~~~~~~~

The ``cu`` module is the original UV-CDAT I/O interface. As of version 3
it is emulated in the ``cdms`` module. It is maintained for backward
compatibility.

The ``cu`` classes are ``Slab``, corresponding to ``TransientVariable``
in CDMS, and ``cuDataset``, corresponding to ``Dataset`` in CDMS.

C.1 Slab
~~~~~~~~

Table C.1 Slab Methods
                      

+------+------+------+
| Type | Meth | Defi |
|      | od   | niti |
|      |      | on   |
+======+======+======+
| Vari | ``ge | Get  |
| ous  | tatt | the  |
|      | ribu | valu |
|      | te(n | e    |
|      | ame) | of   |
|      | ``   | an   |
|      |      | attr |
|      |      | ibut |
|      |      | e.   |
|      |      | ``na |
|      |      | me`` |
|      |      | is   |
|      |      | the  |
|      |      | stri |
|      |      | ng   |
|      |      | name |
|      |      | of   |
|      |      | the  |
|      |      | attr |
|      |      | ibut |
|      |      | e.   |
|      |      | The  |
|      |      | foll |
|      |      | owin |
|      |      | g    |
|      |      | spec |
|      |      | ial  |
|      |      | name |
|      |      | s    |
|      |      | can  |
|      |      | alwa |
|      |      | ys   |
|      |      | be   |
|      |      | used |
|      |      | :    |
|      |      | 'fil |
|      |      | enam |
|      |      | e',  |
|      |      | 'com |
|      |      | ment |
|      |      | s',  |
|      |      | 'gri |
|      |      | d\_n |
|      |      | ame' |
|      |      | ,    |
|      |      | 'gri |
|      |      | d\_t |
|      |      | ype' |
|      |      | ,    |
|      |      | 'tim |
|      |      | e\_s |
|      |      | tati |
|      |      | stic |
|      |      | ',   |
|      |      | 'lon |
|      |      | g\_n |
|      |      | ame' |
|      |      | ,    |
|      |      | 'uni |
|      |      | ts'. |
+------+------+------+
| Vari | ``ge | Get  |
| ous  | tdim | the  |
|      | attr | valu |
|      | ibut | e    |
|      | e(di | of a |
|      | m, f | dime |
|      | ield | nsio |
|      | )``  | n    |
|      |      | attr |
|      |      | ibut |
|      |      | e.   |
|      |      | ``di |
|      |      | m``  |
|      |      | is   |
|      |      | the  |
|      |      | dime |
|      |      | nsio |
|      |      | n    |
|      |      | numb |
|      |      | er,  |
|      |      | an   |
|      |      | inte |
|      |      | ger  |
|      |      | in   |
|      |      | the  |
|      |      | rang |
|      |      | e    |
|      |      | 0..r |
|      |      | ank- |
|      |      | 1.   |
|      |      | ``fi |
|      |      | eld` |
|      |      | `    |
|      |      | is a |
|      |      | stri |
|      |      | ng,  |
|      |      | one  |
|      |      | of:  |
|      |      | "nam |
|      |      | e",  |
|      |      | "val |
|      |      | ues" |
|      |      | ,    |
|      |      | "len |
|      |      | gth" |
|      |      | ,    |
|      |      | "uni |
|      |      | ts", |
|      |      | "wei |
|      |      | ghts |
|      |      | ",   |
|      |      | "bou |
|      |      | nds" |
|      |      | .    |
+------+------+------+
| None | ``in | Prin |
|      | fo(f | t    |
|      | lag= | slab |
|      | None | info |
|      | , de | rmat |
|      | vice | ion. |
|      | =sys | If   |
|      | .std | ``fl |
|      | out) | ag`` |
|      | ``   | is   |
|      |      | nonz |
|      |      | ero, |
|      |      | dime |
|      |      | nsio |
|      |      | n    |
|      |      | valu |
|      |      | es,  |
|      |      | weig |
|      |      | hts, |
|      |      | and  |
|      |      | boun |
|      |      | ds   |
|      |      | are  |
|      |      | also |
|      |      | prin |
|      |      | ted. |
|      |      | Outp |
|      |      | ut   |
|      |      | is   |
|      |      | sent |
|      |      | to   |
|      |      | ``de |
|      |      | vice |
|      |      | ``.  |
+------+------+------+
| List | ``li | Prin |
|      | stal | t    |
|      | l(al | slab |
|      | l=No | info |
|      | ne)` | rmat |
|      | `    | ion. |
|      |      | If   |
|      |      | ``al |
|      |      | l``  |
|      |      | is   |
|      |      | nonz |
|      |      | ero, |
|      |      | dime |
|      |      | nsio |
|      |      | n    |
|      |      | valu |
|      |      | es,  |
|      |      | weig |
|      |      | hts, |
|      |      | and  |
|      |      | boun |
|      |      | ds   |
|      |      | are  |
|      |      | also |
|      |      | prin |
|      |      | ted. |
+------+------+------+
| List | ``li | List |
|      | stdi | dime |
|      | matt | nsio |
|      | ribu | n    |
|      | tes( | attr |
|      | dim, | ibut |
|      |  fie | es.  |
|      | ld)` | Retu |
|      | `    | rns  |
|      |      | a    |
|      |      | list |
|      |      | of   |
|      |      | stri |
|      |      | ng   |
|      |      | attr |
|      |      | ibut |
|      |      | e    |
|      |      | name |
|      |      | s    |
|      |      | whic |
|      |      | h    |
|      |      | can  |
|      |      | be   |
|      |      | inpu |
|      |      | t    |
|      |      | to   |
|      |      | ``ge |
|      |      | tdim |
|      |      | attr |
|      |      | ibut |
|      |      | e``. |
|      |      | ``di |
|      |      | m``  |
|      |      | is   |
|      |      | the  |
|      |      | dime |
|      |      | nsio |
|      |      | n    |
|      |      | numb |
|      |      | er,  |
|      |      | an   |
|      |      | inte |
|      |      | ger  |
|      |      | in   |
|      |      | the  |
|      |      | rang |
|      |      | e    |
|      |      | 0..r |
|      |      | ank- |
|      |      | 1.   |
|      |      | ``fi |
|      |      | eld` |
|      |      | `    |
|      |      | is a |
|      |      | stri |
|      |      | ng,  |
|      |      | one  |
|      |      | of:  |
|      |      | "nam |
|      |      | e",  |
|      |      | "val |
|      |      | ues" |
|      |      | ,    |
|      |      | "len |
|      |      | gth" |
|      |      | ,    |
|      |      | "uni |
|      |      | ts", |
|      |      | "wei |
|      |      | ghts |
|      |      | ",   |
|      |      | "bou |
|      |      | nds" |
|      |      | .    |
+------+------+------+
| None | ``se | Set  |
|      | tatt | an   |
|      | ribu | attr |
|      | te(n | ibut |
|      | ame, | e.   |
|      |  val | ``na |
|      | ue)` | me`` |
|      | `    | is   |
|      |      | the  |
|      |      | stri |
|      |      | ng   |
|      |      | name |
|      |      | of   |
|      |      | the  |
|      |      | attr |
|      |      | ibut |
|      |      | e.   |
|      |      | ``va |
|      |      | lue` |
|      |      | `    |
|      |      | is   |
|      |      | the  |
|      |      | valu |
|      |      | e    |
|      |      | of   |
|      |      | the  |
|      |      | attr |
|      |      | ibut |
|      |      | e    |
+------+------+------+

C.2 ``cuDataset``
~~~~~~~~~~~~~~~~~

Table C.2 cuDataset Methods
                           

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

cleardefault()

.. raw:: html

   </td>

.. raw:: html

   <td>

Clear the default variable name.

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

default\_variable(vname )

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Set the default variable name.

.. raw:: html

   </p>

.. raw:: html

   <p>

vname is the string variable name.

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

Array

.. raw:: html

   </td>

.. raw:: html

   <td>

dimensionarray(dname, vname=None)

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Values of the axis named dname.

.. raw:: html

   </p>

.. raw:: html

   <p>

dname is the string axis name.

.. raw:: html

   </p>

.. raw:: html

   <p>

vname is the string variable name. The default is the variable name set
by default\_variable.

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

Axis

.. raw:: html

   </td>

.. raw:: html

   <td>

dimensionobject(dname, vname=None)

.. raw:: html

   </td>

.. raw:: html

   <td>

Get an axis. dname is the string name of an axis. vname is a string
variable name. The default is the variable name set by
default\_variable.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

Various

.. raw:: html

   </td>

.. raw:: html

   <td>

getattribute (vname, attribute)

.. raw:: html

   </td>

.. raw:: html

   <td>

Get an attribute value. vname is a string variable name. attribute is
the string attribute name.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

String

.. raw:: html

   </td>

.. raw:: html

   <td>

getdimensionunits (dname,vname=None)

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Get the units for the given dimension.

.. raw:: html

   </p>

.. raw:: html

   <p>

dname is the string name of an axis.

.. raw:: html

   </p>

.. raw:: html

   <p>

vnameis a string variable name. The default is the variable name set by
default\_variable.

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

Various

.. raw:: html

   </td>

.. raw:: html

   <td>

getglobal (attribute)

.. raw:: html

   </td>

.. raw:: html

   <td>

Get the value of the global attribute. attribute is the string attribute
name.

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

getslab (vname, \*args)

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Read data for a variable.

.. raw:: html

   </p>

.. raw:: html

   <p>

vname is the string name of the variable.

.. raw:: html

   </p>

.. raw:: html

   <p>

args is an argument list corresponding to the dimensions of the
variable. Arguments for each dimension can be:

.. raw:: html

   </p>

.. raw:: html

   <ol>

.. raw:: html

   <li>

":" or None -- select the entire dimension

.. raw:: html

   </li>

.. raw:: html

   <li>

Ellipsis -- select entire dimensions between the ones given.

.. raw:: html

   </li>

.. raw:: html

   <li>

a pair of successive arguments giving an interval in world coordinates.

.. raw:: html

   </li>

.. raw:: html

   <li>

a CDMS-style tuple of world coordinates e.g. (start, stop, 'cc')

.. raw:: html

   </li>

.. raw:: html

   </ol>

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

listall (vname=None, all=None)

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Get info about data from the file.

.. raw:: html

   </p>

.. raw:: html

   <p>

vname is the string name of the variable.

.. raw:: html

   </p>

.. raw:: html

   <p>

If all is non-zero, dimension values, weights, and bounds are returned
as well

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

listattribute (vname=None )

.. raw:: html

   </td>

.. raw:: html

   <td>

Return a list of attribute names. vname is the name of the variable. The
default is the variable name set by default\_variable.

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

listdimension (vname=None)

.. raw:: html

   </td>

.. raw:: html

   <td>

Return a list of the dimension names associated with a variable. vname
is the name of the variable. The default is the variable name set by
default\_variable.

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

listglobal ()

.. raw:: html

   </td>

.. raw:: html

   <td>

Return a list of the global attribute names.

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

listvariable ()

.. raw:: html

   </td>

.. raw:: html

   <td>

Return a list of the variables in the file.

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

showall (vname=None, all=None, device=sys.stdout)

.. raw:: html

   </td>

.. raw:: html

   <td>

Print a description of the variable. vname is the string name of the
variable. If all is non-zero, dimension values, weights, and bounds are
returned as well. Output is sent to device.

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

showattribute (vname=None, device=sys.stdout)

.. raw:: html

   </td>

.. raw:: html

   <td>

Print the attributes of a variable. vname is the string name of the
variable. Output is sent to device.

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

showdimension (vname=None, device=sys.stdout)

.. raw:: html

   </td>

.. raw:: html

   <td>

Print the dimension names associated with a variable. vname is the
string name of the variable. Output is sent to device.

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

showglobal (device=sys.stdout )

.. raw:: html

   </td>

.. raw:: html

   <td>

Print the global file attributes. Output is sent to device.

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

showvariable (device=sys.stdout )

.. raw:: html

   </td>

.. raw:: html

   <td>

Print the list of variables in the file.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>
