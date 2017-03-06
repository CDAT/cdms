from compute_graph import ComputeNode, register_computation

UNARY_NODE_TYPE = "unary_ndarray"
BINARY_NODE_TYPE = "binary_ndarray"
AXIS_NODE_TYPE = "axis_ndarray"
SUBSET_NODE_TYPE = "subset_ndarray"

# Error messages
INVALID_AXIS_OPERATION = "Expected axis/reduce/accumulate operation, got '%s'."
INVALID_AXIS_MODE = "Expected mode of reduce or accumulate; got '%s'."
INVALID_REDUCE_FUNC = "Function %s is not reducable."
INVALID_ACCUM_FUNC = "Function %s is not accumlatable."
INVALID_UNARY_FUNC = "Expected unary function; received '%s'."
INVALID_BINARY_FUNC = "Expected binary function; received '%s'."
INCOMPATIBLE_ARRAYS = "Arrays not same shape; first is %s and second is %s."

binary_funcs = ["remainder", "hypot", "arctan2", "outerproduct", "fmod", "logical_and", "logical_or", "logical_xor", "bitwise_and", "bitwise_or", "bitwise_xor", "not_equal", "add", "multiply", "subtract", "equal", "less", "less_equal", "greater", "greater_equal", "divide", "power"]


@register_computation(BINARY_NODE_TYPE)
def binary_compute(attributes):
    import cdms2.MV2 as MV2

    func = attributes["func"]
    first = attributes["first"]
    second = attributes["second"]
    outer = attributes.get("outer", False)

    if func not in binary_funcs:
        raise ValueError(INVALID_BINARY_FUNC % func)

    compute_algo = getattr(MV2, func.lower())

    if outer:
        return compute_algo.outer(first, second)
    else:
        return compute_algo(first, second)

unary_funcs = ["log", "log10", "conjugate", "sin", "cos", "tan", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh", "fabs", "nonzero", "around", "floor", "ceil", "sqrt", "absolute", "diagonal", "reshape", "resize"]


@register_computation(UNARY_NODE_TYPE)
def unary_compute(attributes):
    import cdms2.MV2 as MV2

    d = dict(attributes)
    func = attributes["func"]
    arg = attributes["arg"]

    if func not in unary_funcs:
        raise ValueError(INVALID_UNARY_FUNC % func)

    for a in ("func", "arg"):
        del d[a]

    compute_algo = getattr(MV2, func.lower())
    return compute_algo(arg, **d)

axis_ops = ["any", "all", "max", "min", "sort", "count", "product", "sum", "average", "choose", "take", "transpose", "argsort", "repeat"]
accum_ops = ["logical_and", "logical_or", "logical_xor", "bitwise_and", "bitwise_or", "bitwise_xor", "not_equal", "add", "multiply", "subtract"]
reduce_ops = ["logical_and", "logical_or", "logical_xor", "bitwise_and", "bitwise_or", "bitwise_xor", "not_equal", "add", "multiply"]


@register_computation(AXIS_NODE_TYPE)
def axis_compute(attributes):
    import cdms2.MV2 as MV2
    d = dict(attributes)
    func = attributes["func"]
    arg = attributes["arg"]
    axis = attributes["axis"]

    if func not in axis_ops and func not in reduce_ops and func not in accum_ops:
        raise ValueError(INVALID_AXIS_OPERATION % func)

    compute_algo = getattr(MV2, func.lower())
    mode = attributes.get("mode", False)

    for a in ("func", "arg", "mode", "axis"):
        if a in d:
            del d[a]

    if mode == "reduce":
        return compute_algo.reduce(arg, axis=axis, **d)
    elif mode == "accumulate":
        return compute_algo.accumulate(arg, axis=axis, **d)
    else:
        return compute_algo(arg, axis=axis, **d)


@register_computation(SUBSET_NODE_TYPE)
def subset_compute(attributes):
    # Differs from geospatial subset by using indices, rather than
    # geospatial values.
    arr = attributes["array"]
    ind1 = attributes["ind1"]
    ind2 = attributes.get("ind2", None)
    if ind2 is None:
        return arr[ind1]
    step = attributes.get("step", None)
    if step is None:
        return arr[ind1:ind2]
    return arr[ind1:ind2:step]


class NDArraySubsetFunction(ComputeNode):
    def __init__(self, array, ind1, ind2=None, step=None):
        # Handles both slicing and getitem
        super(NDArraySubsetFunction, self).__init__()
        self.node_type = SUBSET_NODE_TYPE
        self.node_params = {
            "array": "Array to subset.",
            "ind1": "Index to retrieve, or the start of a slice.",
            "ind2": "End of the slice.",
            "step": "Step value for the slice."
        }

        self.array = array
        self.ind1 = ind1
        self.ind2 = ind2
        self.step = step


class NDArrayBinaryFunction(ComputeNode):
    def __init__(self, func, first, second, outer=False):
        super(NDArrayBinaryFunction, self).__init__()
        self.node_type = BINARY_NODE_TYPE
        self.node_params = {
            "func": "Function used for calculation.",
            "first": "First array to pass in.",
            "second": "Second array to pass in.",
            "outer": "Whether this should be an outer product."
        }
        if func not in binary_funcs:
            raise ValueError(INVALID_BINARY_FUNC % func)
        self.func = func
        self.first = first
        self.second = second
        self.outer = outer


class NDArrayUnaryFunction(ComputeNode):
    def __init__(self, func, arg, **kwargs):
        super(NDArrayUnaryFunction, self).__init__(**kwargs)
        self.node_type = UNARY_NODE_TYPE
        self.node_params = {
            "func": "Function used for calculation.",
            "arg": "Argument to pass in.",
        }
        if func not in unary_funcs:
            raise ValueError(INVALID_UNARY_FUNC % func)
        self.func = func
        self.arg = arg


class NDArrayAxisFunction(ComputeNode):
    def __init__(self, func, arg, axis, mode=None, **kwargs):
        super(NDArrayAxisFunction, self).__init__(**kwargs)
        self.node_type = AXIS_NODE_TYPE
        self.node_params = {
            "func": "Function used for calculation.",
            "arg": "Argument to pass in.",
            "axis": "Which axis/axes to perform function on.",
            "mode": "reduce/accumulate, for certain operations."
        }

        if mode is not None:
            mode = mode.lower()
            if mode == "reduce":
                if func not in reduce_ops:
                    raise ValueError(INVALID_REDUCE_FUNC % func)
            elif mode == "accumulate":
                if func not in accum_ops:
                    raise ValueError(INVALID_ACCUM_FUNC % func)
            else:
                raise ValueError(INVALID_AXIS_MODE % mode)
            self.mode = mode
        else:
            if func not in axis_ops:
                raise ValueError(INVALID_AXIS_OPERATION % func)
        self.func = func
        self.axis = axis
        self.arg = arg
