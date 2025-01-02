from flask import Flask, request, jsonify, render_template
import threading

app = Flask(__name__)

sensor_data = {
    "temperature": None,
    "humidity": None,
    "rain_intensity": None,
    "rain_detected": None,
    "soil_moisture": None,
    "water_layer": None,
}

data_lock = threading.Lock()

@app.route('/sensor-data', methods=['POST', 'GET'])
def update_sensor_data():
    global sensor_data
    if request.method == 'POST':
        if request.is_json:
            with data_lock:
                sensor_data.update(request.get_json())
            return jsonify({"message": "Data updated"}), 200
        return jsonify({"error": "Invalid JSON"}), 400
    elif request.method == 'GET':
        with data_lock:
            return jsonify(sensor_data), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)