#***************************************************
#** ViSUS Visualization Project                    **
#** Copyright (c) 2010 University of Utah          **
#** Scientific Computing and Imaging Institute     **
#** 72 S Central Campus Drive, Room 3750           **
#** Salt Lake City, UT 84112                       **
#**                                                **
#** For information about this project see:        **
#** http://www.pascucci.org/visus/                 **
#**                                                **
#**      or contact: pascucci@sci.utah.edu         **
#**                                                **
#****************************************************

from visuspy import *

import gc
import sys
import math
import unittest
import string 
import numpy

import unittest
import vcs
import cdms2
  

# ////////////////////////////////////////////////////////////////////////
class TextIdx(unittest.TestCase):
  
  def testIdx(self):
    self.filename="temp/tutorial_1.idx"

    self.filename="https://feedback.llnl.gov/cgi-bin/cdat_to_idx_create.cgi?dataset=nasa_ganymed_7km_3d.xml"
    self.filename="https://feedback.llnl.gov/mod_visus?action=readdataset&dataset=nature%5F2007%5F2d%5Fhourly%2Fmet1"
    self.filename="https://feedback.llnl.gov/mod_visus?action=readdataset&dataset=nature%5F2007%5F2d%5Fhourly%2Fmet1"
    self.filename="https://feedback.llnl.gov/mod_visus?action=readdataset&dataset=nature_2007_met1_hourly"
#    self.WriteIdx()
    self.ReadIdx()
#    self.MergeIdx()
  
  def ReadIdx(self): 
    
    pp=vcs.init()
    dataset=visuspy.Dataset_loadDataset(self.filename)
    self.assertIsNotNone(dataset)
    box=dataset.get().getBox()
    #field=dataset.get().getDefaultField()
    import pdb
    pdb.set_trace()
    Title=dataset.get().getFields()[24].getDescription()
    field=dataset.get().getFields()[24]
    access=dataset.get().createAccess()
    
    sampleid=0
    slice_box=box.getZSlab(4,5)
      
    query=QueryPtr(Query(dataset.get(),ord('r')))
    query.get().position=Position(slice_box)
    query.get().field=field
    time = dataset.get().getTimesteps().getAt(689)
    query.get().time=689
    timeMin = int(dataset.get().getTimesteps().getMin())
    timeMax = int(dataset.get().getTimesteps().getMax())
    timeArray =  dataset.get().getTimesteps().asVector()
    #timeAxis = cdms2.createAxis(range(timeMin,timeMax))
    timeAxis = cdms2.createAxis([689])
    timeAxis.designateTime()

    MaxH=dataset.get().getBitmask().getMaxResolution()
      
#    self.assertTrue(dataset.get().beginQuery(query))
#    self.assertTrue(query.get().nsamples.innerProduct()>0)
#    self.assertTrue(dataset.get().executeQuery(access,query))
      
    query.get().end_resolutions.push_back(MaxH-5)
    query.get().merge_mode=Query.InsertSamples
    self.assertTrue(dataset.get().beginQuery(query))
    self.assertTrue(query.get().nsamples.innerProduct()>0)
    self.assertTrue(dataset.get().executeQuery(access,query))
    print query.get().cur_resolution
    check=convertToNumPyArray(query.get().buffer)
#    T2M = cdms2.MV2.TransientVariable(check[:,:, numpy.newaxis])
    T2M = cdms2.MV2.TransientVariable(check[:])
    T2M.id=Title
    (nlat,nlon) = T2M.shape
    grid= cdms2.createUniformGrid(-90, nlat, 180./(nlat-1), -180, nlon, 360./(nlon-1), order="yx", mask=None)
    T2M.setGrid(grid)
    T2M.setAxis(0,T2M.getGrid().getAxis(0))
    T2M.setAxis(1,T2M.getGrid().getAxis(1))
#    T2M.setAxis(2,timeAxis)
#    gm=vcs.createisofill()
#    gm.levels=vcs.mkscale(250,300)
#    import pdb
#    pdb.set_trace()
#    pp.plot(T2M, gm)
    pp.plot(T2M)
    pp.png("T2M.png")
    pp.interact()
    pp.clear()
#    self.assertTrue(dataset.get().nextQuery(query))
#    self.assertTrue(query.get().nsamples.innerProduct()>0)
#    self.assertTrue(dataset.get().executeQuery(access,query))
#    print query.get().cur_resolution
#    check=convertToNumPyArray(query.get().buffer)
#    T2M = cdms2.MV2.TransientVariable(check[:])
#    T2M.id=Title
#    (nlat,nlon) = T2M.shape
#    grid= cdms2.createUniformGrid(-90, nlat, 180./(nlat-1), -180, nlon, 360./(nlon-1), order="yx", mask=None)
#    T2M.setGrid(grid)
#    T2M.setAxis(0,T2M.getGrid().getAxis(0))
#    T2M.setAxis(1,T2M.getGrid().getAxis(1))
#    pp.plot(T2M,gm)
#    pp.interact()
#    pp.clear()
#    self.assertTrue(dataset.get().nextQuery(query))
#    self.assertTrue(query.get().nsamples.innerProduct()>0)
#    self.assertTrue(dataset.get().executeQuery(access,query))
#    print query.get().cur_resolution
#    check=convertToNumPyArray(query.get().buffer)
#    T2M = cdms2.MV2.TransientVariable(check[:])
#    T2M.id=Title
#    (nlat,nlon) = T2M.shape
#    grid= cdms2.createUniformGrid(-90, nlat, 180./(nlat-1), -180, nlon, 360./(nlon-1), order="yx", mask=None)
#    T2M.setGrid(grid)
#    T2M.setAxis(0,T2M.getGrid().getAxis(0))
#    T2M.setAxis(1,T2M.getGrid().getAxis(1))
#    pp.plot(T2M,gm)
#    pp.png("T2M.png")
#    pp.interact()
#    pp.clear()


    
#    query.get().end_resolutions.push_back(8)
#    query.get().end_resolutions.push_back(12)
#    query.get().merge_mode=Query.InsertSamples
    
    
#    self.assertTrue(dataset.get().beginQuery(query))
#    self.assertTrue(query.get().nsamples.innerProduct()>0)
#    self.assertTrue(dataset.get().executeQuery(access,query))
#    self.assertEqual(query.get().cur_resolution,8)
    

# ////////////////////////////////////////////////////////
if __name__ == '__main__':
  SetCommandLine()
  IdxModule.attach()
  unittest.main()
  IdxModule.detach()


