#!/bin/bash
a=('cdmsobj'  'axis'  'coord'  'grid'  'hgrid'  'avariable'  'sliceut'  'error'  'variable'  'fvariable'  'tvariable'  'dataset'  'database'  'cache'  'selectors'  'MV2'  'convention'  'bindex'  'auxcoord'  'gengrid'  'gsHost'  'gsStaticVariable'  'gsTimeVariable'  'mvBaseWriter'  'mvSphereMesh'  'mvVsWriter'  'mvCdmsRegrid')

for i in "${a[@]}"; do
echo "creating "$i".rst"
echo "$i
========

.. automodule:: Lib.$i
   :members:
" >$i.rst


done

