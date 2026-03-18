# HỆ THỐNG TÌM ĐƯỜNG ĐI NGẮN NHẤT (SHORTEST PATH SYSTEM)

Tài liệu này đặc tả các Interface trao đổi dữ liệu giữa các thành phần: **Frontend**, **Backend**, **Data System**, và **AI Engine**.

---

## 1. Interface: UI gửi yêu cầu tới Backend (Request)

**Frontend** thu thập vị trí người dùng và tiêu chí tìm kiếm, gửi về Backend dưới định dạng file **json** sau:

```json
{ 
  "start_point": { 
    "input_type": "STATION_ID",  
    "value": "JR-East.Yamanote.Shinjuku" 
  }, 
  "end_point": { 
    "input_type": "COORDINATE",  
    "value": { 
      "lat": 35.6585,  
      "lon": 139.7454 
    } 
  }, 
  "preferences": { 
    "optimize_by": "shortest_time" 
  } 
} 
```

Lưu ý: `criteria` có thể là: `shortest_time`, `least_transfers`, `lowest_cost`.

## 2. Interface: Backend gọi Data System

Backend gọi Data System để lấy bản đồ hiện tại. Data System có nhiệm vụ loại bỏ các ga đang đóng cửa hoặc tuyến đường đang bảo trì trước khi trả về dữ liệu "sạch". Data System sẽ viết hàm `get_clean_map_data()` để Backend gọi và trả về graph dưới dạng **dictionary** như sau.

**Dữ liệu trả về từ Data System cho Backend (Đồ thị đã xử lý):**

```python
#kiểu dữ liệu dictionary trong python
raw_graph = {
  "Shinjuku": {
    "metadata": {
      "lat": 35.6897,
      "lon": 139.7004,
      "name_en": "Shinjuku",
      "is_active": true
    },
    "connections": {
      "Yoyogi": {
        "time": 3,
        "cost": 160,
        "line": "Yamanote Line",
        "distance": 2.7
      },
      "Shibuya": {
        "time": 5,
        "cost": 160,
        "line": "Saikyo Line",
        "distance": 4.2
      }
    }
  },
  "Yoyogi": {
    "metadata": {
      "lat": 35.6830,
      "lon": 139.7020,
      "name_en": "Yoyogi",
      "is_active": true
    },
    "connections": {
      "Shinjuku": {
        "time": 3,
        "cost": 160,
        "line": "Yamanote Line",
        "distance": 2.7
      },
      "Harajuku": {
        "time": 2,
        "cost": 160,
        "line": "Yamanote Line",
        "distance": 1.5
      }
    }
  }
}
```

**Quy tắc:** Nếu một ga (ví dụ: Shibuya) có sự cố `station_closed`, Data System phải xóa ga đó khỏi danh sách kết nối trước khi gửi cho AI Engine.

## 3. Interface: Backend gửi dữ liệu cho AI Engine (Input cho thuật toán)

Backend tổng hợp dữ liệu từ Data System và yêu cầu của User để gửi cho AI Engine  thực hiện thuật toán Dijkstra hoặc A*. File **dictionary** dưới đây giúp AI Engine biết được kiểu mình sẽ nhận vào.

```python
#kiểu dữ liệu dictionary trong python
graph = {
    "Shinjuku": {
        "metadata": {
            "lat": 35.6897,
            "lon": 139.7004,
            "name_en": "Shinjuku",
            "is_active": True
        },
        "connections": {
            "Yoyogi": {
                "time": 3,
                "cost": 160,
                "line": "Yamanote Line",
                "distance": 2.7
            },
            "Shibuya": {
                "time": 5,
                "cost": 160,
                "line": "Saikyo Line",
                "distance": 4.2
            }
        }
    },
    "Yoyogi": {
        "metadata": {
            "lat": 35.6830,
            "lon": 139.7020,
            "name_en": "Yoyogi",
            "is_active": True
        },
        "connections": {
            "Shinjuku": { "time": 3, "cost": 160, "line": "Yamanote Line", "distance": 2.7 },
            "Harajuku": { "time": 2, "cost": 160, "line": "Yamanote Line", "distance": 1.5 }
        }
    }
}
```

## 4. Interface: AI Engine trả kết quả cho Backend (Output thuật toán)

Khi cần, backend sẽ gọi hàm `find_optimal_route(graph, start_station, end_station, criteria)` trong file `router` của bên AI, khi đó bên AI sẽ trả lại 1 **dictionary** theo dạng có mẫu sau.

```python
#kiểu dữ liệu dictionary trong python
optimal_route = {
    "status": "SUCCESS",
    "path": ["Shinjuku", "Yoyogi", "Shibuya"],
    "total_time": 8,
    "total_cost": 320,
    "transfers": 1,
}
```

**Trạng thái phản hồi:** Có thể là `SUCCESS` hoặc `NO_ROUTE_FOUND` nếu không tìm thấy đường đi.

## 5. Interface: Backend trả phản hồi cuối cùng cho UI (Response)

Backend định dạng lại kết quả, tính toán thông tin đi bộ và chi tiết hành động để gửi cho UI hiển thị dưới dạng file **json**

```json
{ 
  "status": "SUCCESS", 
  "suggested_start_station": { 
    "id": "JR-East.Yamanote.Shinjuku", 
    "name": "Shinjuku" 
  }, 
  "walking_info": { 
    "distance_meters": 450, 
    "estimated_walking_minutes": 6 
  }, 
  "route": { 
    "path": [ 
      "JR-East.Yamanote.Shinjuku", 
      "JR-East.ChuoSobuLocal.Yoyogi", 
      "JR-East.ChuoRapid.Tokyo" 
    ], 
    "total_time": 25, 
    "total_cost": 400, 
    "transfers": 1,
    "details": [ 
      { 
        "station_id": "JR-East.Yamanote.Shinjuku", 
        "station_name": "Shinjuku", 
        "line": "Yamanote Line", 
        "action": "Board" 
      }, 
      { 
        "station_id": "JR-East.ChuoSobuLocal.Yoyogi", 
        "station_name": "Yoyogi", 
        "line": "Chuo Line", 
        "action": "Transfer" 
      }, 
      { 
        "station_id": "JR-East.ChuoRapid.Tokyo", 
        "station_name": "Tokyo", 
        "line": "Chuo Line", 
        "action": "Exit" 
      }
    ]
  } 
} 
```
