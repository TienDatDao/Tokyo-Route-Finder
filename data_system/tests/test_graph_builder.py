import unittest
import os
import sys
import random
from collections import Counter



# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_SYSTEM_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(DATA_SYSTEM_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ==========================================
# 2. BÂY GIỜ MỚI IMPORT CÁC MODULE CỦA PROJECT
# ==========================================
from data_system.core.graph_builder import build_tokyo_graph
from data_system.core.models import EdgeType

#==========================================
# CẤU HÌNH MỨC ĐỘ TEST
# ==========================================
# 1.0 = Quét 100% dữ liệu (Chậm nhưng cực kỳ an toàn)
# 0.3 = Quét ngẫu nhiên 30% dữ liệu (Nhanh, dùng khi đang code dở)
TEST_COVERAGE = 0.3


class TestGraphBuilderRealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RAW_DIR = os.path.join(DATA_SYSTEM_DIR, "raw_data")

        p_stations = os.path.join(RAW_DIR, "stations.json")
        p_railway = os.path.join(RAW_DIR, "railway.json")
        p_train_types = os.path.join(RAW_DIR, "train_types.json")
        p_groups = os.path.join(RAW_DIR, "station_groups.json")

        if not all(os.path.exists(p) for p in [p_stations, p_railway, p_train_types, p_groups]):
            raise FileNotFoundError()

        cls.graph = build_tokyo_graph(p_stations, p_railway, p_train_types, p_groups)
        cls.all_nodes = list(cls.graph.nodes.keys())

    def _get_sample_nodes(self):
        """Hàm lấy ra số lượng ga cần test dựa trên TEST_COVERAGE"""
        sample_size = int(len(self.all_nodes) * TEST_COVERAGE)
        return random.sample(self.all_nodes, sample_size)

    # ==========================================
    # CÁC KỊCH BẢN KIỂM THỬ TRÊN DỮ LIỆU THẬT
    # ==========================================

    def test_01_no_multi_graph_bug(self):
        """
        CHẶN LỖI ĐA ĐỒ THỊ (MULTI-GRAPH):
        Đảm bảo giữa 2 ga KHÔNG có 2 đường đi trùng lặp y hệt nhau
        (Cùng đích đến, cùng loại hình, cùng tuyến).
        """
        nodes_to_test = self._get_sample_nodes()

        for node_id in nodes_to_test:
            edges = self.graph.edges.get(node_id, [])

            # Tạo một "chữ ký" (Signature) cho mỗi con đường
            # Chữ ký gồm: (Ga_Đích, Loại_Đường, Tên_Tuyến)
            edge_signatures = [(e.to_node, e.edge_type, e.line) for e in edges]

            # Đếm xem có chữ ký nào xuất hiện nhiều hơn 1 lần không
            signature_counts = Counter(edge_signatures)

            for signature, count in signature_counts.items():
                self.assertLessEqual(
                    count, 1,
                    msg=f"LỖI MULTI-GRAPH TẠI GA {node_id}: Đang có {count} đường đi trùng lặp đến {signature[0]} qua tuyến {signature[2]}"
                )

    def test_02_edges_are_bidirectional(self):
        """Đảm bảo mọi con đường đều có 2 chiều (Undirected). Có đi là có lại."""
        nodes_to_test = self._get_sample_nodes()

        for node_a in nodes_to_test:
            edges_from_a = self.graph.edges.get(node_a, [])

            for edge in edges_from_a:
                node_b = edge.to_node
                edges_from_b = self.graph.edges.get(node_b, [])

                # Tìm xem từ B có đường nào vòng ngược lại A với cùng loại/tuyến không
                path_back = [
                    e for e in edges_from_b
                    if e.to_node == node_a and e.edge_type == edge.edge_type and e.line == edge.line
                ]

                self.assertGreater(
                    len(path_back), 0,
                    msg=f"LỖI ĐƯỜNG 1 CHIỀU: Có đường từ {node_a} đến {node_b} nhưng không có đường ngược lại!"
                )

    def test_03_orphan_nodes_warning(self):
        orphan_count = 0
        orphan_list = []

        for node_id in self.all_nodes:
            if node_id not in self.graph.edges or len(self.graph.edges[node_id]) == 0:
                orphan_count += 1
                orphan_list.append(node_id)

    def test_04_print_graph_sample(self):
        """
        IN RA TERMINAL MỘT MẪU DỮ LIỆU ĐỒ THỊ THỰC TẾ.
        Giúp kỹ sư soi bằng mắt xem AI Engine sẽ nhận được cấu trúc gì.
        """
        # Chọn 1 ga cực kỳ sầm uất để soi thử (Bạn có thể đổi sang ID ga khác nếu muốn)
        sample_node_id = "JR-East.Yamanote.Shinjuku"

        print("\n" + "=" * 70)

        if sample_node_id not in self.graph.nodes:
            return

        # 1. In thông tin Node (Nhà ga)
        node = self.graph.nodes[sample_node_id]
        print(f"📍 THÔNG TIN NÚT (NODE):")
        print(f"   - ID:      {node.id}")
        print(f"   - Tên Ga:  {node.name}")
        print(f"   - Tọa độ:  (Lat: {node.lat}, Lon: {node.lon})")

        # 2. In thông tin Edges (Các con đường kết nối)
        edges = self.graph.edges.get(sample_node_id, [])
        print(f"\n🛤️ DANH SÁCH CÁC CẠNH (EDGES) XUẤT PHÁT TỪ GA NÀY ({len(edges)} đường):")

        for i, edge in enumerate(edges, 1):
            print(edge.edge_type, edge.to_node, edge.line, edge.time, edge.cost, edge.distance)
            if edge.edge_type == EdgeType.TRAIN:
                print(f"   {i}. 🚆 Đi TÀU đến: {edge.to_node}")
                print(
                    f"      └─ Tuyến: {edge.line} | T/gian: {edge.time} phút | Phí: {edge.cost}¥ | Khoảng cách: {edge.distance} km")
            elif edge.edge_type == EdgeType.WALK:
                print(f"   {i}. 🚶 Đi BỘ đến:  {edge.to_node}")
                print(f"      └─ Tuyến: Đi bộ chuyển bến | T/gian phạt: {edge.time} phút | K/cách: {edge.distance} km")

        print("=" * 70 + "\n")

if __name__ == '__main__':

    unittest.main(verbosity=2, exit=False)

