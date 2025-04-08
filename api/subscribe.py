import json
from http import HTTPStatus

subscriptions = []  # In-memory; use a DB for persistence

def handler(req):
    if req.method == 'POST':
        try:
            subscription = req.get_json()
            subscriptions.append(subscription)
            return {
                "statusCode": HTTPStatus.OK,
                "body": json.dumps({"status": "success"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": json.dumps({"error": "Invalid JSON"}),
                "headers": {"Content-Type": "application/json"}
            }