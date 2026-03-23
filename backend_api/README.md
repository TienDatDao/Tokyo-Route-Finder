# Hệ thống Backend API cho Tokyo Route Finder

## 1. Tổng quan
Module `backend_api` đóng vai trò là "trạm trung chuyển" dữ liệu giữa **Frontend** (Giao diện người dùng) và các hệ thống lõi (**Data System & AI Engine**). Hệ thống cung cấp các HTTP Endpoints để tiếp nhận yêu cầu tìm đường, điều phối logic xử lý và trả về kết quả dưới định dạng JSON.



## 2. Cấu trúc Thư mục
```plaintext
backend_api/
├── .gitkeep
├── app.py                  # File chạy chính (Flask Server)
├── config.py               # Cấu hình Host, Port, Debug mode
├── main.py
├── README.md               # Tài liệu hướng dẫn
└── services.py             # Logic điều phối giữa Data và AI
```

## 3. Cách Hoạt động

### 1. Tiếp nhận yêu cầu (`app.py`)
* Sử dụng **Flask** để tạo RESTful API.
* Mở cấu hình **CORS** để cho phép Frontend (mặc định Port 8000) truy vấn dữ liệu.
* **Endpoint chính:** `POST /find_route`

### 2. Điều phối Logic (`services.py`)
Nhận dữ liệu thô từ `app.py`, sau đó thực hiện các bước:
1.  Gọi `data_manager` để lấy đồ thị (Graph).
2.  Tìm kiếm Node dựa trên tên ga người dùng nhập.
3.  Chuyển thông tin cho `ai_engine` để tìm lộ trình tối ưu.

### 3. Cấu hình (`config.py`)
Quản lý các thông số vận hành server như `HOST`, `PORT`, và chế độ `DEBUG`.

---

## 4. Các Endpoints Chính

| Phương thức | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `POST` | `/find_route` | Nhận tên ga đi/đến, trả về lộ trình tối ưu |

---

## 5. Lưu ý về các Hàm Đang Phát Triển (Placeholders)
Hiện tại, Backend đang sử dụng các hàm tạm thời (tên tượng trưng) để hoàn thiện luồng xử lý. Các hàm này sẽ được cập nhật khi các Module liên quan hoàn tất:

* **`get_nodes_by_name(name)`** (Dự kiến thuộc *data_system*):
    * **Trạng thái:** Chờ Data Team cung cấp.
    * **Mục tiêu:** Chuyển đổi tên ga (String) thành ID hoặc Object Node.
* **`find_optimal_path(graph, start, end)`** (Dự kiến thuộc *ai_engine*):
    * **Trạng thái:** Chờ AI Team cung cấp.
    * **Mục tiêu:** Thực hiện thuật toán tìm đường ($Dijkstra$ hoặc $A^*$) trên đồ thị.

---

## 6. Ví dụ Sử dụng API

### Yêu cầu (Request)
```json
{
  "start_name": "Shinjuku",
  "end_name": "Shibuya"
}
```

### Phản hồi (Response - Dự kiến)
```json
{
  "status": "success",
  "route": ["Shinjuku", "Yoyogi", "Harajuku", "Shibuya"],
  "total_time": 12,
  "total_cost": 160
}
```

---

## 7. Hướng dẫn Khởi chạy

**Bước 1: Cài đặt thư viện**
```bash
pip install flask flask-cors
```

**Bước 2: Chạy Server**
```powershell
python -m backend_api.app
```
