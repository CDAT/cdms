APPENDIX A
----------

CDMS Classes
~~~~~~~~~~~~

Figure 1, "CDMS Classes", illustrates the class inheritance
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
   :scale: 95% 
   :alt: 

FIGURE 1. CDMS Classes
                       
  



APPENDIX B
----------

Quick Start (Cheat Sheet)
~~~~~~~~~~~~~~~~~~~~~~~~~
.. figure:: /manual/images/cdms_quick_start.jpg
   :scale: 25%
   :alt: cheat sheet

:download:`cdms quick start <docs/cdms_quick_start.pdf>`


VCS Quick Reference (Cheat Sheet)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: /manual/images/vcs_quick_ref.jpg
   :scale: 25%
   :alt:  VCS Cheat Sheet



Release Notes
~~~~~~~~~~~~~

Release 4.0
^^^^^^^^^^^

CDMS version 4.0 adds support for nonrectangular grids:

-  The following grid classes were added: 
      * AbstractHorizontalGrid
      * AbstractCurve-Grid
      * AbstractGenericGrid
      * DatasetCurveGrid
      * FileCurveGrid
      * TransientCurve-Grid
      * DatasetGenericGrid
      * FileGenericGrid
      * TransientGenericGrid.

-  The following axis classes were added:
      * AbstractCoordinateAxis
      * AbstractAuxAxis1D
      * AbstractAxis2D
      * DatasetAuxAxis1D
      * FileAuxAxis1D,
      * TransientAuxAxis1D
      * DatasetAxis2D
      * FileAxis2D
      * TransientAxis2D.

-  The getMesh and clone methods were added for grids.
-  An interface to the SCRIP package was added.

Release 3.0 Overview
^^^^^^^^^^^^^^^^^^^^

CDMS version 3.0 is a significant enhancement of previous versions. The
major changes were:

-  CDAT/CDMS was integrated with the Numpyal Python masked array
   class MV2.MaskedVariable. The MV submodule was added as a wrapper
   around MV.
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
-  The code was modularized, so that Python, CDMS, and Numpyal Python
   can be built and installed separately. This significantly enhances
   the portability of the code.

Details
^^^^^^^

AbstractVariable
''''''''''''''''

-  The functions getRegion, getSlice, getValue, and the slice operators
   all return an instance of MV, a masked array. Singleton dimensions
   are squeezed.
-  The functions subRegion and subSlice return an instance of
   TransientVariable. Singleton dimensions are not squeezed.
-  The xxSlice and xxRegion functions have keywords time, level,
   latitude, and longitude.
-  The input functions have the keyword squeeze.
-  AbstractVariable inherits from class Slab. The following functions
   previously available in module cu are Slab methods:
      * getattribute
      * setattribute
      * listdimattributes
      * getdimattribute
      * listall, and info
-  AbstractVariable implements arithmetic functions, astype.
-  The write function was added.

AbstractAxis
''''''''''''

-  subaxis was renamed subAxis for consistency.
-  Generalized wraparound was implemented, to handle multiple cycles,
   reversing, and negative strides. By default, coordinate intervals are
   closed. The intersection options 'n','e','b',and 's' were added to
   the interval indicator - see mapIntervalExt.

AbstractDatabase
''''''''''''''''

-  The function open is synonymous with openDataset.

Dataset
'''''''

-  The function open is synonymous with openDataset.

cdms module
'''''''''''

-  The following functions were added:
      * asVariable
      * isVariable
      * createVariable
-  The function setAutoReshapeMode was removed. It is replaced by the
   squeeze option for all I/O functions.

CdmsFile
''''''''

-  The function createVariable has a keyword fill\_value. The datatype
   may be a Numpy/MV typecode.
-  The function write was added.

CDMSError
'''''''''

-  All errors are an instance of the class CDMSError.

AbstractRectGrid
''''''''''''''''

-  The function createGaussianGrid was added.

InternalAttributes
''''''''''''''''''

-  The class InternalAttributes was added. 
-  It has methods:
   
   * add\_internal\_attribute
   * is\_internal\_attribute
   * replace\_external\_attributes

TransientVariable
'''''''''''''''''

-  The class TransientVariable was added. It inherits from both
   AbstractVariable and MV.
-  The cdms module function createVariable returns a transient variable.
-  This class does not implement the functions getPaths or getTemplate.

MV
''

-  The MV submodule of cdms was added.

APPENDIX C
----------

Module `cu`
~~~~~~~~~~~

The ``cu`` module is the original CDAT I/O interface. As of version 3
it is emulated in the ``cdms`` module. It is maintained for backward
compatibility.

The ``cu`` classes are ``Slab``, corresponding to ``TransientVariable``
in CDMS, and ``cuDataset``, corresponding to ``Dataset`` in CDMS.

Slab
~~~~

Table Slab Methods
^^^^^^^^^^^^^^^^^^^^^^


.. csv-table:: 
   :header: "Type", "Method", "Definition"
   :widths: 20,50,80
   :align: left

   "Various", "``getdimattribute(dim, field)``", "Get the value of a dimension attribute.  ``dim`` is the dimension number, an integer in the range 0..rank- 1.  ``field`` is a string, one of:  'name', 'values', 'length', 'units', 'weights', 'bounds'."
   "Various", "``getattribute(name)``", "Get the value of an attribute.``name`` is the string name of the attribute. The following special names can always be used:  'filename', 'comments', 'grid_name', 'grid_type', 'time_statistic', 'long_name', 'units'."
   "None", "``info(flag=None, device=sys.stdout)``", "Print slab information.  If ``flag`` is nonzero, dimension values, weights, and bounds are also printed.  Output is sent to ``device``."
   "List", "``listall(all=None)``", "Print slab information.  If ``all`` is nonzero, dimension values, weights, and bounds are also printed."
   "List", "``listdimattributes(dim, field)``", "List dimension attributes.  Returns a list of string attribute names which can be input to ``getdimattribute``.  ``dim`` is the dimension number, an integer in the range 0..rank-1.  ``field`` is a string, one of: 'name', 'values', 'length', 'units', 'weights', 'bounds'."
   "None", "``setattribute(name, value)``", "Set an attribute.  ``name`` is the string name of the attribute.  ``value`` is the value of the attribute."




cuDataset
~~~~~~~~~

Table cuDataset Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table:: 
   :header: "Type", "Method", "Definition"
   :widths: 20, 50, 80
   :align: left

   "None", "``cleardefault()``", "Clear the default variable name."
   "None", "``default_variable(vname``)", "Set the default variable name."
   ,,"vname is the string variable name."
   "Array", "``dimensionarray(dname, vname=None``)", "Values of the axis named dname."
   ,,"dname is the string axis name."
   ,,"vname is the string variable name. The default is the variable name set by default_variable."
   "Axis", "``dimensionobject(dname, vname=None)``", "Get an axis. dname is the string name of an axis. vname is a string variable name. The default is the variable name set by default_variable."
   "Various", "``getattribute (vname, attribute``)", "Get an attribute value. vname is a string variable name. attribute is the string attribute name."
   "String", "``getdimensionunits (dname,vname=None``)", "Get the units for the given dimension."
   ,,"dname is the string name of an axis."
   ,,"vname is a string variable name. The default is the variable name set by default_variable."
   "Various", "``getglobal (attribute)``", "Get the value of the global attribute. attribute is the string attribute name."
   "Variable", "``getslab (vname, \*args)``", "Read data for a variable."
   ,, "vname is the string name of the variable."
   ,, "args is an argument list corresponding to the dimensions of the variable. Arguments for each dimension can be:"
   ,, "- ':' or None -- select the entire dimension"
   ,, "- Ellipsis -- select entire dimensions between the ones given."
   ,, "- a pair of successive arguments giving an interval in world coordinates."
   ,, "- a CDMS-style tuple of world coordinates e.g. (start, stop, 'cc')"
   "List", "``listall (vname=None, all=None)``", "Get info about data from the file."
   ,, "vname is the string name of the variable."
   ,, "If all is non-zero, dimension values, weights, and bounds are returned as well"
   "List", "``listattribute (vname=None )``", "Return a list of attribute names. vname is the name of the variable. The default is the variable name set by default_variable."
   "List", "``listdimension (vname=None)``", "Return a list of the dimension names associated with a variable. vname is the name of the variable. The default is the variable name set by default_variable."
   "List", "``listglobal ()``", "Return a list of the global attribute names."
   "List", "``listvariable ()``", "Return a list of the variables in the file."
   "None", "``showall (vname=None, all=None, device=sys.stdout)``", "Print a description of the variable. vname is the string name of the variable. If all is non-zero, dimension values, weights, and bounds are returned as well. Output is sent to device."
   "None", "``showattribute (vname=None, device=sys.stdout)``", "Print the attributes of a variable. vname is the string name of the variable. Output is sent to device."
   "None", "``showdimension (vname=None, device=sys.stdout)``", "Print the dimension names associated with a variable. vname is the string name of the variable. Output is sent to device." 
   "None", "``showglobal (device=sys.stdout)``", "Print the global file attributes. Output is sent to device."
   "None", "``showvariable (device=sys.stdout)``", "Print the list of variables in the file."

