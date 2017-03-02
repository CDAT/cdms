"""Interface to regridding facilities
"""

__all__ = ["horizontal", "pressure", "crossSection", "scrip", 
           "error", "mvGenericRegrid",]

from error import RegridError
from horizontal import Horizontal, Regridder
from pressure import PressureRegridder
from crossSection import CrossSectionRegridder
from scrip import ConservativeRegridder, BilinearRegridder, BicubicRegridder 
from scrip import DistwgtRegridder, readRegridder
from regrid2 import gsRegrid
from mvGenericRegrid import GenericRegrid
from mvLibCFRegrid import LibCFRegrid
try:
    import ESMF
    from mvESMFRegrid import ESMFRegrid
except:
    pass

from . import git

ESMP_HAS_BEEN_INITIALIZED = False
if not ESMP_HAS_BEEN_INITIALIZED:
    try:
        import ESMF
        ESMF.Manager(debug=False)
        # this turns off the PET file logs
        ESMP_HAS_BEEN_INITIALIZED = True
    except:
        pass
