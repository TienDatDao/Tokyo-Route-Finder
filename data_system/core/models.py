# Định nghĩa cấu trúc node, edge, graph, request, incident
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
 # DƯỚI ĐÂY LÀ TOÀN BỘ NHỮNG ĐỊNH NGHĨA CÓ THỂ CÓ CỦA 1 ĐỒ THỊ BAO GỒM CẢ ĐỒ THỊ VÀ TOÀN BỘ ĐỐI TƯỢNG TRUY VẤN
 # CÓ THỂ CÓ MỘT SỐ THỨ KHÔNG DÙNG TỚI, NHƯNG TÔI CỨ ĐỊNH NGHĨA LUÔN ĐỂ DỰ PHÒNG CHO NHỮNG TÌNH HUỐNG CÓ THỂ XẢY RA TRONG TƯƠNG LAI,
 # NHƯNG HIỆN TẠI CHƯA SỬ DỤNG ĐẾN
# Cac hang so
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

class ResponseStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NO_ROUTE_FOUND = "NO_ROUTE_FOUND"  # Không tìm thấy đường (bị cô lập)
    OUT_OF_SERVICE_AREA = "OUT_OF_SERVICE_AREA"  # Tọa độ ngoài vùng phủ sóng
    ALREADY_AT_DESTINATION = "ALREADY_AT_DESTINATION"  # Điểm đi trùng điểm đến
    START_STATION_CLOSED = "START_STATION_CLOSED"  # Ga xuất phát đang bị đóng cửa
    SYSTEM_ERROR = "SYSTEM_ERROR"  # Lỗi hệ thống không xác định
# Dinh nghia cau truc node, edge, graph
@dataclass
class Node: # dai dien cho 1 nha ga
    id: str
    name: str
    lat: float
    lon: float

@dataclass
class Edge: # dai dien cho 1 tuyen duong giua 2 nha ga
    to_node: str
    edge_type: EdgeType # su dung enum de tranh go sai do da duoc dinh nghia truc tiep o tren
    time: float
    cost: float
    distance: float
    line: Optional[str] = None # neu la di bo thi kh can line

@dataclass
class Graph:
    # dictionary chua cac node
    nodes: Dict[str, Node] = field(default_factory=dict)
    # danh sach ke chua cac duong di
    edges: Dict[str, List[Edge]] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """
        Validate the graph for cleanliness:
        - No duplicate edges
        - All edges reference existing nodes
        - Graph is connected (single component)
        Returns a list of error messages. Empty list means valid.
        """
        errors = []

        # Check for duplicate edges
        seen_edges = set()
        for from_node, edge_list in self.edges.items():
            if from_node not in self.nodes:
                errors.append(f"Node '{from_node}' in edges but not in nodes.")
                continue
            for edge in edge_list:
                edge_key = (from_node, edge.to_node, edge.edge_type, edge.line)
                if edge_key in seen_edges:
                    errors.append(f"Duplicate edge: {from_node} -> {edge.to_node} ({edge.edge_type})")
                else:
                    seen_edges.add(edge_key)
                if edge.to_node not in self.nodes:
                    errors.append(f"Edge from '{from_node}' references non-existent node '{edge.to_node}'")

        # Check connectivity using BFS
        if self.nodes:
            visited = set()
            queue = [next(iter(self.nodes.keys()))]  # Start from first node
            visited.add(queue[0])
            while queue:
                current = queue.pop(0)
                for edge in self.edges.get(current, []):
                    if edge.to_node not in visited:
                        visited.add(edge.to_node)
                        queue.append(edge.to_node)
            if len(visited) < len(self.nodes):
                errors.append(f"Graph is not connected. Visited {len(visited)} out of {len(self.nodes)} nodes.")

        return errors

    def clean(self):
        """
        Clean the graph: remove duplicate edges, remove edges to non-existent nodes.
        """
        # Remove edges to non-existent nodes and deduplicate
        cleaned_edges = {}
        seen_edges = set()
        for from_node, edge_list in self.edges.items():
            if from_node not in self.nodes:
                continue  # Skip invalid from_node
            cleaned_list = []
            for edge in edge_list:
                if edge.to_node not in self.nodes:
                    continue
                edge_key = (from_node, edge.to_node, edge.edge_type, edge.line)
                if edge_key not in seen_edges:
                    cleaned_list.append(edge)
                    seen_edges.add(edge_key)
            if cleaned_list:
                cleaned_edges[from_node] = cleaned_list
        self.edges = cleaned_edges

# dinh nghia doi tuong dau vao tu user

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

# dinh nghia doi tuong su co

@dataclass
class Incident:
    incident_id: str
    type: IncidentType # loai su co
    target_id: str # id cua ga

# dinh nghia doi tuong dau ra tra ve cho frontend
@dataclass
class RouteDetail: # chi tiet tuyen duong
    station_id: str # id ga
    station_name: str # ten ga
    line: str #ten tuyen
    action: str # hanh dong "board", "transfer", "exit"

@dataclass
class Route:
    path: List[str] # mo ta toan bo hanh trinh
    total_time: float
    total_cost: float
    transfers: int
    details: List[RouteDetail]

@dataclass
class RoutingResponse:
    status: ResponseStatus # "SUCCESS", "NO_ROUTE_FOUND",...
    suggested_start_station: Optional[Dict[str, str]] = None
    walking_info: Optional[Dict[str, float]] = None
    route: Optional[Route] = None
