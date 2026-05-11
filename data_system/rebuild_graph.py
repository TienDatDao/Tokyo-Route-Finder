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
from data_system.core import data_manager as dm

RAW_DATA_DIR = str(project_root / "data_system" / "raw_data")

def rebuild_graph_with_incidents(incidents_json_str):
    """
    Rebuild graph và lưu cache với incidents hiện tại.
    Được gọi từ admin panel.
    
    🔧 QUAN TRỌNG: Sau khi áp dụng incidents, LƯU VÀO CACHE!
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
        
        # Force rebuild graph
        graph = dm.force_rebuild_and_cache(RAW_DATA_DIR)
        
        # Áp dụng incidents
        if incidents_list:
            from data_system.core.incident_manager import apply_incidents
            graph = apply_incidents(graph, incidents_list)
            print(f"[DEBUG] Applied {len(incidents_list)} incidents to graph", file=sys.stderr)
        else:
            print("[DEBUG] No incidents to apply - using clean graph", file=sys.stderr)
        
        # ✅ 🔧 QUAN TRỌNG: Lưu incidents vào cache file
        dm.save_incidents_to_cache(incidents_list)
        print(f"[DEBUG] Saved {len(incidents_list)} incidents to cache", file=sys.stderr)
        
        # Validate graph
        errors = graph.validate()
        
        result = {
            "status": "SUCCESS",
            "message": f"Graph rebuilt with {len(incidents_list)} incidents",
            "graph_nodes": len(graph.nodes),
            "graph_edges": sum(len(edges) for edges in graph.edges.values()),
            "validation_errors": errors if errors else [],
            "incidents_applied": [
                {"id": inc.incident_id, "type": inc.type.value, "target": inc.target_id}
                for inc in incidents_list
            ]
        }
        
        print(json.dumps(result, ensure_ascii=False))
        
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
            "message": f"Error rebuilding graph: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Lấy JSON string từ command line argument
    incidents_json = sys.argv[1] if len(sys.argv) > 1 else "[]"
    rebuild_graph_with_incidents(incidents_json)



