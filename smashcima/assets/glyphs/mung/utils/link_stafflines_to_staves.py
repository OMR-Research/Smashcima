from mung.graph import NotationGraph
from mung.node import Node

from .get_new_node_id import get_new_node_id


def link_stafflines_to_staves(graph: NotationGraph):
    """Takes all stafflines and creates the 'staff' objects, naively,
    by grouping them top-to-bottom in groups of 5. Mask is not computed."""
    all_lines = [
        n for n in graph.vertices
        if n.class_name == "staffLine"
    ]
    all_lines.sort(key=lambda n: n.top)

    all_staves = [
        n for n in graph.vertices
        if n.class_name == "staff"
    ]
    all_staves.sort(key=lambda n: n.top)

    assert len(all_lines) % 5 == 0, \
        "Staffline count is not divisible by 5"
    assert len(all_lines) == len(all_staves) * 5, \
        "Staves and stafflines cannot be paired up"

    for i in range(len(all_lines) // 5):
        lines = all_lines[i*5:(i+1)*5]
        staff = all_staves[i]

        for line in lines:
            graph.add_edge(staff.id, line.id)

        # top = min(l.top for l in lines)
        # left = min(l.left for l in lines)
        # bottom = max(l.bottom for l in lines)
        # right = min(l.right for l in lines)

        # staff = Node(
        #     id_=get_new_node_id(graph),
        #     class_name="staff",
        #     top=top,
        #     left=left,
        #     width=right-left,
        #     height=bottom-top,
        #     outlinks=[l.id for l in lines],
        #     inlinks=[],
        #     dataset=lines[0].dataset,
        #     document=lines[0].document
        # )

        # # graph.add_vertex(...)
        # graph._NotationGraph__id_to_node_mapping[staff.id] = staff
        # graph._NotationGraph__nodes.append(staff)
