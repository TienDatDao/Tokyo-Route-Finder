# 🚀 Hướng Dẫn Chạy Admin Panel

## Chuẩn Bị Môi Trường

### 1. Cài đặt Dependencies Node.js

Mở PowerShell và điều hướng vào thư mục `admin_panel`:

```powershell
cd C:\Users\hieuv\PycharmProjects\Tokyo-Route-Finder\admin_panel
npm install
```

## Chạy Admin Panel

### 1. Khởi động Server Admin Panel

Chạy lệnh sau từ thư mục `admin_panel`:

```powershell
npm start
```

hoặc:

```powershell
node server.js
```

Admin panel sẽ chạy tại: **http://localhost:5001**

## Sử Dụng Admin Panel

### Các Tính Năng

1. **Áp Dụng Sự Cố**
   - Chọn loại sự cố: "Đóng Cửa Ga" hoặc "Bảo Trì Tuyến"
   - Chọn ga/tuyến từ danh sách
   - Nhấn nút "Áp Dụng" để áp dụng sự cố
   - Bản đồ sẽ được rebuild tự động

2. **Xem Sự Cố Đang Hoạt Động**
   - Danh sách các sự cố hiện tại được hiển thị real-time
   - Có thể xóa từng sự cố bằng nút "Xóa"

3. **Reset Tất Cả Sự Cố**
   - Nhấn nút "Reset Tất Cả" để xóa tất cả sự cố
   - Bản đồ sẽ quay về trạng thái bình thường

4. **Thông Tin Hệ Thống**
   - Xem tổng số ga, tuyến và sự cố hoạt động

## Yêu Cầu

- Node.js 14.0+ đã được cài đặt
- Python 3.10+ để chạy data_system
- Cổng 5001 không bị chiếm dụng
- Backend Flask (port 5000) và Frontend (port 8000) chạy song song (nếu cần)

## Lưu Ý

- Mỗi lần áp dụng/xóa sự cố, admin panel sẽ gọi Python script để rebuild graph
- Quá trình rebuild có thể mất vài giây tùy thuộc vào kích thước dữ liệu
- Sự cố được lưu trong bộ nhớ của server, nếu restart server sẽ mất dữ liệu

