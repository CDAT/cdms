from distributed.protocol import register_serialization
from cdms2.fvariable import FileVariable
from cdms2.tvariable import TransientVariable, createVariable
import zlib
import cdms2


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
    f = cdms2.open(header['filename'], mode='r')[header['id']]
    return(f)


register_serialization(TransientVariable, serialize_TV, deserialize_TV)
register_serialization(FileVariable, serialize_FV, deserialize_FV)
