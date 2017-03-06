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
        val = f(attributes["objid"], **attributes.get("args", {}))
    if objtype == "grid":
        val = f.getGrid(attributes['objid'])
        tgrid = val.subGrid(None, None)
        tgrid.attributes = dict(val.attributes)
        tgrid.id = val.id
        val = tgrid
    if objtype == "axis":
        val = f.getAxis(attributes['objid'])
        # Create a copy of the axis so when the file
        # closes, we still have a valid version of it.
        val = val.subaxis(0, len(val))
    if objtype == "attribute":
        val = f.attributes[attributes['objid']]
    if objtype == "attributes":
        val = f.attributes.keys()
    # We should figure out how to cache files
    # That way if we're using OPeNDAP, we won't
    # waste time renegotiating the same file.
    f.close()
    return val


class DatasetFunction(ComputeNode):
    def __init__(self, uri, objtype, id=None, **args):
        super(DatasetFunction, self).__init__()
        self.node_type = DATASET_NODE_TYPE
        self.node_params = {
            "uri": "URI for a dataset",
            "objtype": "Type of object to retrieve.",
            "objid": "id of the object to retrieve"
        }
        if objtype not in obj_types:
            raise ValueError(INVALID_DATASET_FUNC % objtype)
        self.uri = uri
        self.objtype = objtype
        self.objid = id
        if args:
            self.args = args