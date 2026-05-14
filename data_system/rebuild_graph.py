"""
Script để rebuild graph từ data_system khi có incidents mới.
Được gọi bởi admin panel sau khi apply incident.
"""
import json
import sys
from pathlib import Path

# Thêm đường dẫn
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_system.core.models import Incident, IncidentType
from data_system.core.graph_manager import GraphManager

CACHE_DIR = str(project_root / "data_system" / "cache")
RAW_DATA_DIR = str(project_root / "data_system" / "raw_data")


def rebuild_graph_with_incidents(incidents_json_str):
    """
    Rebuild graph và lưu cache với incidents hiện tại.
    Được gọi từ admin panel.
    
    Flow:
    1. Parse incidents từ JSON
    2. Apply incidents vào original graph
    3. So sánh và validate
    4. Lưu vào cache
    """
    try:
        # Parse incidents từ JSON string
        incidents_list = []
        if incidents_json_str and incidents_json_str.strip() and incidents_json_str.strip() != '[]':
            incidents_data = json.loads(incidents_json_str)
            if incidents_data:  # kiểm tra rõ ràng nếu list không rỗng
                for inc_data in incidents_data:
                    incident = Incident(
                        incident_id=inc_data.get("incident_id", ""),
                        type=IncidentType(inc_data.get("type", "STATION_CLOSED")),
                        target_id=inc_data.get("target_id", "")
                    )
                    incidents_list.append(incident)
        
        print(f"[DEBUG] Parsed {len(incidents_list)} incidents from JSON", file=sys.stderr)
        
        # Tạo graph manager
        manager = GraphManager(CACHE_DIR)

        # Nếu chưa có original graph, build từ raw data
        if not manager.original_graph:
            print("[DEBUG] Original graph not found, building from raw data...", file=sys.stderr)
            manager.build_and_save_original(RAW_DATA_DIR)

        # Áp dụng incidents (hoặc reset nếu không có incidents)
        if incidents_list:

            result = manager.apply_and_save_incidents(
                incidents_list,
                RAW_DATA_DIR
            )

        else:

            print(
                "[DEBUG] No incidents - resetting to original",
                file=sys.stderr
            )

            result = manager.reset_to_original(
                RAW_DATA_DIR
            )

        # So sánh original vs current
        comparison = manager.compare_graphs()

        # Thêm comparison vào result
        result["comparison"] = comparison

        # Output JSON
        # Output JSON
        print(json.dumps(
            result,
            ensure_ascii=False,
            default=lambda o: (
                o.value if hasattr(o, "value")
                else o.__dict__
            )
        ))
        
    except json.JSONDecodeError as e:
        error_result = {
            "status": "ERROR",
            "message": f"JSON parse error: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_result = {
            "status": "ERROR",
            "message": f"Error rebuilding graph: {str(e)}",
            "type": type(e).__name__
        }
        print(json.dumps(error_result, ensure_ascii=False), file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Lấy JSON string từ command line argument
    incidents_json = sys.argv[1] if len(sys.argv) > 1 else "[]"
    rebuild_graph_with_incidents(incidents_json)

