import visuspy
import numpy
import cdms2

import pdb
class Visus:
    def __init__(self, visus, field, i):
        self.visus=visus
        self.field=field
        self.box=visus.get().getBox()
        self.access=visus.get().createAccess()
        self.timeMin = int(visus.get().getTimesteps().getMin())
        self.timeMax = int(visus.get().getTimesteps().getMax())
        self.timeArray =  visus.get().getTimesteps().asVector()
        #timeAxis = cdms2.createAxis(range(timeMin,timeMax))
        self.timeAxis = cdms2.createAxis([689])
        self.timeAxis.designateTime()

        self.MaxH=visus.get().getBitmask().getMaxResolution()
        self.index =i
        self._data = None

        #    self.assertTrue(dataset.get().beginQuery(query))
        #    self.assertTrue(query.get().nsamples.innerProduct()>0)
        #    self.assertTrue(dataset.get().executeQuery(access,query))


    def __getitem__(self, slice):

        pdb.set_trace()
        if( self._data is None):
            self.slice_box=self.box.getZSlab(0,1)
            self.query=visuspy.QueryPtr(visuspy.Query(self.visus.get(),ord('r')))
            self.query.get().position=visuspy.Position(self.slice_box)
            self.query.get().field=self.visus.get().getFields()[self.index]
            self.query.get().end_resolutions.push_back(self.MaxH-5)
            self.query.get().merge_mode=visuspy.Query.InsertSamples
            self.query.get().time=689
            time = self.visus.get().getTimesteps().getAt(689)
            self.visus.get().beginQuery(self.query)
            self.visus.get().executeQuery(self.access,self.query)
            check=visuspy.convertToNumPyArray(self.query.get().buffer)
            self._data = cdms2.MV2.TransientVariable(check[:])
            self._data.id=self.visus.get().getFields()[self.index].getDescription()
        return self._data
#        (nlat,nlon) = self._data.shape
#        grid= cdms2.createUniformGrid(-90, nlat, 180./(nlat-1), -180, nlon, 360./(nlon-1), order="yx", mask=None)
#        self._data.setGrid(grid)
#        self._data.setAxis(0,self._data.getGrid().getAxis(0))
#        self._data.setAxis(1,self._data.getGrid().getAxis(1))

    def __repr__(self):
        return cdms2.tvariable.TransientVariable.__repr__(self._data)

    def _getShape(self):
        if( not hasattr(self, '_data')):
            dummy = self[0]
        return self._data.shape

    shape = property(_getShape, None)



