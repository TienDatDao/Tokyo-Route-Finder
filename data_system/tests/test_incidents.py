# Giả lập sự cố xem đồ thị có cập nhật trọng số linh tinh không, có thể xảy ra vô cùng
import unittest
import os
import sys

# Cấu hình đường dẫn tự động
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_SYSTEM_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(DATA_SYSTEM_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from data_system.core.models import Graph, Node, Edge, EdgeType, Incident, IncidentType
from data_system.core.incident_manager import apply_incidents
from data_system.core.graph_builder import build_tokyo_graph

class TestIncidentApplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RAW_DIR = os.path.join(DATA_SYSTEM_DIR, "raw_data")
        p_stations = os.path.join(RAW_DIR, "stations.json")
        p_railway = os.path.join(RAW_DIR, "railway.json")
        p_train_types = os.path.join(RAW_DIR, "train_types.json")
        p_groups = os.path.join(RAW_DIR, "station_groups.json")

        if not all(os.path.exists(p) for p in [p_stations, p_railway, p_train_types, p_groups]):
            raise FileNotFoundError("Missing raw data files")

        cls.graph = build_tokyo_graph(p_stations, p_railway, p_train_types, p_groups)

    def test_station_closed_removes_node_and_edges(self):
        """Test that STATION_CLOSED removes the node and all related edges."""
        original_nodes = len(self.graph.nodes)
        original_edges = sum(len(edges) for edges in self.graph.edges.values())

        # Close a station
        incident = Incident(incident_id="test1", type=IncidentType.STATION_CLOSED, target_id="JR-East.Yamanote.Shinjuku")
        filtered_graph = apply_incidents(self.graph, [incident])

        # Check node removed
        self.assertNotIn("JR-East.Yamanote.Shinjuku", filtered_graph.nodes)
        self.assertEqual(len(filtered_graph.nodes), original_nodes - 1)

        # Check edges removed (should be less edges)
        filtered_edges_count = sum(len(edges) for edges in filtered_graph.edges.values())
        self.assertLess(filtered_edges_count, original_edges)

    def test_line_maintenance_removes_edges(self):
        """Test that LINE_MAINTENANCE removes edges for the line."""
        # Find a line with edges
        target_line = "Yamanote Line"
        original_edges = sum(len(edges) for edges in self.graph.edges.values())

        incident = Incident(incident_id="test2", type=IncidentType.LINE_MAINTENANCE, target_id=target_line)
        filtered_graph = apply_incidents(self.graph, [incident])

        # Check that some edges are removed
        filtered_edges_count = sum(len(edges) for edges in filtered_graph.edges.values())
        self.assertLess(filtered_edges_count, original_edges)

        # Check no edges with that line remain
        for edges in filtered_graph.edges.values():
            for edge in edges:
                self.assertNotEqual(edge.line, target_line)

    def test_multiple_incidents(self):
        """Test applying multiple incidents."""
        incidents = [
            Incident(incident_id="test3", type=IncidentType.STATION_CLOSED, target_id="JR-East.Yamanote.Shinjuku"),
            Incident(incident_id="test4", type=IncidentType.LINE_MAINTENANCE, target_id="Yamanote Line")
        ]
        filtered_graph = apply_incidents(self.graph, incidents)

        # Node removed
        self.assertNotIn("JR-East.Yamanote.Shinjuku", filtered_graph.nodes)
        # No edges with the line
        for edges in filtered_graph.edges.values():
            for edge in edges:
                self.assertNotEqual(edge.line, "Yamanote Line")

    def test_no_incidents_returns_copy(self):
        """Test that no incidents return a copy of the graph."""
        filtered_graph = apply_incidents(self.graph, [])
        self.assertEqual(len(filtered_graph.nodes), len(self.graph.nodes))
        self.assertEqual(sum(len(edges) for edges in filtered_graph.edges.values()), sum(len(edges) for edges in self.graph.edges.values()))

if __name__ == '__main__':
    unittest.main()
