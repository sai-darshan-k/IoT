from flask import Flask, request, jsonify, render_template
import threading
import datetime
import requests

app = Flask(__name__)

sensor_data = {
    "temperature": None,
    "humidity": None,
    "rain_intensity": None,
    "rain_detected": None,
    "soil_moisture": None,
    "water_layer": None,
    "motor_status": "OFF",  # Add motor status
    "last_update": None
}

data_lock = threading.Lock()

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = "8146490643:AAHZht2KYlFkxvxGJ4wtuQI36A4IunU36EI"
TELEGRAM_CHAT_ID = "1514494157"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram_message(message):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

@app.route('/sensor-data', methods=['POST', 'GET'])
def update_sensor_data():
    global sensor_data
    if request.method == 'POST':
        if request.is_json:
            with data_lock:
                data = request.get_json()
                sensor_data.update(data)
                sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({"message": "Data updated", "timestamp": sensor_data["last_update"]}), 200
        return jsonify({"error": "Invalid JSON"}), 400
    elif request.method == 'GET':
        with data_lock:
            return jsonify(sensor_data), 200

@app.route('/motor-control', methods=['POST', 'GET'])
def motor_control():
    global sensor_data
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_status = data.get("motor_status")
            if new_status in ["ON", "OFF"]:
                with data_lock:
                    if sensor_data["motor_status"] != new_status:
                        sensor_data["motor_status"] = new_status
                        sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # Send command to Telegram (Arduino will pick it up)
                        send_telegram_message(new_status.lower())
                return jsonify({"message": "Motor status updated", "motor_status": new_status}), 200
            return jsonify({"error": "Invalid motor status"}), 400
        return jsonify({"error": "Invalid JSON"}), 400
    elif request.method == 'GET':
        with data_lock:
            return jsonify({"motor_status": sensor_data["motor_status"]}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)