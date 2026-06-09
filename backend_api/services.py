import config
from pathlib import Path
import os
import sys

# Thêm thư mục gốc dự án vào đường dẫn tìm kiếm module
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data_system.core.graph_manager import GraphManager
import ai_engine.router as ai

RAW_DATA_PATH = project_root / config.DATA_RAW_DIR
CACHE_DIR = project_root / "data_system" / "cache"
VALID_CRITERIA = {"shortest_time", "lowest_cost", "least_transfers"}

# Singleton instance của GraphManager

def _get_graph_manager():
    manager = GraphManager(str(CACHE_DIR))
    # Ensure manager có raw data path để auto-build nếu cần
    manager.set_raw_data_path(str(RAW_DATA_PATH))
    return manager


def _build_search_graph(graph):
    search_graph = {}

    for node_id, node in graph.nodes.items():
        search_graph[node_id] = {
            "metadata": {
                "name": node.name,
                "lat": node.lat,
                "lon": node.lon
            },
            "connections": []
        }

    for from_node, edges in graph.edges.items():
        for edge in edges:
            if from_node not in search_graph or edge.to_node not in search_graph:
                continue
            search_graph[from_node]["connections"].append({
                "to": edge.to_node,
                "line": edge.line or "walk",
                "time": edge.time,
                "cost": edge.cost
            })
            if from_node == "JR-East.Yamanote.Shibuya":
                print(search_graph[from_node]["connections"][:5])

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

    # Get current graph (with incidents applied if any)
    manager = _get_graph_manager()
    graph = manager.get_current_graph()
    
    # Helper function to find nodes by name
    def get_node_ids_by_name(g, station_name):
        if not station_name:
            return []
        lookup = station_name.strip().lower()
        exact_matches = [node_id for node_id, node in g.nodes.items() if node.name.strip().lower() == lookup]
        if exact_matches:
            return exact_matches
        partial_matches = [node_id for node_id, node in g.nodes.items() if lookup in node.name.strip().lower()]
        return partial_matches
    
    start_nodes = get_node_ids_by_name(graph, start_name)
    end_nodes = get_node_ids_by_name(graph, end_name)

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
        else:
            print(f"Warning: Station {station_id} not found in graph nodes")

    print(f"Generated {len(path_coords)} coordinates for path")

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


def get_filtered_stations(raw_dir: str):
    """
    Trả về danh sách stations đã loại trừ những ga bị đóng cửa.
    """
    manager = _get_graph_manager()
    graph = manager.get_current_graph()
    stations = []
    for node_id, node in graph.nodes.items():
        stations.append({
            "id": node_id,
            "name": node.name,
            "coord": [node.lon, node.lat],  # Note: coord is [lon, lat]
            "title": {
                "en": node.name
            }
        })
    return stations
