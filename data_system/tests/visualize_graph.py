import os
import sys
import networkx as nx
import plotly.graph_objects as go

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
    # Trỏ vào thư mục raw_data/
    RAW_DIR = os.path.join(DATA_SYSTEM_DIR, "raw_data")

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
        print("LỖI: Không tìm thấy các file sau:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n Vui lòng kiểm tra lại xem file đã nằm đúng trong data_system/raw_data/ chưa!")
        return

    # Xây dựng Đồ thị từ file thật
    my_graph = build_tokyo_graph(p_stations, p_railway, p_train_types, p_groups)

    # ==========================================
    # BIẾN ĐỔI DATA SANG PLOTLY ĐỂ VẼ BẢN ĐỒ INTERACTIVE
    # ==========================================
    print("Đang xử lý tọa độ để vẽ bản đồ interactive (Sẽ mất vài giây vì dữ liệu rất lớn)...")

    # Tạo figure Plotly
    fig = go.Figure()

    # Thêm nodes
    node_x = []
    node_y = []
    node_text = []
    for node_id, node in my_graph.nodes.items():
        node_x.append(node.lon)
        node_y.append(node.lat)
        node_text.append(f"Tên: {node.name}<br>ID: {node_id}")

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(size=6, color='darkblue', opacity=0.6),
        text=node_text,
        hoverinfo='text',
        name='Nhà ga'
    ))

    # Thêm edges
    train_x = []
    train_y = []
    train_text = []
    walk_x = []
    walk_y = []
    walk_text = []

    for start_node, edges in my_graph.edges.items():
        start_lon = my_graph.nodes[start_node].lon
        start_lat = my_graph.nodes[start_node].lat
        for edge in edges:
            end_lon = my_graph.nodes[edge.to_node].lon
            end_lat = my_graph.nodes[edge.to_node].lat
            if edge.edge_type == EdgeType.TRAIN:
                train_x.extend([start_lon, end_lon, None])
                train_y.extend([start_lat, end_lat, None])
                train_text.append(f"Tàu: {start_node} -> {edge.to_node}<br>Trọng số: {edge.time}")
            else:
                walk_x.extend([start_lon, end_lon, None])
                walk_y.extend([start_lat, end_lat, None])
                walk_text.append(f"Đi bộ: {start_node} -> {edge.to_node}<br>Trọng số: {edge.time}")

    # Vẽ edges tàu
    fig.add_trace(go.Scatter(
        x=train_x, y=train_y,
        mode='lines',
        line=dict(width=1, color='royalblue'),
        hoverinfo='text',
        text=train_text,
        name='Tuyến tàu'
    ))

    # Vẽ edges đi bộ
    fig.add_trace(go.Scatter(
        x=walk_x, y=walk_y,
        mode='lines',
        line=dict(width=2, color='red'),
        hoverinfo='text',
        text=walk_text,
        name='Đi bộ'
    ))

    # Cấu hình layout
    fig.update_layout(
        title=f"Bản Đồ Mạng Lưới Tàu Tokyo Thực Tế ({len(my_graph.nodes)} Nhà ga)",
        xaxis=dict(title='Kinh độ (Longitude)', autorange=True),
        yaxis=dict(title='Vĩ độ (Latitude)', autorange=True),
        showlegend=True,
        hovermode='closest'
    )

    # Lưu thành file HTML interactive
    fig.write_html('tokyo_graph_interactive.html')
    print(" Đã tạo xong bản đồ interactive! Mở file tokyo_graph_interactive.html để xem.")

    # Xuất PNG siêu cao (tùy chọn)
    fig.write_image('tokyo_graph_high_res.png', width=4000, height=3000, scale=2)


if __name__ == "__main__":
    main()