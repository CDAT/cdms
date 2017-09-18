"""
CDMS Xlink objects - pointers to other objects
"""
<<<<<<< HEAD
from .cdmsobj import CdmsObj
=======
from cdmsobj import CdmsObj
>>>>>>> master


class Xlink(CdmsObj):
    def __init__(self, xlinkNode=None):
        assert xlinkNode is None or xlinkNode.tag == 'xlink',\
            'Node is not a link node'
        CdmsObj.__init__(self, xlinkNode)
