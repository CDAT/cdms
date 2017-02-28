from compute_graph import ComputeNode, register_computation

DATASET_NODE_TYPE = "dataset"
obj_types = ["variable", "axis", "grid"]


@register_computation(DATASET_NODE_TYPE)
def compute_dataset(attributes):
    import cdms2
    uri = attributes["uri"]
    f = cdms2.open(uri)

    objtype = attributes["objtype"]
    val = None
    if objtype == "variable":
        if attributes.get("memory", True):
            val = f(attributes["id"])
        else:
            # Use a file variable
            val = f[attributes["id"]]
    if objtype == "grid":
        val = f.getGrid(attributes['id'])
    if objtype == "axis":
        val = f.getAxis(attributes['id'])
    f.close()
    return val


class DatasetFunction(ComputeNode):
    def __init__(self, uri, func, id, **args):
        super(DatasetFunction, self).__init__()
        self.node_type = DATASET_NODE_TYPE
        self.node_params = {
            "uri": "URI for a dataset",
            "objtype": "Type of object to retrieve.",
            "array": "Array to perform objtypetion on"
        }
        if objtype not in obj_types:
            raise ValueError(INVALID_DATASET_FUNC % objtype)
        self.objtype = objtype
        self.array = array
        self.args = args
