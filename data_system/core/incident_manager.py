# Quản lý sự cố
from typing import List
from .models import Graph, Incident, IncidentType

def apply_incidents(graph: Graph, incidents: List[Incident]) -> Graph:
    """
    Áp dụng danh sách incidents vào graph, trả về graph đã được filter.
    - STATION_CLOSED: Remove node và tất cả edges liên quan.
    - LINE_MAINTENANCE: Remove edges của tuyến bị bảo trì.
    """
    # Sao chép graph để không modify original
    filtered_graph = Graph()
    filtered_graph.nodes = graph.nodes.copy()
    filtered_graph.edges = {node: edges.copy() for node, edges in graph.edges.items()}

    for incident in incidents:
        if incident.type == IncidentType.STATION_CLOSED:
            # Remove node
            if incident.target_id in filtered_graph.nodes:
                del filtered_graph.nodes[incident.target_id]
            # Remove edges liên quan
            if incident.target_id in filtered_graph.edges:
                del filtered_graph.edges[incident.target_id]
            # Remove edges pointing to this node
            for node, edges in filtered_graph.edges.items():
                filtered_graph.edges[node] = [e for e in edges if e.to_node != incident.target_id]

        elif incident.type == IncidentType.LINE_MAINTENANCE:
            # Remove edges của tuyến này
            for node, edges in filtered_graph.edges.items():
                filtered_graph.edges[node] = [e for e in edges if e.line != incident.target_id]

    # Clean lại sau khi filter
    filtered_graph.clean()

    return filtered_graph
