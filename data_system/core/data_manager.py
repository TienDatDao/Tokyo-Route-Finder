import os
import pickle
import gzip
import threading
from typing import Optional, List

from data_system.core.models import Graph, Incident
from data_system.core.graph_builder import build_tokyo_graph
from data_system.core.incident_manager import apply_incidents
from data_system.utils.logger import logger

# Đường dẫn lưu file Cache nhị phân (nén gzip)
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "tokyo_graph.pkl.gz")

# Biến RAM để lưu đồ thị (Singleton)
_IN_MEMORY_GRAPH: Optional[Graph] = None
# Lock để thread-safe
_CACHE_LOCK = threading.Lock()


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def force_rebuild_and_cache(raw_dir: str) -> Graph:
    """
    Hàm này CHỈ ĐƯỢC GỌI khi Admin Panel yêu cầu cập nhật bản đồ gốc.
    Nó sẽ đọc lại 4 file JSON, tính toán lại toàn bộ và lưu ra file .pkl.gz
    """
    global _IN_MEMORY_GRAPH

    logger.info("Bắt đầu rebuild và cache đồ thị từ dữ liệu thô...")

    p_stations = os.path.join(raw_dir, "stations.json")
    p_railway = os.path.join(raw_dir, "railway.json")
    p_train_types = os.path.join(raw_dir, "train_types.json")
    p_groups = os.path.join(raw_dir, "station_groups.json")

    # 1. Build đồ thị mới
    new_graph = build_tokyo_graph(p_stations, p_railway, p_train_types, p_groups)

    # 2. Lưu xuống ổ cứng (Pickle nén gzip)
    _ensure_cache_dir()
    try:
        with gzip.open(CACHE_FILE, 'wb') as f:
            pickle.dump(new_graph, f)
        logger.info(f"Đã lưu cache đồ thị vào {CACHE_FILE} (nén gzip)")
    except Exception as e:
        logger.error(f"Lỗi khi lưu cache: {e}")
        raise

    # 3. Cập nhật lại RAM
    _IN_MEMORY_GRAPH = new_graph
    logger.info(f"Đồ thị đã load vào RAM: {len(new_graph.nodes)} nodes, {sum(len(edges) for edges in new_graph.edges.values())} edges")
    return new_graph


def get_clean_graph(raw_dir: str, incidents: Optional[List[Incident]] = None) -> Graph:
    """
    Hàm này được Backend gọi mỗi khi cần lấy Đồ thị.
    Ưu tiên 1: Lấy từ RAM
    Ưu tiên 2: Lấy từ file .pkl.gz
    Ưu tiên 3: Build lại từ JSON (chỉ dùng lần chạy đầu tiên)
    Nếu có incidents, áp dụng filter vào graph.
    """
    global _IN_MEMORY_GRAPH

    # 1. NẾU ĐÃ CÓ TRÊN RAM -> TRẢ VỀ LUÔN
    if _IN_MEMORY_GRAPH is not None:
        logger.debug("Lấy đồ thị từ RAM cache")
        graph = _IN_MEMORY_GRAPH
    # 2. NẾU CÓ FILE CACHE TRÊN Ổ CỨNG -> ĐỌC LÊN RAM
    elif os.path.exists(CACHE_FILE):
        try:
            with gzip.open(CACHE_FILE, 'rb') as f:
                graph = pickle.load(f)
            _IN_MEMORY_GRAPH = graph
            logger.info(f"Đã load đồ thị từ cache disk: {len(graph.nodes)} nodes")
        except Exception as e:
            logger.error(f"Lỗi khi load cache từ disk: {e}. Sẽ rebuild...")
            graph = force_rebuild_and_cache(raw_dir)
    # 3. CHƯA CÓ GÌ CẢ (CHẠY LẦN ĐẦU) -> BUILD TỪ ĐẦU VÀ LƯU CACHE
    else:
        logger.info("Không có cache, bắt đầu build đồ thị từ đầu...")
        graph = force_rebuild_and_cache(raw_dir)

    # Áp dụng incidents nếu có
    if incidents:
        logger.debug(f"Áp dụng {len(incidents)} incidents vào đồ thị")
        graph = apply_incidents(graph, incidents)

    return graph
