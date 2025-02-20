from mung.graph import NotationGraph


def get_new_node_id(graph: NotationGraph) -> int:
    """Returns the next ID that's larger than the largest ID in the graph"""
    if len(graph.vertices) == 0:
        return 0
    return max(n.id for n in graph.vertices) + 1
