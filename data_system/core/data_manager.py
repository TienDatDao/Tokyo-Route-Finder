import os
import pickle
import json
from typing import Optional, List

from data_system.core.models import Graph, Incident, IncidentType
from data_system.core.graph_builder import build_tokyo_graph
from data_system.core.incident_manager import apply_incidents

# Đường dẫn lưu file Cache nhị phân
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "tokyo_graph.pkl")
INCIDENTS_CACHE_FILE = os.path.join(CACHE_DIR, "incidents.json")

# Biến RAM để lưu đồ thị (Singleton)
_IN_MEMORY_GRAPH: Optional[Graph] = None
_IN_MEMORY_INCIDENTS: List[Incident] = []


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def save_incidents_to_cache(incidents: List[Incident]) -> None:
    """
    Lưu danh sách incidents vào file cache.
    Được gọi khi admin panel apply incidents mới.
    """
    global _IN_MEMORY_INCIDENTS
    _ensure_cache_dir()
    
    incidents_data = []
    for incident in incidents:
        incidents_data.append({
            "incident_id": incident.incident_id,
            "type": incident.type.value,
            "target_id": incident.target_id
        })
    
    with open(INCIDENTS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(incidents_data, f, ensure_ascii=False, indent=2)
    
    _IN_MEMORY_INCIDENTS = incidents
    
    # Clear graph cache để đảm bảo lần sau áp dụng incidents mới
    clear_graph_cache()


def load_incidents_from_cache() -> List[Incident]:
    """
    Tải danh sách incidents từ file cache.
    Được gọi tự động khi get_clean_graph() và incidents chưa được load.
    """
    global _IN_MEMORY_INCIDENTS
    
    if _IN_MEMORY_INCIDENTS:
        return _IN_MEMORY_INCIDENTS
    
    if not os.path.exists(INCIDENTS_CACHE_FILE):
        return []
    
    try:
        with open(INCIDENTS_CACHE_FILE, 'r', encoding='utf-8') as f:
            incidents_data = json.load(f)
        
        incidents = []
        for inc_data in incidents_data:
            incident = Incident(
                incident_id=inc_data.get("incident_id", ""),
                type=IncidentType(inc_data.get("type", "STATION_CLOSED")),
                target_id=inc_data.get("target_id", "")
            )
            incidents.append(incident)
        
        _IN_MEMORY_INCIDENTS = incidents
        return incidents
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️  Lỗi tải incidents cache: {str(e)}")
        return []


def clear_incidents_cache() -> None:
    """
    Xóa toàn bộ incidents từ cache.
    Được gọi khi reset hệ thống.
    """
    global _IN_MEMORY_INCIDENTS
    _IN_MEMORY_INCIDENTS = []
    if os.path.exists(INCIDENTS_CACHE_FILE):
        os.remove(INCIDENTS_CACHE_FILE)


def clear_graph_cache() -> None:
    """
    Xóa đồ thị từ RAM cache.
    Được gọi khi incidents thay đổi để đảm bảo lần sau load lại graph mới.
    """
    global _IN_MEMORY_GRAPH
    _IN_MEMORY_GRAPH = None


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
    
    🔧 QUAN TRỌNG: Tự động tải incidents từ cache và áp dụng!
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

    # ✅ 🔧 TỪ ĐÂY LÀ PHẦN QUAN TRỌNG: Áp dụng incidents
    # Nếu không được truyền vào, tự động tải từ cache
    if incidents is None:
        incidents = load_incidents_from_cache()
    
    # Áp dụng incidents vào graph
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
