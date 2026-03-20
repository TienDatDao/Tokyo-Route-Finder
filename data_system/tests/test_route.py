import os
import sys
import networkx as nx
import json

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình đường dẫn tự động
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_SYSTEM_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(DATA_SYSTEM_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from data_system.core.models import Graph, Incident, IncidentType
from data_system.core.incident_manager import apply_incidents
from data_system.core.data_manager import get_clean_graph

class TestRouteWithIncidents:
    def __init__(self, raw_dir: str):
        self.raw_dir = raw_dir
        self.start_station = "JR-East.Joetsu.Minakami"
        self.end_station = "JR-East.Ryomo.Maebashi"

    def _build_networkx_graph(self, graph: Graph):
        """Chuyển Graph sang NetworkX để tính shortest path."""
        G = nx.DiGraph()
        for node_id, node in graph.nodes.items():
            G.add_node(node_id)
        for start_id, edges in graph.edges.items():
            for edge in edges:
                G.add_edge(start_id, edge.to_node, weight=edge.time)  # Sử dụng time làm weight
        return G

    def _calculate_route(self, graph: Graph):
        """Tính shortest path từ start đến end."""
        G = self._build_networkx_graph(graph)
        if self.start_station not in G or self.end_station not in G:
            return None, float('inf')
        try:
            path = nx.shortest_path(G, source=self.start_station, target=self.end_station, weight='weight')
            total_time = nx.shortest_path_length(G, source=self.start_station, target=self.end_station, weight='weight')
            return path, total_time
        except nx.NetworkXNoPath:
            return None, float('inf')

    def test_route_before_and_after_incidents(self, incidents: list[Incident]):
        """Test và in ra route trước và sau incidents."""
        print("BAT DAU TEST TUYEN DUONG VOI INCIDENTS")
        print(f"Tu: {self.start_station} -> Den: {self.end_station}")
        print("-" * 50)

        # Lấy graph gốc
        original_graph = get_clean_graph(self.raw_dir)
        path_before, time_before = self._calculate_route(original_graph)

        print("TRUOC KHI AP DUNG INCIDENTS:")
        if path_before:
            print(f"  Tuyen duong: {' -> '.join(path_before)}")
            print(f"  Tong thoi gian: {time_before:.1f} phut")
        else:
            print("  Khong tim thay duong di!")

        # Áp dụng incidents
        filtered_graph = get_clean_graph(self.raw_dir, incidents=incidents)
        path_after, time_after = self._calculate_route(filtered_graph)

        print("\nSAU KHI AP DUNG INCIDENTS:")
        if path_after:
            print(f"  Tuyen duong: {' -> '.join(path_after)}")
            print(f"  Tong thoi gian: {time_after:.1f} phut")
        else:
            print("  Khong tim thay duong di!")

        # Mở lại: loại bỏ incidents và test lại
        reopened_graph = get_clean_graph(self.raw_dir, incidents=[])  # Không áp dụng incidents
        path_reopen, time_reopen = self._calculate_route(reopened_graph)

        print("\nSAU KHI MO LAI (LOAI BO INCIDENTS):")
        if path_reopen:
            print(f"  Tuyen duong: {' -> '.join(path_reopen)}")
            print(f"  Tong thoi gian: {time_reopen:.1f} phut")
        else:
            print("  Khong tim thay duong di!")

        print("-" * 50)
        print("HOAN THANH TEST")

if __name__ == "__main__":
    # Nhận arguments từ command line
    raw_dir = os.path.join(DATA_SYSTEM_DIR, "raw_data")
    
    # Lấy start/end stations từ arguments (app.js sẽ pass)
    if len(sys.argv) > 1:
        start_station = sys.argv[1]
    else:
        start_station = "JR-East.Joetsu.Minakami"
    
    if len(sys.argv) > 2:
        end_station = sys.argv[2]
    else:
        end_station = "JR-East.Ryomo.Maebashi"
    
    # Nhận incidents từ argument
    incidents_json = sys.argv[3] if len(sys.argv) > 3 else '[]'
    try:
        incidents_data = json.loads(incidents_json)
    except json.JSONDecodeError as e:
        print(f"LOI: JSON khong hop le: {e}")
        print("Vui long nhap JSON dung dinh dang.")
        sys.exit(1)

    # Chuyển thành list Incident
    incidents = []
    for item in incidents_data:
        try:
            incident_type = IncidentType[item['type']]
            incidents.append(Incident(
                incident_id=item['incident_id'],
                type=incident_type,
                target_id=item['target_id']
            ))
        except KeyError as e:
            print(f"LOI: Thieu key trong incident: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"LOI: Gia tri khong hop le: {e}")
            sys.exit(1)

    # Tạo tester với custom stations
    tester = TestRouteWithIncidents(raw_dir)
    tester.start_station = start_station
    tester.end_station = end_station
    tester.test_route_before_and_after_incidents(incidents)
