import data_system.core.data_manager as dm
import ai_engine.routing as ai

def handle_find_route(payload):
    # 1. Lấy tên ga từ cục JSON của Đạt
    start_name = payload.get("start_point", {}).get("value")
    end_name = payload.get("end_point", {}).get("value")
    criteria = payload.get("preferences", {}).get("optimize_by", "shortest_time")

    # 2. Gọi Member 3: Đổi tên ga sang danh sách ID Node
    # (Giả sử Member 3 cung cấp hàm này)
    start_nodes = dm.get_nodes_by_name(start_name)
    end_nodes = dm.get_nodes_by_name(end_name)
    
    if not start_nodes or not end_nodes:
        return {"status": "ERROR", "message": "Không tìm thấy ga hoặc ga đang đóng cửa"}

    # 3. Gọi Member 3: Lấy đồ thị sạch (đã áp dụng sự cố)
    graph = dm.get_clean_graph("data_system/raw_data")

    # 4. Gọi Member 1 (AI): Tìm đường đi tối ưu
    ai_result = ai.find_optimal_route(graph, start_nodes, end_nodes, criteria)

    # 5. Đóng gói lại thật đẹp theo ý Đạt
    return {
        "status": "SUCCESS",
        "data": {
            "path": ai_result.get("path", []),
            "total_time": ai_result.get("duration", 0),
            "total_cost": ai_result.get("cost", 0)
        }
    }