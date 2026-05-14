"""
Test GraphManager - Kiểm tra xem hệ thống hoạt động đúng không.
"""
import json
import sys
import os
from pathlib import Path

# Add parent directories to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

# Change to project root
os.chdir(str(project_root))

from data_system.core.models import Incident, IncidentType
from data_system.core.graph_manager import GraphManager

CACHE_DIR = str(project_root / "data_system" / "cache")
RAW_DATA_DIR = str(project_root / "data_system" / "raw_data")


def test_graph_manager():
    """Test GraphManager workflow"""
    
    print("\n" + "="*60)
    print("🧪 GraphManager Test Suite")
    print("="*60)
    
    try:
        # 1. Initialize manager
        print("\n1️⃣  Initializing GraphManager...")
        manager = GraphManager(CACHE_DIR)
        print("   ✅ Manager initialized")
        
        # 2. Build original graph
        print("\n2️⃣  Building original graph...")
        original = manager.build_and_save_original(RAW_DATA_DIR)
        print(f"   ✅ Original graph built:")
        print(f"      • Nodes: {len(original.nodes)}")
        print(f"      • Edges: {sum(len(edges) for edges in original.edges.values())}")
        
        # 3. Get original graph
        print("\n3️⃣  Getting original graph from cache...")
        original2 = manager.get_original_graph()
        assert len(original.nodes) == len(original2.nodes), "Original graph mismatch!"
        print("   ✅ Original graph retrieved correctly")
        
        # 4. Apply test incidents
        print("\n4️⃣  Applying test incidents...")
        test_incidents = [
            Incident(
                incident_id="test_1",
                type=IncidentType.STATION_CLOSED,
                target_id="JR-East.Yamanote.Shinjuku"
            ),
            Incident(
                incident_id="test_2",
                type=IncidentType.STATION_CLOSED,
                target_id="Toei.Marunouchi.Roppongi"
            )
        ]
        
        result = manager.apply_and_save_incidents(test_incidents)
        print("   ✅ Incidents applied:")
        print(f"      • Status: {result['status']}")
        print(f"      • Nodes removed: {result['removed_nodes']}")
        print(f"      • Edges removed: {result['removed_edges']}")
        
        # 5. Compare graphs
        print("\n5️⃣  Comparing original vs current...")
        comparison = manager.compare_graphs()
        print("   ✅ Comparison:")
        print(f"      • Original: {comparison['original']['nodes']} nodes, {comparison['original']['edges']} edges")
        print(f"      • Current:  {comparison['current']['nodes']} nodes, {comparison['current']['edges']} edges")
        print(f"      • Removed:  {comparison['difference']['nodes_removed']} nodes, {comparison['difference']['edges_removed']} edges")
        
        # 6. Get current graph
        print("\n6️⃣  Getting current graph...")
        current = manager.get_current_graph()
        print(f"   ✅ Current graph retrieved:")
        print(f"      • Nodes: {len(current.nodes)}")
        print(f"      • Edges: {sum(len(edges) for edges in current.edges.values())}")
        
        # 7. Verify incidents were saved
        print("\n7️⃣  Verifying incidents saved...")
        loaded_incidents = manager.get_current_incidents()
        assert len(loaded_incidents) == 2, "Incidents not saved correctly!"
        print(f"   ✅ {len(loaded_incidents)} incidents loaded from cache")
        
        # 8. Reset to original
        print("\n8️⃣  Resetting to original...")
        reset_result = manager.reset_to_original()
        print(f"   ✅ Reset completed:")
        print(f"      • Status: {reset_result['status']}")
        print(f"      • Nodes: {reset_result['nodes']}")
        print(f"      • Edges: {reset_result['edges']}")
        
        # 9. Verify reset
        print("\n9️⃣  Verifying reset...")
        reset_incidents = manager.get_current_incidents()
        assert len(reset_incidents) == 0, "Incidents not cleared!"
        print("   ✅ Incidents cleared successfully")
        
        # 10. Get graph after reset (should be original)
        print("\n🔟 Getting graph after reset...")
        graph_after_reset = manager.get_current_graph()
        assert len(graph_after_reset.nodes) == len(original.nodes), "Reset failed - graph mismatch!"
        print(f"   ✅ Graph after reset matches original")
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_graph_manager()

