CDMS Manual Table of Contents
=============================

`CHAPTER 1 Introduction <cdms_1.html>`__
''''''''''''''''''''''''''''''''''''''''

-  `1.1 Overview <cdms_1.html#1.1>`__
-  `1.2 Variables <cdms_1.html#1.2>`__
-  `1.3 File I/O <cdms_1.html#1.3>`__
-  `1.4 Coordinate Axes <cdms_1.html#1.4>`__
-  `1.5 Attributes <cdms_1.html#1.5>`__
-  `1.6 Masked values <cdms_1.html#1.6>`__
-  `1.7 File Variables <cdms_1.html#1.7>`__
-  `1.8 Dataset Variables <cdms_1.html#1.8>`__
-  `1.9 Grids <cdms_1.html#1.9>`__

   -  `1.9.1 Example: a curvilinear grid <cdms_1.html#1.9.1>`__
   -  `1.9.2 Example: a generic grid <cdms_1.html#1.9.2>`__

-  `1.10 Regridding <cdms_1.html#1.10>`__

   -  `1.10.1 CDMS Regridder <cdms_1.html#1.10.1>`__
   -  `1.10.2 SCRIP Regridder <cdms_1.html#1.10.2>`__

-  `1.11 Time types <cdms_1.html#1.11>`__
-  `1.12 Plotting data <cdms_1.html#1.12>`__
-  `1.13 Databases <cdms_1.html#1.13>`__

`CHAPTER 2 CDMS Python Application Programming Interface <cdms_2.html>`__
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

-  `2.1 Overview <cdms_2.html#2.1>`__

   -  `Table 2.1 Python types used in CDMS <cdms_2.html#table_2.1>`__

-  `2.2 A first example <cdms_2.html#2.2>`__
-  `2.3 cdms module <cdms_2.html#2.3>`__

   -  `Table 2.2 cdms module functions <cdms_2.html#table_2.2>`__
   -  `Table 2.3 Class Tags <cdms_2.html#table_2.3>`__

-  `2.4 CdmsObj <cdms_2.html#2.4>`__

   -  `Table 2.4 Attributes common to all CDMS
      objects <cdms_2.html#table_2.4>`__
   -  `Table 2.5 Getting and setting
      attributes <cdms_2.html#table_2.5>`__

-  `2.5 CoordinateAxis <cdms_2.html#2.5>`__

   -  `Table 2.6 CoordinateAxis types <cdms_2.html#table_2.6>`__
   -  `Table 2.7 CoordinateAxis Internal
      Attributes <cdms_2.html#table_2.7>`__
   -  `Table 2.8 Axis Constructors <cdms_2.html#table_2.8>`__
   -  `Table 2.9 CoordinateAxis Methods <cdms_2.html#table_2.9>`__
   -  `Table 2.10 Axis Methods, additional to CoordinateAxis
      methods <cdms_2.html#table_2.10>`__
   -  `Table 2.11 Axis Slice Operators <cdms_2.html#table_2.11>`__

-  `2.6 CdmsFile <cdms_2.html#2.6>`__

   -  `Table 2.12 CdmsFile Internal
      Attributes <cdms_2.html#table_2.12>`__
   -  `Table 2.13 CdmsFile Constructors <cdms_2.html#table_2.13>`__
   -  `Table 2.14 CdmsFile Methods <cdms_2.html#table_2.14>`__
   -  `Table 2.15 CDMS Datatypes <cdms_2.html#table_2.15>`__

-  `2.7 Database <cdms_2.html#2.7>`__

   -  `2.7.1 Overview <cdms_2.html#2.7.1>`__

      -  `Table 2.16 Database Internal
         Attributes <cdms_2.html#table_2.16>`__
      -  `Table 2.17 Database Constructors <cdms_2.html#table_2.17>`__
      -  `Table 2.18 Database Methods <cdms_2.html#table_2.18>`__

   -  `2.7.2 Searching a database <cdms_2.html#2.7.2>`__

      -  `Table 2.19 SearchResult Methods <cdms_2.html#table_2.19>`__
      -  `Table 2.20 ResultEntry Attributes <cdms_2.html#table_2.20>`__
      -  `Table 2.21 ResultEntry Methods <cdms_2.html#table_2.21>`__

   -  `2.7.3 Accessing data <cdms_2.html#2.7.3>`__
   -  `2.7.4 Examples of database searches <cdms_2.html#2.7.4>`__

-  `2.8 Dataset <cdms_2.html#2.8>`__

   -  `Table 2.22 Dataset Internal
      Attributes <cdms_2.html#table_2.22>`__
   -  `Table 2.23 Dataset Constructors <cdms_2.html#table_2.23>`__
   -  `Table 2.24 Open Modes <cdms_2.html#table_2.24>`__
   -  `Table 2.25 Dataset Methods <cdms_2.html#table_2.25>`__

-  `2.9 MV module <cdms_2.html#2.9>`__

   -  `Table 2.26 Variable Constructors in module
      MV <cdms_2.html#table_2.26>`__
   -  `Table 2.27 MV functions <cdms_2.html#table_2.27>`__

-  `2.10 HorizontalGrid <cdms_2.html#2.10>`__

   -  `Table 2.28 <cdms_2.html#table_2.28>`__
   -  `Table 2.29 HorizontalGrid Internal
      Attributes <cdms_2.html#table_2.29>`__
   -  `Table 2.30 RectGrid Constructors <cdms_2.html#table_2.30>`__
   -  `Table 2.31 HorizontalGrid Methods <cdms_2.html#table_2.31>`__
   -  `Table 2.32 RectGrid Methods, additional to HorizontalGrid
      Methods <cdms_2.html#table_2.32>`__

-  `2.11 Variable <cdms_2.html#2.11>`__

   -  `Table 2.33 Variable Internal
      Attributes <cdms_2.html#table_2.33>`__
   -  `Table 2.34 Variable Constructors <cdms_2.html#table_2.34>`__
   -  `Table 2.35 Variable Methods <cdms_2.html#table_2.35>`__
   -  `Table 2.36 Variable Slice Operators <cdms_2.html#table_2.36>`__
   -  `Table 2.37 Index and Coordinate
      Intervals <cdms_2.html#table_2.37>`__
   -  `2.11.1 Selectors <cdms_2.html#2.11.1>`__

      -  `Table 2.38 Selector keywords <cdms_2.html#table_2.38>`__

   -  `2.11.2 Selector examples <cdms_2.html#2.11.2>`__

-  `2.12 Examples <cdms_2.html#2.12>`__

`CHAPTER 3 cdtime Module <cdms_3.html>`__
'''''''''''''''''''''''''''''''''''''''''

-  `3.1 Time types <cdms_3.html#3.1>`__
-  `3.2 Calendars <cdms_3.html#3.2>`__
-  `3.3 Time Constructors <cdms_3.html#3.3>`__

   -  `Table 3.1 Time Constructors <cdms_3.html#table_3.1>`__

-  `3.4 Relative Time <cdms_3.html#3.4>`__

   -  `Table 3.2 Relative Time Members <cdms_3.html#table_3.2>`__

-  `3.5 Component Time <cdms_3.html#3.5>`__

   -  `Table 3.3 Component Time Members <cdms_3.html#table_3.3>`__

-  `3.6 Time Methods <cdms_3.html#3.6>`__

   -  `Table 3.4 Time Methods <cdms_3.html#table_3.4>`__

`CHAPTER 4 Regridding Data <cdms_4.html>`__
'''''''''''''''''''''''''''''''''''''''''''

-  `4.1 Overview <cdms_4.html#4.1>`__

   -  `4.1.1 CDMS horizontal regridder <cdms_4.html#4.1.1>`__
   -  `4.1.2 SCRIP horizontal regridder <cdms_4.html#4.1.2>`__
   -  `4.1.3 Pressure-level regridder <cdms_4.html#4.1.3>`__
   -  `4.1.4 Cross-section regridder <cdms_4.html#4.1.4>`__

-  `4.2 regrid module <cdms_4.html#4.2>`__

   -  `4.2.1 CDMS horizontal regridder <cdms_4.html#4.2.1>`__

      -  `Table 4.1 CDMS Regridder
         Constructor <cdms_4.html#table_4.1>`__

   -  `4.2.2 SCRIP Regridder <cdms_4.html#4.2.2>`__

      -  `Table 4.2 SCRIP Regridder
         Constructor <cdms_4.html#table_4.2>`__

-  `4.3 regridder functions <cdms_4.html#4.3>`__

   -  `4.3.1 CDMS regridder functions <cdms_4.html#4.3.1>`__

      -  `Table 4.3 CDMS Regridder function <cdms_4.html#table_4.3>`__

   -  `4.3.2 SCRIP Regridder functions <cdms_4.html#4.3.2>`__

      -  `Table 4.4 SCRIP Regridder functions <cdms_4.html#table_4.4>`__

-  `4.4 Examples <cdms_4.html#4.4>`__

   -  `4.4.1 CDMS regridder <cdms_4.html#4.4.1>`__
   -  `4.4.2 SCRIP regridder <cdms_4.html#4.4.2>`__

`CHAPTER 5 Plotting CDMS data in Python <cdms_5.html>`__
''''''''''''''''''''''''''''''''''''''''''''''''''''''''

-  `5.1 Overview <cdms_5.html#5.1>`__
-  `5.2 Examples <cdms_5.html#5.2>`__

   -  `5.2.1 Example: plotting a gridded variable <cdms_5.html#5.2.1>`__
   -  `5.2.2 Example: using plot keywords. <cdms_5.html#5.2.2>`__
   -  `5.2.3 Example: plotting a time-latitude
      slice <cdms_5.html#5.2.3>`__
   -  `5.2.4 Example: plotting subsetted data <cdms_5.html#5.2.4>`__

-  `5.3 plot method <cdms_5.html#5.3>`__

   -  `Table 5.1 plot keywords <cdms_5.html#table_5.1>`__

`CHAPTER 6 Climate Data Markup Language (CDML) <cdms_6.html>`__
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

-  `6.1 Introduction <cdms_6.html#6.1>`__
-  `6.2 Elements <cdms_6.html#6.2>`__

   -  `Table 6.1 CDML Tags <cdms_6.html#table_6.1>`__

-  `6.3 Special Characters <cdms_6.html#6.3>`__

   -  `Table 6.2 Special Character Encodings <cdms_6.html#table_6.2>`__

-  `6.4 Identifiers <cdms_6.html#6.4>`__
-  `6.5 CF Metadata Standard <cdms_6.html#6.5>`__
-  `6.6 CDML Syntax <cdms_6.html#6.6>`__

   -  `6.6.1 Dataset Element <cdms_6.html#6.6.1>`__

      -  `Table 6.3 Dataset Attributes <cdms_6.html#table_6.3>`__

   -  `6.6.2 Axis Element <cdms_6.html#6.6.2>`__

      -  `Table 6.4 Axis Attributes <cdms_6.html#table_6.4>`__

   -  `6.6.3 partition attribute <cdms_6.html#6.6.3>`__
   -  `6.6.4 Grid Element <cdms_6.html#6.6.4>`__

      -  `Table 6.5 RectGrid Attributes <cdms_6.html#table_6.5>`__

   -  `6.6.5 Variable Element <cdms_6.html#6.6.5>`__

      -  `Table 6.6 Variable Attributes <cdms_6.html#table_6.6>`__

   -  `6.6.6 Attribute Element <cdms_6.html#6.6.6>`__

-  `6.7 A Sample CDML Document <cdms_6.html#6.7>`__

`CHAPTER 7 CDMS Utilities <cdms_7.html>`__
''''''''''''''''''''''''''''''''''''''''''

-  `7.1 cdscan: Importing datasets into CDMS <cdms_7.html#7.1>`__

   -  `7.1.1 Overview <cdms_7.html#7.1.1>`__
   -  `7.1.2 cdscan Syntax <cdms_7.html#7.1.2>`__

      -  `Table 7.1 cdscan command options <cdms_7.html#table_7.1>`__

   -  `7.1.3 Examples <cdms_7.html#7.1.3>`__
   -  `7.1.4 File Formats <cdms_7.html#7.1.4>`__
   -  `7.1.5 Name Aliasing <cdms_7.html#7.1.5>`__

`APPENDIX A CDMS Classes <cdms_appendix.html#a>`__
''''''''''''''''''''''''''''''''''''''''''''''''''

`APPENDIX B Version Notes <cdms_appendix.html#b>`__
'''''''''''''''''''''''''''''''''''''''''''''''''''

-  `B.1 Version 4.0 <cdms_appendix.html#b.1>`__
-  `B.2 Version 3.0 Overview <cdms_appendix.html#b.2>`__
-  `B.3 V3.0 Details <cdms_appendix.html#b.3>`__

   -  `B.3.1 AbstractVariable <cdms_appendix.html#b.3.1>`__
   -  `B.3.2 AbstractAxis <cdms_appendix.html#b.3.2>`__
   -  `B.3.3 AbstractDatabase <cdms_appendix.html#b.3.3>`__
   -  `B.3.4 Dataset <cdms_appendix.html#b.3.4>`__
   -  `B.3.5 cdms module <cdms_appendix.html#b.3.5>`__
   -  `B.3.6 CdmsFile <cdms_appendix.html#b.3.6>`__
   -  `B.3.7 CDMSError <cdms_appendix.html#b.3.7>`__
   -  `B.3.8 AbstractRectGrid <cdms_appendix.html#b.3.8>`__
   -  `B.3.9 InternalAttributes <cdms_appendix.html#b.3.9>`__
   -  `B.3.10 TransientVariable <cdms_appendix.html#b.3.10>`__
   -  `B.3.11 MV <cdms_appendix.html#b.3.11>`__

`APPENDIX C cu Module <cdms_appendix.html#c>`__
'''''''''''''''''''''''''''''''''''''''''''''''

-  `C.1 Slab <cdms_appendix.html#c.1>`__

   -  `Table C.1 Slab Methods <cdms_appendix.html#table_c.1>`__

-  `C.2 cuDataset <cdms_appendix.html#c.2>`__

   -  `Table C.2 cuDataset Methods <cdms_appendix.html#table_c.2>`__
