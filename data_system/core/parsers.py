# Đọc và bóc tách dữ liệu từ các file raw_data
import json
import os
from typing import Dict, List, Any

from .models import Node
from ..utils.logger import logger

def load_json(file_path: str) -> Any:
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError
    try:
        with (open(file_path, 'r', encoding="utf-8") as f):
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error((f"File {file_path} is error formating: {e}"))
        raise ValueError(f"Invalid file path: {file_path}")


def parse_stations(file_path: str) -> Dict[str, Node]:
    raw_data = load_json(file_path)
    nodes: Dict[str, Node] = {}

    # ĐỌC DỮ LIỆU
    if isinstance(raw_data, list):
        for data in raw_data:
            try:
                station_id = data.get("id")
                if not station_id:
                    continue

                # Bóc tách tên ga (Ưu tiên tiếng Anh, nếu không có lấy tiếng Nhật)
                title = data.get("title", {})
                name = title.get("en", title.get("ja", "Unknown"))

                # Bóc tách tọa độ ([Kinh độ, Vĩ độ])
                coord = data.get("coord")
                if not coord or len(coord) < 2:
                    logger.warning(f"Bỏ qua nhà ga {station_id} vì thiếu tọa độ.")
                    continue

                lon, lat = float(coord[0]), float(coord[1])

                nodes[station_id] = Node(id=station_id, name=name, lat=lat, lon=lon)
            except Exception as e:
                logger.warning(f"Lỗi đọc ga {data.get('id')}: {e}")
                continue
    logger.info(f"Đã nạp thành công {len(nodes)} nhà ga vào bộ nhớ.")
    return nodes

def parse_railway(file_path: str) -> Dict[str, Any]:
    return load_json(file_path)

def parse_train_types(file_path: str) -> Dict[str, Any]:
    return load_json(file_path)

def parse_station_groups(file_path: str) -> List[List[List[str]]]:
    raw_groups = load_json(file_path)
    return raw_groups
