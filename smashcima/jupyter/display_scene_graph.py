import IPython.display
import ipycytoscape

from smashcima.scene.AffineSpace import AffineSpace
from ..scene.Scene import Scene
from smashcima.scene.SceneObject import SceneObject, Link
from typing import List
import ipywidgets
import IPython
import pprint
from copy import deepcopy


_CYTOSCAPE_STYLE = [
    {
        "selector": "node",
        "css": {
            "content": "data(name)",
            "text-valign": "center",
            "color": "white",
            "text-outline-width": 2,
            "text-outline-color": "data(color)",
            "background-color": "data(color)"
        }
    },
    {
        "selector": "node:parent",
        "css": {
            "background-opacity": 0.333
        }
    },
    {
        "selector": "edge",
        "style": {
            "width": 4,
            "opacity": 0.5,
            "line-color": "data(color)",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "data(color)",
            "curve-style": "bezier"
        }
    }
]


def _scene_object_to_color(scene_object: SceneObject) -> str:
    typename = str(type(scene_object))
    if "smashcima.scene.visual" in typename: return "green"
    if "smashcima.scene.semantic" in typename: return "#11479e"
    return "gray"


def _scene_object_to_node(scene_object: SceneObject) -> ipycytoscape.Node:
    node = ipycytoscape.Node()
    node.data["id"] = str(id(scene_object))
    node.data["name"] = type(scene_object).__name__
    node.data["color"] = _scene_object_to_color(scene_object)
    return node


def _link_to_edge(link: Link) -> ipycytoscape.Edge:
    edge = ipycytoscape.Edge()
    edge.data["source"] = str(id(link.source))
    edge.data["target"] = str(id(link.target))
    edge.data["color"] = _scene_object_to_color(link.source)
    return edge


def _populate_graph_from_scene(graph: ipycytoscape.Graph, scene: Scene):
    nodes: List[ipycytoscape.Node] = []
    edges: List[ipycytoscape.Edge] = []

    for obj in scene.objects.values():
        nodes.append(_scene_object_to_node(obj))
        for outlink in obj.outlinks:
            edges.append(_link_to_edge(outlink))
    
    graph.add_nodes(nodes)
    graph.add_edges(edges)


def display_scene_graph(scene: Scene):
    """Displays an interactive scene graph jupyter widget"""
    
    # === create widgets ===
    
    widget = ipycytoscape.CytoscapeWidget()
    out = ipywidgets.Output()

    # === setup cytoscape graph ===

    _populate_graph_from_scene(widget.graph, scene)
    
    widget.set_layout(name="dagre", nodeSpacing=10, edgeLengthVal=10)
    widget.set_style(_CYTOSCAPE_STYLE)

    # === handle interactions ===

    with out:
        print("Click on node to preview it.")

    def handle_node_click(node: dict):
        with out:
            out.clear_output()
            obj = scene.objects[int(node["data"]["id"])]
            print(pprint.pformat(obj))

    widget.on("node", "click", handle_node_click)

    # === display in jupyter ===

    IPython.display.display(widget)
    IPython.display.display(out)


def display_scene_object_graph(
    obj: SceneObject,
    recurse_via_inlinks=True,
    discard_object_inlinks=True
):
    """Displays an interactive scene graph for a single scene object"""
    # isolate the given object from the graph by making a copy
    # and removing all inlinks
    obj_clone = deepcopy(obj)
    if discard_object_inlinks:
        obj_clone.inlinks = []
    scene = Scene(root_space=AffineSpace())
    scene.objects.clear() # remove the root affine space
    scene.add(obj_clone, recurse_via_inlinks=recurse_via_inlinks)
    display_scene_graph(scene)
