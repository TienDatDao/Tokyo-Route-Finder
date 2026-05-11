"""
Script để lấy danh sách tất cả các ga và tuyến từ dữ liệu raw.
Được gọi bởi admin panel.
"""
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
# Thêm đường dẫn
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_system.core.parsers import parse_stations, parse_railway

RAW_DATA_DIR = str(project_root / "data_system" / "raw_data")

def get_stations_and_lines():
    """Lấy danh sách ga và tuyến"""
    try:
        # Parse stations
        stations_path = Path(RAW_DATA_DIR) / "stations.json"
        stations_data = parse_stations(str(stations_path))
        
        stations_dict = {}
        for node_id, node in stations_data.items():
            stations_dict[node_id] = node.name
        
        # Parse railway để lấy danh sách tuyến
        railway_path = Path(RAW_DATA_DIR) / "railway.json"
        railway_data = parse_railway(str(railway_path))
        
        # railway_data là list của objects, extract 'id' từ mỗi object
        lines = []
        if isinstance(railway_data, list):
            for item in railway_data:
                if isinstance(item, dict) and 'id' in item:
                    lines.append(item['id'])
        elif isinstance(railway_data, dict):
            lines = list(railway_data.keys())
        lines.sort()
        
        result = {
            "stations": stations_dict,
            "lines": lines,
            "total_stations": len(stations_dict),
            "total_lines": len(lines)
        }
        
        # Output JSON directly
        sys.stdout.write(json.dumps(result, ensure_ascii=False))
        sys.stdout.flush()
        
    except Exception as e:
        # Output error as JSON
        error_result = {"error": str(e)}
        sys.stdout.write(json.dumps(error_result, ensure_ascii=False))
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    get_stations_and_lines()

