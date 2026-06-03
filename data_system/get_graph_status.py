"""
Get current graph status - compare original vs current with incidents.
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_system.core.graph_manager import GraphManager

CACHE_DIR = str(project_root / "data_system" / "cache")


def get_graph_status():
    """
    Lấy thông tin trạng thái graph hiện tại.
    """
    try:
        manager = GraphManager(CACHE_DIR)
        
        # So sánh original vs current
        comparison = manager.compare_graphs()
        
        result = {
            "status": "SUCCESS",
            "graph_status": {
                "original": comparison["original"],
                "current": comparison["current"],
                "difference": comparison["difference"]
            },
            "incidents": [
                {
                    "incident_id": inc.incident_id,
                    "type": inc.type.value,
                    "target_id": inc.target_id
                }
                for inc in comparison["incidents"]
            ],
            "cache_status": {
                "has_original": manager.original_graph is not None or Path(manager.original_graph_file).exists(),
                "has_current": manager.current_graph is not None or Path(manager.current_graph_file).exists(),
                "has_incidents": len(comparison["incidents"]) > 0
            }
        }
        
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            "status": "ERROR",
            "message": f"Error getting graph status: {str(e)}",
            "type": type(e).__name__
        }
        print(json.dumps(error_result, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    get_graph_status()

