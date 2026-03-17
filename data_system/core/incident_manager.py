# Quản lý sự cố
from typing import List
from .models import Graph, Incident, IncidentType

def apply_incidents(graph: Graph, incidents: List[Incident]) -> Graph:
    """
    Áp dụng danh sách incidents vào graph, trả về graph đã được filter.
    - STATION_CLOSED: Remove node và tất cả edges liên quan.
    - LINE_MAINTENANCE: Remove edges của tuyến bị bảo trì.
    - STATION_REOPEN: Add lại node và edges liên quan (tương tự đóng nhưng ngược lại).
    - LINE_REOPEN: Add lại edges của tuyến (tương tự bảo trì nhưng ngược lại).
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

        elif incident.type == IncidentType.STATION_REOPEN:
            # Add lại node nếu chưa có
            if incident.target_id not in filtered_graph.nodes and incident.target_id in graph.nodes:
                filtered_graph.nodes[incident.target_id] = graph.nodes[incident.target_id]
            # Add lại edges liên quan từ original graph
            if incident.target_id in graph.edges:
                filtered_graph.edges[incident.target_id] = graph.edges[incident.target_id].copy()
            # Add edges pointing to this node từ original
            for node, edges in graph.edges.items():
                for e in edges:
                    if e.to_node == incident.target_id and node not in filtered_graph.edges:
                        filtered_graph.edges[node] = []
                    if e.to_node == incident.target_id and e not in filtered_graph.edges.get(node, []):
                        filtered_graph.edges[node].append(e)

        elif incident.type == IncidentType.LINE_REOPEN:
            # Add lại edges của tuyến từ original
            for node, edges in graph.edges.items():
                for e in edges:
                    if e.line == incident.target_id:
                        if node not in filtered_graph.edges:
                            filtered_graph.edges[node] = []
                        if e not in filtered_graph.edges[node]:
                            filtered_graph.edges[node].append(e)

    # Clean lại sau khi filter
    filtered_graph.clean()

    return filtered_graph
