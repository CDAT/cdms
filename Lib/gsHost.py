#/usr/bin/env python

"""
A file-like object to access a host file. Thereby granting entry to an entire
data set.
Dave Kindig and Alex Pletzer, Tech-X (2011)
This code is provided with the hope that it will be useful. 
No guarantee is provided whatsoever. Use at your own risk.
"""

import os.path
from ctypes import c_char_p, c_int, CDLL, byref
import cdms2
from cdms2.avariable import AbstractVariable
from cdms2.tvariable import TransientVariable
from cdms2.cdmsobj import CdmsObj
from cdms2.gsStaticVariable import StaticVariable
from cdms2.gsTimeVariable import TimeVariable

# IF pycf is being loaded in dataset.py, we don't need to check here.
from pycf import libCFConfig, __path__
LIBCF = __path__[0] + '/libcf'

def open(hostfile, mode = 'r'):
    """
    Open host file
    @param hostfile host file
    @param mode valid cdms2 open file mode
    """

    outHostFile = Host(hostfile, mode)
    return outHostFile

class Host:
    """
    A LibCF/GRIDSPEC host file object. This acts as the single point of entry to
    a host file. Variables and grids can be requested solely through the Host
    object. The host object is a hybrid between a variable and file object. 
    Host relies on the libcf shared object. As such, if there is a problem
    consult http://www.unidata.ucar.edu/software/libcf/docs/libcf/ for details
    on building host files and all related GRIDSPEC files.

    @return Host class on __init__
    """

    def __init__(self, hostfile, mode = 'r'):
        """
        Constructor
        @param hostfile path to the host
        @param mode read only at the moment
        """
        
        # Data dir based on location of hostfile
        self.libcfdll = None
        self.dirname  = os.path.dirname(hostfile)
        self.uri      = hostfile
        self.id       = os.path.dirname(hostfile)
        self.mode     = mode
        self._status_ = 'open'

        for sosuffix in '.so', '.dylib', '.dll', '.a':
            self.libcfdll = CDLL(LIBCF + sosuffix)
            if self.libcfdll:
                break
        if self.libcfdll == None: 
            print 'libcf not installed or incorrect path\n  ', self.libcfdll
            self._status_ = 'closed'

        elif self._status_ == 'open':

            libcfdll = self.libcfdll

            self.hostId_t = c_int(-1)
            self.globalId_t = c_int(-1)

            # number of grid files
            self.ngrids = 0
            
            # number of static var files 
            self.nstatFiles = 0

            # number of time dependent var files 
            self.ntimeFiles = 0

            # number of time files
            self.ntimeSlices = 0

            self.mosaicFilename = ""

            # Filenames
            self.timeFilenames = []
            self.statFilenames = []
            self.gridFilenames = []
            self.gridNames     = []

            self.hostFileVars = [ "timeFilenames", 
                                  "statFilenames", 
                                  "gridFilenames", 
                                  "gridNames    " ]
            
            # {'varName': fileNames}
            # fileNames is array of ngrid
            self.gridVars = {}

            # {'varName': fileNames}
            # fileNames is array of ntimes x ngrid
            self.timeDepVars = {}

            # {'varName': fileNames}
            # fileNames is array of ngrid
            self.statVars = {}

            # {coordName: gridFiles}
            self.coords = {}

            # flags checking whethed host was constructed
            self.hostFileOpened = False

            # host file name
            self.hostFilename = ""

            status = libcfdll.nccf_def_host_from_file(hostfile,
                                                   byref(self.hostId_t))
            if status != 0:
                print "ERROR: File %s doesn't exist or is not a valid host file" % \
                    hostfile
                print "error code: ", status
                return

            # Attach global attrs
            libcfdll.nccf_def_global_from_file( hostfile, byref(self.globalId_t))

            self.hostFileOpened = True
            self.hostFilename = hostfile

            i_t = c_int()
            status = libcfdll.nccf_inq_host_ngrids(self.hostId_t, byref(i_t))
            self.ngrids = i_t.value
            status = libcfdll.nccf_inq_host_nstaticdata(self.hostId_t, byref(i_t))
            self.nstatFiles = i_t.value
            status = libcfdll.nccf_inq_host_ntimedata(self.hostId_t, byref(i_t))
            self.ntimeFiles = i_t.value
            status = libcfdll.nccf_inq_host_ntimes(self.hostId_t, byref(i_t))
            self.ntimeSlices = i_t.value

            varName_t = c_char_p(" " * (libCFConfig.NC_MAX_NAME+1))
            fName_t = c_char_p(" " * (libCFConfig.NC_MAX_NAME+1))

            # Grid names and data
            for gfindx in range(self.ngrids):
                status = libcfdll.nccf_inq_host_gridfilename(self.hostId_t, 
                                                          gfindx, 
                                                          fName_t)
                self.gridFilenames.append(fName_t.value)

                f = cdms2.open(fName_t.value, 'r')
                varNames = f.listvariable()
                for vn in varNames:
                    if not self.gridVars.has_key(vn):
                        # allocate
                        self.gridVars[vn] = ["" for ig in range(self.ngrids)] 

                    # set file name
                    self.gridVars[vn][gfindx] = fName_t.value

                # Get the grid names
                status = libcfdll.nccf_inq_host_grid_name(self.hostId_t, 
                                                          gfindx, 
                                                          fName_t)
                self.gridNames.append(fName_t.value)

            # static data
            for vfindx in range(self.nstatFiles):
                for gfindx in range(self.ngrids):
                    status = libcfdll.nccf_inq_host_statfilename(self.hostId_t, 
                                                              vfindx, gfindx, 
                                                              fName_t)
                    self.statFilenames.append(fName_t.value)
                    varNames = cdms2.open(fName_t.value, 'r').listvariable()
                    for vn in varNames:
                        if not self.statVars.has_key(vn):
                            # allocate
                            self.statVars[vn] = ["" for ig in range(self.ngrids)] 

                        # set file name
                        self.statVars[vn][gfindx] = fName_t.value

            # time dependent data
            for vfindx in range(self.ntimeFiles):
                for tfindx in range(self.ntimeSlices):
                    for gfindx in range(self.ngrids):
                        status = libcfdll.nccf_inq_host_timefilename(self.hostId_t, 
                                                                  vfindx, tfindx, gfindx, 
                                                                  fName_t)
                        self.timeFilenames.append(fName_t.value)
                        varNames = cdms2.open(fName_t.value, 'r').listvariable()
                        for vn in varNames:
                            if not self.timeDepVars.has_key(vn):
                                # allocate
                                self.timeDepVars[vn] = [["" for ig in range(self.ngrids)] \
                                                            for it in range(self.ntimeSlices)]
                            # set file name
                            self.timeDepVars[vn][tfindx][gfindx] = fName_t.value
                      
          ## now close the host file NOT HERE. USE __del__
          #status = libcfdll.nccf_free_host(self.hostId_t)
    
    def listhostfilevars(self):
        """
        Return the variables contained in the host file. These are referenced
        to create grids or variables and are attributes in the host object
        @return list of variable names
        """
        return self.hostFileVars

    def getMosaic(self):
        """
        Get the mosaic filename
        @return mfn Mosaic filename
        """
        from gsMosaic import Mosaic
        mosaicFilename = c_char_p(" " * (libCFConfig.NC_MAX_NAME + 1))
        status = self.libcfdll.nccf_inq_host_mosaicfilename(self.hostId_t, mosaicFilename)
        mfn = Mosaic(mosaicFilename, "r")

        return mfn

    def writeMosaic(self):
        raise CDMSError, "Method Not Implemented"

    def getCoordinates(self, gindx):
        """
        Given a grid Index return the coordinates of that grid
        @param gindx Grid index
        @return coordinates list of coordinates
        """
        gridFile = cdms2.open(self.gridFilenames[gindx])
        c = []
        for i in range(len(self.coordinates)):
          c.append(gridFile(self.coordinates[i]))

        return c
    
    def getLatitude(self, gindx):
        """
        Given a grid Index return the coordinates of that grid
        @param gindx Grid index
        @return coordinates list of coordinates
        """
        gridFile = cdms2.open(self.gridFilenames[gindx])
        for i in range(len(self.coordinates)):
          crd = gridFile(self.coordinates[i])
          if crd.hasattr(UNITS):
            from re import search
            # Look for some form of degrees_north
            if search('degree', crd.units) and search('[nN]', crd.units):
                gridFile.close()
                return crd

    def getLongitude(self, gindx):
        """
        Given a grid Index return the coordinates of that grid
        @param gindx Grid index
        @return coordinates list of coordinates
        """
        gridFile = cdms2.open(self.gridFilenames[gindx])
        for i in range(len(self.coordinates)):
          crd = gridFile(self.coordinates[i])
          if crd.hasattr(UNITS):
            from re import search
            # Look for some form of degrees_east
            if search('degree', crd.units) and search('[eE]', crd.units):
                return crd

    def getNumGrids(self):
        """
        Get number of grids (tiles)
        @return number of grids
        """
        return len(self.gridFilenames)

    def getNumStatDataFiles(self):
        """
        Get number of static data files 
        @return number static files
        """
        return self.nstatFiles

    def getNumTimeDataFiles(self):
        """
        Get number of time dependent data files
        @return number time data files
        """
        return self.ntimeFiles

    def listvariable(self):
        """
        @return list of all variables, including static and time dependent
        """
        return self.statVars.keys() + self.timeDepVars.keys()

    def listvariables(self):
        """
        Synonymous to listvariable
        @return list of all variables, including static and time dependent
        """
        return self.listvariable()

    def listattribute(self, varName):
        """
        List the given variables attributes
        @param varName variable name
        @return attributes list
        """
        print 'Host.listatt'
        fName = ""
        if self.statVars.has_key(varName):
            fName = self.statVars[varName][0]
        elif self.timeDepVars.has_key(varName):
            fName = self.timeDepVars[varName][0][0]
        if fName:
            var = cdms2.open(fName, 'r')(varName)
            return var.listattributes()
        else:
            return []

    def listattributes(self, varName):
        """
        Synonymous to listattribute
        @param varName variable name
        @return attributes list
        """
        return self.listattribute(varName)

    def listdimension(self, varName):
        """
        List a variable's dimensions
        @param varName variable name
        @return [nGrids, (n0, n1, ...)]
        """
        pass
        
    def listglobal(self, attName = ""):
        """
        List global attributes of host file
        @param [attName] - Optional attribute to get a value
        @return list 
        """ 

        natts = c_int(-1)
        self.global_atts = {}
        attName_t = c_char_p(" " * (libCFConfig.NC_MAX_NAME+1))
        attValu_t = c_char_p(" " * (libCFConfig.NC_MAX_NAME+1))
        self.libcfdll.nccf_inq_global_natts( self.globalId_t, byref(natts))
        for i in range(natts.value):
            self.libcfdll.nccf_inq_global_attval(self.globalId_t, i, attName_t, attValu_t)
            if not self.global_atts.has_key( attName_t.value ):
                self.global_atts[attName_t.value] = attValu_t.value
        
        if attName == "":
            return self.global_atts.keys()
        elif self.global_atts.has_key(attName):
            return (attName, self.global_atts[attName])

    def showglobal(self, attName = ""):
        """
        synonymous to listglobal
        @param [attName] - Optional attribute to get a value
        @return list 
        """
        return self.listglobal()

    def addglobal(self, name, value):
        """
        Add a global attribute to a file
        @param name attribute name
        @param value attribute value
        @return status 0 if valid
        """
        status = self.libcfdll.nccf_add_global_att( self.globalId_t, name, value)
        return status

    def addfiletohost(self, filename):
        """
        Using libcf, add a file name to the host file
        @param filename file to be added
        @return status 0 if valid return
        """
        status = self.libcfdll.nccf_add_host_file(self.hostId_t, filename)
        return status

    def __repr__(self): 
        """
        Python repr()
        @return res Print statement
        """
        res = "< '%s',  URI: '%s', MODE: '%s', STATUS: '%s',\n libcf: %s >" % \
            ( self.__class__, self.uri, self.mode, self._status_, self.libcfdll)
        return res 

    def __del__(self):
        """
        Free the host file from memory
        """
        self.libcfdll.nccf_free_host( self.hostId_t )

#    def __getitem__(self, varName, **speclist):
    def __getitem__(self, varName):
        """
        self(variableName) 
        The returned variable is a var[nGrids][[nTimes, nz], ny,  nx]
        Note that for nTimes, the time across files are concatenated together
        @param varName name of variable
        @return aggregated transient variable
        """
        # Static variables
        if self.statVars.has_key(varName):
            staticVariables = StaticVariable(self, varName, **speclist)
#            staticVariables = StaticVariable(self, varName)

            return staticVariables.vars 

        # Time variables
        elif self.timeDepVars.has_key(varName):
            timeVariables = TimeVariable(self, varName)
#            timeVariables = TimeVariable(self, varName, **speclist)
            
            return timeVariables.vars
    
#    def __call__(self, varName):
        """
        Equivalent to self[varName] -- Return a list of file variables
        including the grid for each.
        @varName variable name
        @return File variable

        NOTE:
        Currently returns a transient variable. File variable needs still to
        be implemented
        """
        return self.__getitem__(varName, **speclist)

##############################################################################

def test():
    import sys
    """
    A path to the host file must be present. This also assumes that
    the data are in the same directory as the host file.
    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="hostFilename",
                  help="host file name")

    options, args = parser.parse_args()
    if not options.hostFilename:
        print "need to provide a host file, use -h to get a full list of options"
        sys.exit(1)

    print 'open file..., create grdspec file object...'
    gf = cdms2.open(options.hostFilename)
    if gf._status_ == 'closed': 
        print "File not opened"
        sys.exit(1)
    print 
    print "type=", type(gf)
    print 'listvariable...'
    print gf.listvariable()
    print 'listattributes...'
    print gf.listattribute('distance')
    print gf.listattribute('v')
    print 'listglobals...'
    print gf.listglobal()
    print 'print...'
    print gf
    print 'access static data...', 'distance' in gf.listvariable()
    print type(gf['distance'])
    di = gf['distance']
    print di[0].size
    print gf['distance'][0].shape
    print 'acess time dependent data...', "V" in gf.listvariables()
    print gf['V'][0].size


    # Test the mosaic
    print 'getMosaic...', 'getMosaic' in dir(gf)
    mosaic = gf.getMosaic()
    for c in mosaic.coordinate_names: print c
    for t in mosaic.tile_contacts: print "%s -> %s" % (t, mosaic.tile_contacts[t])

##############################################################################

if __name__ == "__main__": test()
