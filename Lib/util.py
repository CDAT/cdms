import os

from .error import CDMSError

def base_doc(base):
    def wrapper(fn):
        doc = getattr(base, fn.__name__).__doc__
        fn.__doc__ = doc
        return fn
    return wrapper

valid_bool_str = ["true", "false"]

def getenv_bool(name, default=None):
    value = os.environ.get(name, default)

    if value is None:
        raise CDMSError("{!r} was not set".format(name))

    if value.lower() not in valid_bool_str:
        raise CDMSError(
            "{!r} is not a valid value for {!r}, allowed values: {!r}".format(
                value, name, valid_bool_str))

    return True if value.lower() == "true" else False
