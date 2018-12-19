import lazy_import
import zlib
# from distributed.protocol import register_serialization
# from cdms2.fvariable import FileVariable
# from cdms2.tvariable import TransientVariable, createVariable

register_serialization = lazy_import.lazy_function("distributed.protocol.register_serialization")
FileVariable = lazy_import.lazy_class("cdms2.fvariable.FileVariable")
TransientVariable = lazy_import.lazy_function("cdms2.tvariable.TransientVariable")
createVariable = lazy_import.lazy_function("cdms2.tvariable.createVariable")

# from cdms2 import open
open = lazy_import.lazy_function("cdms2.open")


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
