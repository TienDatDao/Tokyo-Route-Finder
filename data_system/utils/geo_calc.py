import math
from typing import List, Tuple, Optional
from ..core.models import Node

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách Haversine giữa 2 điểm (km).
    """
    R = 6371.0  # Bán kính Trái Đất (km)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def find_nearest_station(lat: float, lon: float, nodes: dict[str, Node]) -> Optional[Tuple[str, float]]:
    """
    Tìm ga gần nhất với tọa độ (lat, lon) từ dict nodes.
    Trả về (station_id, distance_km) hoặc None nếu không có nodes.
    """
    if not nodes:
        return None

    nearest_id = None
    min_distance = float('inf')

    for station_id, node in nodes.items():
        dist = haversine_distance(lat, lon, node.lat, node.lon)
        if dist < min_distance:
            min_distance = dist
            nearest_id = station_id

    return (nearest_id, min_distance) if nearest_id else None
