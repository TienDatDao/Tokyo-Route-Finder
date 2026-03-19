import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG (AUTO PATHING)
# ==========================================
# 1. Lấy đường dẫn của thư mục test/ hiện tại
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Đi ngược lên 1 cấp để tới thư mục data_system/
DATA_SYSTEM_DIR = os.path.dirname(CURRENT_DIR)

# 3. Thêm thư mục gốc (chứa data_system) vào biến môi trường để import không bị lỗi
ROOT_DIR = os.path.dirname(DATA_SYSTEM_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Bây giờ có thể import an toàn
from data_system.core.graph_builder import build_tokyo_graph
from data_system.core.models import EdgeType


def main():
    print("🚀 BẮT ĐẦU NẠP DỮ LIỆU THẬT 🚀")

    # Trỏ chính xác vào thư mục raw_data/
    RAW_DIR = os.path.join(DATA_SYSTEM_DIR, "raw_data")

    # Lưu ý: Ở tin nhắn trước bạn gõ là "station.json", tôi để "stations.json" theo các file trước.
    p_stations = os.path.join(RAW_DIR, "stations.json")
    p_railway = os.path.join(RAW_DIR, "railway.json")
    p_train_types = os.path.join(RAW_DIR, "train_types.json")
    p_groups = os.path.join(RAW_DIR, "station_groups.json")

    # Kiểm tra an toàn xem file có tồn tại không
    missing_files = []
    for p in [p_stations, p_railway, p_train_types, p_groups]:
        if not os.path.exists(p):
            missing_files.append(p)

    if missing_files:
        print("❌ LỖI: Không tìm thấy các file sau:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n👉 Vui lòng kiểm tra lại xem file đã nằm đúng trong data_system/raw_data/ chưa!")
        return

    # Xây dựng Đồ thị từ file thật
    my_graph = build_tokyo_graph(p_stations, p_railway, p_train_types, p_groups)

    # ==========================================
    # BIẾN ĐỔI DATA SANG NETWORKX ĐỂ VẼ BẢN ĐỒ
    # ==========================================
    print("Đang xử lý tọa độ để vẽ hình (Sẽ mất vài giây vì dữ liệu rất lớn)...")
    G = nx.DiGraph()
    pos = {}

    for node_id, node in my_graph.nodes.items():
        G.add_node(node_id, label=node.name)
        pos[node_id] = (node.lon, node.lat)  # Trục X = lon, Trục Y = lat

    train_edges = []
    walk_edges = []

    for start_node, edges in my_graph.edges.items():
        for edge in edges:
            G.add_edge(start_node, edge.to_node)
            if edge.edge_type == EdgeType.TRAIN:
                train_edges.append((start_node, edge.to_node))
            else:
                walk_edges.append((start_node, edge.to_node))

    # ==========================================
    # RENDER LÊN MÀN HÌNH (Đã tối ưu cho Big Data)
    # ==========================================
    plt.figure(figsize=(15, 12))
    plt.title(f"Bản Đồ Mạng Lưới Tàu Tokyo Thực Tế ({len(my_graph.nodes)} Nhà ga)", fontsize=16, fontweight='bold')

    # Vẽ Node (Thu nhỏ size lại để không bị đè nhau)
    nx.draw_networkx_nodes(G, pos, node_color='darkblue', node_size=10, alpha=0.6)

    # Vẽ Tàu (Nét mỏng, màu xanh lam nhạt)
    nx.draw_networkx_edges(G, pos, edgelist=train_edges, edge_color='royalblue', width=0.5, alpha=0.7, arrows=False)

    # Vẽ Đi bộ (Màu đỏ, nét mỏng hơn)
    nx.draw_networkx_edges(G, pos, edgelist=walk_edges, edge_color='red', width=0.8, alpha=0.5, arrows=False)

    plt.axis('off')
    plt.tight_layout()
    print("✅ Đã vẽ xong! Mở cửa sổ bản đồ...")
    plt.show()


if __name__ == "__main__":
    main()