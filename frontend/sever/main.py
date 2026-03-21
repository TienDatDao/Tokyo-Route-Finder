import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Đảm bảo đường dẫn để sau này bạn import data_system dễ dàng
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

app = Flask(__name__)
CORS(app) # Rất quan trọng để Frontend gọi được vào Backend

@app.route('/api/find-path', methods=['POST'])
def receive_data():
    try:
        # Hứng dữ liệu JSON từ FE
        data = request.json
        
        # In ra terminal để bạn kiểm tra
        print("--- ĐÃ NHẬN DỮ LIỆU TỪ FRONTEND ---")
        print(f"Dữ liệu: {data}")
        print("----------------------------------")

        # Phản hồi lại cho FE để biết đã nhận thành công
        return jsonify({
            "status": "success",
            "message": "Backend đã nhận được dữ liệu!",
            "received_data": data
        }), 200

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Server đang chạy tại http://localhost:5000")
    app.run(debug=True, port=5000)