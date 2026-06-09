# 🚀 Admin Panel - Tokyo Route Finder

English | [Tiếng Việt](#hướng-dẫn-tiếng-việt)

## Overview

The Admin Panel is a web-based management interface for Tokyo Route Finder. It allows administrators to:
- Monitor the current state of the railway network
- Create and manage incidents (station closures, line maintenance)
- View real-time incident information
- Automatically rebuild the route graph when incidents are applied

## Prerequisites

Before running the Admin Panel, ensure you have:

- **Node.js 14.0+** - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Python 3.10+** - Required for data system integration
- **Port 5001** - Must be available (not in use by other services)
- **Git** (optional, for cloning the repository)

### Verify Installation

```bash
node --version  # Should show v14.0 or higher
npm --version   # Should show 6.0 or higher
python --version  # Should show 3.10 or higher
```

## Installation

### Step 1: Navigate to Admin Panel Directory

```bash
cd d:\AI\Tokyo-Route-Finder\admin_panel
```

### Step 2: Install Dependencies

Run this command only once (the first time):

```bash
npm install
```

This will install the required Node.js packages:
- `express`: Web framework
- `cors`: Cross-Origin Resource Sharing
- `body-parser`: Middleware for parsing request bodies
- `axios`: HTTP client library

## Running the Admin Panel

### Method 1: Using npm script (Recommended)

```bash
npm start
```

### Method 2: Direct Node.js execution

```bash
node server.js
```

### Expected Output

You should see output similar to:

```
Admin panel server running on port 5001
```

### Access the Admin Panel

Open your web browser and navigate to:

```
http://localhost:5001
```

## Features

### 1. Apply Incidents
- **Incident Types**:
  - 🚫 **Station Closed** (`STATION_CLOSED`): Temporarily close a station
  - 🔧 **Line Maintenance** (`LINE_MAINTENANCE`): Close an entire railway line
  
- **How to Use**:
  1. Select incident type from dropdown
  2. Choose a station or line from the list
  3. Click "Apply Incident" button
  4. The route graph will automatically rebuild
  5. The frontend will reflect the changes in real-time

### 2. View Active Incidents
- Real-time display of all currently active incidents
- Shows incident ID, type, and affected station/line
- Click "Remove" button to delete individual incidents

### 3. Reset All Incidents
- Click "Reset All" button to remove all incidents at once
- The network returns to normal operation
- Graph rebuilds automatically

### 4. System Information
- View total number of stations
- View total number of lines
- View number of active incidents
- Monitor system status

## API Endpoints

The admin panel provides these REST API endpoints:

### GET /api/stations-and-lines
Retrieves all stations and lines in the network.

**Response Example:**
```json
{
  "stations": [
    {
      "station_id": "1001",
      "name_en": "Tokyo",
      "name_ja": "東京"
    }
  ],
  "lines": [
    {
      "line_id": "L001",
      "name_en": "Yamanote Line",
      "name_ja": "山手線"
    }
  ]
}
```

### POST /api/apply-incident
Applies or removes an incident.

**Request Body:**
```json
{
  "action": "apply",
  "target_id": "1001",
  "type": "STATION_CLOSED"
}
```

**Parameters:**
- `action`: `"apply"` or `"remove"`
- `target_id`: Station ID or Line ID
- `type`: `"STATION_CLOSED"` or `"LINE_MAINTENANCE"`

## Troubleshooting

### Port 5001 Already in Use

If you get an error that port 5001 is already in use:

**Option 1: Find and stop the process using port 5001**
```bash
netstat -ano | findstr :5001  # Find the process ID
taskkill /PID <PID> /F         # Kill the process (replace <PID> with the actual ID)
```

**Option 2: Change the port in server.js**
Edit `server.js` and change:
```javascript
const PORT = 5001;  // Change 5001 to another port like 5002
```

### Python Script Execution Errors

If you get errors about Python scripts not executing:

1. Verify Python is installed: `python --version`
2. Check that data_system directory exists and has required Python files
3. Ensure Python is added to your system PATH

### Cannot Connect to Admin Panel

- Check that the server is running (look for the "running on port 5001" message)
- Make sure port 5001 is not blocked by firewall
- Try accessing `http://127.0.0.1:5001` instead of `http://localhost:5001`

### Incidents Not Appearing on Frontend

- Ensure the frontend is running and connected to the backend API
- Check browser console for any JavaScript errors
- Verify the graph has been rebuilt after applying the incident

## Project Structure

```
admin_panel/
├── server.js              # Express server (main entry point)
├── package.json           # Node.js dependencies
├── README.md              # This file
├── SETUP.md              # Detailed setup guide (Vietnamese)
├── admin.html            # Main HTML interface
├── admin.css             # Styling
├── admin.js              # Frontend JavaScript logic
└── public/               # Static assets
    ├── index.html
    ├── css/
    └── js/
```

## Integration with Other Components

### Backend API
- **Location**: `../backend_api/app.py`
- **Port**: 5000
- **Function**: Handles route finding requests

### Frontend
- **Location**: `../frontend/index.html`
- **Port**: 8000
- **Function**: Main user interface for route finding

### Data System
- **Location**: `../data_system/`
- **Function**: Manages graph building and incident handling

## Notes

- **Data Persistence**: Incidents are stored in server memory. They will be lost if the server restarts.
- **Graph Rebuild Time**: Building the graph with incidents may take a few seconds depending on data size.
- **Concurrent Usage**: The admin panel should be the only tool modifying the graph to avoid conflicts.
- **Auto-reload**: The graph is automatically rebuilt when incidents are applied or removed.

## Support & Debugging

### Enable Verbose Logging

Edit `server.js` and add console.log statements to track operations:

```javascript
console.log('Processing incident:', { action, target_id, type });
```

### Check Network Requests

Open browser DevTools (F12) and go to the **Network** tab to inspect API calls.

---

# 🚀 Admin Panel - Tokyo Route Finder

## Hướng Dẫn Tiếng Việt

## Tổng Quan

Admin Panel là giao diện quản lý nền tảng web cho Tokyo Route Finder. Nó cho phép quản trị viên:
- Theo dõi trạng thái của mạng đường sắt
- Tạo và quản lý sự cố (đóng cửa ga, bảo trì tuyến)
- Xem thông tin sự cố real-time
- Tự động rebuild graph khi sự cố được áp dụng

## Yêu Cầu Hệ Thống

Trước khi chạy Admin Panel, hãy đảm bảo bạn có:

- **Node.js 14.0+** - [Tải tại đây](https://nodejs.org/)
- **npm** (đi kèm với Node.js)
- **Python 3.10+** - Cần thiết cho tích hợp data system
- **Cổng 5001** - Phải có sẵn (không bị chiếm dụng)
- **Git** (tùy chọn, để clone repository)

### Kiểm Tra Cài Đặt

```bash
node --version  # Phải ≥ v14.0
npm --version   # Phải ≥ 6.0
python --version  # Phải ≥ 3.10
```

## Cài Đặt

### Bước 1: Điều Hướng Vào Thư Mục Admin Panel

```bash
cd d:\AI\Tokyo-Route-Finder\admin_panel
```

### Bước 2: Cài Đặt Dependencies

Chạy lệnh này chỉ một lần (lần đầu tiên):

```bash
npm install
```

Lệnh này sẽ cài đặt các gói Node.js cần thiết:
- `express`: Web framework
- `cors`: Hỗ trợ Cross-Origin
- `body-parser`: Parser middleware
- `axios`: HTTP client

## Chạy Admin Panel

### Cách 1: Sử Dụng npm script (Khuyến Nghị)

```bash
npm start
```

### Cách 2: Chạy trực tiếp Node.js

```bash
node server.js
```

### Kết Quả Mong Đợi

Bạn sẽ thấy thông báo tương tự như:

```
Admin panel server running on port 5001
```

### Truy Cập Admin Panel

Mở trình duyệt web và điều hướng đến:

```
http://localhost:5001
```

## Các Tính Năng

### 1. Áp Dụng Sự Cố
- **Loại Sự Cố**:
  - 🚫 **Đóng Cửa Ga** (`STATION_CLOSED`): Tạm đóng một ga
  - 🔧 **Bảo Trì Tuyến** (`LINE_MAINTENANCE`): Đóng toàn bộ một tuyến đường sắt
  
- **Cách Sử Dụng**:
  1. Chọn loại sự cố từ dropdown
  2. Chọn ga hoặc tuyến từ danh sách
  3. Nhấn nút "Áp Dụng Sự Cố"
  4. Graph sẽ tự động rebuild
  5. Frontend sẽ phản ánh thay đổi real-time

### 2. Xem Các Sự Cố Đang Hoạt Động
- Hiển thị real-time tất cả sự cố đang hoạt động
- Hiển thị ID sự cố, loại, và ga/tuyến bị ảnh hưởng
- Nhấn nút "Xóa" để xóa từng sự cố

### 3. Reset Tất Cả Sự Cố
- Nhấn nút "Reset Tất Cả" để xóa tất cả sự cố
- Mạng đường sắt quay lại trạng thái bình thường
- Graph tự động rebuild

### 4. Thông Tin Hệ Thống
- Xem tổng số ga
- Xem tổng số tuyến
- Xem số sự cố đang hoạt động
- Theo dõi trạng thái hệ thống

## API Endpoints

Admin panel cung cấp các REST API endpoints:

### GET /api/stations-and-lines
Lấy tất cả các ga và tuyến trong mạng.

**Ví Dụ Response:**
```json
{
  "stations": [
    {
      "station_id": "1001",
      "name_en": "Tokyo",
      "name_ja": "東京"
    }
  ],
  "lines": [
    {
      "line_id": "L001",
      "name_en": "Yamanote Line",
      "name_ja": "山手線"
    }
  ]
}
```

### POST /api/apply-incident
Áp dụng hoặc xóa một sự cố.

**Request Body:**
```json
{
  "action": "apply",
  "target_id": "1001",
  "type": "STATION_CLOSED"
}
```

**Tham Số:**
- `action`: `"apply"` hoặc `"remove"`
- `target_id`: ID ga hoặc ID tuyến
- `type`: `"STATION_CLOSED"` hoặc `"LINE_MAINTENANCE"`

## Khắc Phục Sự Cố

### Cổng 5001 Đã Được Sử Dụng

Nếu nhận lỗi cổng 5001 đã được sử dụng:

**Cách 1: Tìm và dừng tiến trình sử dụng cổng 5001**
```bash
netstat -ano | findstr :5001  # Tìm Process ID
taskkill /PID <PID> /F         # Kết thúc tiến trình
```

**Cách 2: Thay đổi cổng trong server.js**
Chỉnh sửa `server.js` và thay đổi:
```javascript
const PORT = 5001;  // Đổi 5001 thành cổng khác như 5002
```

### Lỗi Thực Thi Python Script

Nếu nhận lỗi về Python scripts:

1. Kiểm tra Python được cài: `python --version`
2. Kiểm tra thư mục data_system tồn tại và có file Python cần thiết
3. Đảm bảo Python được thêm vào system PATH

### Không Thể Kết Nối Admin Panel

- Kiểm tra server đang chạy (tìm thông báo "running on port 5001")
- Đảm bảo cổng 5001 không bị firewall chặn
- Thử truy cập `http://127.0.0.1:5001` thay vì `http://localhost:5001`

### Sự Cố Không Hiển Thị Trên Frontend

- Đảm bảo frontend đang chạy và kết nối với backend API
- Kiểm tra browser console có JavaScript errors
- Xác minh graph đã rebuild sau khi áp dụng sự cố

## Cấu Trúc Dự Án

```
admin_panel/
├── server.js              # Express server (điểm vào chính)
├── package.json           # Node.js dependencies
├── README.md              # File này
├── SETUP.md              # Hướng dẫn cài đặt chi tiết
├── admin.html            # Giao diện HTML chính
├── admin.css             # CSS styling
├── admin.js              # Frontend JavaScript logic
└── public/               # Static assets
    ├── index.html
    ├── css/
    └── js/
```

## Tích Hợp Với Các Thành Phần Khác

### Backend API
- **Vị Trí**: `../backend_api/app.py`
- **Cổng**: 5000
- **Chức Năng**: Xử lý yêu cầu tìm đường

### Frontend
- **Vị Trí**: `../frontend/index.html`
- **Cổng**: 8000
- **Chức Năng**: Giao diện chính cho người dùng

### Data System
- **Vị Trí**: `../data_system/`
- **Chức Năng**: Quản lý xây dựng graph và xử lý sự cố

## Lưu Ý Quan Trọng

- **Lưu Trữ Dữ Liệu**: Sự cố được lưu trong bộ nhớ server. Chúng sẽ bị mất nếu server restart.
- **Thời Gian Rebuild Graph**: Xây dựng graph với sự cố có thể mất vài giây tùy vào kích thước dữ liệu.
- **Sử Dụng Đồng Thời**: Admin panel nên là công cụ duy nhất sửa đổi graph để tránh xung đột.
- **Tự Động Rebuild**: Graph được tự động rebuild khi sự cố được áp dụng hoặc xóa.

## Hỗ Trợ & Debug

### Bật Verbose Logging

Chỉnh sửa `server.js` và thêm console.log để theo dõi hoạt động:

```javascript
console.log('Processing incident:', { action, target_id, type });
```

### Kiểm Tra Network Requests

Mở DevTools (F12) và chuyển sang tab **Network** để kiểm tra các API calls.

