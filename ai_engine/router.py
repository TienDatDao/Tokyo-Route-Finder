import heapq
import math
import itertools

# ================= HEURISTIC (Haversine) =================
def calculate_haversine_km(lat1, lon1, lat2, lon2):
    R = 6371  # Bán kính trái đất (km)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    x = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(x))

def heuristic(current, goal, graph, criteria):
    """
    Đồng bộ đơn vị của Heuristic (h) với chi phí thực tế (g).
    """
    if current not in graph or goal not in graph:
        return 0
        
    lat1 = graph[current]["metadata"]["lat"]
    lon1 = graph[current]["metadata"]["lon"]
    lat2 = graph[goal]["metadata"]["lat"]
    lon2 = graph[goal]["metadata"]["lon"]
    
    distance_km = calculate_haversine_km(lat1, lon1, lat2, lon2)
    
    # Quy đổi khoảng cách ra đơn vị tương ứng để đảm bảo tính Admissible (không đánh giá lố)
    if criteria == "shortest_time":
        # Giả sử tàu chạy tối đa 60km/h -> 1 km tốn 1 phút
        return distance_km * 1.0 
    elif criteria == "lowest_cost":
        # Giả sử giá vé rẻ nhất là 10 Yên/km
        return distance_km * 10.0
    elif criteria == "least_transfers":
        # Khoảng cách không ảnh hưởng đến số lần chuyển tuyến
        return 0 
        
    return distance_km

# ================= MAIN FUNCTION =================
def find_optimal_route(graph, start, end, criteria):
    if start not in graph or end not in graph:
        return {"status": "NO_ROUTE_FOUND"}

    if start == end:
        return {"status": "SUCCESS", "route": {"path": [start], "total_time": 0, "total_cost": 0, "transfers": 0, "details": []}}

    # Priority queue: (f_score, counter, g_score, current_station, current_line, current_time, current_cost, current_transfers)
    pq = []
    counter = itertools.count() # Giải quyết triệt để lỗi TypeError khi so sánh các phần tử trùng f_score
    
    # Push điểm bắt đầu
    heapq.heappush(pq, (0, next(counter), 0, start, None, 0, 0, 0))
    
    # Từ điển lưu chi phí tốt nhất để đến 1 ga trên 1 tuyến cụ thể: (station, line) -> g_score
    best_g = {}
    best_g[(start, None)] = 0
    
    # Từ điển lưu vết để dựng lại đường đi: (station, line) -> (prev_station, prev_line, edge_data)
    came_from = {}

    while pq:
        f, _, g, current, current_line, curr_time, curr_cost, curr_transfers = heapq.heappop(pq)

        # Nếu đã tìm thấy đích, dừng lại và dựng lộ trình
        if current == end:
            return reconstruct_path(came_from, start, end, current_line, curr_time, curr_cost, curr_transfers)

        # Tránh xử lý lại nếu đã tìm được đường tốt hơn đến (node, line) này
        if best_g.get((current, current_line), float('inf')) < g:
            continue

        for neighbor, edge in graph[current]["connections"].items():
            neighbor_line = edge["line"]
            
            # Tính toán thay đổi dựa trên tuyến (line)
            is_transfer = (current_line is not None and current_line != neighbor_line)
            
            # Tính metrics tích lũy
            next_time = curr_time + edge["time"]
            next_cost = curr_cost + edge["cost"]
            next_transfers = curr_transfers + (1 if is_transfer else 0)

            # Xác định trọng số g mới dựa trên tiêu chí
            if criteria == "shortest_time":
                # Thêm penalty thời gian nếu phải đổi tàu (VD: tốn 3 phút đi bộ đổi line)
                weight = edge["time"] + (3 if is_transfer else 0)
            elif criteria == "lowest_cost":
                weight = edge["cost"]
            elif criteria == "least_transfers":
                # Chi phí tăng vọt nếu đổi tàu, ngược lại phí rất nhỏ để ưu tiên đường ngắn hơn nếu cùng line
                weight = 100 if is_transfer else 1 
            else:
                weight = edge["time"]

            new_g = g + weight

            # Cập nhật nếu tìm được đường tốt hơn đến neighbor trên tuyến neighbor_line
            if new_g < best_g.get((neighbor, neighbor_line), float('inf')):
                best_g[(neighbor, neighbor_line)] = new_g
                came_from[(neighbor, neighbor_line)] = (current, current_line, edge)
                
                h = heuristic(neighbor, end, graph, criteria)
                f_new = new_g + h
                
                heapq.heappush(
                    pq, 
                    (f_new, next(counter), new_g, neighbor, neighbor_line, next_time, next_cost, next_transfers)
                )

    return {"status": "NO_ROUTE_FOUND"}

# ================= SUPPORT FUNCTIONS =================
def reconstruct_path(came_from, start, end, end_line, total_time, total_cost, total_transfers):
    """
    Lần ngược từ đích về điểm xuất phát để xây dựng lại lộ trình và JSON details.
    """
    current = end
    current_line = end_line
    path_edges = []
    
    # Backtrack
    while current != start:
        prev, prev_line, edge_data = came_from[(current, current_line)]
        path_edges.append({
            "from": prev,
            "to": current,
            "line": current_line,
            "prev_line": prev_line
        })
        current = prev
        current_line = prev_line
        
    path_edges.reverse() # Đảo ngược từ Start -> End

    # Khởi tạo dữ liệu trả về
    path_stations = [start]
    details = []

    # Xử lý node Start
    first_line = path_edges[0]["line"] if path_edges else None
    details.append({
        "station_id": f"dummy_id_{start}", # Cần map ID thực tế từ graph nếu có
        "station_name": start,
        "line": first_line,
        "action": "Board"
    })

    # Xử lý các node trung gian và End
    for i, step in enumerate(path_edges):
        path_stations.append(step["to"])
        
        # Xác định Action
        is_last_station = (i == len(path_edges) - 1)
        
        if is_last_station:
            action = "Exit"
        elif step["line"] != path_edges[i+1]["line"]:
            action = "Transfer"
        else:
            action = "Continue" # Hoặc có thể bỏ qua không đưa vào details nếu Frontend không cần hiển thị các ga đi ngang qua
            
        details.append({
            "station_id": f"dummy_id_{step['to']}",
            "station_name": step["to"],
            "line": step["line"],
            "action": action
        })

    return {
        "status": "SUCCESS",
        "suggested_start_station": {
            "id": f"dummy_id_{start}",
            "name": start
        },
        "route": {
            "path": path_stations,
            "total_time": total_time,
            "total_cost": total_cost,
            "transfers": total_transfers,
            "details": details
        }
    }