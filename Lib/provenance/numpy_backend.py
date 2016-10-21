import cdms2
from .node import GetVariableOperation, SubsetVariableOperation, TransformOperation, VariableNode, FileNode
import operator
import cdutil
import numpy


def open_file(uri):
    return cdms2.open(uri)


def close_file(f):
    f.close()


def toJSON(value):
    if isinstance(value, numpy.ndarray):
        return value.tolist()
    else:
        return value


def deriveAxis(operation, axis_id, parents):
    if operation == "get":
        if len(parents) != 1:
            raise ValueError("Cannot get axis '%s' without a parent to retrieve it from." % axis_id)
        if isinstance(parents[0], cdms2.dataset.CdmsFile):
            return parents[0].getAxis(axis_id)
        elif isinstance(parents[0], cdms2.avariable.AbstractVariable):
            return parents[0].getAxis(parents[0].getAxisIndex(axis_id))
        else:
            raise ValueError("Cannot get axis '%s' from parent of type '%s'" % (axis_id, type(parents[0])))

    if operation == "create":
        data = numpy.array(parents[0])
        if len(parents) > 1:
            bounds = numpy.array(parents[1])
        else:
            bounds = None
        return cdms2.createAxis(data, bounds=bounds, id=axis_id)


class NumpyGetVariableOperation(GetVariableOperation):
    """
    Implements the retrieval of a variable from a file.

    Expects just an "id" argument, and the parent should be a file object (as defined by the backend, not a node).
    """
    def evaluate(self, values):
        # At some point we should include support for numpy.zeroes/numpy.ones
        var_id = self._arguments["id"]
        return values[0](var_id)


class NumpySubsetVariableOperation(SubsetVariableOperation):
    """
    Reduces one or more axes of a variable.

    Expects a dictionary of axes and the selectors to use to reduce those axes (axes specified by ID)
    """
    def evaluate(self, values):
        variable = values[0]
        axes = self._arguments["axes"]

        # Validate that the axes exist
        var_axis_ids = variable.getAxisIds()
        for ax in axes:
            if ax not in var_axis_ids:
                raise ValueError("No axis '%s' found." % (ax))

        kwargs = axes.copy()
        kwargs["squeeze"] = self._arguments.get("squeeze", False)
        kwargs["order"] = self._arguments.get('order', None)
        kwargs["grid"] = self._arguments.get('grid', None)

        return variable(**kwargs)


class NumpyTransformVariableOperation(TransformOperation):
    """
    Calls the appropriate function on a variable.
    """
    func_map = {
        "remainder": cdms2.MV2.remainder,
        "hypot": cdms2.MV2.hypot,
        "arctan2": cdms2.MV2.arctan2,
        "outerproduct": cdms2.MV2.outerproduct,
        "log": cdms2.MV2.log,
        "log10": cdms2.MV2.log10,
        "conjugate": cdms2.MV2.conjugate,
        "sin": cdms2.MV2.sin,
        "cos": cdms2.MV2.cos,
        "tan": cdms2.MV2.tan,
        "arcsin": cdms2.MV2.arcsin,
        "arccos": cdms2.MV2.arccos,
        "arctan": cdms2.MV2.arctan,
        "sinh": cdms2.MV2.sinh,
        "cosh": cdms2.MV2.cosh,
        "tanh": cdms2.MV2.tanh,
        "fabs": cdms2.MV2.fabs,
        "nonzero": cdms2.MV2.nonzero,
        "around": cdms2.MV2.around,
        "floor": cdms2.MV2.floor,
        "ceil": cdms2.MV2.ceil,
        "sqrt": cdms2.MV2.sqrt,
        "absolute": cdms2.MV2.absolute,
        "sometrue": cdms2.MV2.sometrue,
        "alltrue": cdms2.MV2.alltrue,
        "max": cdms2.MV2.max,
        "min": cdms2.MV2.min,
        "sort": cdms2.MV2.sort,
        "count": cdms2.MV2.count,
        "product": cdms2.MV2.product,
        "sum": cdms2.MV2.sum,
        "average": cdms2.MV2.average,
        "choose": cdms2.MV2.choose,
        "take": cdms2.MV2.take,
        "transpose": cdms2.MV2.transpose,
        "argsort": cdms2.MV2.argsort,
        "repeat": cdms2.MV2.repeat,
        "reshape": cdms2.MV2.reshape,
        "resize": cdms2.MV2.resize,
        "diagonal": cdms2.MV2.diagonal,
        "add": cdms2.MV2.add,
        "subtract": cdms2.MV2.subtract,
        "multiply": cdms2.MV2.multiply,
        "divide": cdms2.MV2.divide,
        "equal": cdms2.MV2.equal,
        "less_equal": cdms2.MV2.less_equal,
        "greater_equal": cdms2.MV2.greater_equal,
        "less": cdms2.MV2.less,
        "greater": cdms2.MV2.greater,
        "not_equal": cdms2.MV2.not_equal,
        "not": cdms2.MV2.logical_not,
        "and": cdms2.MV2.bitwise_and,
        "or": cdms2.MV2.bitwise_or,
        "xor": cdms2.MV2.bitwise_xor,
        "pow": cdms2.MV2.power,
        "neg": cdms2.MV2.negative,
    }

    def execute_transform(self, func_name, args, kwargs):
        return self.func_map[func_name](*args, **kwargs)
