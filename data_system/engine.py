def get_clean_map_data(active_events):
    """
    Hàm này lấy dữ liệu gốc và lọc dựa trên các sự cố đang diễn ra.
    active_events: Danh sách các sự cố như station_closed[cite: 57, 97].
    Trả về: Một Dictionary đồ thị đã được làm sạch.
    """
    # 1. Giả sử đây là dữ liệu gốc từ database hoặc file
    raw_graph = {
        "Shinjuku": {"metadata": {"is_active": True}, "connections": {...}},
        "Shibuya": {"metadata": {"is_active": True}, "connections": {...}}
    }

    # 2. Xử lý logic lọc dữ liệu 
    for event in active_events:
        target = event.get("target")
        if event.get("type") == "station_closed" and target in raw_graph:
            # Xóa ga bị đóng cửa khỏi bản đồ trước khi gửi đi
            del raw_graph[target]
            print(f"Hệ thống Data: Đã loại bỏ ga {target} do đang đóng cửa.")

    # 3. Trả về Dictionary
    return raw_graph