CHAPTER 5 Plotting CDMS data in Python
--------------------------------------

5.1 Overview
~~~~~~~~~~~~

Data read via the CDMS Python interface can be plotted using the ``vcs``
module. This module, part of the Ultrascale Visualization Climate Data
Analysis Tool (UV-CDAT) is documented in the UV-CDAT reference manual.
The ``vcs`` module provides access to the functionality of the VCS
visualization program.

Examples of plotting data accessed from CDMS are given below, as well as
documentation for the plot routine keywords.

5.2 Examples
~~~~~~~~~~~~

In the following examples, it is assumed that variable ``psl`` is
dimensioned (time, latitude, longitude). ``psl`` is contained in the
dataset named ``'sample.xml'``.

5.2.1 Example: plotting a gridded variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

{% highlight python %} 1 import cdms, vcs 2 3 f =
cdms.open('sample.xml') 4 psl = f.variables['psl'] 5 sample = psl[0] 6
w=vcs.init() 7 8 w.plot(sample) 9 f.close() {% endhighlight %}

**Notes:**

+------+------+
| Line | Note |
|      | s    |
+======+======+
| 5    | Get  |
|      | a    |
|      | hori |
|      | zont |
|      | al   |
|      | slic |
|      | e,   |
|      | for  |
|      | the  |
|      | firs |
|      | t    |
|      | time |
|      | poin |
|      | t.   |
+------+------+
| 6    | Crea |
|      | te   |
|      | a    |
|      | VCS  |
|      | Canv |
|      | as   |
|      | ``w` |
|      | `.   |
+------+------+
| 8    | Plot |
|      | the  |
|      | data |
|      | .    |
|      | Beca |
|      | use  |
|      | samp |
|      | le   |
|      | is a |
|      | tran |
|      | sien |
|      | t    |
|      | vari |
|      | able |
|      | ,    |
|      | it   |
|      | enca |
|      | psul |
|      | ates |
|      | all  |
|      | the  |
|      | time |
|      | ,    |
|      | lati |
|      | tude |
|      | ,    |
|      | long |
|      | itud |
|      | e,   |
|      | and  |
|      | attr |
|      | ibut |
|      | e    |
|      | info |
|      | rmat |
|      | ion. |
+------+------+
| 9    | Clos |
|      | e    |
|      | the  |
|      | file |
|      | .    |
|      | This |
|      | must |
|      | be   |
|      | done |
|      | afte |
|      | r    |
|      | the  |
|      | refe |
|      | renc |
|      | e    |
|      | to   |
|      | the  |
|      | pers |
|      | iste |
|      | nt   |
|      | vari |
|      | able |
|      | ``ps |
|      | l``. |
+------+------+

Thats it! The axis coordinates, variable name, description, units, etc.
are obtained from variable sample.

What if the units are not explicitly defined for ``psl``, or a different
description is desired? ``plot`` has a number of other keywords which
fill in the extra plot information.

5.2.2 Example: using aplot keywords.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

{% highlight python %} w.plot(array, units='mm/day',
file\_comment='High-frequency reanalysis', long\_name="Sea level
pressure", comment1="Sample plot", hms="18:00:00", ymd="1978/01/01") {%
endhighlight %}

**Note:** Keyword arguments can be listed in any order.

5.2.3 Example: plotting a time-latitude slice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming that variable ``psl`` has domain ``(time,latitude,longitude)``,
this example selects and plots a time-latitude slice:

{% highlight python %} 1 samp = psl[:,:,0] 2 w = vcs.init() 3
w.plot(samp, name='sea level pressure') {% endhighlight %}

Notes:

+------+------+
| Line | Note |
|      | s    |
+======+======+
| 1    | ``sa |
|      | mp`` |
|      | is a |
|      | slic |
|      | e    |
|      | of   |
|      | ``ps |
|      | l``, |
|      | at   |
|      | inde |
|      | x    |
|      | ``0` |
|      | `    |
|      | of   |
|      | the  |
|      | last |
|      | dime |
|      | nsio |
|      | n.   |
|      | Sinc |
|      | e    |
|      | ``sa |
|      | mp`` |
|      | was  |
|      | obta |
|      | ined |
|      | from |
|      | the  |
|      | slic |
|      | e    |
|      | oper |
|      | ator |
|      | ,    |
|      | it   |
|      | is a |
|      | tran |
|      | sien |
|      | t    |
|      | vari |
|      | able |
|      | ,    |
|      | whic |
|      | h    |
|      | incl |
|      | udes |
|      | the  |
|      | lati |
|      | tude |
|      | and  |
|      | time |
|      | info |
|      | rmat |
|      | ion. |
+------+------+
| 3    | The  |
|      | ``na |
|      | me`` |
|      | keyw |
|      | ord  |
|      | defi |
|      | nes  |
|      | the  |
|      | iden |
|      | tifi |
|      | er,  |
|      | by   |
|      | defa |
|      | ult  |
|      | the  |
|      | name |
|      | in   |
|      | the  |
|      | file |
|      | .    |
+------+------+

5.2.4 Example: plotting subsetted data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Calling the variable ``psl`` as a function reads a subset of the
variable. The result variable ``samp`` can be plotted directly:

{% highlight python %} ... 1 samp = psl(time = (0.0,100.0), longitude =
180.0) 2 w = vcs.init() 3 w.plot(samp) {% endhighlight %}

5.3 ``plot`` method
~~~~~~~~~~~~~~~~~~~

The ``plot`` method is documented in the UV-CDAT Reference Manual. This
section augments the documentation with a description of the optional
keyword arguments. The general form of the plot command is:

{% highlight python %} canvas.plot(array [, args] [,key=value [,
key=value [, ...] ] ]) {% endhighlight %}

where:

-  canvas is a VCS Canvas object, created with the vcs.init method.

-  array is a variable, masked array, or Numeric array having between
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

   See the UV-CDAT Reference Manual and VCS Reference Manual for a
   detailed description of these arguments.

-  ``key=value``, ... are optional keyword/value pairs, listed in any
   order. These are defined in the table below.

Table 5.1 ``plot`` keywords
                           

.. raw:: html

   <table class="table">

::

    <tr>
      <th>Key</th>

      <th>Type</th>

      <th>Value</th>
    </tr>

    <tr>
      <td ><code>comment1</code></td>

      <td >string</td>

      <td >Comment plotted above <code>file_comment</code></td>
    </tr>

    <tr>
      <td ><code>comment2</code></td>

      <td >string</td>

      <td >Comment plotted above <code>comment1</code></td>
    </tr>

    <tr>
      <td ><code>comment3</code></td>

      <td >string</td>

      <td >Comment plotted above <code>comment2</code></td>
    </tr>

    <tr>
      <td ><code>continents</code></td>

      <td >0 or 1</td>

      <td >if <code>1</code>, plot continental outlines (default:plot if <code>xaxis</code> is
      longitude, <code>yaxis</code> is latitude -or- <code>xname</code> is 'longitude' and <code>yname</code> is
      'latitude'</td>
    </tr>

    <tr>
      <td ><code>file_comment</code></td>

      <td >string</td>

      <td >Comment, defaults to <code>variable.parent.comment</code></td>
    </tr>

    <tr>
      <td ><code>grid</code></td>

      <td >CDMS grid object</td>

      <td >Grid associated with the data. Defaults to
      <code>variable.getGrid()</code></td>
    </tr>

    <tr>
      <td ><code>hms</code></td>

      <td >string</td>

      <td >Hour, minute, second</td>
    </tr>

    <tr>
      <td ><code>long_name</code></td>

      <td >string</td>

      <td >Descriptive variable name, defaults to <code>variable.long_name</code>.</td>
    </tr>

    <tr>
      <td ><code>missing_value</code></td>

      <td >same type as array</td>

      <td >Missing data value, defaults to <code>variable.getMissing()</code></td>
    </tr>

    <tr>
      <td ><code>name</code></td>

      <td >string</td>

      <td >Variable name, defaults to <code>variable.id</code></td>
    </tr>

    <tr>
      <td ><code>time</code></td>

      <td >cdtime relative or absolute</td>

      <td >
        <p>Time associated with the data.</p>

        <p><strong>Example:</strong></p>

        <p><code>cdtime.reltime(30.0, "days since 1978-1-1")</code>.</p>
      </td>
    </tr>

    <tr>
      <td ><code>units</code></td>

      <td >string</td>

      <td >Data units. Defaults to <code>variable.units</code></td>
    </tr>

    <tr>
      <td ><code>variable</code></td>

      <td >CDMS variable object</td>

      <td >Variable associated with the data. The variable grid must have the
      same shape as the data array.</td>
    </tr>

    <tr>
      <td ><code>xarray</code> (<code>[y|z|t|w]array</code>)</td>

      <td >1-D Numeric array</td>

      <td ><em>Rectangular grids only</em>. Array of coordinate values, having the
      same length as the corresponding dimension. Defaults to xaxis[:\]
      (y|z|t|waxis[:])</td>
    </tr>

    <tr>
      <td ><code>xaxis</code> (<code>[y|z|t|w]axis</code>)</td>

      <td >CDMS axis object</td>

      <td ><em>Rectangular grids only</em>. Axis object. <code>xaxis</code> defaults to
      <code>grid.getAxis(0)</code>, <code>yaxis</code> defaults to <code>grid.getAxis(1)</code></td>
    </tr>

    <tr>
      <td ><code>xbounds</code> (<code>ybounds</code>)</td>

      <td >2-D Numeric array</td>

      <td ><em>Rectangular grids only</em>. Boundary array of shape <code>(n,2)</code> where
      <code>n</code> is the axis length. Defaults to <code>xaxis.getBounds()</code>, or
      <code>xaxis.genGenericBounds()</code> if <code>None</code>, similarly for <code>ybounds</code>.</td>
    </tr>

    <tr>
      <td ><code>xname</code> (<code>[y|z|t|w]name</code>)</td>

      <td >string</td>

      <td ><em>Rectangular grids only</em>. Axis name. Defaults to <code>xaxis.id</code>
      (<code>[y|z|t|w]axis.id</code>)</td>
    </tr>

    <tr>
      <td ><code>xrev</code> (<code>yrev</code>)</td>

      <td >0 or 1</td>

      <td >
        <p>If <code>xrev</code> (<code>yrev</code>) is 1, reverse the direction of the x-axis (y-axis). Defaults to
        0, with the following exceptions:</p>

        <ul>
          <li>If the y-axis is latitude, and has decreasing values, <code>yrev</code> defaults to
          1</li>

          <li>If the y-axis is a vertical level, and has increasing pressure levels, <code>yrev</codE>
          defaults to 1.</li>
        </ul>
      </td>
    </tr>

    <tr>
      <td ><code>xunits</code> (<code>[y|z|t|w]units</code>)</td>

      <td >string</td>

      <td ><em>Rectangular grids only</em>. Axis units. Defaults to <code>xaxis.units</code>
      (<code>[y|z|t|w]axis.units</code>).</td>
    </tr>

.. raw:: html

   </table>
