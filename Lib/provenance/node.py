import weakref
import logging


class Node(object):
    def __init__(self, backend):
        self.__cache__ = None
        self.backend = backend

    def __getstate__(self):
        d = {}
        for k, v in self.__dict__.items():
            if k not in ("__cache__", "backend"):
                d[k] = v
        return d

    def __setstate__(self, d):
        for k, v in d.items():
            setattr(self, k, v)
        self.__cache__ = None
        import numpy_backend
        self.backend = numpy_backend

    def get_value(self):
        """
        Retrieves the cached version of the value, or calculates it if no cache is available.

        Uses a weakreference to avoid memory pressure, recalculates if necessary.
        """
        if self.__cache__ is None or self.__cache__() is None:
            try:
                v = self.derive()
            except Exception as e:
                # Dump the provenance representation to a graphviz file so we can debug
                all_nodes = [self]
                node_dots = [self.to_dot_node(0)]
                edges = {}
                ind = 0
                while ind < len(all_nodes):
                    n = all_nodes[ind]
                    if hasattr(n, "parents"):
                        ind_edges = []
                        for p in n.parents:
                            p_ind = len(all_nodes)
                            node_dots.append(p.to_dot_node(p_ind))
                            all_nodes.append(p)
                            ind_edges.append(p_ind)
                        edges[ind] = ind_edges
                    ind += 1
                dotgraph = """
digraph {{
    {nodes}
    {edges}
}}"""
                edge_strings = []
                edge_str = "{r_node} -> {p_node}"
                for n in edges:
                    for p in edges[n]:
                        edge_strings.append(edge_str.format(r_node=node_dots[n], p_node=node_dots[p]))
                dotgraph = dotgraph.format(nodes="\n    ".join(node_dots), edges="\n    ".join(edge_strings))
                import traceback
                traceback.print_stack()
                print e
                raise ValueError("Unable to derive value. Below is graphviz representation of provenance.\n\n%s" % dotgraph)
            try:
                self.__cache__ = weakref.ref(v)
            except TypeError:
                self.__cache__ = lambda: v
        return self.__cache__()

    def to_dot_node(self, index):
        node_type = str(type(self).__name__)
        return "{node_type}_{index} [label=\"{node_type}\"]".format(index=index, node_type=node_type)

    def to_dict(self, node_graph):
        raise NotImplementedError("Please implement to_dict for node type %s" % (type(self)))

    def derive(self):
        raise NotImplementedError("Please implement derive for node type %s" % (type(self)))


class FileNode(Node):
    def __init__(self, uri, backend):
        super(FileNode, self).__init__(backend)
        self._uri = uri

    def derive(self):
        return self.backend.open_file(self._uri)

    def to_dict(self, node_graph):
        return {"type": "file", "uri": self._uri}

    def finalize(self, f):
        self.backend.close_file(f)
        self.__cache__ = None


class RawValueNode(Node):
    def __init__(self, value, backend):
        super(RawValueNode, self).__init__(backend)
        self.value = value

    def derive(self):
        return self.value

    def to_dict(self, node_graph):
        value = self.backend.toJSON(self.value)
        return {"type": "value", "value": value}


class VariableNode(Node):
    def __init__(self, operation, parents, backend):
        super(VariableNode, self).__init__(backend)
        self._oper = operation
        self.parents = parents

    def derive(self):
        parent_values = []
        files = []
        for p in self.parents:
            parent_values.append(p.get_value())
            if isinstance(p, FileNode):
                files.append((p, parent_values[-1]))
        value = self._oper.evaluate(parent_values)
        for node, file in files:
            # Makes sure files get closed properly.
            # This is incredibly wasteful. Should really just open/close once.
            node.finalize(file)
        return value

    def to_dict(self, node_graph):
        parent_indices = []
        for parent in self.parents:
            if parent not in node_graph:
                raise ValueError("Variable %s has parent not in graph." % self)
            parent_indices.append(node_graph.index(parent))

        return {
            "type": "variable",
            "parents": parent_indices,
            "operation": self._oper.to_dict()
        }


class AxisNode(Node):
    def __init__(self, operation, parents, axis_id, backend):
        super(AxisNode, self).__init__(backend)
        if operation.lower() not in ("create", "get"):
            raise ValueError("No such operation '%s' on axes." % operation)
        self._oper = operation.lower()
        self.parents = parents
        self.id = axis_id

    def to_dict(self, node_graph):
        parent_indices = []
        for parent in self.parents:
            if parent not in node_graph:
                raise ValueError("Axis %s has parent not in graph." % self)
            parent_indices.append(node_graph.index(parent))
        axis = self.get_value()

        axis_marked = None
        if axis.isLatitude():
            axis_marked = "latitude"
        elif axis.isLongitude():
            axis_marked = "longitude"
        elif axis.isTime():
            axis_marked = "time"
        elif axis.isLevel():
            axis_marked = "level"

        return {
            "type": "axis",
            "operation": self._oper,
            "id": self.id,
            "parents": parent_indices,
            "axis": axis_marked
        }

    def derive(self):
        parent_values = []
        for p in self.parents:
            parent_values.append(p.get_value())
        return self.backend.deriveAxis(self._oper, self.id, parent_values)


class MetadataNode(Node):
    """
    Update an attribute on an object.
    """

    def __init__(self, attribute, value, parent, backend):
        super(MetadataNode, self).__init__(backend)
        self.attr = attribute
        self.value = value
        self.parents = [parent]

    def to_dict(self, node_graph):
        parent_indices = []
        for parent in self.parents:
            if parent not in node_graph:
                raise ValueError("MetadataNode has parent not in graph.")
            parent_indices.append(node_graph.index(parent))

        return {
            "type": "metadata",
            "parents": parent_indices,
            "value": self.value,
            "attribute": self.attr
        }

    def derive(self):
        parent_value = self.parents[0].get_value()
        setattr(parent_value, self.attr, self.value)
        return parent_value


class OperationNode(object):
    def __init__(self, spec):
        for k in self.required_arguments:
            if k not in spec:
                raise ValueError("Missing required argument: %s" % k)
            if not isinstance(spec[k], self.required_arguments[k]):
                raise TypeError("Argument '%s' should be of type %s." % (k, self.required_arguments[k]))
        self._arguments = spec

    def to_dict(self):
        base = {
            "type": self.type_key
        }

        for arg in self._arguments:
            base[arg] = self._arguments[arg]

        return base

    def evaluate(self, values):
        raise NotImplementedError("Please implement evaluate for operation type: %s" % (type(self)))


class GetVariableOperation(OperationNode):
    """
    Implements the retrieval of a variable from a file.

    Expects just an "id" argument, and the parent should be a file object (as defined by the backend, not a node).
    """
    type_key = "get"
    required_arguments = {"id": (str, unicode)}


class SubsetVariableOperation(OperationNode):
    """
    Reduces one or more axes of a variable.

    Expects a dictionary of axes and the selectors to use to reduce those axes (axes specified by ID)
    """
    type_key = "subset"
    required_arguments = {"axes": dict}


class TransformOperation(OperationNode):
    """
    Calls the appropriate function on a variable.
    """
    type_key = "transform"
    required_arguments = {"function": (str, unicode)}
    argument_specs = {
        "remainder": ([0, 1], {}),
        "hypot": ([0, 1], {}),
        "arctan2": ([0, 1], {}),
        "outerproduct": ([0, 1], {}),
        "log": ([0], {}),
        "log10": ([0], {}),
        "conjugate": ([0], {}),
        "sin": ([0], {}),
        "cos": ([0], {}),
        "tan": ([0], {}),
        "arcsin": ([0], {}),
        "arccos": ([0], {}),
        "arctan": ([0], {}),
        "sinh": ([0], {}),
        "cosh": ([0], {}),
        "tanh": ([0], {}),
        "fabs": ([0], {}),
        "nonzero": ([0], {}),
        "around": ([0], {}),
        "floor": ([0], {}),
        "ceil": ([0], {}),
        "sqrt": ([0], {}),
        "absolute": ([0], {}),
        "sometrue": ([0], {"axis": None}),
        "alltrue": ([0], {"axis": None}),
        "max": ([0], {"axis": None}),
        "min": ([0], {"axis": None}),
        "sort": ([0], {"axis": None}),
        "count": ([0], {"axis": None}),
        "product": ([0], {"axis": None, "dtype": None}),
        "sum": ([0], {"axis": None, "fill_value": 0, "dtype": None}),
        "average": ([0], {"axis": None, "returned": False, "weights": None}),
        "choose": (["indices", 0], {}),
        "take": ([0, "indices"], {"axis": None}),
        "transpose": ([0], {"axis": None}),
        "argsort": ([0], {"axis": -1, "fill_value": None}),
        "repeat": ([0, "count"], {"axis": None}),
        "reshape": ([0, "shape"], {"axis": None, "attributes": None, "id": None, "grid": None}),
        "resize": ([0, "shape"], {"axis": None, "attributes": None, "id": None, "grid": None}),
        "diagonal": ([0], {"axis1": 0, "axis2": 1, "offset": 0}),
        "add": ([0, 1], {}),
        "subtract": ([0, 1], {}),
        "multiply": ([0, 1], {}),
        "divide": ([0, 1], {}),
        "equal": ([0, 1], {}),
        "less_equal": ([0, 1], {}),
        "greater_equal": ([0, 1], {}),
        "less": ([0, 1], {}),
        "greater": ([0, 1], {}),
        "not_equal": ([0, 1], {}),
        "and": ([0, 1], {}),
        "or": ([0, 1], {}),
        "xor": ([0, 1], {}),
        "pow": ([0, 1], {}),
        "neg": ([0], {}),
        "not": ([0], {}),
    }

    def evaluate(self, values):
        func = self._arguments["function"]
        if func not in self.argument_specs:
            raise ValueError("Unknown transform %s." % func)

        args, kwargs = self.argument_specs[func]
        sub_args, sub_kwargs = [], {}
        for a in args:
            if isinstance(a, int):
                sub_args.append(values[a])
            if isinstance(a, (str, unicode)):
                sub_args.append(self._arguments[a])
        for kw, default in kwargs.iteritems():
            val = self._arguments.get(kw, default)
            # grid and weights are special ones that can use
            # parent values, so check if they're ints.
            if kw in ("grid", "weights") and isinstance(val, int):
                val = values[val]
            sub_kwargs[kw] = val
        return self.execute_transform(func, sub_args, sub_kwargs)


def create_operation(oper_spec, backend):
    oper_dict = {}
    # Gather all of the implemented types
    for clz in OperationNode.__subclasses__():
        oper_dict[clz.type_key] = clz

    oper_class = oper_dict.get(oper_spec["type"].lower(), None)

    if oper_class is None:
        raise ValueError("No operation of type '%s' defined." % oper_spec["type"])

    for sc in oper_class.__subclasses__():
        if sc.__module__ == backend.__name__:
            return sc(oper_spec)

    raise NotImplementedError("No implementation of operation type %s found in module %s." % (oper_spec["type"], backend.__name__))
