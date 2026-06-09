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


# =========================================================
# HELPERS
# =========================================================

def get_station_base_name(station_id: str) -> str:
    """
    JR-East.Yamanote.Shibuya
    -> shibuya
    """
    return station_id.split(".")[-1].strip().lower()


def get_line_id(station_id: str) -> str:
    """
    JR-East.Yamanote.Shibuya
    -> JR-East.Yamanote
    """
    parts = station_id.split(".")

    if len(parts) <= 1:
        return station_id

    return ".".join(parts[:-1])


def add_bidirectional_edge(
        graph: Graph,
        node_a: str,
        node_b: str,
        edge_type: EdgeType,
        line: str,
        time: float,
        cost: float,
        distance: float
):
    """
    Add 2-way edge safely
    """

    edge_ab = Edge(
        to_node=node_b,
        edge_type=edge_type,
        line=line,
        time=time,
        cost=cost,
        distance=distance
    )

    edge_ba = Edge(
        to_node=node_a,
        edge_type=edge_type,
        line=line,
        time=time,
        cost=cost,
        distance=distance
    )

    graph.add_edge(node_a, edge_ab)
    graph.add_edge(node_b, edge_ba)


# =========================================================
# TRAIN EDGES
# =========================================================

def _add_edges_for_station_list(
        graph: Graph,
        line_id: str,
        station_list: List[str]
):
    """
    Connect adjacent stations on same railway line
    """

    for i in range(len(station_list) - 1):

        station_a = station_list[i]
        station_b = station_list[i + 1]

        if (
                station_a not in graph.nodes or
                station_b not in graph.nodes
        ):
            continue

        node_a = graph.nodes[station_a]
        node_b = graph.nodes[station_b]

        distance = haversine_distance(
            node_a.lat,
            node_a.lon,
            node_b.lat,
            node_b.lon
        )

        # realistic urban train speed
        time_min = round(
            (distance / config.TRAIN_SPEED_KMH) * 60,
            1
        )

        add_bidirectional_edge(
            graph=graph,
            node_a=station_a,
            node_b=station_b,
            edge_type=EdgeType.TRAIN,
            line=line_id,  # IMPORTANT
            time=time_min,
            cost=round(distance * config.TRAIN_COST_PER_KM),
            distance=distance
        )


def _build_train_edges(
        graph: Graph,
        raw_railway,
        raw_train_types
):
    """
    Build train edges
    """

    if not isinstance(raw_railway, list):
        return

    total_train_edges = 0

    for line_data in raw_railway:

        line_id = line_data.get(
            "id",
            "UnknownLine"
        )

        station_list = line_data.get(
            "stations",
            []
        )

        before = sum(
            len(v)
            for v in graph.edges.values()
        )

        _add_edges_for_station_list(
            graph=graph,
            line_id=line_id,
            station_list=station_list
        )

        after = sum(
            len(v)
            for v in graph.edges.values()
        )

        total_train_edges += (
                after - before
        )

    logger.info(
        f"Built {total_train_edges} train edges"
    )


# =========================================================
# WALK / TRANSFER EDGES
# =========================================================

def _build_walk_edges(
        graph: Graph,
        raw_groups
):
    """
    Build transfer/walk edges
    """

    transfer_edges = 0

    for complex_group in raw_groups:

        all_stations = []

        for fare_zone in complex_group:
            all_stations.extend(fare_zone)

        # =====================================================
        # GROUP BY BASE NAME
        # =====================================================

        grouped = {}

        for station_id in all_stations:

            if station_id not in graph.nodes:
                continue

            base_name = get_station_base_name(
                station_id
            )

            grouped.setdefault(
                base_name,
                []
            ).append(station_id)

        # =====================================================
        # BUILD TRANSFER EDGES
        # =====================================================

        for base_name, station_ids in grouped.items():

            if len(station_ids) < 2:
                continue

            for station_a in station_ids:

                node_a = graph.nodes[station_a]

                candidates = []

                for station_b in station_ids:

                    if station_a == station_b:
                        continue

                    # =========================================
                    # ONLY SAME REAL STATION
                    # =========================================

                    base_a = get_station_base_name(
                        station_a
                    )

                    base_b = get_station_base_name(
                        station_b
                    )

                    if base_a != base_b:
                        continue

                    # =========================================
                    # AVOID SAME LINE
                    # =========================================

                    line_a = get_line_id(station_a)
                    line_b = get_line_id(station_b)

                    if line_a == line_b:
                        continue

                    node_b = graph.nodes[station_b]

                    distance = haversine_distance(
                        node_a.lat,
                        node_a.lon,
                        node_b.lat,
                        node_b.lon
                    )

                    # =========================================
                    # TOO FAR = NOT TRANSFER
                    # =========================================

                    if (
                            distance >
                            config.MAX_TRANSFER_DISTANCE_KM
                    ):
                        continue

                    candidates.append(
                        (
                            distance,
                            station_b
                        )
                    )

                # =============================================
                # NEAREST TRANSFERS ONLY
                # =============================================

                candidates.sort()

                # =====================================================
                # ONLY CONNECT NEAREST STATION PER DIFFERENT LINE
                # =====================================================

                nearest_per_line = {}

                for distance, station_b in candidates:

                    target_line = get_line_id(station_b)

                    if (
                            target_line not in nearest_per_line
                            or distance < nearest_per_line[target_line][0]
                    ):
                        nearest_per_line[target_line] = (
                            distance,
                            station_b
                        )

                # =====================================================
                # BUILD WALK EDGES
                # =====================================================

                for distance, station_b in nearest_per_line.values():
                    is_same_fare_zone = any(
                        (
                                station_a in fz and
                                station_b in fz
                        )
                        for fz in complex_group
                    )

                    # IMPORTANT:
                    # make walking expensive enough
                    base_walk = (
                        6
                        if is_same_fare_zone
                        else 10
                    )

                    walk_time = (
                            base_walk
                            + distance * 20
                    )

                    add_bidirectional_edge(
                        graph=graph,
                        node_a=station_a,
                        node_b=station_b,
                        edge_type=EdgeType.WALK,
                        line="__walk__",
                        time=round(walk_time, 1),
                        cost=0,
                        distance=distance
                    )

                    transfer_edges += 2
# =========================================================
# MAIN
# =========================================================

def build_tokyo_graph(
        stations_path: str,
        railway_path: str,
        train_types_path: str,
        groups_path: str
) -> Graph:

    logger.info(
        "Building Tokyo graph..."
    )

    graph = Graph()

    # =====================================================
    # LOAD DATA
    # =====================================================

    graph.nodes = parse_stations(
        stations_path
    )

    raw_railway = parse_railway(
        railway_path
    )

    raw_train_types = parse_train_types(
        train_types_path
    )

    raw_groups = parse_station_groups(
        groups_path
    )

    # =====================================================
    # BUILD EDGES
    # =====================================================

    _build_train_edges(
        graph,
        raw_railway,
        raw_train_types
    )

    _build_walk_edges(
        graph,
        raw_groups
    )

    # =====================================================
    # CLEAN GRAPH
    # =====================================================

    graph.clean()

    # =====================================================
    # VALIDATE
    # =====================================================

    validation_errors = graph.validate()

    for error in validation_errors:
        logger.warning(error)

    # =====================================================
    # STATS
    # =====================================================

    total_nodes = len(graph.nodes)

    total_edges = sum(
        len(edges)
        for edges in graph.edges.values()
    )

    logger.info(
        f"Tokyo graph built successfully: "
        f"{total_nodes} nodes | "
        f"{total_edges} edges"
    )

    return graph