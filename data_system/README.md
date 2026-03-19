# Hệ thống Dữ liệu cho Tokyo Route Finder

## Tổng quan

Module `data_system` chịu trách nhiệm quản lý và xử lý dữ liệu cho ứng dụng Tokyo Route Finder. Nó xử lý việc tải dữ liệu JSON thô, xây dựng biểu diễn đồ thị sạch của mạng lưới đường sắt Tokyo, áp dụng các sự cố thời gian thực (ví dụ: đóng cửa ga hoặc bảo trì tuyến), và cung cấp đồ thị sạch cho các thuật toán định tuyến.

Hệ thống đảm bảo đồ thị là **sạch**: không có cạnh trùng lặp, tham chiếu hợp lệ, và các thành phần kết nối.

## Cấu trúc Thư mục

```
data_system/
├── __init__.py
├── config.py                 # Các hằng số cấu hình (tốc độ, chi phí, v.v.)
├── engine.py                 # Placeholder cho logic engine
├── interface.py              # Placeholder cho API interface
├── core/                     # Logic cốt lõi
│   ├── models.py             # Các mô hình dữ liệu (Graph, Node, Edge, Incident, v.v.)
│   ├── parsers.py            # Phân tích dữ liệu JSON thô thành định dạng có thể sử dụng
│   ├── graph_builder.py      # Xây dựng đồ thị từ dữ liệu đã phân tích
│   ├── data_manager.py       # Quản lý cache đồ thị và áp dụng sự cố
│   └── incident_manager.py   # Áp dụng sự cố để lọc đồ thị
├── raw_data/                 # Các file dữ liệu JSON thô
│   ├── stations.json         # Thông tin ga (id, tên, tọa độ)
│   ├── railway.json          # Các tuyến đường sắt và danh sách ga
│   ├── train_types.json      # Metadata cho loại tàu (hiện tại tải nhưng không sử dụng nhiều)
│   └── station_groups.json   # Các cụm ga phức tạp cho kết nối đi bộ
├── tests/                    # Các unit tests
│   ├── test_graph_builder.py # Test xây dựng đồ thị
│   ├── test_parsers.py       # Test phân tích dữ liệu
│   ├── test_incidents.py     # Test xử lý sự cố
│   └── ...
├── utils/                    # Các hàm tiện ích
│   ├── geo_calc.py           # Tính toán địa lý (khoảng cách Haversine, tìm ga gần nhất)
│   ├── logger.py             # Thiết lập logging có cấu trúc
│   └── validators.py         # Validation schema JSON
└── README.md                 # File này
```

## Mô tả Dữ liệu

### Các File Dữ liệu Thô
- **stations.json**: Danh sách ga với `id`, `title` (tên tiếng Anh/Nhật), và `coord` (kinh độ, vĩ độ).
- **railway.json**: Danh sách tuyến đường sắt với `id`, `title`, và `stations` (danh sách ID ga theo thứ tự).
- **train_types.json**: Metadata cho loại tàu (hiện tại tải nhưng không sử dụng nhiều).
- **station_groups.json**: Danh sách lồng nhau đại diện cho các cụm ga phức tạp (khu vực soát vé) cho kết nối đi bộ.

### Dữ liệu Đã Xử lý
- **Graph**: Đồ thị có hướng với nodes (ga) và edges (kết nối tàu/đi bộ).
  - **Nodes**: ID ga, tên, lat/lon.
  - **Edges**: To-node, loại (TRAIN/WALK), thời gian, chi phí, khoảng cách, tuyến (cho TRAIN).
- **Incidents**: Sự kiện như đóng cửa ga hoặc bảo trì tuyến để lọc đồ thị.

## Cách Hoạt động

### 1. Tải và Phân tích Dữ liệu
- `parsers.py` tải các file JSON và chuyển đổi thành các object Python (ví dụ: dict của Nodes từ stations.json).
- Validators trong `utils/validators.py` có thể kiểm tra cấu trúc JSON cho lỗi.

### 2. Xây dựng Đồ thị
- `graph_builder.py` xây dựng đồ thị:
  - Phân tích ga thành nodes.
  - Thêm edges TRAIN giữa các ga liên tiếp trên tuyến.
  - Thêm edges WALK giữa các ga trong cùng cụm, với hình phạt chuyển tuyến.
- Sử dụng `config.py` cho hằng số (ví dụ: tốc độ tàu 40 km/h, thời gian đi bộ 2-7 phút).
- Làm sạch và validate đồ thị (không trùng lặp, kết nối, tham chiếu hợp lệ).

### 3. Xử lý Sự cố
- `incident_manager.py` áp dụng sự cố:
  - **STATION_CLOSED**: Loại bỏ node và tất cả edges liên quan.
  - **LINE_MAINTENANCE**: Loại bỏ edges cho tuyến bị ảnh hưởng.
- Trả về bản sao đồ thị đã lọc.

### 4. Quản lý Dữ liệu
- `data_manager.py` cache đồ thị (pickle) và áp dụng sự cố theo yêu cầu.
- `get_clean_graph(raw_dir, incidents=None)`: Trả về đồ thị, tùy chọn đã lọc.

### 5. Tiện ích
- `geo_calc.py`: Khoảng cách Haversine, tìm ga gần nhất.
- `logger.py`: Logging có cấu trúc với timestamp.
- `validators.py`: Validate schema JSON.

## Các Hàm Chính

- `build_tokyo_graph(stations_path, railway_path, train_types_path, groups_path) -> Graph`: Xây dựng đồ thị đầy đủ.
- `get_clean_graph(raw_dir, incidents=None) -> Graph`: Lấy đồ thị đã cache/đã lọc.
- `apply_incidents(graph, incidents) -> Graph`: Lọc đồ thị với sự cố.
- `haversine_distance(lat1, lon1, lat2, lon2) -> float`: Tính khoảng cách.
- `find_nearest_station(lat, lon, nodes) -> Optional[Tuple[str, float]]`: Tìm ga gần nhất.

## Ví dụ Sử dụng

```python
from data_system.core.data_manager import get_clean_graph
from data_system.core.models import Incident, IncidentType

# Lấy đồ thị sạch
graph = get_clean_graph("data_system/raw_data")

# Áp dụng sự cố
incidents = [Incident(incident_id="1", type=IncidentType.STATION_CLOSED, target_id="JR-East.Yamanote.Shinjuku")]
filtered_graph = get_clean_graph("data_system/raw_data", incidents=incidents)

print(f"Nodes gốc: {len(graph.nodes)}, Đã lọc: {len(filtered_graph.nodes)}")
```

## Cấu hình

Chỉnh sửa `config.py` để thay đổi hằng số:
- `TRAIN_SPEED_KMH`: Tốc độ tàu (km/h).
- `TRAIN_COST_YEN`: Chi phí mỗi đoạn.
- `WALK_TIME_SAME_ZONE_MIN`: Thời gian đi bộ trong cùng khu vực.
- `WALK_TIME_DIFF_ZONE_MIN`: Thời gian đi bộ qua khu vực.

## Testing

Chạy tests với:
```bash
python -m pytest data_system/tests
```

Các tests chính: xây dựng đồ thị, áp dụng sự cố, validation.

## Lưu ý

- Đồ thị được cache trong `data_system/cache/tokyo_graph.pkl` để tối ưu hiệu suất.
- Sự cố được áp dụng động mà không sửa đổi đồ thị gốc.
- Đảm bảo các file raw_data là JSON hợp lệ; sử dụng validators để kiểm tra.
- Cho định tuyến, đồ thị sạch được truyền đến AI engine.
