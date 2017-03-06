from compute_graph import ComputeNode, register_computation

GEOSPATIAL_NODE_TYPE = "geospatial"
functions = ["subset", "lat", "lon", "time", "lev", "axis"]

INVALID_GEOSPATIAL_FUNC = "Expected geospatial function; received '%s'."


@register_computation(GEOSPATIAL_NODE_TYPE)
def compute_geo(attributes):
    array = attributes["array"]
    func = attributes["func"]
    args = attributes.get("args", {})

    if func == "subset":
        return array(**args)

    if func == "lat":
        return array.getLatitude()

    if func == "lon":
        return array.getLongitude()

    if func == "time":
        return array.getTime()

    if func == "lev":
        return array.getLevel()

    if func == "axis":
        return array.getAxis(args["index"])


class GeospatialFunction(ComputeNode):
    def __init__(self, func, array, **args):
        super(GeospatialFunction, self).__init__()
        self.node_type = GEOSPATIAL_NODE_TYPE
        self.node_params = {
            "func": "Function used for calculation.",
            "array": "Array to perform function on"
        }
        if func not in functions:
            raise ValueError(INVALID_GEOSPATIAL_FUNC % func)
        self.func = func
        self.array = array
        if args:
            self.args = args
