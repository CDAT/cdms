API
===

.. currentmodule:: cdms2

Classes
-------
.. csv-table::
   :header:  "Type", "Constructor"
   :widths:  10, 40
   :align: left

   ":ref:`avariable`", "CDMS Variable objects, abstract interface"
   ":ref:`axis`", "CDMS Axis objects"
   ":ref:`fvariable`", "CDMS File-based variables."
   ":ref:`bindex`", "Bin index for non-rectilinear grids"
   ":ref:`cache`", "CDMS cache management and file movement objects"
   ":ref:`variable`", "DatasetVariable: Dataset-based variables"
   ":ref:`cdurllib`", "Customized URLopener"
   ":ref:`cdurlparse`", "Parse (absolute and relative) URLs."
   ":ref:`cdxmllib`", "A parser for XML, using the derived class as static DTD."
   ":ref:`coord`", "CDMS CoordinateAxis objects"
   ":ref:`cudsinterface`", "Emulation of old cu package"
   ":ref:`database`", "CDMS database objects"
   ":ref:`dataset`", "CDMS dataset and file objects"
   ":ref:`forecast`", "CDMS Forecast"
   ":ref:`gengrid`", "CDMS Generic Grids"
   ":ref:`grid`", "CDMS Grid objects"
   ":ref:`hgrid`", "CDMS HorizontalGrid objects"
   ":ref:`MV2`", "CDMS Variable objects, MaskedArray interface"
   ":ref:`mvCdmsRegrid`", "Cdms2 interface to multiple regridders"
   ":ref:`selectors`", "Classes to support easy selection of climate data"
   ":ref:`tvariable`", "TransientVariable (created by createVariable) is a child of both AbstractVariable and the masked array class."
   ":ref:`mvBaseWriter`", "Abstract class for writing data into file"
   ":ref:`mvSphereMesh`", "Class for representing grids on the sphere"
   ":ref:`mvVsWriter`", "Write data to VizSchema compliant file"
   ":ref:`mvVTKSGWriter`", "Write data to VTK file format using the structured grid format"
   ":ref:`mvVTKUGWriter`", "Write data to VTK file format using the unstructured grid format"
   ":ref:`restApi`", ""
   ":ref:`slabinterface`", "Read part of the old cu slab interface implemented over CDMS"

.. autosummary::

   avariable
   axis
   fvariable
   bindex 
   variable
   cache
   cdurllib
   cdurlparse
   cdxmllib
   coord
   cudsinterface
   database
   dataset
   forecast
   gengrid
   grid
   hgrid
   MV2
   mvCdmsRegrid
   selectors
   tvariable
   mvBaseWriter
   mvSphereMesh
   mvVsWriter
   mvVTKSGWriter
   mvVTKUGWriter
   restApi
   slabinterface
   

Regridder
---------

.. autosummary:: 

   regrid2.horizontal
   regrid2.esmf
   regrid2.crossSection
   regrid2.gsRegrid
   regrid2.mvESMFRegrid
   regrid2.mvGenericRegrid
   regrid2.pressure
   regrid2.scrip
   regrid2.mvcdms2.FRegrid
   

 








   



   




