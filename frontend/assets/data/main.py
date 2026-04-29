import json
import os

# Tự động xác định thư mục đang chứa file script này
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def process_stations(input_filename, output_filename):
    # Tạo đường dẫn đầy đủ đến file input và output
    input_path = os.path.join(BASE_DIR, input_filename)
    output_path = os.path.join(BASE_DIR, output_filename)

    # 1. Đọc dữ liệu từ file JSON
    if not os.path.exists(input_path):
        print(f"Lỗi: Không tìm thấy file {input_filename} tại {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Lỗi: File JSON không đúng định dạng.")
            return

    station_groups = {}

    # 2. Lọc và gom nhóm
    for entry in data:
        # Kiểm tra nếu không có tọa độ hoặc tọa độ không hợp lệ thì bỏ qua (xóa)
        coords = entry.get('coord')
        if not coords or not isinstance(coords, list) or len(coords) < 2:
            continue 

        # Lấy tên trạm làm khóa (key) để xử lý trùng lặp
        # Sử dụng .get() để tránh lỗi nếu thiếu trường title
        title_dict = entry.get('title', {})
        station_name = title_dict.get('en')
        
        if not station_name:
            continue

        if station_name not in station_groups:
            # Lưu lại bản ghi đầu tiên làm gốc và tạo danh sách tọa độ
            station_groups[station_name] = {
                "original_entry": entry,
                "all_coords": [coords]
            }
        else:
            # Nếu trùng tên, thêm tọa độ vào danh sách để tính trung bình
            station_groups[station_name]["all_coords"].append(coords)

    # 3. Tính toán trung bình và tạo danh sách kết quả
    processed_data = []
    for name, info in station_groups.items():
        all_coords = info["all_coords"]
        
        # Tính toán tọa độ trung bình từ danh sách all_coords
        avg_lon = sum(c[0] for c in all_coords) / len(all_coords)
        avg_lat = sum(c[1] for c in all_coords) / len(all_coords)

        # Cập nhật tọa độ mới vào bản ghi gốc (làm tròn 6 chữ số thập phân)
        final_entry = info["original_entry"]
        final_entry["coord"] = [round(avg_lon, 6), round(avg_lat, 6)]
        
        processed_data.append(final_entry)

    # 4. Ghi dữ liệu đã xử lý ra file mới
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4, ensure_ascii=False)
    
    print(f"Xử lý hoàn tất! Đã lưu {len(processed_data)} nhà ga vào file {output_filename}")

# Thực thi chương trình
if __name__ == "__main__":
    process_stations('stations.json', 'stations2.json')