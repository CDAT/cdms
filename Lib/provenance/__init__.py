import json
import node
import numpy_backend
import os


def derive(json_spec, backend=numpy_backend):
    if isinstance(json_spec, (str, unicode)):
        definition = json.loads(json_spec)
    elif isinstance(json_spec, dict):
        definition = json_spec
    else:
        raise ValueError("json_spec must be a dictionary or JSON-encoded text.")

    variable_id = definition.get("id", None)
    derivation = definition.get("derivation", [])

    derivation_results = []
    for step in derivation:
        if "type" not in step:
            raise ValueError("No derivation step type provided.")

        result = None

        if step["type"].lower() == "file":
            result = node.FileNode(step["uri"], backend)

        if step["type"].lower() == "variable":
            operation = node.create_operation(step["operation"], backend)
            result = node.VariableNode(operation, [derivation_results[i] for i in step["parents"]], backend)

        if step["type"].lower() == "value":
            result = node.RawValueNode(step["value"], backend)

        if step["type"].lower() == "axis":
            result = node.AxisNode(step["operation"], [derivation_results[i] for i in step["parents"]], step["args"], backend)

        if result is None:
            raise ValueError("Unsupported derivation step type: %s" % (step["type"]))

        derivation_results.append(result)

    var = derivation_results[-1].get_value()
    if "id" in definition:
        var.id = str(definition["id"])
    return var


def export(node, path=None, fmt=None):
    """
    Convert the node's data graph into a serialized format and store it at path.

    If fmt is None, it will default to using whatever format is specified in
    path's file extension, or, if none found, will use JSON.
    """

    if node is None:
        raise ValueError("Object not tracking provenance.")

    if fmt is None and path is not None:
        _, fmt = os.path.splitext(path)
        fmt = fmt[1:]

    if not fmt:
        fmt = "json"

    if fmt == "json":
        graph = graphToDict(node)
        if path:
            with open(path, "w") as outfile:
                json.dump(graph, outfile)
        else:
            return json.dumps(graph)
    else:
        raise NotImplementedError("No export for filetype %s implemented." % fmt)


def graphToDict(obj_node):
    if obj_node is None:
        raise ValueError("Object not tracking provenance.")
    all_nodes = [obj_node]
    index = 0

    # Accumulate node and its ancestors into all_nodes
    while index < len(all_nodes):
        n = all_nodes[index]
        if hasattr(n, "parents"):
            all_nodes.extend(n.parents)
        index += 1

    graph = {
        "id": obj_node.get_value().id,
        "derivation": []
    }

    ordered_nodes = all_nodes[::-1]

    # Assemble the derivation
    for n in ordered_nodes:
        graph["derivation"].append(n.to_dict(ordered_nodes))

    graph["type"] = graph["derivation"][-1]["type"]

    return graph
