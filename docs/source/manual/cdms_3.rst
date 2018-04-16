Module: CdTime
--------------

Time Types
^^^^^^^^^^
.. highlight:: python
   :linenothreshold: 3

.. testsetup:: *

   import requests
   fnames = [ 'clt.nc', 'geos-sample', 'xieArkin-T42.nc', 'remap_grid_POP43.nc', 'remap_grid_T42.nc', 'rmp_POP43_to_T42_conserv.n', 'rmp_T42_to_POP43_conserv.nc', 'ta_ncep_87-6-88-4.nc', 'rmp_T42_to_C02562_conserv.nc' ]
   for file in fnames:
       url = 'https://cdat.llnl.gov/cdat/sample_data/'+file
       r = requests.get(url)
       open(file, 'wb').write(r.content)

.. testcleanup:: *

    import os
    fnames = [ 'clt.nc', 'geos-sample', 'xieArkin-T42.nc', 'remap_grid_POP43.nc', 'remap_grid_T42.nc', 'rmp_POP43_to_T42_conserv.n', 'rmp_T42_to_POP43_conserv.nc', 'ta_ncep_87-6-88-4.nc', 'rmp_T42_to_C02562_conserv.nc' ]
    for file in fnames:
       os.remove(file)


The ``cdtime`` module implements the CDMS time types, methods, and
calendars. These are made available with the command:

.. doctest::

   >>> import cdtime

Two time types are available: relative time and component time. Relative
time is time relative to a fixed base time. It consists of:

-  a units string, of the form ‘units since basetime’, and
-  a floating-point value

For example, the time “28.0 days since 1996-1-1” has value=28.0, and
units=’days since 1996-1-1’

Component time consists of the integer fields year, month, day, hour,
minute, and the floating-point field second. A sample component time is
``1996-2-28 12:10:30.0``

The ``cdtime`` module contains functions for converting between these
forms, based on the common calendars used in climate simulation. Basic
arithmetic and comparison operators are also available.

Calendars
^^^^^^^^^

A calendar specifies the number of days in each month, for a given year.
cdtime supports these calendars:

-  ``cdtime.GregorianCalendar``: years evenly divisible by four are leap
   years, except century years not evenly divisible by 400. This is
   sometimes called the proleptic Gregorian calendar, meaning that the
   algorithm for leap years applies for all years.
-  ``cdtime.MixedCalendar``: mixed Julian/Gregorian calendar. Dates
   before 158210-15 are encoded with the Julian calendar, otherwise are
   encoded with the Gregorian calendar. The day immediately following
   1582-10-4 is 1582-10-15. This is the default calendar.
-  ``cdtime.JulianCalendar``: years evenly divisible by four are leap
   years,
-  ``cdtime.NoLeapCalendar``: all years have 365 days,
-  ``cdtime.Calendar360``: all months have 30 days.

Several ``cdtime`` functions have an optional calendar argument. The
default calendar is the ``MixedCalendar``. The default calendar may be
changed with the command:


``cdtime.DefaultCalendar = newCalendar``

Time Constructors
^^^^^^^^^^^^^^^^^

The following table describes the methods for creating time types.
 
Table Time Constructors
~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table:: 
   :header:  "Type", "Constructor", "Defintion"
   :widths:  10, 40, 80
   :align: left

   "Reltime", "``cdtime.reltime(value, relunits)``", "Create a relative time type."
   ,, "``value`` is an integer or floating point value."
   ,, "``relunits`` is a string of the form 'unit(s) [since basetime]' where ``unit = [second | minute | hour | day | week | month | season | year ]``"
   ,, "``basetime`` has the form ``yyyy-mm-dd hh:mi:ss``.  The default basetime is 1979-1-1, if no ``since`` clause is specified.  **Example:**  ``r = cdtime.reltime(28, 'days since 1996-1-1')``"

   "Comptime", "``cdtime.comptime(year, month=1, day=1, hour=0, minute=0, second=0.0)``", "Create a component time type."
   ,,"``year`` is an integer."
   ,,"``month`` is an integer in the range 1 .. 12"
   ,,"``day`` is an integer in the range 1 .. 31"
   ,,"``hour`` is an integer in the range 0 .. 23"
   ,,"``minute`` is an integer in the range 0 .. 59"
   ,,"``second`` is a floating point number in the range 0.0 ,, 60.0. **Example:** ``c = cdtime.comptime(1996, 2, 28)``"


Relative Time
^^^^^^^^^^^^^

A relative time type has two members, value and units. Both can be set.

Table Relative Time Members
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+----------+---------+-------------------------------------------------------+
| Type     | Name    | Summary                                               |
+==========+=========+=======================================================+
| Float    | value   | Number of units                                       |
+----------+---------+-------------------------------------------------------+
| String   | units   | Relative units, of the form “unit(s) since basetime   |
+----------+---------+-------------------------------------------------------+

Component Time
^^^^^^^^^^^^^^

A component time type has six members, all of which are settable.

Table Component Time
~~~~~~~~~~~~~~~~~~~~
.. csv-table:: 
   :header: "Type", "Name", "Summary"
   :widths: 15, 15, 50

   "Integer", "year",  "Year value"
   "Integer", "month", "Month, in the range 1..12"
   "Integer", "day", "Day of month, in the range 1 .. 31"
   "Integer", "hour", "Hour, in the range 0 .. 23"
   "Integer", "minute", "Minute, in the range 0 .. 59"
   "Float", "second", "Seconds, in the range 0.0 .. 60.0"

Time Methods
^^^^^^^^^^^^

The following methods apply both to relative and component times.

Table Time Methods
~~~~~~~~~~~~~~~~~~
.. csv-table:: 
   :header: "Type", "Method", "Definition"
   :widths: 20, 75, 80
   :align: left

   "Comptime or Reltime", "``t.add(value,intervalUnits, calendar=cdtime.Default-Calendar)``", "Add an interval of time to a time type t.  Returns the same type of time."
   ,, "``value`` is the   Float number of interval units."
   ,, "``intervalUnits`` is ``cdtime.[Second (s) | Minute(s) Hour(s) | Day(s) |  Week(s) | Month(s) | Season(s) | Year(s) ]``"
   ,, "``calendar`` is the calendar type."
   "Integer", "``t.cmp(t2, calendar=cdtime.DefaultCalendar)``", "Compare time values t and t2. Returns -1, 0, 1 as t is less than, equal to, or greater than t2 respectively."
   ,, "``t2`` is the time to compare."
   ,, "``calendar`` is the calendar type."
   "Comptime or Reltime", "``t.sub(value,intervalUnits, calendar=cdtime.DefaultCalendar)``", "Subtract an interval of time from a time type t.  Returns the same type of time."
   ,, "``value`` is the Float number of interval units."
   ,, "``intervalUnits`` is cdtime.[Second (s) | Minute(s) | Hour(s) | Day(s) | Week(s) | Month(s) | Season(s) | Year(s)]"
   ,, "``calendar`` is the calendar type. "
   "Comptime", "``t.tocomp(calendar = cdtime.DefaultCalendar)``", "Convert to component time.  Returns the equivalent component time."
   ,, "``calendar`` is the calendar type."
   "Reltime", "``t.torel(units, calendar=cdtime.DefaultCalendar)``", "Convert to relative time.  Returns the equivalent relative time."
   

Examples
^^^^^^^^
.. 

   >>> from cdtime import *
   >>> c = comptime(1996,2,28)
   >>> r = reltime(28,"days since 1996-1-1")          
   >>> print r.add(1,Day)
   29.000000 days since 1996-1-1
   >>> print c.add(36,Hours)
   1996-2-29 12:0:0.0 


**Note:** When adding or subtracting intervals of months or years, only the month and year of the result are significant.   The reason is that intervals in months/years are not commensurate with intervals in days or fractional days. This leads to results that may be surprising.

.. 

   >>> c = comptime(1979,8,31)      
   >>> c.add(1,Month)               
   1979-9-1 0:0:0.0                 
                    

In other words, the day component of c was ignored in the addition, and the day/hour/minute components of the results are just the defaults.  If the interval is in years, the interval is converted internally to months:            
                    
..                     

   >>> c = comptime(1979,8,31)      
   >>> c.add(2,Years)               
   1981-8-1 0:0:0.0                 

Compare time values.
                    
.. 

   >>> from cdtime import *         
   >>> r = cdtime.reltime(28,"days since 1996-1-1")   
   >>> c = comptime(1996,2,28)      
   >>> print c.cmp(r)               
   1

..   >>> print r.cmp(c)               
..   -1
..   >>> print r.cmp(r)               
..   1
                    
Subtract an interval of time.

.. 

   >>> from cdtime import *         
   >>> r = cdtime.reltime(28,"days since 1996-1-1")   
   >>> c = comptime(1996,2,28)      
   >>> print r.sub(10,Days)         
   18.000000 days since 1996-1-1        
   >>> print c.sub(30,Days)         
   1996-1-29 0:0:0.0                

                    
For intervals of years or months, see the **note** under add() in the example above.

Convert to component time.

.. 

   >>> r = cdtime.reltime(28,"days since 1996-1-1")   
   >>> r.tocomp()
   1996-1-29 0:0:0.0                


Convert to relative time.

.. 
                    
   >>> c = comptime(1996,2,28)      
   >>> print c.torel("days since 1996-1-1")           
   58.000000 days since 1996-1-1        
   >>> r = reltime(28,"days since 1996-1-1")          
   >>> print r.torel("days since 1995")               
   393.000000 days since 1995           
   >>> print r.torel("days since 1995").value         
   393.0          

