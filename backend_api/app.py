from flask import Flask, request, jsonify
from flask_cors import CORS
import config
import services

app = Flask(__name__)
CORS(app) # Mở cửa cho cổng 8000

@app.route('/find-route', methods=['POST'])
def find_route():
    # Nhận gói hàng JSON
    data = request.get_json()
    
    # Chuyển cho bên Services xử lý logic
    result = services.handle_find_route(data)
    
    # Trả hàng lại cho Frontend
    return jsonify(result)

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)