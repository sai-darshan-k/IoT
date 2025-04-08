import json
from datetime import datetime
from pywebpush import webpush
from http import HTTPStatus

# In-memory storage (resets on serverless restart; use a DB for persistence)
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

VAPID_PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEVs/yMz9J3jg34cHaB8scL12mP9e4n3zQinyaBxWCYhL7fil9UFo+HI0gRdtK+Ak8wIOiSXaLZTsWPwhqsZQPFA=="
VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQghJNqg05NbTpXSsfunHYxCehltrDMPtVfQ6qv2ElJjh6hRANCAARWz/IzP0neODfhwdoHyxwvXaY/17iffNCKfJoHFYJiEvt+KX1QWj4cjSBF20r4CTzAg6JJdotlOxY/CGqxlA8U"

def generate_environmental_analysis(data):
    analysis = ["Environmental Analysis\n🔍"]
    if data["temperature"] is not None:
        temp = data["temperature"]
        if temp > 30:
            analysis.append(f"The current temperature is {temp}°C, which is significantly above the ideal range. This may cause plant stress and increased water evaporation. Consider providing shade and increasing watering frequency.")
    if data["humidity"] is not None:
        hum = data["humidity"]
        if hum > 60:
            analysis.append(f"Current humidity is {hum}%, which is good for most tropical plants but may be high for desert species. This promotes healthy leaf development and reduces transpiration stress.")
    if data["soil_moisture"] is not None:
        soil = data["soil_moisture"]
        if soil > 2500:
            analysis.append(f"Soil moisture reading is {soil}, indicating critically dry soil. Immediate watering is recommended to prevent plant wilting and root damage.")
    if data["rain_detected"] is not None:
        rain_intensity = data["rain_intensity"] if data["rain_intensity"] is not None else "--"
        if data["rain_detected"] != "Rain Detected":
            analysis.append(f"Currently no rainfall (intensity reading: {rain_intensity}) with soil moisture readings indicating dry conditions. Watering is recommended based on soil moisture status.")
    analysis.append("Overall Assessment: Multiple environmental stressors detected. Immediate attention recommended to prevent plant damage.")
    return "\n\n".join(analysis)

def send_push_notification(analysis_text):
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps({"body": analysis_text}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:saidarshan9569@gmail.com"}
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

def handler(req):
    if req.method == 'POST':
        try:
            data = req.get_json()
            sensor_data.update(data)
            sensor_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fixed typo
            analysis_text = generate_environmental_analysis(sensor_data)
            send_push_notification(analysis_text)
            return {
                "statusCode": HTTPStatus.OK,
                "body": json.dumps({"message": "Data updated", "timestamp": sensor_data["last_update"]}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": json.dumps({"error": "Invalid JSON"}),
                "headers": {"Content-Type": "application/json"}
            }
    elif req.method == 'GET':
        return {
            "statusCode": HTTPStatus.OK,
            "body": json.dumps(sensor_data),
            "headers": {"Content-Type": "application/json"}
        }