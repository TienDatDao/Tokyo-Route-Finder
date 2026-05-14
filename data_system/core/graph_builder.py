# Lắp ráp dữ liệu thành graph
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


# ==========================================
# HELPER
# ==========================================

def get_station_base_name(station_id: str) -> str:
    """
    Ví dụ:
    JR-East.Yamanote.Shibuya -> Shibuya
    TokyoMetro.Ginza.Shibuya -> Shibuya
    """
    return station_id.split(".")[-1]


# ==========================================
# TRAIN EDGES
# ==========================================

def _add_edges_for_station_list(
        graph: Graph,
        line_name: str,
        station_list: List[str]
):
    """
    Nối các ga liền kề trên cùng tuyến
    """

    for i in range(len(station_list) - 1):

        station_a = station_list[i]
        station_b = station_list[i + 1]

        if station_a not in graph.nodes or station_b not in graph.nodes:
            continue

        node_a = graph.nodes[station_a]
        node_b = graph.nodes[station_b]

        distance = haversine_distance(
            node_a.lat,
            node_a.lon,
            node_b.lat,
            node_b.lon
        )

        # tốc độ tàu nội đô thực tế hơn
        time_min = round(
            (distance / config.TRAIN_SPEED_KMH) * 60,
            1
        )

        cost_yen = config.TRAIN_COST_YEN

        if station_a not in graph.edges:
            graph.edges[station_a] = []

        if station_b not in graph.edges:
            graph.edges[station_b] = []

        edge_ab = Edge(
            to_node=station_b,
            edge_type=EdgeType.TRAIN,
            line=line_name,
            time=time_min,
            cost=cost_yen,
            distance=distance
        )

        edge_ba = Edge(
            to_node=station_a,
            edge_type=EdgeType.TRAIN,
            line=line_name,
            time=time_min,
            cost=cost_yen,
            distance=distance
        )

        graph.edges[station_a].append(edge_ab)
        graph.edges[station_b].append(edge_ba)


def _build_train_edges(
        graph: Graph,
        raw_railway,
        raw_train_types: Dict
):
    """
    Build train edges
    """

    if not isinstance(raw_railway, list):
        return

    for line_data in raw_railway:

        line_id = line_data.get("id", "Unknown Line")

        title = line_data.get("title", {})

        line_name = title.get(
            "en",
            title.get("ja", line_id)
        )

        station_list = line_data.get("stations", [])

        _add_edges_for_station_list(
            graph,
            line_name,
            station_list
        )


# ==========================================
# WALK / TRANSFER EDGES
# ==========================================

def _build_walk_edges(
        graph: Graph,
        raw_groups: List[List[List[str]]]
):
    """
    Build transfer edges giữa các line trong cùng station complex
    """

    for complex_group in raw_groups:

        all_stations_in_complex = []

        for fare_zone in complex_group:
            all_stations_in_complex.extend(fare_zone)

        for station_a, station_b in combinations(
                all_stations_in_complex,
                2
        ):

            if (
                    station_a not in graph.nodes or
                    station_b not in graph.nodes
            ):
                continue

            # ==================================================
            # CHỈ NỐI GA CÙNG TÊN
            # ==================================================

            base_a = get_station_base_name(station_a).lower()
            base_b = get_station_base_name(station_b).lower()

            # Chỉ transfer nếu cùng tên ga
            if base_a != base_b:
                continue

            # ==================================================
            # TÍNH KHOẢNG CÁCH
            # ==================================================

            node_a = graph.nodes[station_a]
            node_b = graph.nodes[station_b]

            distance = haversine_distance(
                node_a.lat,
                node_a.lon,
                node_b.lat,
                node_b.lon
            )

            # ==================================================
            # CHỈ CHO TRANSFER NẾU ĐỦ GẦN
            # ==================================================

            # if distance > 0.7:
            #     continue

            # ==================================================
            # CHECK FARE ZONE
            # ==================================================

            is_same_fare_zone = any(
                (
                        station_a in fz and
                        station_b in fz
                )
                for fz in complex_group
            )

            # ==================================================
            # TRANSFER PENALTY
            # ==================================================

            if is_same_fare_zone:
                walk_time = config.WALK_TIME_SAME_ZONE_MIN
            else:
                walk_time = config.WALK_TIME_DIFF_ZONE_MIN

            if station_a not in graph.edges:
                graph.edges[station_a] = []

            if station_b not in graph.edges:
                graph.edges[station_b] = []

            edge_ab = Edge(
                to_node=station_b,
                edge_type=EdgeType.WALK,
                line=None,
                time=walk_time,
                cost=0.0,
                distance=distance
            )

            edge_ba = Edge(
                to_node=station_a,
                edge_type=EdgeType.WALK,
                line=None,
                time=walk_time,
                cost=0.0,
                distance=distance
            )
            print(
                f"TRANSFER: "
                f"{station_a} <--> {station_b}"
            )
            graph.edges[station_a].append(edge_ab)
            graph.edges[station_b].append(edge_ba)


# ==========================================
# MAIN
# ==========================================

def build_tokyo_graph(
        stations_path: str,
        railway_path: str,
        train_types_path: str,
        groups_path: str
) -> Graph:

    logger.info("Bắt đầu xây dựng đồ thị Tokyo...")

    graph = Graph()

    # ==================================================
    # LOAD NODES
    # ==================================================

    graph.nodes = parse_stations(stations_path)

    # ==================================================
    # LOAD RAW DATA
    # ==================================================

    raw_railway = parse_railway(railway_path)

    raw_train_types = parse_train_types(
        train_types_path
    )

    raw_groups = parse_station_groups(
        groups_path
    )

    # ==================================================
    # BUILD EDGES
    # ==================================================

    _build_train_edges(
        graph,
        raw_railway,
        raw_train_types
    )

    _build_walk_edges(
        graph,
        raw_groups
    )

    # ==================================================
    # CLEAN GRAPH
    # ==================================================

    graph.clean()

    # ==================================================
    # VALIDATE
    # ==================================================

    validation_errors = graph.validate()

    if validation_errors:

        for error in validation_errors:
            logger.warning(
                f"Graph validation error: {error}"
            )

    # ==================================================
    # STATS
    # ==================================================

    total_nodes = len(graph.nodes)

    total_edges = sum(
        len(edges)
        for edges in graph.edges.values()
    )

    logger.info(
        f"Đã xây dựng xong Đồ thị: "
        f"{total_nodes} Nhà ga | "
        f"{total_edges} Đoạn đường."
    )

    return graph