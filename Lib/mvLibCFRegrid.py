"""
LibCF regridding class

This code is provided with the hope that it will be useful. 
No guarantee is provided whatsoever. Use at your own risk.

David Kindig and Alex Pletzer, Tech-X Corp. (2012)
"""

from regrid2 import gsRegrid
from regrid2 import GenericRegrid
class LibCFRegrid(GenericRegrid):
    """
    """
    def __init__(self, srcGrid, dstGrid, srcGridMask = None, 
                 srcBounds = None, **args):
        """
        Constructor
        @param srcGrid array
        @param dstGrid array
        @param srcBounds cell boundaries
        @param **args keyword arguments, eg mkCyclic, handleCut, ...
                      to be passed to gsRegrid
        """
        self.regridMethodStr = 'linear'
        self.mkCyclic = args.get('mkCyclic', False)
        self.handleCut = args.get('handleCut', False)
        self.regridObj = gsRegrid.Regrid(srcGrid, dstGrid, 
                                         src_bounds = srcBounds,
                                         mkCyclic = self.mkCyclic,
                                         handleCut = self.handleCut)
        if srcGridMask is not None: 
            self.regridObj.setMask(srcGridMask)

    def computeWeights(self, **args):
        """
        Compute interpolation weights
        @param **args arguments to be passed to gsRegrid, e.g. 
                      nitermax, tolpos, ...
        """
        nitermax = args.get('nitermax', 20)
        tolpos = args.get('tolpos', 0.01)
        self.regridObj.computeWeights(nitermax=nitermax, tolpos=tolpos)

    def apply(self, srcData, dstData, missingValue = None, **args):
        """
        Regrid source to destination
        @param srcData array (input)
        @param dstData array (output)
        @param missingValue value that should be set for points falling outside the src domain, 
                            pass None if these should not be touched.        
        """
        self.regridObj.apply(srcData, dstData, missingValue)

    def getDstGrid(self):
        """
        Get the grid of the dst data (maybe larger than the 
        dst grid passed to the constructor due to column/row
        padding)
        @return shape
        """
        return self.regridObj.getDstGrid()
        
    def fillInDiagnosticData(self, diag, rootPe):
        """
        Fill in diagnostic data
        @param diag a dictionary whose entries, if present, will be filled
                    valid entries are: 'numDstPoints' and 'numValid'
        @param rootPe not used
        """
        for entry in 'numDstPoints', 'numValid':
                if diag.has_key(entry):
                        meth = 'get' + entry[0].upper() + entry[1:]
                        diag[entry] = eval('self.regridObj.' + meth + '()')
        diag['regridTool'] = 'libcf'
        diag['regridMethod'] = self.regridMethodStr
        diag['handleCut'] = self.handleCut
        diag['mkCyclic'] = self.mkCyclic
