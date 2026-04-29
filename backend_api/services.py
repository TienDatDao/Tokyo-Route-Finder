import config
from pathlib import Path
import os
import sys

# Thêm thư mục gốc dự án vào đường dẫn tìm kiếm module
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import data_system.core.data_manager as dm
import ai_engine.router as ai

RAW_DATA_PATH = project_root / config.DATA_RAW_DIR
VALID_CRITERIA = {"shortest_time", "lowest_cost", "least_transfers"}


def _build_search_graph(graph):
    search_graph = {}

    for node_id, node in graph.nodes.items():
        search_graph[node_id] = {
            "metadata": {
                "name": node.name,
                "lat": node.lat,
                "lon": node.lon
            },
            "connections": {}
        }

    for from_node, edges in graph.edges.items():
        for edge in edges:
            if from_node not in search_graph or edge.to_node not in search_graph:
                continue
            search_graph[from_node]["connections"][edge.to_node] = {
                "line": edge.line or "walk",
                "time": edge.time,
                "cost": edge.cost
            }

    return search_graph


def handle_find_route(payload):
    start_name = payload.get("startName") or payload.get("start_name") or payload.get("start_station")
    end_name = payload.get("endName") or payload.get("end_name") or payload.get("end_station")
    criteria = payload.get("criteria") or payload.get("priority") or "shortest_time"
    criteria = criteria if criteria in VALID_CRITERIA else "shortest_time"

    if not start_name or not end_name:
        return {
            "status": "ERROR",
            "message": "Vui lòng cung cấp ga xuất phát và ga đích."
        }

    graph = dm.get_clean_graph(str(RAW_DATA_PATH))
    start_nodes = dm.get_node_ids_by_name(graph, start_name)
    end_nodes = dm.get_node_ids_by_name(graph, end_name)

    if not start_nodes or not end_nodes:
        return {
            "status": "ERROR",
            "message": "Không tìm thấy ga bắt đầu hoặc ga kết thúc."
        }

    search_graph = _build_search_graph(graph)
    ai_result = ai.find_optimal_route(search_graph, start_nodes, end_nodes, criteria)

    if ai_result.get("status") != "SUCCESS":
        return {
            "status": "ERROR",
            "message": "Không tìm thấy tuyến đường phù hợp giữa hai ga."
        }

    path_coords = []
    for station_id in ai_result["route"]["path"]:
        node = graph.nodes.get(station_id)
        if node:
            path_coords.append([node.lat, node.lon])

    return {
        "status": "SUCCESS",
        "route": {
            "path": ai_result["route"]["path"],
            "pathCoords": path_coords,
            "total_time": ai_result["route"]["total_time"],
            "total_cost": ai_result["route"]["total_cost"],
            "transfers": ai_result["route"]["transfers"],
            "details": ai_result["route"]["details"]
        }
    }
