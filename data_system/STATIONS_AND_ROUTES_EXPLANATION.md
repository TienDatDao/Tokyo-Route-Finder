# Giải Thích Về Ga Và Tuyến Đường Trong Dự Án Tokyo-Route-Finder

## Tổng Quan

Dự án Tokyo-Route-Finder xây dựng một hệ thống tìm đường đi trong mạng lưới tàu điện ngầm và đường sắt của Tokyo. Hệ thống dựa trên một đồ thị (graph) đại diện cho các ga (stations) và các tuyến đường (routes/lines) kết nối chúng. Đồ thị này được xây dựng từ dữ liệu thô và cho phép tính toán tuyến đường tối ưu dựa trên thời gian, chi phí hoặc số lần chuyển tuyến.

## Cấu Trúc Dữ Liệu

### 1. Ga (Stations)
- **Nguồn dữ liệu**: `raw_data/stations.json`
- **Cấu trúc**: Mỗi ga là một object JSON với các trường:
  - `id`: Mã định danh duy nhất của ga (ví dụ: "JR-East.Yamanote.Shinjuku")
  - `railway`: Tuyến đường chính mà ga thuộc về (ví dụ: "JR-East.Yamanote")
  - `coord`: Tọa độ [longitude, latitude] (ví dụ: [139.70149, 35.65796])
  - `title`: Tên ga đa ngôn ngữ (ja, en, ko, zh-Hans, zh-Hant)
  - `thumbnail`: Hình ảnh thumbnail (tùy chọn)

- **Ví dụ**:
```json
{
  "id": "JR-East.Yamanote.Shibuya",
  "railway": "JR-East.Yamanote",
  "coord": [139.70149, 35.65796],
  "title": {
    "ja": "渋谷",
    "en": "Shibuya",
    "ko": "시부야",
    "zh-Hans": "涩谷",
    "zh-Hant": "澀谷"
  }
}
```

### 2. Tuyến Đường (Railways/Lines)
- **Nguồn dữ liệu**: `raw_data/railway.json`
- **Cấu trúc**: Mỗi tuyến là một object JSON với các trường:
  - `id`: Mã định danh tuyến (ví dụ: "JR-East.Yamanote")
  - `title`: Tên tuyến đa ngôn ngữ
  - `stations`: Mảng các ID ga theo thứ tự trên tuyến
  - `ascending`/`descending`: Hướng đi (OuterLoop/InnerLoop)
  - `color`: Màu sắc đại diện tuyến trên bản đồ
  - `carComposition`: Số toa tàu

- **Ví dụ**: Tuyến Yamanote Line bao gồm các ga từ Osaki đến Shinagawa theo vòng tròn.

### 3. Nhóm Ga (Station Groups/Complexes)
- **Nguồn dữ liệu**: `raw_data/station_groups.json`
- **Cấu trúc**: Mảng các "complex" (nhóm ga), mỗi complex là mảng các "fare_zone" (khu vực soát vé), mỗi fare_zone là mảng ID ga.
- **Mục đích**: Đại diện cho các ga kết nối với nhau bằng đường đi bộ trong cùng khu vực (như ga trung chuyển).

- **Ví dụ**:
```json
[[
  "JR-East.Yamanote.Shibuya",
  "JR-East.SaikyoKawagoe.Shibuya",
  "JR-East.ShonanShinjuku.Shibuya"
], [
  "TokyoMetro.Ginza.Shibuya"
]]
```
Ở đây, Shibuya có nhiều ga từ các tuyến khác nhau, chia thành các fare_zone riêng biệt.

## Cách Xây Dựng Đồ Thị

Đồ thị được xây dựng trong `core/graph_builder.py` từ 4 file JSON trên.

### 1. Nodes (Ga)
- Mỗi ga trong `stations.json` trở thành một node trong đồ thị.
- Node chứa: id, name (từ title.en), lat, lon.

### 2. Edges (Tuyến Đường)
Có hai loại edges:

#### a. Edges Tàu (Train Edges)
- Nguồn: `railway.json`
- Cách tạo: Nối các ga liền kề trong danh sách `stations` của mỗi tuyến.
- Thuộc tính:
  - `edge_type`: "train"
  - `line`: Tên tuyến (ví dụ: "Yamanote Line")
  - `time`: Thời gian di chuyển = (khoảng cách / tốc độ tàu) * 60 phút
  - `cost`: Chi phí cố định (config.TRAIN_COST_YEN)
  - `distance`: Khoảng cách Haversine giữa 2 ga

#### b. Edges Đi Bộ (Walk Edges)
- Nguồn: `station_groups.json`
- Cách tạo: Nối tất cả cặp ga trong cùng complex bằng tổ hợp chập 2.
- Thuộc tính:
  - `edge_type`: "walk"
  - `line`: null
  - `time`: Thời gian đi bộ (config.WALK_TIME_SAME_ZONE_MIN nếu cùng fare_zone, ngược lại WALK_TIME_DIFF_ZONE_MIN)
  - `cost`: 0
  - `distance`: Khoảng cách Haversine

### 3. Làm Sạch Đồ Thị
- Loại bỏ edges trùng lặp.
- Loại bỏ edges tham chiếu đến nodes không tồn tại.
- Validate: Đồ thị phải liên thông (connected).

## Ví Dụ Minh Họa

Giả sử từ ga Shibuya (JR-East.Yamanote.Shibuya) đến Shinjuku (JR-East.Yamanote.Shinjuku):
- Train edge: Trực tiếp trên Yamanote Line, khoảng cách ~3.5km, thời gian ~5 phút, chi phí 200 yên.
- Nếu có sự cố, có thể đi bộ qua các ga khác trong complex hoặc chuyển tuyến.

## Sự Cố (Incidents)
- Có thể áp dụng incidents như đóng ga (STATION_CLOSED) hoặc bảo trì tuyến (LINE_MAINTENANCE).
- Khi áp dụng, edges liên quan sẽ bị loại bỏ khỏi đồ thị.

## Kết Luận
Đồ thị Tokyo bao gồm hàng nghìn nodes và edges, đại diện cho mạng lưới phức tạp của Tokyo. Việc xây dựng dựa trên dữ liệu thực tế đảm bảo độ chính xác, và hệ thống có thể xử lý các sự cố động để cung cấp tuyến đường thay thế.</content>
<parameter name="filePath">C:\Users\hieuv\PycharmProjects\Tokyo-Route-Finder\data_system\STATIONS_AND_ROUTES_EXPLANATION.md
