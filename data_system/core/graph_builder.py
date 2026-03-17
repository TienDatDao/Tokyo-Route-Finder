# Lắp ráp dữ liệu thành graph
import logging
import math
from typing import Dict, List
from itertools import combinations

from .models import Graph, Edge, EdgeType
from .parsers import (
    parse_stations,
    parse_railway,
    parse_train_types,
    parse_station_groups
)
from ..config import config
from ..utils.logger import logger
from ..utils.geo_calc import haversine_distance


# CÁC HÀM XÂY DỰNG ĐỒ THỊ
# Các hàm xây dựng đồ thị sẽ được gọi từ hàm chính build_tokyo_graph() ở dưới, mỗi hàm sẽ đảm nhận một phần việc cụ thể như xây dựng cạnh tàu,
# xây dựng cạnh đi bộ, v.v...
def _add_edges_for_station_list(graph: Graph, line_name: str, station_list: List[str]):
    # Hàm phụ trợ: Nối các ga liền kề trong một mảng
    for i in range(len(station_list) - 1):
        station_a = station_list[i]
        station_b = station_list[i + 1]

        if station_a not in graph.nodes or station_b not in graph.nodes:
            continue

        node_a = graph.nodes[station_a]
        node_b = graph.nodes[station_b]

        distance = haversine_distance(node_a.lat, node_a.lon, node_b.lat, node_b.lon)
        time_min = round((distance / config.TRAIN_SPEED_KMH) * 60, 1)
        cost_yen = config.TRAIN_COST_YEN

        if station_a not in graph.edges: graph.edges[station_a] = []
        if station_b not in graph.edges: graph.edges[station_b] = []

        graph.edges[station_a].append(
            Edge(to_node=station_b, edge_type=EdgeType.TRAIN, line=line_name, time=time_min, cost=cost_yen,
                 distance=distance))
        graph.edges[station_b].append(
            Edge(to_node=station_a, edge_type=EdgeType.TRAIN, line=line_name, time=time_min, cost=cost_yen,
                 distance=distance))


def _build_train_edges(graph: Graph, raw_railway, raw_train_types: Dict):
    # Kéo đường ray: Nối các ga liền kề nhau trên cùng một tuyến
    if isinstance(raw_railway, list):
        for line_data in raw_railway:
            line_id = line_data.get("id", "Unknown Line")
            title = line_data.get("title", {})
            line_name = title.get("en", title.get("ja", line_id))
            station_list = line_data.get("stations", [])

            _add_edges_for_station_list(graph, line_name, station_list)

def _build_walk_edges(graph: Graph, raw_groups: List[List[List[str]]]):
    # Xây đường đi bộ: Nối các ga trong cùng 1 cụm (Station Complex)

    for complex_group in raw_groups:
        # Gom tất cả các ID trong cụm này thành 1 list phẳng để xử lý
        all_stations_in_complex = []
        for fare_zone in complex_group:
            all_stations_in_complex.extend(fare_zone)

        # Nối tất cả các ga trong cụm này với nhau bằng tổ hợp chập 2
        for station_a, station_b in combinations(all_stations_in_complex, 2):
            if station_a not in graph.nodes or station_b not in graph.nodes:
                continue

            # Xác định xem 2 ga này có cùng khu vực soát vé (fare_zone) không
            is_same_fare_zone = any((station_a in fz and station_b in fz) for fz in complex_group)

            # Tính toán tgian chuyển tuyến đi bộ dựa trên việc có cùng khu vực soát vé hay không
            if is_same_fare_zone:
                walk_time = config.WALK_TIME_SAME_ZONE_MIN
            else:
                walk_time = config.WALK_TIME_DIFF_ZONE_MIN

            distance = haversine_distance(
                graph.nodes[station_a].lat, graph.nodes[station_a].lon,
                graph.nodes[station_b].lat, graph.nodes[station_b].lon
            )

            if station_a not in graph.edges: graph.edges[station_a] = []
            if station_b not in graph.edges: graph.edges[station_b] = []

            # Thêm cạnh đi bộ (Chiều A->B và B->A)
            walk_edge_a_to_b = Edge(to_node=station_b, edge_type=EdgeType.WALK, time=walk_time, cost=0.0,
                                    distance=distance)
            walk_edge_b_to_a = Edge(to_node=station_a, edge_type=EdgeType.WALK, time=walk_time, cost=0.0,
                                    distance=distance)

            graph.edges[station_a].append(walk_edge_a_to_b)
            graph.edges[station_b].append(walk_edge_b_to_a)


# HÀM CHÍNH
def build_tokyo_graph(
        stations_path: str,
        railway_path: str,
        train_types_path: str,
        groups_path: str
) -> Graph:
    # Tổng hợp 4 file JSON thành 1 Đồ thị duy nhất.
    logger.info("Bắt đầu xây dựng đồ thị Tokyo...")

    graph = Graph()

    # (Nạp Nodes)
    graph.nodes = parse_stations(stations_path)

    # Đọc dữ liệu thô còn lại
    raw_railway = parse_railway(railway_path)
    raw_train_types = parse_train_types(train_types_path)
    raw_groups = parse_station_groups(groups_path)

    # Kéo đường ray (Edges: Train)
    _build_train_edges(graph, raw_railway, raw_train_types)

    # Xây đường đi bộ (Edges: Walk)
    _build_walk_edges(graph, raw_groups)

    # Làm sạch đồ thị: loại bỏ duplicate edges và edges không hợp lệ
    graph.clean()

    # Validate đồ thị
    validation_errors = graph.validate()
    if validation_errors:
        for error in validation_errors:
            logger.warning(f"Graph validation error: {error}")
        # Có thể raise exception nếu muốn strict, nhưng tạm thời chỉ log
        # raise ValueError("Graph validation failed: " + "; ".join(validation_errors))

    # Thống kê hệ thống
    total_nodes = len(graph.nodes)
    total_edges = sum(len(edges) for edges in graph.edges.values())
    logger.info(f"Đã xây dựng xong Đồ thị: {total_nodes} Nhà ga | {total_edges} Đoạn đường.")

    return graph