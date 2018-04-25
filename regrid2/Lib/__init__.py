"""Interface to regridding facilities
"""

__all__ = ["horizontal", "pressure", "crossSection", "scrip",
           "error", "mvGenericRegrid", ]

from .error import RegridError  # noqa
from .horizontal import Horizontal, Regridder  # noqa
from .pressure import PressureRegridder  # noqa
from .crossSection import CrossSectionRegridder  # noqa
from .scrip import ConservativeRegridder, BilinearRegridder, BicubicRegridder  # noqa
from .scrip import DistwgtRegridder, readRegridder  # noqa
from regrid2 import gsRegrid  # noqa
from .mvGenericRegrid import GenericRegrid  # noqa
from .mvLibCFRegrid import LibCFRegrid  # noqa
try:
    import ESMF
    ESMF.deprecated.__globals__[
        'warnings'].warn_explicit = ESMF.deprecated.__globals__['warnings'].formatwarning
    from .mvESMFRegrid import ESMFRegrid  # noqa
except BaseException:
    pass

ESMF_HAS_BEEN_INITIALIZED = False
if not ESMF_HAS_BEEN_INITIALIZED:
    try:
        import ESMF
        ESMF.deprecated.__globals__[
            'warnings'].warn_explicit = ESMF.deprecated.__globals__['warnings'].formatwarning
        ESMF.Manager(debug=False)
        # this turns off the PET file logs
        ESMF_HAS_BEEN_INITIALIZED = True
    except BaseException:
        pass
