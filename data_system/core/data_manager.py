import os
import pickle
from typing import Optional, List

from data_system.core.models import Graph, Incident
from data_system.core.graph_builder import build_tokyo_graph
from data_system.core.incident_manager import apply_incidents

# Đường dẫn lưu file Cache nhị phân
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "tokyo_graph.pkl")

# Biến RAM để lưu đồ thị (Singleton)
_IN_MEMORY_GRAPH: Optional[Graph] = None


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def force_rebuild_and_cache(raw_dir: str) -> Graph:
    """
    Hàm này CHỈ ĐƯỢC GỌI khi Admin Panel yêu cầu cập nhật bản đồ gốc.
    Nó sẽ đọc lại 4 file JSON, tính toán lại toàn bộ và lưu ra file .pkl
    """
    global _IN_MEMORY_GRAPH

    p_stations = os.path.join(raw_dir, "stations.json")
    p_railway = os.path.join(raw_dir, "railway.json")
    p_train_types = os.path.join(raw_dir, "train_types.json")
    p_groups = os.path.join(raw_dir, "station_groups.json")

    # 1. Build đồ thị mới
    new_graph = build_tokyo_graph(p_stations, p_railway, p_train_types, p_groups)

    # 2. Lưu xuống ổ cứng (Pickle)
    _ensure_cache_dir()
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(new_graph, f)


    # 3. Cập nhật lại RAM
    _IN_MEMORY_GRAPH = new_graph
    return new_graph


def get_clean_graph(raw_dir: str, incidents: Optional[List[Incident]] = None) -> Graph:
    """
    Hàm này được Backend gọi mỗi khi cần lấy Đồ thị.
    Ưu tiên 1: Lấy từ RAM
    Ưu tiên 2: Lấy từ file .pkl
    Ưu tiên 3: Build lại từ JSON (chỉ dùng lần chạy đầu tiên)
    Nếu có incidents, áp dụng filter vào graph.
    """
    global _IN_MEMORY_GRAPH

    # 1. NẾU ĐÃ CÓ TRÊN RAM -> TRẢ VỀ LUÔN
    if _IN_MEMORY_GRAPH is not None:
        graph = _IN_MEMORY_GRAPH
    # 2. NẾU CÓ FILE CACHE TRÊN Ổ CỨNG -> ĐỌC LÊN RAM
    elif os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            graph = pickle.load(f)
        _IN_MEMORY_GRAPH = graph
    # 3. CHƯA CÓ GÌ CẢ (CHẠY LẦN ĐẦU) -> BUILD TỪ ĐẦU VÀ LƯU CACHE
    else:
        graph = force_rebuild_and_cache(raw_dir)

    # Áp dụng incidents nếu có
    if incidents:
        graph = apply_incidents(graph, incidents)

    return graph


def get_node_ids_by_name(graph, station_name):
    if graph is None or not station_name:
        return []

    lookup = station_name.strip().lower()
    exact_matches = [node_id for node_id, node in graph.nodes.items() if node.name.strip().lower() == lookup]
    if exact_matches:
        return exact_matches

    partial_matches = [node_id for node_id, node in graph.nodes.items() if lookup in node.name.strip().lower()]
    return partial_matches
