def base_doc(base):
    def wrapper(fn):
        doc = getattr(base, fn.__name__).__doc__
        fn.__doc__ = doc
        return fn
    return wrapper
