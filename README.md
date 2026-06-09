# Tokyo-Route-Finder
Tokyo Route Finder là ứng dụng tìm đường trên bản đồ Tokyo, hiển thị lộ trình tốt nhất bằng cách sử dụng backend Flask và frontend Leaflet.

## Cách chạy

### 1. Chạy Backend

1. Mở terminal và điều hướng vào thư mục `backend_api`:
   ```bash
   cd d:\AI\Tokyo-Route-Finder\backend_api
   ```
2. Cài đặt thư viện nếu chưa có:
   ```bash
   pip install flask flask-cors
   ```
3. Chạy server:
   ```bash
   python app.py
   ```
4. Backend sẽ lắng nghe tại:
   - `http://127.0.0.1:5000`
   - `http://localhost:5000`

### 2. Chạy Frontend

1. Mở terminal khác và điều hướng vào `frontend`:
   ```bash
   cd d:\AI\Tokyo-Route-Finder\frontend
   ```
2. Chạy server tĩnh:
   ```bash
   python -m http.server 8000
   ```
3. Mở trình duyệt vào:
   - `http://localhost:8000`

### 3. Chạy Admin Panel

1. Mở terminal mới và điều hướng vào `admin_panel`:
   ```bash
   cd d:\AI\Tokyo-Route-Finder\admin_panel
   ```
2. Cài đặt dependencies (chỉ cần lần đầu):
   ```bash
   npm install
   ```
3. Chạy server Admin Panel:
   ```bash
   npm start
   ```
   hoặc
   ```bash
   node server.js
   ```
4. Mở trình duyệt vào:
   - `http://localhost:5001`

**Lưu ý**: Admin panel sẽ kết nối với Python scripts để quản lý sự cố (đóng ga, bảo trì tuyến)

## Tính năng đã cập nhật

- Đường đi được vẽ bằng **đường màu xanh** (blue) dưới các điểm ga.
- Các ga trên lộ trình được hiển thị bằng **chấm tròn màu xanh lá**.
- Danh sách kết quả chỉ hiển thị các bước quan trọng: **Board, Transfer, Arrive**.
- **Các bước Continue / đi tiếp đơn giản** sẽ không được liệt kê trong bảng hướng dẫn.
- Khi click vào bước trong danh sách, bản đồ sẽ **bay tới vị trí ga tương ứng**.
- Giao diện giữ nguyên tìm kiếm khởi hành và đích, không còn chức năng chặn ga/tuyến.

## Cấu trúc chính

- `backend_api/app.py`: Flask server xử lý endpoint `/api/find-path`.
- `backend_api/services.py`: Điều phối tìm đường từ Data System và AI Engine.
- `frontend/index.html`: Giao diện chính.
- `frontend/js/app.js`: Khởi tạo map và gọi API.
- `frontend/js/components/map-view.js`: Quản lý hiển thị bản đồ, tô màu ga và đường đi.
- `frontend/js/components/controls.js`: Quản lý tìm kiếm, hiển thị kết quả và xử lý click ga.

## Lưu ý

- Nếu backend không chạy, frontend sẽ không nhận được kết quả tìm đường.
- Nếu bạn muốn thay đổi host/port backend, chỉnh `backend_api/config.py`.
