from compute_graph import ComputeNode, register_computation

METADATA_NODE_TYPE = "metadata"


@register_computation(METADATA_NODE_TYPE)
def compute_metadata(attributes):
    import cdms2
    obj = attributes["obj"]
    if "attribute" not in attributes:
        return obj.attributes.keys()
    attr = attributes["attribute"]
    if "value" not in attributes:
        return obj.attributes[attr]
    # Copy the object and update the attribute
    # Then return the copy
    if isinstance(obj, cdms2.grid.AbstractGrid):
        tgrid = obj.subGrid(None, None)
        tgrid.attributes = dict(obj.attributes)
        tgrid.id = obj.id
        obj = tgrid
    elif isinstance(obj, cdms2.avariable.AbstractVariable):
        obj = obj()
    elif isinstance(obj, cdms2.axis.AbstractAxis):
        obj = obj.subAxis(0, len(obj))
    else:
        # Add more copying strategies here
        # compute_graph should handle eliminating unneeded results
        pass
    setattr(obj, attr, attributes["value"])
    return obj


class MetadataFunction(ComputeNode):
    def __init__(self, obj, attribute=None, value=None):
        super(MetadataFunction, self).__init__()
        self.node_type = METADATA_NODE_TYPE
        self.node_params = {
            "obj": "Object to get/set metadata from/on",
            "attribute": "Attribute get/set",
            "value": "Value to set"
        }
        self.obj = obj
        self.attribute = attribute
        self.value = value
