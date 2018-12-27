import zlib
from . import tvariable
from . import fvariable
from cdms2 import open
import distributed.protocol

register_serialization = distributed.protocol.register_serialization
FileVariable = fvariable.FileVariable
TransientVariable = tvariable.TransientVariable
createVariable = tvariable.createVariable


def serialize_TV(tv):
    state = zlib.compress(tv.dumps().encode("utf-8"))
    return {"TV": state}, []


def deserialize_TV(header, frames):
    TV = header['TV']
    newvar = createVariable(TV, fromJSON=True)
    return newvar


def serialize_FV(fv):
    xx = {'filename': fv.getattribute("filename"), 'id': fv.id}, []
    return(xx)


def deserialize_FV(header, frames):
    f = open(header['filename'], mode='r')[header['id']]
    return(f)


register_serialization(TransientVariable, serialize_TV, deserialize_TV)
register_serialization(FileVariable, serialize_FV, deserialize_FV)
