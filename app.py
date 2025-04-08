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
    "last_update": None,
    "pump_status": "OFF"  # Add pump status tracking
}

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

@app.route('/pump-control', methods=['POST'])
def pump_control():
    global sensor_data
    if request.is_json:
        data = request.get_json()
        if 'action' in data:
            with data_lock:
                # Update local pump status
                sensor_data["pump_status"] = data['action']
            return jsonify({"message": f"Pump {data['action']} command sent", "status": data['action']}), 200
        return jsonify({"error": "Missing 'action' parameter"}), 400
    return jsonify({"error": "Invalid JSON"}), 400

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)