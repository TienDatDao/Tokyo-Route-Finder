from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
from collections import deque


# =========================================================
# ENUMS
# =========================================================

class EdgeType(str, Enum):
    TRAIN = "train"
    WALK = "walk"


class InputType(str, Enum):
    STATION_ID = "STATION_ID"
    COORDINATE = "COORDINATE"


class OptimizedBy(str, Enum):
    SHORTEST_TIME = "shortest_time"
    LOWEST_COST = "lowest_cost"
    LEAST_TRANSFER = "least_transfer"


class IncidentType(str, Enum):
    STATION_CLOSED = "STATION_CLOSED"
    LINE_MAINTENANCE = "LINE_MAINTENANCE"
    STATION_GROUP_CLOSED = "STATION_GROUP_CLOSED"


class ResponseStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NO_ROUTE_FOUND = "NO_ROUTE_FOUND"
    OUT_OF_SERVICE_AREA = "OUT_OF_SERVICE_AREA"
    ALREADY_AT_DESTINATION = "ALREADY_AT_DESTINATION"
    START_STATION_CLOSED = "START_STATION_CLOSED"
    SYSTEM_ERROR = "SYSTEM_ERROR"


# =========================================================
# GRAPH STRUCTURES
# =========================================================

@dataclass
class Node:
    id: str
    name: str
    lat: float
    lon: float


@dataclass
class Edge:
    to_node: str
    edge_type: EdgeType
    time: float
    cost: float
    distance: float

    # IMPORTANT:
    # WALK phải có identity riêng
    line: str = "__walk__"

    # optional future extensions
    service_type: Optional[str] = None
    direction: Optional[str] = None


@dataclass
class Graph:
    nodes: Dict[str, Node] = field(default_factory=dict)

    # adjacency list
    edges: Dict[str, List[Edge]] = field(default_factory=dict)

    # =====================================================
    # EDGE HELPERS
    # =====================================================

    def add_edge(
            self,
            from_node: str,
            edge: Edge
    ):
        if from_node not in self.edges:
            self.edges[from_node] = []

        self.edges[from_node].append(edge)

    # =====================================================
    # CLEAN GRAPH
    # =====================================================

    def clean(self):
        """
        Remove:
        - edges to invalid nodes

        KEEP:
        - valid multiedges
        """

        cleaned_edges = {}

        for from_node, edge_list in self.edges.items():

            if from_node not in self.nodes:
                continue

            valid_edges = []

            seen = set()

            for edge in edge_list:

                if edge.to_node not in self.nodes:
                    continue

                # IMPORTANT:
                # preserve legitimate multiedges
                edge_key = (
                    edge.to_node,
                    edge.edge_type,
                    edge.line,
                    round(edge.time, 3),
                    round(edge.cost, 3),
                    round(edge.distance, 3),
                    edge.service_type,
                    edge.direction
                )

                if edge_key in seen:
                    continue

                seen.add(edge_key)

                valid_edges.append(edge)

            if valid_edges:
                cleaned_edges[from_node] = valid_edges

        self.edges = cleaned_edges

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(self) -> List[str]:

        errors = []

        # ---------------------------------------------
        # invalid node references
        # ---------------------------------------------

        for from_node, edge_list in self.edges.items():

            if from_node not in self.nodes:
                errors.append(
                    f"Edge source missing node: {from_node}"
                )
                continue

            for edge in edge_list:

                if edge.to_node not in self.nodes:
                    errors.append(
                        f"Invalid edge: "
                        f"{from_node} -> {edge.to_node}"
                    )

        # ---------------------------------------------
        # connectivity
        # ---------------------------------------------

        if self.nodes:

            start = next(iter(self.nodes.keys()))

            visited = set([start])

            queue = deque([start])

            while queue:

                current = queue.popleft()

                for edge in self.edges.get(current, []):

                    nxt = edge.to_node

                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)

            if len(visited) != len(self.nodes):

                errors.append(
                    f"Graph disconnected: "
                    f"{len(visited)}/{len(self.nodes)} reachable"
                )

        return errors


# =========================================================
# INPUT STRUCTURES
# =========================================================

@dataclass
class Coordinate:
    lat: float
    lon: float


@dataclass
class Point:
    input_type: InputType
    value: Union[str, Coordinate]


@dataclass
class Preferences:
    optimized_by: OptimizedBy = OptimizedBy.SHORTEST_TIME


@dataclass
class RoutingRequest:
    start_point: Point
    end_point: Point
    preferences: Preferences


# =========================================================
# INCIDENTS
# =========================================================

@dataclass
class Incident:
    incident_id: str
    type: IncidentType
    target_id: str


# =========================================================
# RESPONSE STRUCTURES
# =========================================================

@dataclass
class RouteDetail:
    station_id: str
    station_name: str
    line: str
    action: str


@dataclass
class Route:
    path: List[str]
    total_time: float
    total_cost: float
    transfers: int
    details: List[RouteDetail]


@dataclass
class RoutingResponse:
    status: ResponseStatus
    suggested_start_station: Optional[Dict[str, str]] = None
    walking_info: Optional[Dict[str, float]] = None
    route: Optional[Route] = None