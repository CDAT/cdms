CHAPTER 6 Climate Data Markup Language (CDML)
---------------------------------------------

6.1 Introduction
~~~~~~~~~~~~~~~~

The Climate Data Markup Language (CDML) is the markup language used to
represent metadata in CDMS. CDML is based on the W3C XML standard
(http://www.w3.org). This chapter defines the syntax of CDML. Read this
section if you will be building or maintaining a CDMS database.

XML, the eXtensible Markup Language, makes it possible to define
interoperable dialects of markup languages. The most recent version of
HTML, the Web hypertext markup language, is an XML dialect. CDML is also
an XML dialect, geared toward the representation of gridded climate
datasets. XML provides rigor to the metadata representation, ensuring
that applications can access it correctly. XML also deals with
internationalization issues, and holds forth the promise that utilities
for browsing, editing, and other common tasks will be available in the
future.

CDML files have the file extension .xml or .cdml.

6.2 Elements
~~~~~~~~~~~~

A CDML document consists of a nested collection of elements. An element
is a description of the metadata associated with a CDMS object. The form
of an element is:

``<tag attribute-list> element-content </tag>``

or

``<tag attribute-list />``

where

-  ``tag`` is a string which defines the type of element
-  ``attribute-list`` is a blank-separated list of attribute-value
   pairs, of the form:

   ``attribute = "value"``
-  ``element-content`` depends on the type of element. It is either a
   list of elements, or text which defines the element values. For
   example, the content of an axis element either is a list of axis
   values, or is a linear element. For datasets, the content is the
   blank-separated list of elements corresponding to the axes, grids,
   and variables contained in the dataset.

The CDML elements are:

Table 6.1 CDML Tags
                   

+------------+---------------------------------------+
| Tag        | Description                           |
+============+=======================================+
| attr       | Extra attribute                       |
+------------+---------------------------------------+
| axis       | Coordinate axis                       |
+------------+---------------------------------------+
| domain     | Axes on which a variable is defined   |
+------------+---------------------------------------+
| domElem    | Element of a variable domain          |
+------------+---------------------------------------+
| linear     | Linearly-spaced axis values           |
+------------+---------------------------------------+
| rectGrid   | Rectilinear Grid                      |
+------------+---------------------------------------+
| variable   | Variable                              |
+------------+---------------------------------------+

6.3 Special Characters
~~~~~~~~~~~~~~~~~~~~~~

XML reserves certain characters for markup. If they appear as content,
they must be encoded to avoid confusion with markup:

Table 6.2 Special Character Encodings
                                     

+-------------+------------+
| Character   | Encoding   |
+=============+============+
| <           | &lt;       |
+-------------+------------+
| >           | &gt;       |
+-------------+------------+
| &           | &amp;      |
+-------------+------------+
| “           | &quot;     |
+-------------+------------+
| ‘           | &apos;     |
+-------------+------------+

For example, the comment

{% highlight text %} Certain "special characters", such as <, >, and ,
must be encoded. {% endhighlight %}

would appear in an attribute string as:

{% highlight html %} comment = "Certain "special characters", such as <,
>, and ', must be encoded." {% endhighlight %}

6.4 Identifiers
~~~~~~~~~~~~~~~

In CDMS, all objects in a dataset have a unique string identifier. The
id attribute holds the value of this identifier. If the variable, axis,
or grid has a string name within a data file, then the id attribute
ordinarily has this value. Alternatively, the name of the object in a
data file can be stored in the name\_in\_file attribute, which can
differ from the id. Datasets also have IDs, which can be used within a
larger context (databases).

An identifer must start with an alphabetic character (upper or lower
case), an underscore (\_), or a colon (:). Characters after the first
must be alphanumeric, an underscore, or colon. There is no restriction
on the length of an identifier.

6.5 CF Metadata Standard
~~~~~~~~~~~~~~~~~~~~~~~~

`The CF metadata standard <http://cfconventions.org/>`__ defines a set
of conventions for usage of netCDF. This standard is supported by CDML.
The document defines names and usage for metadata attributes. CF
supersedes the GDT 1.3 standard.

6.6 CDML Syntax
~~~~~~~~~~~~~~~

The following notation is used in this section:

-  A ``monospaced block`` is used for a syntax specification.
-  **Bold** text indicates literals.
-  (R\|S) denotes either R or S.
-  R\*denotes zero or more R.
-  R+ denotes one or more R.

A CDML document consists of a prolog followed by a single dataset
element.

``CDML-document ::= prolog dataset-element``

The prolog defines the XML version, and the Document Type Definition
(DTD), a formal specification of the document syntax. See http://
www.w3.org/TR/1998/REC-xml-19980210 for a formal definition of XML
Version 1.0.

``prolog ::= <?xml version="1.0"?> <!DOCTYPE dataset SYSTEM "http://www-pcmdi.llnl.gov/~drach/cdms/cdml.dtd">``

6.6.1 Dataset Element
^^^^^^^^^^^^^^^^^^^^^

A dataset element describes a single dataset. The content is a list of
elements corresponding to the axes, grids, and variables contained in
the dataset. Axis, variable, and grid elements can be listed in any
order, and an element ID can be used before the element is actually
defined.

``dataset-element ::=`` **** ``dataset-content`` ****

``dataset-content ::= (axis-element | grid-element | variable-element)* extra-attribute-element+``

Table 6.3 Dataset Attributes
                            

.. raw:: html

   <table class="table">

.. raw:: html

   <tr>

.. raw:: html

   <th>

Attribute

.. raw:: html

   </th>

.. raw:: html

   <th>

Required

.. raw:: html

   </th>

.. raw:: html

   <th>

CF

.. raw:: html

   </th>

.. raw:: html

   <th>

GDT

.. raw:: html

   </th>

.. raw:: html

   <th>

Notes

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

appendices

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Version number

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

calendar

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Calendar used for encoding time axes.

.. raw:: html

   </p>

.. raw:: html

   <p>

``gregorian`` \| ``julian`` \| ``noleap`` \|\ ``360_day`` \|
``proleptic_gregorian`` \| ``standard``

.. raw:: html

   </p>

.. raw:: html

   <p>

Note: for the CF convention, the calendar attribute is placed on the
time axis.

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

comment

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Additional dataset information

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

conventions

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

The netCDF metadata standard. Example: "CF-1.0"

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

cdms\_filemap

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Map of partitioned axes to files. See note below.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

directory

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Root directory of the dataset

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

frequency

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Temporal frequency

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

history

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Evolution of the data

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

id

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Dataset identifier

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

institution

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Who made or supplied the data

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

production

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

How the data was produced (see source)

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

project

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Project associated with the data Example: "CMIP 2"

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

references

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Published or web-based references that describe the data or methods used
to produce it

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

source

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

The method of production of the original data.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

template

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Filename template. This is an alternate mechanism, other than
cdms\_filemap, for describing the file mapping. See ‘cdimport -h’ for
details.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

title

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

A succinct description of the data.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>

**Notes:**

The ``cdms_filemap`` attribute describes how the dataset is partitioned
into files. The format is:

``filemap ::= [ varmap, varmap, ...]``

``varmap ::= [ namelist, slicelist ]``

``namelist ::= [ name, name, ... ]``

``slicelist ::= [ indexlist, indexlist, ,,, ]``

``indexlist ::= [ time0, time1, lev0, lev1, path ]``

``name ::= variable name``

``time0 ::= first index of time in the file, or '-' if not split on time``

``time1 ::= last index of time + 1, in the file, or '-' if not split on time``

``lev0 ::= first index of vertical levels in the file, or '-' if not split on level``

``lev1 ::= last index +1 of vertical levels in the file, or '-' if not split on level``

``path ::= pathname of the file containing data for this time/level range.``

The pathname is appended to the value of the directory attribute, to
obtain an absolute pathname.

6.6.2 Axis Element
^^^^^^^^^^^^^^^^^^

An axis element describes a single coordinate axis. The content can be a
blank-separated list of axis values or a linear element. A linear
element is a representation of a linearly-spaced axis as (start, delta,
length).

``axis-element ::=`` **** ``axis-content`` ****

``axis-content ::= (axis-values | linear-element) extra-attribute-element*``

``axis-values ::= [value*]``

``linear-element ::=`` ** **

Table 6.4
         

.. raw:: html

   <table class="table">

::

    <tr>
      <th>Attribute</th>

      <th>Required?</th>

      <th>CF</th>

      <th>GDT</th>

      <th>Notes</th>
    </tr>

    <tr>
      <td><code>associate</code></td>

      <td>N</td>

      <td>N</td>

      <td>Y</td>

      <td>IDs of variables containing alternative sets of coordinates.</td>
    </tr>

    <tr>
      <td><code>axis</code></td>

      <td>N</td>

      <td>Y</td>

      <td>Y</td>

      <td>
        <p>The spatial type of the axis:</p>

        <ul>
          <li>"T" - time</li>

          <li>"X" - longitude</li>

          <li>"Y" - latitude</li>

          <li>"Z" - vertical level</li>

          <li>"-" - not spatiotemporal</li>
        </ul>
      </td>
    </tr>

    <tr>
      <td><code>bounds</code></td>

      <td>N</td>

      <td>Y</td>

      <td>Y</td>

      <td>ID of the boundary variable</td>
    </tr>

    <tr>
      <td><code>calendar</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>See dataset.calendar</td>
    </tr>

    <tr>
      <td><code>climatology</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>Range of dates to which climatological statistics apply.</td>
    </tr>

    <tr>
      <td><code>comment</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>String comment</td>
    </tr>

    <tr>
      <td><code>compress</code></td>

      <td>N</td>

      <td>Y</td>

      <td>Y</td>

      <td>Dimensions which have been compressed by gathering</td>
    </tr>

    <tr>
      <td><code>datatype</code></td>

      <td>Y</td>

      <td>N</td>

      <td>N</td>

      <td>Char, Short, Long, Float, Double, or String</td>
    </tr>

    <tr>
      <td><code>dates</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>Range of dates to which statistics for a typical diurnal cycle apply.</td>
    </tr>

    <tr>
      <td><code>expand</code></td>

      <td>N</td>

      <td>N</td>

      <td>Y</td>

      <td>Coordinates prior to contraction</td>
    </tr>

    <tr>
      <td><code>formula_terms</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>Variables that correspond to the terms in a formula.</td>
    </tr>

    <tr>
      <td><code>id</code></td>

      <td>Y</td>

      <td>N</td>

      <td>N</td>

      <td>Axis identifier. Also the name of the axis in the underlying file(s), if
      name_in_file is undefined.</td>
    </tr>

    <tr>
      <td><code>isvar</code></td>

      <td>N</td>

      <td>N</td>

      <td>N</td>

      <td>
        <p>'true' | 'false'</p>

        <p>'false' if the axis does not have coordinate values explicitly defined in the
        underlying file(s).</p>

        <p>Default: 'true'</p>
      </td>
    </tr>

    <tr>
      <td><code>leap_month</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>For a user-defined calendar, the month which is lengthened by a day in leap
      years.</td>
    </tr>

    <tr>
      <td><code>leap_year</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>An example of a leap year for a user-defined calendar. All years that differ
      from this year by a multiple of four are leap years.</td>
    </tr>

    <tr>
      <td><code>length</code></td>

      <td>N</td>

      <td>N</td>

      <td>N</td>

      <td>Number of axis values, including values for which no data is defined. Cf.
      partition_length.</td>
    </tr>

    <tr>
      <td><code>long_name</code></td>

      <td>N</td>

      <td>Y</td>

      <td>Y</td>

      <td>Long description of a physical quantity</td>
    </tr>

    <tr>
      <td><code>modulo</code></td>

      <td>N</td>

      <td>N</td>

      <td>Y</td>

      <td>Arithmetic modulo of an axis with circular topology.</td>
    </tr>

    <tr>
      <td><code>month_lengths</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>Length of each month in a non-leap year for a user-defined calendar.</td>
    </tr>

    <tr>
      <td><code>name_in_file</code></td>

      <td>N</td>

      <td>N</td>

      <td>N</td>

      <td>Name of the axis in the underlying file(s). See id.</td>
    </tr>

    <tr>
      <td><code>partition</code></td>

      <td>N</td>

      <td>N</td>

      <td>N</td>

      <td>How the axis is split across files.</td>
    </tr>

    <tr>
      <td><code>partition_lengt h</code></td>

      <td>N</td>

      <td>N</td>

      <td>N</td>

      <td>Number of axis points for which data is actually defined. If data is missing
      for some values, this will be smaller than the length.</td>
    </tr>

    <tr>
      <td><code>positive</code></td>

      <td>N</td>

      <td>Y</td>

      <td>Y</td>

      <td>Direction of positive for a vertical axis</td>
    </tr>

    <tr>
      <td><code>standard_name</code></td>

      <td>N</td>

      <td>Y</td>

      <td>N</td>

      <td>Reference to an entry in the standard name table.</td>
    </tr>

    <tr>
      <td><code>topology</code></td>

      <td>N</td>

      <td>N</td>

      <td>Y</td>

      <td>
        <p>Axis topology.</p>

        <p>'circular' | 'linear'</p>
      </td>
    </tr>

    <tr>
      <td><code>units</code></td>

      <td>Y</td>

      <td>Y</td>

      <td>Y</td>

      <td>Units of a physical quantity</td>
    </tr>

    <tr>
      <td><code>weights</code></td>

      <td>N</td>

      <td>N</td>

      <td>N</td>
      <td>Name of the weights array </td>
    </tr>

.. raw:: html

   </table>

6.6.3 partition attribute
^^^^^^^^^^^^^^^^^^^^^^^^^

For an axis in a dataset, the .partition attribute describes how an axis
is split across files. It is a list of the start and end indices of each
axis partition.

FIGURE 4. Partitioned axis
                          

.. figure:: /images/timeLine.jpg
   :alt: 

For example, Figure 4 shows a time axis, representing the 36 months,
January 1980 through December 1982, with December 1981 missing. The
first partition interval is (0,12), the second is (12,23), and the third
is (24,36), where the interval (i,j) represents all indices k such that
i <= k < j. The .partition attribute for this axis would be the list:

``[0, 12, 12, 23, 24, 36]``

Note that the end index of the second interval is strictly less than the
start index of the following interval. This indicates that data for that
period is missing.

6.6.4 Grid Element
^^^^^^^^^^^^^^^^^^

A grid element describes a horizontal, latitude-longitude grid which is
rectilinear in topology,

``grid-element ::=`` **<rectGrid** ``grid-attributes``\ **>**
``extra-attribute-element*`` **</rectGrid>**

Table 6.5 RectGrid Attributes
                             

.. raw:: html

   <table class="table">

::

    <th>Attribute</th> <th>Required?</th> <th>GDT?</th> <th>Notes</th>

.. raw:: html

   </tr>

::

    <tr><td><code>id</code></td><td>Y</td><td>N</td><td>Grid identifier</td></tr>
    <tr><td><code>type</code></td><td>Y</td><td>N</td><td><p>Grid classification</p><p>"gaussian" | "uniform" | "equalarea" |"generic"</p><p>Default: "generic"</p></td></tr>
    <tr><td><code>latitude</code></td><td>Y</td><td>N</td><td>Latitude axis name</td></tr>
    <tr><td><code>longitude</code></td><td>Y</td><td>N</td><td>Longitude axis name</td></tr>
    <tr><td><code>mask</code></td><td>N</td><td>N</td><td>Name of associated mask variable</td></tr>
    <tr><td><code>order</code></td><td>Y</td><td>N</td><td><p>Grid ordering "yx" | "xy"</p><p>Default: “yx”, axis order is latitude, longitude</p></td></tr>

.. raw:: html

   </table>

6.6.5 Variable Element
^^^^^^^^^^^^^^^^^^^^^^

A variable element describes a data variable. The domain of the variable
is an ordered list of domain elements naming the axes on which the
variable is defined. A domain element is a reference to an axis or grid
in the dataset.

The length of a domain element is the number of axis points for which
data can be retrieved. The partition\_length is the number of points for
which data is actually defined. If data is missing, this is less than
the length.

``variable-element ::=`` **<variable** ``variable-attributes``\ **>**
``variable-content`` **</variable>**

``variable-content ::=`` variable-domain extra-attributeelement\*\`

``variable-domain ::=`` **<domain>** ``domain-element*`` **</domain>**

``domain-element ::=`` **<domElem name=**"``axis-name``"\*\*
start=\ **"``Integer``" **\ length=\ **"``Integer``"
**\ partition\_length=\ **"``Integer``"**/>\*\*

Table 6.6 Variable Attributes
                             

.. raw:: html

   <table class="table">

.. raw:: html

   <tr>

.. raw:: html

   <th>

Attribute

.. raw:: html

   </th>

.. raw:: html

   <th>

Required?

.. raw:: html

   </th>

.. raw:: html

   <th>

CF

.. raw:: html

   </th>

.. raw:: html

   <th>

GDT

.. raw:: html

   </th>

.. raw:: html

   <th>

Notes

.. raw:: html

   </th>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

id

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Variable identifier. Also, the name of the variable in the underlying
file(s), if name\_in\_file is undefined.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

add\_offset

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Additive offset for packing data. See scale\_factor.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

associate

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

IDs of variables containing alternative sets of coordinates

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

axis

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

.. raw:: html

   <p>

Spatio-temporal dimensions.

.. raw:: html

   </p>

.. raw:: html

   <p>

Example: "TYX" for a variable with domain (time, latitude, longitude)

.. raw:: html

   </p>

.. raw:: html

   <p>

Note: for CF, applies to axes only.

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

cell\_methods

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

The method used to derive data that represents cell values, e.g.,
"maximum", "mean", "variance", etc.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

comments

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Comment string

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

coordinates

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

IDs of variables containing coordinate data.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

datatype

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Char, Short, Long, Float, Double, or String

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

grid\_name

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Id of the grid

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

grid\_type

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

"gaussian" \| "uniform" \| "equalarea" \| "generic"

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

long\_name

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Long description of a physical quantity.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

missing\_value

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Value used for data that are unknown or missint.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

name\_in\_file

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Name of the variable in the underlying file(s). See id.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

scale\_factor

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Multiplicative factor for packing data. See add\_offset.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

standard\_name

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Reference to an entry in the standard name table.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

subgrid

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Records how data values represent subgrid variation.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

template

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Name of the file template to use for this variable. Overrides the
dataset value.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

units

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Units of a physical quantity.

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

valid\_max

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Largest valid value of a variable

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

valid\_min

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Smallest valid value of a variable

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   <tr>

.. raw:: html

   <td>

valid\_range

.. raw:: html

   </td>

.. raw:: html

   <td>

N

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Y

.. raw:: html

   </td>

.. raw:: html

   <td>

Largest and smallest valid values of a variable

.. raw:: html

   </td>

.. raw:: html

   </tr>

.. raw:: html

   </table>

6.6.6 Attribute Element
^^^^^^^^^^^^^^^^^^^^^^^

Attributes which are not explicitly defined by the GDT convention are
represented as extra attribute elements. Any dataset, axis, grid, or
variable element can have an extra attribute as part of its content.
This representation is also useful if the attribute value has non-blank
whitespace characters (carriage returns, tabs, linefeeds) which are
significant.

The datatype is one of: **Char**, **Short**, **Long**, **Float**,
**Double**, or **String**.

``extra-attribute-element ::=`` **<attr name=**"``attribute-name``"
**datatype=**"``attribute-datatype``"**>** ``attribute-value``
**</attr>**

6.7 A Sample CDML Document
~~~~~~~~~~~~~~~~~~~~~~~~~~

Dataset "sample" has two variables, and six axes.

**Note:**

-  The file is indented for readability. This is not required; the added
   whitespace is ignored.
-  The dataset contains three axes and two variables. Variables u and v
   are functions of time, latitude, and longitude.
-  The global attribute cdms\_filemap describes the mapping between
   variables and files. The entry
   ``[[u],[[0,1,-,-,u_2000.nc],[1,2,-,-,u_2001.nc],[2,3,,-,u_2002.nc] ]``
   indicates that variable ``u`` is contained in file u\_2000.nc for
   time index 0, u\_2001.nc for time index 1, etc.

{% highlight xml %}

.. raw:: html

   <?xml version="1.0"?>

.. raw:: html

   <!DOCTYPE dataset SYSTEM "http://www-pcmdi.llnl.gov/software/cdms/cdml.dtd">

 [-90. -78. -66. -54. -42. -30. -18. -6. 6. 18. 30. 42. 54. 66. 78. 90.]

::

    <axis
        id ="longitude"
        length="32"
        units="degrees_east"
        datatype="Double"
    >

        [ 0. 11.25 22.5 33.75 45. 56.25 67.5 78.75 90.

        101.25 112.5 123.75 135. 146.25 157.5 168.75 180. 191.25

        202.5 213.75 225. 236.25 247.5 258.75 270. 281.25 292.5

        303.75 315. 326.25 337.5 348.75]
    </axis>

    <axis
        id ="time"
        partition="[0 1 1 2 2 3]"
        calendar="gregorian"
        units="days since 2000-1-1"
        datatype="Double"
        length="3"
        name_in_file="time"
    >

        [ 0. 366. 731.]
    </axis>

    <variable
        id ="u"
        missing_value="-99.9"
        units="m/s"
        datatype="Double"
    >
        <domain>
            <domElem name="time" length="3" start="0"/>
            <domElem name="latitude" length="16" start="0"/>
            <domElem name="longitude" length="32" start="0"/>
        </domain>
    </variable>

    <variable
        id ="v"
        missing_value="-99.9"
        units="m/s"
        datatype="Double"
    >
        <domain>
            <domElem name="time" length="3" start="0"/>
            <domElem name="latitude" length="16" start="0"/>
            <domElem name="longitude" length="32" start="0"/>
        </domain>
    </variable>

 {% endhighlight %}
