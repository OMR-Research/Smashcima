from mung.graph import NotationGraph
from mung.node import Node


def link_nodes_to_staves(graph: NotationGraph):
    """
    Everything links to staves and staves link to stafflines.
    Links are created based on the closest staff to the node in question.
    """
    # get all staves on the page
    staves = [
        n for n in graph.vertices
        if n.class_name == "staff"
    ]
    assert len(staves) > 0, "There must be at least one staff"

    # go through all the nodes
    for node in graph.vertices:

        # ignore staves, they cannot be assigned to themselves
        # and stafflines, they have to be assigned separately
        if node.class_name in ["staff", "staffLine"]:
            continue

        # find the closest staff
        closest_staff = min(
            staves,
            key=lambda s: _distance_to_staff(s, node)
        )
        
        # link node to the staff
        graph.add_edge(node.id, closest_staff.id)


def _distance_to_staff(staff: Node, node: Node) -> float:
    # stupid implementation that just computes
    # vertical distance of centerpoints
    staff_y = (staff.top + staff.bottom) // 2
    node_y = (node.top + node.bottom) // 2
    return abs(staff_y - node_y)
