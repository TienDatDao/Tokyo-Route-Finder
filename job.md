# 🗾 Tokyo Route Finder - Project Documentation

## Tổng Quan Project
**Tokyo Route Finder** là một ứng dụng tìm lộ trình tối ưu trên mạng lưới tàu điện ngầm và các tuyến xe lửa ở Tokyo. Ứng dụng gồm 4 thành phần chính: **Backend API** (Flask), **Frontend** (Leaflet + JavaScript), **Data System** (quản lý dữ liệu đồ thị), và **AI Engine** (thuật toán tìm đường).

---

# 📁 CẤU TRÚC THƯUC MỤC

## 1. 📂 ROOT LEVEL FILES (Thư mục gốc)

### **Flow.md**
- **Mục đích**: Tài liệu quy định các Interface trao đổi dữ liệu giữa các thành phần (Frontend ↔ Backend ↔ Data System ↔ AI Engine)
- **Nội dung chính**: 
  - Format JSON request/response
  - Cấu trúc dữ liệu đồ thị (graph)
  - Quy tắc xử lý dữ liệu
  - Các tiêu chí tối ưu hóa (shortest_time, lowest_cost, least_transfers)

### **README.md**
- **Mục đích**: Hướng dẫn chạy ứng dụng
- **Nội dung chính**:
  - Cách chạy Backend (port 5000)
  - Cách chạy Frontend (port 8000)
  - Các tính năng đã cập nhật
  - Cấu trúc chính của ứng dụng

### **Ruleset.md**
- **Mục đích**: Quy chuẩn làm việc và workflow GitHub cho toàn nhóm
- **Nội dung chính**:
  - Cấu trúc nhánh (main, dev, feature/*, fix/*, docs/*)
  - Quy tắc commit/merge
  - Quy trình phát triển (workflow)
  - Hướng dẫn làm việc nhóm

### **x.json**
- **Mục đích**: File ví dụ về format request tới API
- **Nội dung**: Định dạng JSON request với các trường (start_point, end_point, preferences)

---

## 2. 📂 ADMIN_PANEL (Bảng Quản Trị - Node.js Express Server)

### **Mục đích**: Cung cấp giao diện web để quản lý các sự cố (station closed, line maintenance) và rebuild graph

### **server.js** ⭐ CHÍNH
- **Vai trò**: Express server chính của admin panel (chạy trên port 5001)
- **Các endpoint chính**:
  - `GET /api/stations-and-lines` → Lấy danh sách ga và tuyến từ Python
  - `POST /api/apply-incident` → Áp dụng sự cố (đóng ga hoặc bảo trì tuyến)
  - `GET /api/active-incidents` → Lấy danh sách sự cố đang hoạt động
  - `GET /api/graph-status` → So sánh original vs current graph
  - `POST /api/reset-incidents` → Reset tất cả sự cố
- **Chức năng**: Gọi Python scripts để rebuild graph khi có thay đổi incidents

### **admin.js**
- **Vai trò**: Frontend logic cho bảng quản trị (chạy trên port 5001)
- **Chức năng**:
  - Quản lý trạng thái overrides (stations/edges)
  - Setup tab switching (Stations Tab, Edge Cost Tab)
  - Search functionality để tìm ga/tuyến
  - Render station list và edge list
  - Lưu/xóa overrides vào localStorage
  - Gửi request tới server.js để áp dụng incidents

### **admin.html** & **admin.css**
- **Mục đích**: HTML layout và styling cho giao diện admin panel
- **Nội dung**: 
  - Tabs để switch giữa Station Management và Edge Cost Adjustments
  - Search box để filter ga/tuyến
  - List hiển thị các ga/tuyến
  - Buttons để apply/remove sự cố
  - Display graph status (original vs current)

### **SETUP.md**
- **Mục đích**: Hướng dẫn cài đặt và chạy admin panel
- **Nội dung**: 
  - Cài đặt npm dependencies
  - Chạy server (port 5001)
  - Sử dụng các tính năng admin panel

### **package.json**
- **Vai trò**: Dependencies configuration cho Node.js project
- **Dependencies chính**: express, cors, body-parser, axios

### **public/** - Thư mục Static Files
- **index.html**: HTML tĩnh cho admin panel
- **css/style.css**: CSS styling
- **js/admin.js**: Frontend JavaScript (có thể duplicate)

---

## 3. 📂 AI_ENGINE (Thuật Toán Tìm Đường)

### **Mục đích**: Implement các thuật toán tìm lộ trình tối ưu (A*, Dijkstra, heuristic functions)

### **router.py** ⭐ CHÍNH
- **Vai trò**: Chứa logic tìm đường tối ưu
- **Hàm chính**:
  - `find_optimal_route(graph, start, end, criteria)` → Hàm chính sử dụng A* algorithm
  - `heuristic(current, goals, graph, criteria)` → Tính heuristic dựa trên tiêu chí tối ưu
  - `calculate_haversine_km(lat1, lon1, lat2, lon2)` → Tính khoảng cách giữa 2 điểm
  - `normalize_line(line)` → Chuẩn hóa tên tuyến
- **Tiêu chí tối ưu**:
  - `shortest_time`: Sử dụng heuristic dựa trên khoảng cách Haversine
  - `lowest_cost`: Dijkstra (heuristic = 0)
  - `least_transfers`: Dijkstra (heuristic = 0)
- **Output**: Trả về object `{status, route: {path, total_time, total_cost, transfers, details}}`

---

## 4. 📂 BACKEND_API (Flask Server - Trung Tâm Điều Phối)

### **Mục đích**: REST API server điều phối giữa Frontend, Data System, và AI Engine

### **app.py** ⭐ CHÍNH
- **Vai trò**: Flask application chính (chạy trên port 5000)
- **Endpoint**:
  - `POST /api/find-path` hoặc `POST /find-route` → Nhận request tìm đường từ frontend
  - `GET /api/stations` → Lấy danh sách ga từ Data System
- **Cấu hình**: HOST = '0.0.0.0', PORT = 5000, Debug = True
- **CORS**: Cho phép frontend (port 8000) truy cập

### **services.py** ⭐ CHÍNH
- **Vai trò**: Xử lý logic tìm đường
- **Hàm chính**:
  - `handle_find_route(payload)` → Nhận yêu cầu từ frontend, gọi Data System + AI Engine
  - `_get_graph_manager()` → Tạo GraphManager singleton
  - `_build_search_graph(graph)` → Chuyển đổi graph thành format để gửi cho AI Engine
  - `get_filtered_stations(raw_data_path)` → Lấy danh sách ga
- **Flow**:
  1. Parse request từ frontend (start_name, end_name, criteria)
  2. Gọi GraphManager lấy current graph (đã apply incidents)
  3. Find node IDs dựa trên station names
  4. Build search graph
  5. Gọi AI Engine (router.py) để tìm đường
  6. Trả về kết quả với path coordinates

### **config.py**
- **Mục đích**: Cấu hình server
- **Nội dung**:
  - PORT = 5000
  - DEBUG = True
  - HOST = '0.0.0.0'
  - DATA_RAW_DIR = "data_system/raw_data"

### **main.py**
- **Mục đích**: Alternative entry point (có thể là legacy file hoặc backup)

### **README.md**
- **Mục đích**: Hướng dẫn backend API

---

## 5. 📂 DATA_SYSTEM (Quản Lý Dữ Liệu Đồ Thị)

### **Mục đích**: Quản lý lifecycle của graph, handle incidents (station_closed, line_maintenance), cache, rebuild graph

### **Các File Python Chính:**

#### **engine.py**
- **Mục đích**: Hàm `get_clean_map_data()` để lọc dữ liệu gốc
- **Chức năng**: Xóa các ga/tuyến bị incidents trước khi gửi cho AI Engine

#### **interface.py**
- **Mục đích**: Interface để lấy dữ liệu sạch (documentation comment)
- **Nội dung**: "Chứa hàm get_clean_data để lấy dữ liệu đã được làm sạch từ raw_data"

#### **config.py**
- **Mục đích**: Cấu hình cho Data System
- **Nội dung**:
  - TRAIN_SPEED_KMH = 38.0 km/h
  - TRAIN_COST_YEN = 150 yen
  - WALK_TIME_SAME_ZONE_MIN = 5 phút
  - WALK_TIME_DIFF_ZONE_MIN = 10 phút
  - MAX_TRANSFER_DISTANCE_KM = 0.35 km

#### **get_stations_lines.py** ⭐
- **Mục đích**: Script Python lấy danh sách ga và tuyến từ raw_data
- **Được gọi bởi**: Admin panel server.js
- **Output**: JSON `{stations: {}, lines: [], total_stations, total_lines}`

#### **get_graph_status.py** ⭐
- **Mục đích**: Script Python lấy trạng thái graph (so sánh original vs current)
- **Được gọi bởi**: Admin panel server.js
- **Output**: JSON với original/current stats, incidents list, cache status

#### **rebuild_graph.py** ⭐ QUAN TRỌNG
- **Mục đích**: Rebuild graph từ raw data + apply incidents, lưu vào cache
- **Được gọi bởi**: Admin panel khi apply incident
- **Input**: JSON string chứa danh sách incidents
- **Output**: JSON `{status, message, original_nodes, original_edges, current_nodes, current_edges, removed_nodes, removed_edges, comparison}`
- **Flow**:
  1. Parse incidents từ JSON
  2. Tạo GraphManager
  3. Build original graph từ raw data (nếu chưa có)
  4. Apply incidents
  5. So sánh original vs current
  6. Lưu cache

#### **__init__.py**
- **Mục đích**: Make data_system a Python package

### **core/** - Thư mục Chứa Core Logic

#### **models.py** ⭐ CHÍNH
- **Vai trò**: Định nghĩa tất cả data models
- **Classes**:
  - `Node` - Đại diện một ga (id, name, lat, lon)
  - `Edge` - Đại diện một tuyến đi (to_node, edge_type, time, cost, distance, line)
  - `Graph` - Đại diện toàn bộ đồ thị (nodes dict, edges dict)
  - `Incident` - Đại diện một sự cố (incident_id, type, target_id)
  - `EdgeType` - Enum: TRAIN, WALK
  - `IncidentType` - Enum: STATION_CLOSED, LINE_MAINTENANCE, STATION_GROUP_CLOSED
  - `OptimizedBy` - Enum: SHORTEST_TIME, LOWEST_COST, LEAST_TRANSFER
- **Hàm chính của Graph**:
  - `add_edge()` - Thêm edge
  - `clean()` - Xóa edges invalid
  - `validate()` - Validate toàn bộ graph

#### **graph_manager.py** ⭐ CHÍNH
- **Vai trò**: Quản lý lifecycle của graph (original, current, incidents)
- **Kiến trúc**:
  - Luôn load original graph từ cache
  - Apply incidents để tạo current graph
  - Không mutate original graph (tạo deepcopy)
- **Hàm chính**:
  - `build_and_save_original(raw_data_dir)` - Build original graph từ raw data
  - `apply_and_save_incidents(incidents, raw_data_dir)` - Apply incidents, lưu current graph
  - `reset_to_original(raw_data_dir)` - Reset về original (no incidents)
  - `compare_graphs()` - So sánh original vs current (nodes, edges, diff)
  - `get_current_graph()` - Lấy current graph (với incidents applied)
- **Cache Files**:
  - `graph_original.pkl` - Original graph
  - `graph_current.pkl` - Current graph (with incidents)
  - `incidents.json` - Danh sách incidents hiện tại
  - `graph_metadata.json` - Metadata

#### **parsers.py** ⭐
- **Vai trò**: Đọc và bóc tách dữ liệu từ raw_data files
- **Hàm chính**:
  - `parse_stations(file_path)` - Đọc stations.json, trả về dict of Node objects
  - `parse_railway(file_path)` - Đọc railway.json
  - `parse_train_types(file_path)` - Đọc train_types.json
  - `parse_station_groups(file_path)` - Đọc station_groups.json
  - `load_json(file_path)` - Helper để load JSON file
- **Input Format**: Bóc tách từ JSON (id, name, coordinates)

#### **graph_builder.py** ⭐ CHÍNH
- **Vai trò**: Build toàn bộ graph từ raw data
- **Hàm chính**:
  - `build_tokyo_graph(stations_path, railway_path, train_types_path, groups_path)` - Main function
  - `add_bidirectional_edge()` - Thêm edge 2 chiều
  - `_add_edges_for_station_list()` - Thêm edges giữa các ga liên tiếp trên cùng tuyến
  - `_add_walk_edges()` - Thêm walking edges (transfer giữa các ga gần nhau)
- **Flow**:
  1. Parse stations từ stations.json
  2. Parse railways từ railway.json
  3. Thêm edges cho mỗi tuyến (bidirectional)
  4. Thêm walking edges giữa các ga gần nhau (<0.35 km)
  5. Clean graph (xóa duplicates, invalid edges)
  6. Validate graph

#### **incident_manager.py** ⭐
- **Vai trò**: Apply incidents lên graph
- **Hàm chính**:
  - `apply_incidents(graph, incidents)` - Apply danh sách incidents lên graph
  - `apply_incidents_data()` - Helper functions
- **Xử lý**:
  - STATION_CLOSED: Xóa node, xóa outgoing edges, xóa incoming edges từ các node khác
  - LINE_MAINTENANCE: Xóa tất cả edges thuộc tuyến đó
- **Cơ chế**: Tạo deepcopy graph, rồi apply incidents (không mutate original)

#### **station_group_resolver.py**
- **Vai trò**: Map tên ga → danh sách tất cả node IDs của ga đó
- **Mục đích**: Vì một ga có thể có nhiều node IDs (trên các tuyến khác nhau)
- **Hàm chính**:
  - `__init__(station_groups_path)` - Load station_groups.json
  - `resolve(station_name)` - Trả về list of node IDs cho một station name

### **utils/** - Thư mục Utilities

#### **geo_calc.py**
- **Mục đích**: Các hàm tính toán địa lý
- **Hàm chính**:
  - `haversine_distance(lat1, lon1, lat2, lon2)` - Tính khoảng cách giữa 2 điểm (km)
  - `find_nearest_station(lat, lon, nodes)` - Tìm ga gần nhất từ tọa độ

#### **logger.py**
- **Mục đích**: Setup logging cho data_system
- **Cấu hình**: Log level = CRITICAL (suppress hầu hết logs để tránh encoding issues trên Windows)
- **Hàm**: `setup_logger(name, level, log_file)`, `logger` (global instance)

#### **validators.py**
- **Mục đích**: Validate dữ liệu (có thể trống hoặc chưa implement)

### **raw_data/** - Dữ Liệu Thô (Static JSON Files)

#### **stations.json**
- **Mục đích**: Danh sách tất cả các ga ở Tokyo
- **Format**: Array of objects với fields: id, title (en/ja), coord [lon, lat]
- **Dữ liệu**: ~2499 stations

#### **railway.json**
- **Mục đích**: Danh sách tất cả các tuyến xe lửa/tàu điện ngầm
- **Format**: Array of objects với fields: id, title (en/ja), color, stations (list of station IDs)
- **Dữ liệu**: JR lines, Metro lines, Private railways

#### **train_types.json**
- **Mục đích**: Loại xe lửa (Shinkansen, Local, Express, v.v)
- **Format**: Dictionary hoặc array mô tả các loại tàu

#### **station_groups.json**
- **Mục đích**: Nhóm các ga có cùng tên nhưng trên các tuyến khác nhau
- **Format**: Array of arrays, mỗi array chứa list of node IDs
- **Ví dụ**: [["JR-East.Yamanote.Shinjuku", "JR-East.Saikyo.Shinjuku"], [...]]

### **cache/** - Thư mục Cache (Generated Files)
- **graph_original.pkl** - Original graph (pickle file)
- **graph_current.pkl** - Current graph with incidents (pickle file)
- **incidents.json** - Active incidents list
- **graph_metadata.json** - Metadata về graph

### **tests/** - Thư mục Tests

#### **test_graph_builder.py**
- **Mục đích**: Unit tests cho graph building
- **Test cases chính**:
  - `test_01_no_multi_graph_bug()` - Đảm bảo không có multi-edges trùng lặp
  - `test_02_edges_are_bidirectional()` - Đảm bảo tất cả edges đều 2 chiều
- **Coverage**: 30% của dữ liệu để test nhanh

#### **test_graph_manager.py**, **test_incidents.py**, **test_parsers.py**, **test_geo_calc.py**
- **Mục đích**: Tests cho các module khác

#### **visualize_graph.py**
- **Mục đích**: Script để visualize graph (debugging/development)

#### **testin.py**
- **Mục đích**: Sandbox test script

---

## 6. 📂 FRONTEND (Leaflet + JavaScript - Giao Diện Web)

### **Mục đích**: Giao diện web tương tác cho người dùng, hiển thị map và result route

### **index.html** ⭐ CHÍNH
- **Vai trò**: HTML structure chính
- **Nội dung**:
  - Header: "🗾 Tokyo Route Finder"
  - Sidebar: Search inputs (start/end station), radio buttons (priority), Find Route button, Reload Map button, Results panel
  - Main: Leaflet map container
  - Script imports: Leaflet library, CSS files, JS modules
- **Layout**: Flexbox (Header 60px, App Container: Sidebar 350px + Map flex)
- **Leaflet**: v1.9.4 từ CDN

### **css/main.css** ⭐
- **Mục đích**: Main CSS styling
- **Sections**:
  - Reset (reset.css)
  - Variables (variables.css)
  - Layout (header.css, map-container.css, sidebar.css)
  - Components (buttons.css, cards.css, inputs.css, modal.css)

#### **css/base/reset.css**
- **Mục đích**: CSS reset (margin, padding, box-sizing)

#### **css/base/variables.css**
- **Mục đích**: CSS variables (colors, spacing, fonts)
- **Variables chính**: 
  - Colors: PRIMARY, SECONDARY, TEXT, BACKGROUND
  - Spacing: GAP, PADDING, MARGIN
  - Header height: 60px

#### **css/layout/header.css**
- **Mục đích**: Styling cho header
- **Nội dung**: Height 60px, flexbox, title styling

#### **css/layout/sidebar.css**
- **Mục đích**: Styling cho sidebar
- **Nội dung**: Width 350px, search inputs, buttons, results panel

#### **css/layout/map-container.css**
- **Mục đích**: Styling cho map container
- **Nội dung**: Leaflet map styling, pane management

#### **css/components/buttons.css**, **inputs.css**, **cards.css**, **modal.css**
- **Mục đích**: Component styling

### **js/app.js** ⭐ CHÍNH
- **Vai trò**: Entry point, initialization logic
- **Hàm chính**:
  - `init()` - Main initialization function
  - `calculateAverageCoord(coords)` - Tính tọa độ trung bình
  - `buildUniqueStationGroups(stations)` - Group stations by name
- **Flow**:
  1. Tạo MapView
  2. Tạo UIControls
  3. Fetch stations từ API
  4. Render stations lên map
  5. Setup event listeners (search, find-path, reload)
  6. Gửi request tới backend khi user click "Find Route"
  7. Render path trên map

### **js/config.js**
- **Mục đích**: Config cho frontend
- **Nội dung**:
  - MAP_CENTER = [35.6895, 139.6917] (Tokyo)
  - DEFAULT_ZOOM = 12
  - STATION_DATA_PATH = './assets/data/stations.json'
  - API_BASE_URL = 'http://localhost:5000'
  - COLORS

### **js/components/map-view.js** ⭐
- **Vai trò**: Quản lý Leaflet map display
- **Class**: `MapView`
- **Hàm chính**:
  - `constructor(elementId)` - Initialize Leaflet map
  - `renderStations(stations)` - Render station markers lên map
  - `drawPath(pathData)` - Vẽ đường đi (polyline + station markers)
  - `focusOnStation(coord, name, type)` - Focus vào một ga
  - `focusOnRouteStation(coord)` - Focus vào ga từ route result
  - `clearStations()` - Xóa tất cả station markers
  - `reloadTiles()` - Reload tile layer
- **Features**:
  - Multiple layer groups: stationsLayer, routeMarkersLayer, startMarkerLayer, endMarkerLayer
  - Circle markers cho stations
  - Polyline cho route path
  - OpenStreetMap tiles

### **js/components/controls.js** ⭐
- **Vai trò**: Quản lý UI interactions (search, buttons, results)
- **Class**: `UIControls`
- **Hàm chính**:
  - `constructor()` - Setup event listeners
  - `setupStationSearch(type)` - Setup autocomplete cho start/end station
  - `setupReloadMapButton(callback)` - Setup reload map button
  - `onSearchRequested(callback)` - Callback khi user click "Find Route"
  - `showResults(route)` - Display route results trên sidebar
  - `populateStations(stations)` - Load stations để autocomplete
  - `buildStationGroups(stations)` - Group stations by name
- **Features**:
  - Real-time autocomplete khi type
  - Dropdown suggestions (max 100)
  - Click to select station
  - Display route steps (Board, Transfer, Arrive)
  - Click route step → Focus map vào ga đó

### **js/components/search-bar.js**
- **Mục đích**: Có thể chứa logic search riêng (hiện tại empty)

### **js/services/api.js**
- **Vai trò**: API calls tới backend
- **Hàm chính**:
  - `fetchStations()` - Lấy danh sách ga từ backend API (fallback: từ JSON file hoặc cached data)
- **Features**:
  - Try backend API first
  - Fallback to JSON file
  - Fallback to imported stationsData
  - UTF-8 encoding

### **js/services/routing-engine.js**
- **Vai trò**: Backend communication
- **Hàm chính**:
  - `findOptimalPath(stations, startId, endId, priority)` - Gửi request tới backend
- **Output**: Route result từ backend

### **js/data/stations-data.js**
- **Mục đích**: Fallback data (exported JavaScript module)
- **Nội dung**: Array of station objects (~2499 stations)
- **Sử dụng**: Khi API/file load fail

### **js/utils/helpers.js**
- **Mục đích**: Utility functions (hiện tại empty)

### **js/utils/formatters.js**
- **Mục đích**: Format functions (hiện tại empty)

### **assets/data/** - Dữ Liệu Tĩnh

#### **stations.json**
- **Mục đích**: Fallback station data cho frontend
- **Format**: Array of station objects
- **Dữ liệu**: ~2499 stations từ data_system

#### **railway.json**, **train_types.json**, **station_groups.json**
- **Mục đích**: Copy của raw data từ data_system

#### **main.py**
- **Mục đích**: Có thể là legacy Python file (không dùng)

### **READY.md**
- **Mục đích**: Status document về tính năng hoàn thành
- **Nội dung**: Các tính năng đã fix, working features, test instructions

### **SETUP_GUIDE.md**
- **Mục đích**: Hướng dẫn setup frontend

### **sever/** (typo - should be "server/")
- **main.py** - Có thể là simple static server script

---

## 7. 📂 TEST (Testing & Debugging)

### **event_manager.py**
- **Mục đích**: Có thể là test file hoặc helper cho event management

---

# 📊 ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Port 8000)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ index.html + CSS (Layout: Header + Sidebar + Map)     │ │
│  │ app.js (Init)                                         │ │
│  │ map-view.js (Leaflet rendering)                       │ │
│  │ controls.js (Search, buttons, results)                │ │
│  │ api.js (Fetch stations, call backend)                 │ │
│  │ config.js (Frontend config)                           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────────────────┘
               │ (HTTP POST /api/find-path)
               ▼
┌──────────────────────────────────────────────────────────────┐
│              BACKEND API (Flask, Port 5000)                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ app.py (Flask server, CORS enabled)                   │ │
│  │ services.py (Main logic, orchestration)               │ │
│  │ config.py (Backend config)                            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────┬────────────────────────────────────────────┬──────────┘
       │ (Get graph)                                 │ (Find route)
       ▼                                             ▼
┌──────────────────────┐               ┌──────────────────────┐
│  DATA SYSTEM         │               │  AI ENGINE           │
│  ┌────────────────┐  │               │  ┌────────────────┐  │
│  │ graph_manager  │  │               │  │ router.py      │  │
│  │ graph_builder  │  │               │  │ ┌────────────┐ │  │
│  │ incident_mgr   │  │               │  │ │ A* Algorithm│ │  │
│  │ parsers        │  │               │  │ │ Heuristic   │ │  │
│  │ models         │  │               │  │ └────────────┘ │  │
│  └────────────────┘  │               │  └────────────────┘  │
│        ▲             │               │                      │
│        │ (raw data)  │               │                      │
│        │             │               │                      │
│  ┌──────────────┐    │               │                      │
│  │  raw_data/   │    │               │                      │
│  │  ├─stations  │    │               │                      │
│  │  ├─railway   │    │               │                      │
│  │  ├─train     │    │               │                      │
│  │  └─groups    │    │               │                      │
│  └──────────────┘    │               │                      │
└──────────────────────┘               └──────────────────────┘

         │
         │ (Apply incidents)
         ▼
┌──────────────────────────────────────────────────────────────┐
│          ADMIN PANEL (Node.js Express, Port 5001)           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ server.js (Express server, 4 main endpoints)           │ │
│  │ admin.js (Frontend logic, state management)            │ │
│  │ admin.html + admin.css (UI)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│          ▲                                                   │
│          │ (Call Python scripts)                            │
│          ▼                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Python Scripts:                                        │ │
│  │ ├─ get_stations_lines.py (Get all stations/lines)     │ │
│  │ ├─ get_graph_status.py (Compare original vs current)  │ │
│  │ └─ rebuild_graph.py (Apply incidents, rebuild cache)  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

# 🔄 DATA FLOW - FIND ROUTE REQUEST

```
User clicks "Find Route"
    ↓
Frontend (controls.js) sends POST /api/find-path with:
{
  "startName": "Shinjuku",
  "endName": "Shibuya", 
  "criteria": "shortest_time"
}
    ↓
Backend (services.py) receives request:
1. Parse request (start_name, end_name, criteria)
2. Get GraphManager
3. Load current graph (with incidents applied) ← from cache
4. Find node IDs by station names
5. Build search graph format
    ↓
AI Engine (router.py):
1. Receive search graph + start nodes + end nodes + criteria
2. Run A* algorithm with heuristic function
3. Return route: {path: [...], total_time, total_cost, transfers, details}
    ↓
Backend (services.py) continues:
6. Get path coordinates từ nodes
7. Format response with pathCoords, details
    ↓
Frontend (app.js) receives response:
1. Render path trên map (polyline + markers)
2. Display route steps trên sidebar (Board → Transfer → Arrive)
3. Setup click handlers (click step → focus map)
```

---

# 🔄 DATA FLOW - APPLY INCIDENT

```
Admin clicks "Apply Incident" on admin panel
    ↓
Admin Panel (admin.js) sends POST /api/apply-incident with:
{
  "action": "apply",
  "target_id": "JR-East.Yamanote.Shinjuku",
  "type": "STATION_CLOSED"
}
    ↓
Admin Panel Server (server.js) receives request:
1. Validate input
2. Add incident to currentIncidents array
3. Call rebuildGraph() function
    ↓
rebuildGraph() executes Python script:
cd data_system && python rebuild_graph.py '[...incidents...]'
    ↓
Python (rebuild_graph.py):
1. Parse incidents from JSON
2. Load original graph from cache
3. Apply incidents (remove nodes/edges)
4. Compare original vs current
5. Save current graph to cache
6. Output JSON with stats
    ↓
Admin Panel Server:
1. Parse Python output
2. Update currentIncidents
3. Return response to admin panel
    ↓
Admin Panel (admin.js):
1. Update UI: show active incidents list
2. Show graph status (nodes/edges removed)
3. Success message
```

---

# ⚙️ KEY TECHNOLOGIES

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Frontend** | HTML/CSS/JavaScript ES6 | - | UI & User interactions |
| **Map Library** | Leaflet | 1.9.4 | Interactive map display |
| **Backend** | Flask | Latest | REST API server |
| **Admin Panel** | Node.js + Express | 14+ | Web server for admin |
| **Data Processing** | Python | 3.10+ | Graph building, incidents |
| **Routing Algorithm** | A* | Custom | Optimal path finding |
| **Graph Cache** | Pickle | - | Store/load graphs |
| **Data Storage** | JSON | - | Raw station/railway data |

---

# 🎯 SUMMARY TABLE

| Directory | Main Files | Purpose |
|-----------|-----------|---------|
| **Root** | Flow.md, README.md, Ruleset.md | Documentation |
| **admin_panel/** | server.js, admin.js | Admin UI, incident management |
| **ai_engine/** | router.py | A* routing algorithm |
| **backend_api/** | app.py, services.py | Flask REST API |
| **data_system/** | graph_manager, graph_builder, incident_manager | Graph management, incident handling |
| **data_system/core/** | models.py, parsers.py | Data structures, file parsing |
| **data_system/raw_data/** | stations.json, railway.json | Static Tokyo transit data |
| **data_system/tests/** | test_*.py | Unit tests |
| **frontend/** | index.html, app.js | Web UI, user interface |
| **frontend/js/** | map-view.js, controls.js, api.js | Frontend components |
| **frontend/css/** | main.css, components/* | Styling |

---

# 🚀 HOW TO RUN

```bash
# 1. Terminal 1: Backend API
cd backend_api
python app.py  # Listens on http://localhost:5000

# 2. Terminal 2: Frontend
cd frontend
python -m http.server 8000  # Listens on http://localhost:8000

# 3. Terminal 3 (Optional): Admin Panel
cd admin_panel
npm install
npm start  # Listens on http://localhost:5001

# Open browser: http://localhost:8000
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-04  
**Status**: Complete & Comprehensive
