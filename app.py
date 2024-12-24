from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Store sensor data in memory (for demo purposes)
sensor_data = {}

# Endpoint to receive sensor data from ESP32
@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    global sensor_data
    sensor_data = request.get_json()
    if not sensor_data:
        return jsonify({"error": "Invalid data"}), 400

    print(f"Received data: {sensor_data}")
    return jsonify({"message": "Data received successfully"}), 200

# Webpage to display sensor data
@app.route('/')
def index():
    return jsonify(sensor_data)

if __name__ == "__main__":
    app.run(debug=True)
