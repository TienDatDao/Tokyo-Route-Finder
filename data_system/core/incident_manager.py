from typing import List
from copy import deepcopy

from .models import (
    Graph,
    Incident,
    IncidentType,
    EdgeType
)


def apply_incidents(
        graph: Graph,
        incidents: List[Incident]
) -> Graph:

    filtered_graph = deepcopy(graph)

    for incident in incidents:

        # ==========================================
        # STATION CLOSED
        # ==========================================

        if incident.type == IncidentType.STATION_CLOSED:

            station_id = incident.target_id

            if station_id in filtered_graph.nodes:
                del filtered_graph.nodes[station_id]

            filtered_graph.edges.pop(
                station_id,
                None
            )

            for node_id in filtered_graph.edges:

                filtered_graph.edges[node_id] = [

                    edge

                    for edge in
                    filtered_graph.edges[node_id]

                    if edge.to_node != station_id
                ]

        # ==========================================
        # LINE MAINTENANCE
        # ==========================================

        elif incident.type == IncidentType.LINE_MAINTENANCE:

            closed_line = incident.target_id

            removed_edges = 0

            for node_id in filtered_graph.edges:

                original_count = len(
                    filtered_graph.edges[node_id]
                )

                filtered_graph.edges[node_id] = [

                    edge

                    for edge in
                    filtered_graph.edges[node_id]

                    if not (
                        edge.edge_type == EdgeType.TRAIN
                        and edge.line == closed_line
                    )
                ]

                removed_edges += (
                    original_count
                    - len(filtered_graph.edges[node_id])
                )

            print(
                f"🚧 Removed "
                f"{removed_edges} edges "
                f"for line maintenance: "
                f"{closed_line}"
            )

    # ==========================================
    # REMOVE ISOLATED NODES
    # ==========================================

    isolated_nodes = []

    for node_id in list(filtered_graph.nodes.keys()):

        if (
                node_id not in filtered_graph.edges
                or len(filtered_graph.edges[node_id]) == 0
        ):
            isolated_nodes.append(node_id)

    for node_id in isolated_nodes:

        filtered_graph.nodes.pop(node_id, None)
        filtered_graph.edges.pop(node_id, None)

    # ==========================================
    # CLEAN
    # ==========================================

    filtered_graph.clean()

    return filtered_graph