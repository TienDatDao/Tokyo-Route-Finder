# 📊 Data System - Hệ thống Quản lý Dữ liệu Tokyo Route Finder

## 🎯 Tổng quan

Module `data_system` là **trái tim xử lý dữ liệu** của ứng dụng Tokyo Route Finder. Nó chịu trách nhiệm:

1. **Tải dữ liệu thô** từ các file JSON (ga, tuyến đường, nhóm ga)
2. **Xây dựng đồ thị sạch** biểu diễn mạng lưới đường sắt Tokyo
3. **Quản lý sự cố thời gian thực** (đóng cửa ga, bảo trì tuyến)
4. **Cung cấp đồ thị cho AI engine** để tính toán tuyến đường tối ưu

### Đặc điểm chính:
- ✅ **Đồ thị sạch**: Không trùng lặp, tham chiếu hợp lệ, liên tục
- ✅ **2 lớp dữ liệu**: Original Graph (bản gốc) và Current Graph (có áp dụng incidents)
- ✅ **Cache thông minh**: Lưu đồ thị nhị phân (pickle) và incidents (JSON)
- ✅ **Rebuild tự động**: Khi incidents thay đổi, tự động rebuild graph mới từ dữ liệu gốc

---

## 📁 Cấu trúc Thư mục

```
data_system/
├── __init__.py
├── config.py                      # ⚙️ Cấu hình (tốc độ tàu, chi phí, khoảng cách đi bộ, v.v.)
├── engine.py                      # 🔧 Engine placeholder cho xử lý dữ liệu tùy chỉnh
├── interface.py                   # 🌐 Interface placeholder để giao tiếp với API
│
├── core/                          # 🧠 LOGIC CỐT LÕI
│   ├── models.py                  # 📦 Các mô hình dữ liệu (Graph, Node, Edge, Incident)
│   ├── parsers.py                 # 🔄 Phân tích JSON thô thành objects Python
│   ├── graph_builder.py           # 🔨 Xây dựng đồ thị từ dữ liệu ga và tuyến
│   ├── graph_manager.py           # 📈 Quản lý vòng đời đồ thị (build, apply incidents, cache)
│   ├── incident_manager.py        # 🚫 Áp dụng sự cố để lọc đồ thị
│   ├── data_manager.py            # 💾 Quản lý cache đồ thị (pickle + incidents JSON)
│   ├── station_group_resolver.py  # 🏙️ Giải quyết cụm ga phức tạp
│   └── __pycache__/               # Cache Python
│
├── raw_data/                      # 📥 DỮ LIỆU GỐC (JSON)
│   ├── stations.json              # Danh sách ~2500 ga với tên, tọa độ
│   ├── railway.json               # ~60 tuyến đường với danh sách ga theo thứ tự
│   ├── train_types.json           # Metadata cho loại tàu
│   └── station_groups.json        # Nhóm ga phức tạp (VD: Shinjuku có 5 ga riêng)
│
├── cache/                         # 💾 BỘ NHỚ ĐỆM
│   ├── graph_original.pkl         # Đồ thị gốc (không có incidents)
│   ├── graph_current.pkl          # Đồ thị hiện tại (đã áp dụng incidents)
│   ├── incidents.json             # Danh sách incidents hiện tại
│   └── graph_metadata.json        # Thống kê đồ thị (số node, edge, v.v.)
│
├── utils/                         # 🛠️ HÀM TIỆN ÍCH
│   ├── geo_calc.py                # 🗺️ Tính toán địa lý (Haversine, tìm ga gần nhất)
│   ├── logger.py                  # 📝 Logging có cấu trúc
│   ├── validators.py              # ✔️ Validation schema JSON
│   └── __pycache__/
│
├── tests/                         # 🧪 UNIT TESTS
│   ├── test_graph_builder.py      # Test xây dựng đồ thị
│   ├── test_parsers.py            # Test phân tích dữ liệu
│   ├── test_incidents.py          # Test áp dụng sự cố
│   ├── test_route.py              # Test tính toán tuyến đường
│   ├── test_geo_calc.py           # Test hàm địa lý
│   ├── visualize_graph.py         # Công cụ visualize đồ thị
│   └── __pycache__/
│
└── README.md                      # File này
```

---

## 📊 Mô tả Dữ liệu

### 📥 Dữ liệu Thô (Raw Data)

#### **stations.json**
```json
[
  {
    "id": "JR-East.Yamanote.Shinjuku",
    "title": "Shinjuku",
    "coord": [35.330116, 139.710387]
  }
]
```

#### **railway.json**
```json
[
  {
    "id": "JR-East.Yamanote",
    "title": "Yamanote Line",
    "stations": [
      "JR-East.Yamanote.Tokyo",
      "JR-East.Yamanote.Yurakucho",
      "JR-East.Yamanote.Shinjuku",
      ...
    ]
  }
]
```

#### **station_groups.json**
```json
{
  "Shinjuku": [
    "JR-East.Yamanote.Shinjuku",
    "JR-East.Chuo.Shinjuku",
    "JR-East.SobuRapid.Shinjuku"
  ]
}
```

### 📦 Dữ liệu Đã Xử lý (Processed Data)

#### **Graph** - Đồ thị có hướng
- **Nodes**: Dictionary {station_id → Node}
- **Edges**: Dictionary adjacency list {from_node → [Edge, Edge, ...]}

#### **Node** - Một ga
```python
@dataclass
class Node:
    id: str              # "JR-East.Yamanote.Shinjuku"
    name: str            # "Shinjuku"
    lat: float           # 35.330116
    lon: float           # 139.710387
```

#### **Edge** - Một kết nối tàu hoặc đi bộ
```python
@dataclass
class Edge:
    to_node: str         # Ga đích
    edge_type: EdgeType  # "train" hoặc "walk"
    time: float          # Thời gian (phút)
    cost: float          # Chi phí (Yên)
    distance: float      # Khoảng cách (km)
    line: str            # "JR-East.Yamanote" (cho train), "__walk__" (cho walk)
```

#### **Incident** - Sự cố
```python
@dataclass
class Incident:
    incident_id: str     # ID duy nhất
    type: IncidentType   # "STATION_CLOSED" hoặc "LINE_MAINTENANCE"
    target_id: str       # ID ga hoặc tuyến bị ảnh hưởng
```

---

## 🔄 Quy trình Hoạt động

### **Kiến trúc Chính**
```
RAW DATA (JSON)
    ↓
    └─→ PARSERS: Tải và chuyển đổi thành objects Python
        ↓
BUILD FRESH GRAPH
    ↓
    ├─→ Tạo nodes từ stations
    ├─→ Thêm TRAIN edges (liên tiếp trên tuyến)
    ├─→ Thêm WALK edges (trong cụm ga)
    └─→ Validate & Clean
        ↓
ORIGINAL GRAPH → [CACHE pickle]
    ↓
APPLY INCIDENTS
    ↓
    ├─→ STATION_CLOSED: Xóa node + tất cả edges liên quan
    └─→ LINE_MAINTENANCE: Xóa TRAIN edges cho tuyến
        ↓
CURRENT GRAPH → [CACHE pickle]
    ↓
INCIDENTS → [CACHE JSON]
```

### **Bước 1️⃣: Tải & Phân tích Dữ liệu**
- **parsers.py** tải các file JSON từ `raw_data/`
- Chuyển đổi thành:
  - Dictionary `nodes`: {station_id → Node}
  - Dictionary `railways`: {line_id → [station_ids]}
  - Dictionary `station_groups`: {base_name → [full_ids]}

### **Bước 2️⃣: Xây dựng Đồ thị**
- **graph_builder.py** tạo Graph:
  - Thêm tất cả **TRAIN edges** giữa ga liên tiếp trên tuyến
  - Thêm **WALK edges** giữa ga trong cùng cụm (với hình phạt chuyển tuyến)
  - Tính thời gian = khoảng cách / tốc độ tàu
  - Tính chi phí = (khoảng cách × chi phí/km) + hình phạt chuyển
  - **Làm sạch**: Xóa edges tới node không tồn tại
  - **Validate**: Không trùng lặp, không self-loop

### **Bước 3️⃣: Lưu Original Graph**
- **GraphManager** lưu graph gốc vào `cache/graph_original.pkl`
- Được lưu **một lần duy nhất**
- Dùng để rebuild graph khi incidents thay đổi

### **Bước 4️⃣: Áp dụng Incidents**
- **incident_manager.py** nhận fresh graph + danh sách incidents
- Tạo **deep copy** của graph
- Với mỗi incident:
  - **STATION_CLOSED**: Xóa node ga + tất cả edges vào/ra
  - **LINE_MAINTENANCE**: Xóa TRAIN edges cho tuyến
- Trả về **filtered graph**

### **Bước 5️⃣: Lưu Current Graph**
- **GraphManager** lưu current graph vào `cache/graph_current.pkl`
- Lưu danh sách incidents vào `cache/incidents.json`
- Cập nhật thống kê trong `cache/graph_metadata.json`

### **Bước 6️⃣: Cấp phát cho AI Engine**
- **data_manager.py** trả về `current_graph`
- AI engine sử dụng graph này để tính tuyến đường tối ưu
- Nếu không có incidents: `current_graph` = `original_graph`

---

## 🛠️ Các Lớp Chính

### **GraphManager** (`core/graph_manager.py`)
```python
class GraphManager:
    def __init__(self, cache_dir: str)
    def build_graph_from_raw(raw_dir: str) → Graph
    def load_original() → Graph
    def apply_incidents_and_save(raw_dir: str, incidents: List[Incident]) → None
    def get_current() → Graph
    def get_original() → Graph
```

**Tác vụ**:
- Quản lý vòng đời graph
- Maintain original + current versions
- Rebuild graph từ raw data
- Lưu/tải cache

### **GraphBuilder** (`core/graph_builder.py`)
```python
def build_tokyo_graph(
    stations_path: str,
    railway_path: str,
    train_types_path: str,
    groups_path: str
) → Graph
```

**Tác vụ**:
- Phân tích ga thành nodes
- Thêm TRAIN edges (liên tiếp trên tuyến)
- Thêm WALK edges (trong cụm ga)
- Validate & clean graph

### **IncidentManager** (`core/incident_manager.py`)
```python
def apply_incidents(graph: Graph, incidents: List[Incident]) → Graph
```

**Tác vụ**:
- Deep copy graph gốc
- Lọc nodes/edges dựa trên incidents
- Trả về graph đã lọc

### **DataManager** (`core/data_manager.py`)
```python
def get_clean_graph(raw_dir: str, incidents: List[Incident] = None) → Graph
def save_incidents_to_cache(incidents: List[Incident]) → None
def load_incidents_from_cache() → List[Incident]
def clear_graph_cache() → None
```

**Tác vụ**:
- Quản lý cache RAM (singleton)
- Lưu/tải incidents
- Trả về clean graph với incidents tùy chọn

---

## ⚙️ Cấu hình (config.py)

```python
@dataclass
class GraphConfig:
    TRAIN_SPEED_KMH: float = 38.0              # Tốc độ tàu (km/h)
    TRAIN_COST_YEN: float = 150.0              # Chi phí cơ sở (Yên)
    TRAIN_COST_PER_KM = 35.0                   # Chi phí theo km (Yên/km)
    WALK_TIME_SAME_ZONE_MIN: float = 5.0       # Thời gian đi bộ cùng khu vực (phút)
    WALK_TIME_DIFF_ZONE_MIN: float = 10.0      # Thời gian đi bộ khác khu vực (phút)
    MAX_TRANSFER_DISTANCE_KM: float = 0.35     # Khoảng cách tối đa để kết nối (km)
    TRANSFER_PENALTY_MIN: float = 8.0          # Hình phạt chuyển tuyến (phút)
```

---

## 🔧 Hàm Chính

### **Xây dựng Đồ thị**
```python
# core/graph_builder.py
build_tokyo_graph(stations_path, railway_path, train_types_path, groups_path) → Graph
```

### **Quản lý Graph**
```python
# core/graph_manager.py
manager = GraphManager("data_system/cache")
graph = manager.build_graph_from_raw("data_system/raw_data")
manager.apply_incidents_and_save("data_system/raw_data", incidents)
current = manager.get_current()
```

### **Quản lý Dữ liệu**
```python
# core/data_manager.py
graph = get_clean_graph("data_system/raw_data")  # Lấy original graph
graph = get_clean_graph("data_system/raw_data", incidents)  # Lấy filtered graph
save_incidents_to_cache(incidents)  # Lưu incidents
incidents = load_incidents_from_cache()  # Tải incidents
```

### **Xử lý Sự cố**
```python
# core/incident_manager.py
filtered = apply_incidents(graph, incidents)  # Áp dụng incidents
```

### **Tiện ích**
```python
# utils/geo_calc.py
distance = haversine_distance(lat1, lon1, lat2, lon2)  # Tính khoảng cách
nearest = find_nearest_station(lat, lon, nodes)  # Tìm ga gần nhất
```

---

## 📋 Ví dụ Sử dụng

### **Lấy Đồ thị Gốc (không có incidents)**
```python
from data_system.core.graph_manager import GraphManager

manager = GraphManager("data_system/cache")
original_graph = manager.get_original()

# Graph có ~2500 nodes và ~20000+ edges
print(f"Nodes: {len(original_graph.nodes)}")
print(f"Edges: {sum(len(e) for e in original_graph.edges.values())}")
```

### **Áp dụng Incidents và Lấy Đồ thị Lọc**
```python
from data_system.core.models import Incident, IncidentType
from data_system.core.graph_manager import GraphManager

# Tạo incidents
incidents = [
    Incident(
        incident_id="1",
        type=IncidentType.STATION_CLOSED,
        target_id="JR-East.Yamanote.Shinjuku"
    ),
    Incident(
        incident_id="2",
        type=IncidentType.LINE_MAINTENANCE,
        target_id="JR-East.Yamanote"
    )
]

# Rebuild graph với incidents
manager = GraphManager("data_system/cache")
manager.apply_incidents_and_save("data_system/raw_data", incidents)

# Lấy filtered graph
current_graph = manager.get_current()
```

### **Xóa Tất cả Incidents (Restore Original)**
```python
from data_system.core.graph_manager import GraphManager

manager = GraphManager("data_system/cache")
manager.apply_incidents_and_save("data_system/raw_data", [])  # Empty list

# Graph quay về original
current_graph = manager.get_current()
```

---

## 🧪 Testing

### Chạy tất cả tests:
```bash
cd C:\Users\hieuv\PycharmProjects\Tokyo-Route-Finder
python -m pytest data_system/tests/ -v
```

### Chạy test cụ thể:
```bash
python -m pytest data_system/tests/test_graph_builder.py -v
python -m pytest data_system/tests/test_incidents.py -v
python -m pytest data_system/tests/test_route.py -v
```

### Visualize đồ thị:
```bash
python data_system/tests/visualize_graph.py
```

---

## 🐛 Ghi chú Quan trọng

### **Tại sao luôn rebuild từ raw data?**
- ❌ **KHÔNG** mutate original graph trong RAM
- ✅ **LUÔN** rebuild fresh graph từ raw data
- ✅ **Áp dụng** incidents lên fresh graph
- ✅ **LƯU** original + current separate

### **Tại sao cần hai graphs?**
- **original_graph**: Bản gốc không thay đổi, dùng để rebuild khi incidents thay đổi
- **current_graph**: Phiên bản hiện tại với incidents đã áp dụng, dùng cho AI engine

### **Khi nào graph được rebuild?**
- Lần đầu tiên ứng dụng khởi động
- Khi admin panel áp dụng incidents mới
- Khi admin panel xóa incidents (restore original)

### **Incident types**
- **STATION_CLOSED**: Ga bị đóng → xóa node + tất cả edges
- **LINE_MAINTENANCE**: Tuyến bảo trì → xóa TRAIN edges trên tuyến

---

## 📊 Thống kê Graph

Sau khi build xong, metadata được lưu trong `cache/graph_metadata.json`:
```json
{
  "total_nodes": 2470,
  "total_edges": 25000,
  "train_edges": 24000,
  "walk_edges": 1000,
  "railway_count": 60,
  "build_timestamp": "2024-01-15T10:30:00",
  "build_duration_seconds": 5.234
}
```

---

## 🚀 Roadmap Cải tiến (Future)

- ⏳ **Database integration**: Thay thế JSON bằng PostgreSQL/MongoDB để quản lý dữ liệu thời gian thực
- ⏳ **Incremental updates**: Thay vì rebuild toàn bộ, chỉ rebuild phần bị ảnh hưởng bởi incidents
- ⏳ **Real-time sync**: Đồng bộ dữ liệu với server khi có thay đổi
- ⏳ **Caching layer**: Redis để cache graph metadata
- ⏳ **Performance monitoring**: Theo dõi thời gian build, apply incidents, query

---

## 🔍 Chi tiết Kỹ thuật

### Làm sạch Đồ thị (Graph Cleaning)

```python
graph.clean()  # Removes:
    # 1. Edges to non-existent nodes
    # 2. Self-loops
    # 3. Duplicate edges (keeps first occurrence)
    # KEEPS:
    # - Isolated nodes (gas không có kết nối)
    # - Nodes with only walk edges
```

### Validation Đồ thị

```python
errors = graph.validate()  # Returns list of errors:
    # - Nodes not found errors
    # - Orphaned edges
    # - Cycle detection (optional)
```

### StationGroupResolver

Giải quyết các cụm ga phức tạp (VD: Shinjuku có 5 ga riêng):

```python
from data_system.core.station_group_resolver import StationGroupResolver

resolver = StationGroupResolver("raw_data/station_groups.json")
nodes = resolver.resolve("Shinjuku")
# → ["JR-East.Yamanote.Shinjuku", "JR-East.Chuo.Shinjuku", ...]
```

---

## 📈 Tối ưu Hiệu suất

### Cache Strategy
- **pickle** cho graph nhị phân: Nhanh hơn JSON ~10x
- **JSON** cho incidents: Dễ đọc, dễ debug, dễ quản lý phiên bản
- **RAM cache** (singleton): Tránh reload graph mỗi lần request

### Build Time
- **Lần đầu**: ~5-10 giây (phụ thuộc vào số lượng ga/tuyến)
- **Lần sau**: ~1-2 giây (load từ cache)
- **Áp dụng incidents**: ~1 giây (deep copy + filter)

### Kích thước
- **Đồ thị**: ~50-100 MB (pickle format)
- **Incidents cache**: ~1-10 KB (JSON format)
- **Metadata**: ~1 KB

---

## 🐛 Troubleshooting

### Lỗi: `NodeNotFound` khi tính tuyến
```
networkx.exception.NodeNotFound: Source JR-East.Yamanote.Shinjuku is not in G
```
**Nguyên nhân**: Ga bị xóa bởi incident nhưng AI engine vẫn gửi request tới ga này
**Cách khắc**: Đảm bảo frontend validate ga trước khi gửi request

### Lỗi: `UnicodeEncodeError` khi in Japanese
```
UnicodeEncodeError: 'charmap' codec can't encode character
```
**Nguyên nhân**: Terminal console không hỗ trợ UTF-8
**Cách khắc**: Thêm `# -*- coding: utf-8 -*-` vào đầu file Python

### Graph không update sau khi áp dụng incidents
**Nguyên nhân**: AI engine load graph từ cache cũ
**Cách khắc**: Xóa `cache/graph_current.pkl` hoặc gọi `clear_graph_cache()`

---

## 📞 Liên hệ / Support

- **Issues**: Kiểm tra test files trong `data_system/tests/`
- **Documentation**: Xem docstrings trong mỗi class/function
- **Examples**: Xem `tests/test_route.py` cho ví dụ sử dụng

---

**Phiên bản**: 1.0.0 (2024)
**Phát triển bởi**: Tokyo Route Finder Team
