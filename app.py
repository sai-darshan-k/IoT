from flask import Flask, request, jsonify, render_template
import threading
import datetime
from pywebpush import webpush
import json

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

subscriptions = []
data_lock = threading.Lock()

VAPID_PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEVs/yMz9J3jg34cHaB8scL12mP9e4n3zQinyaBxWCYhL7fil9UFo+HI0gRdtK+Ak8wIOiSXaLZTsWPwhqsZQPFA=="
VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQghJNqg05NbTpXSsfunHYxCehltrDMPtVfQ6qv2ElJjh6hRANCAARWz/IzP0neODfhwdoHyxwvXaY/17iffNCKfJoHFYJiEvt+KX1QWj4cjSBF20r4CTzAg6JJdotlOxY/CGqxlA8U"

def generate_notification_content(data):
    """Generate concise notification content from environmental data"""
    alerts = []
    
    # Add critical alerts only - we want notifications to be important and actionable
    if data["temperature"] is not None and data["temperature"] > 30:
        alerts.append(f"⚠️ High temp: {data['temperature']}°C - Consider shading plants")
    
    if data["soil_moisture"] is not None and data["soil_moisture"] > 2500:
        alerts.append(f"🌱 Critical soil moisture: Plants need water!")
    
    if data["rain_detected"] == "Rain Detected":
        alerts.append("🌧️ Rain detected - Irrigation not needed")
    elif data["soil_moisture"] is not None and data["soil_moisture"] > 2200:
        alerts.append("💧 Watering recommended based on soil moisture")
    
    if data["humidity"] is not None and data["humidity"] < 30:
        alerts.append(f"💧 Low humidity: {data['humidity']}% - Consider misting plants")
    
    # If no critical alerts, provide a status update
    if not alerts:
        if all(value is None for key, value in data.items() if key != "last_update"):
            return None  # No data to report
        alerts.append("✅ All environmental parameters within normal range")
    
    title = "CropCare AI Alert"
    body = "\n".join(alerts)
    
    return {
        "title": title,
        "body": body,
        "icon": "/static/notification-icon.png",  # Make sure this path exists
        "badge": "/static/badge-icon.png",  # Make sure this path exists
        "timestamp": datetime.datetime.now().timestamp(),
        "tag": "cropcare-update",  # Group similar notifications
        "renotify": True  # Make each notification trigger a new sound/vibration
    }

def send_push_notification(data):
    notification_content = generate_notification_content(data)
    if not notification_content or not subscriptions:
        return
    
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps(notification_content),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:saidarshan9569@gmail.com",
                    "aud": "https://iot-delta-vert.vercel.app"  # Use your actual site URL
                }
            )
            print("Push notification sent successfully")
        except Exception as e:
            print(f"Failed to send notification: {e}")
            # Could remove invalid subscriptions here

@app.route('/sensor-data', methods=['POST', 'GET'])
def update_sensor_data():
    global sensor_data
    if request.method == 'POST':
        if request.is_json:
            with data_lock:
                data = request.get_json()
                sensor_data.update(data)
                sensor_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_push_notification(sensor_data)  # Send the notification
            return jsonify({"message": "Data updated", "timestamp": sensor_data["last_update"]}), 200
        return jsonify({"error": "Invalid JSON"}), 400
    elif request.method == 'GET':
        with data_lock:
            return jsonify(sensor_data), 200

@app.route('/vapid-public-key')
def get_vapid_public_key():
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription = request.get_json()
    if not subscription or not isinstance(subscription, dict):
        return jsonify({"error": "Invalid subscription data"}), 400
    
    with data_lock:
        # Check if subscription already exists
        if subscription not in subscriptions:
            subscriptions.append(subscription)
            print(f"New subscription added. Total subscribers: {len(subscriptions)}")
    
    return jsonify({"status": "success", "message": "Subscription successful"}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    subscription = request.get_json()
    if not subscription:
        return jsonify({"error": "Invalid subscription data"}), 400
    
    with data_lock:
        if subscription in subscriptions:
            subscriptions.remove(subscription)
            print(f"Subscription removed. Total subscribers: {len(subscriptions)}")
    
    return jsonify({"status": "success", "message": "Unsubscribed successfully"}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)