from flask import Flask, request, jsonify, render_template
import threading
import datetime

app = Flask(__name__)

sensor_data = {
    "temperature": None,
    "humidity": None,
    "rain_intensity": None,
    "rain_detected": None,
    "soil_moisture": None,
    "water_layer": None,
    "last_update": None
}

motor_status = "OFF"  # Global variable to track motor status
data_lock = threading.Lock()

@app.route('/sensor-data', methods=['POST', 'GET'])
def update_sensor_data():
    global sensor_data
    if request.method == 'POST':
        if request.is_json:
            with data_lock:
                data = request.get_json()
                sensor_data.update(data)
                # Add timestamp for when data was updated
                sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({"message": "Data updated", "timestamp": sensor_data["last_update"]}), 200
        return jsonify({"error": "Invalid JSON"}), 400
    elif request.method == 'GET':
        with data_lock:
            return jsonify(sensor_data), 200

@app.route('/motor-control', methods=['POST', 'GET'])
def motor_control():
    global motor_status
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if 'motor_status' in data:
                motor_status = data['motor_status']
                print(f"Motor status updated to: {motor_status}")
                return jsonify({"message": "Motor status updated", "status": motor_status}), 200
        return jsonify({"error": "Invalid JSON"}), 400
    elif request.method == 'GET':
        return jsonify({"motor_status": motor_status}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)