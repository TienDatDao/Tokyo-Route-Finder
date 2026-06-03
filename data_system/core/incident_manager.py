from typing import List
from copy import deepcopy
from pathlib import Path

from .station_group_resolver import (
    StationGroupResolver
)
from .models import (
    Graph,
    Incident,
    IncidentType,
    EdgeType
)
BASE_DIR = Path(__file__).resolve().parent.parent

STATION_GROUPS_PATH = (
    BASE_DIR
    / "raw_data"
    / "station_groups.json"
)

resolver = StationGroupResolver(
    STATION_GROUPS_PATH
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

            raw_target = incident.target_id

            station_name = (
                raw_target
                .split(".")[-1]
            )

            station_nodes = resolver.resolve(
                station_name
            )

            print(
                f"🚫 Closing station group: "
                f"{station_name}"
            )

            print(
                f"   Removing {len(station_nodes)} nodes"
            )

            for station_id in station_nodes:

                # Remove node
                if station_id in filtered_graph.nodes:
                    del filtered_graph.nodes[station_id]

                # Remove outgoing edges
                filtered_graph.edges.pop(
                    station_id,
                    None
                )

                # Remove incoming edges
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