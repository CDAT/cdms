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
  

# ////////////////////////////////////////////////////////////////////////
class TextIdx(unittest.TestCase):
  
  def testIdx(self):
    self.filename="temp/tutorial_1.idx"

    self.filename="https://feedback.llnl.gov/cgi-bin/cdat_to_idx_create.cgi?dataset=nasa_ganymed_7km_3d.xml"
    self.filename="https://feedback.llnl.gov/mod_visus?action=readdataset&dataset=nature%5F2007%5F2d%5Fhourly%2Fmet1"
#    self.WriteIdx()
    self.ReadIdx()
#    self.MergeIdx()
  
  # WriteIdx
  def WriteIdx(self): 
    
    dataset_box=NdBox(NdPoint(0,0,0),NdPoint.one(16,16,16))
    
    idxfile=IdxFile();
    idxfile.box=NdBox(dataset_box)
    idxfile.fields.push_back(Field("myfield",DType.parseFromString("uint32")))

    bSaved=idxfile.save(self.filename)
    self.assertTrue(bSaved)
    
    dataset=Dataset.loadDataset(self.filename)
    self.assertIsNotNone(dataset)
    access=dataset.get().createAccess()
    
    sampleid=0
    
    for Z in range(0,16):
      slice_box=dataset.get().getBox().getZSlab(Z,Z+1)
      
      query=QueryPtr(Query(dataset.get(),ord('w')))
      query.get().position=Position(slice_box)
      
      self.assertTrue(dataset.get().beginQuery(query))
      self.assertEqual(query.get().nsamples.innerProduct(),16*16)
      
      buffer=Array(query.get().nsamples,query.get().field.dtype)
      query.get().buffer=buffer
      
      fill=convertToNumPyArray(buffer)
      for Y in range(16):
        for X in range(16):
          fill[Y,X]=sampleid
          sampleid+=1

      self.assertTrue(dataset.get().executeQuery(access,query))

  # ReadIdx
  def ReadIdx(self): 
    
    import pdb
    pdb.set_trace()
    p=vcs.init()
    dataset=Dataset_loadDataset(self.filename)
    self.assertIsNotNone(dataset)
    box=dataset.get().getBox()
    field=dataset.get().getDefaultField()
    access=dataset.get().createAccess()
    
    sampleid=0
    for Z in range(0,16):
      slice_box=box.getZSlab(Z,Z+1)
      
      query=QueryPtr(Query(dataset.get(),ord('r')))
      query.get().position=Position(slice_box)
      
      self.assertTrue(dataset.get().beginQuery(query))
#      self.assertEqual(query.get().nsamples.innerProduct(),16*16)
      self.assertTrue(dataset.get().executeQuery(access,query))
      
      check=convertToNumPyArray(query.get().buffer)
      p.plot(check)
      p.interact()
#      for Y in range(16):
#        for X in range(16):
#          self.assertEqual(check[Y,X],sampleid)
#          sampleid+=1

  def MergeIdx(self): 
    
    dataset=Dataset_loadDataset(self.filename)
    self.assertIsNotNone(dataset)
    
    box=dataset.get().getBox()
    access=dataset.get().createAccess()
    field=dataset.get().getDefaultField()
    MaxH=dataset.get().getBitmask().getMaxResolution()
    self.assertEqual(MaxH,12) #in the bitmask_pattern "V012012012012" the very last bit of the bitmask is at position MaxH=12 
    
    #I want to read data from first slice Z=0
    slice_box=box.getZSlab(0,1);
    
    #create and read data from VisusFIle up to resolution FinalH=8 (<MaxH)
    query=QueryPtr(Query(dataset.get(),ord('r')))
    query.get().position=Position(slice_box)
    query.get().end_resolutions.push_back(8)
    query.get().end_resolutions.push_back(12)
    query.get().merge_mode=Query.InsertSamples
    
    # end_resolution=8
    
    self.assertTrue(dataset.get().beginQuery(query))
    self.assertTrue(query.get().nsamples.innerProduct()>0)
    self.assertTrue(dataset.get().executeQuery(access,query))
    self.assertEqual(query.get().cur_resolution,8)
    
    # end_resolution=12
    self.assertTrue(dataset.get().nextQuery(query))
    self.assertEqual(query.get().nsamples.innerProduct(),16*16)
    self.assertTrue(dataset.get().executeQuery(access,query))
    self.assertEqual(query.get().cur_resolution,12)
    
    #verify the data is correct
    check=convertToNumPyArray(query.get().buffer)
    sampleid=0
    for Y in range(0,16):
      for X in range(0,16):
        self.assertEqual(check[Y,X],sampleid)
        sampleid+=1 
        
    # finished
    
    self.assertFalse(dataset.get().nextQuery(query)) 


# ////////////////////////////////////////////////////////
if __name__ == '__main__':
  SetCommandLine()
  IdxModule.attach()
  unittest.main()
  IdxModule.detach()


