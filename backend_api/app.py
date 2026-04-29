from flask import Flask, request, jsonify
from flask_cors import CORS
import config
import services

app = Flask(__name__)
CORS(app) # Mở cửa cho cổng 8000

@app.route('/find-route', methods=['POST'])
@app.route('/api/find-path', methods=['POST'])
def find_route():
    data = request.get_json()
    result = services.handle_find_route(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)