import uuid
import datetime
from fastapi import Request

from configs.env import timestamp_format

def get_request_id(request: Request):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime(timestamp_format)
    refferer = request.headers.get("Referer")
    user_agent = request.headers.get("User-Agent")
    client_ip = request.client.host
    real_ip = request.headers.get("X-Real-IP")
    forward_for = request.headers.get("X-Forwarded-For")
    request_url = request.url
    request_method = request.method

    print(f"Request ID: {request_id}, Timestamp: {timestamp}, Referer: {refferer}, User Agent: {user_agent}, Client IP: {client_ip}, Real IP: {real_ip}, Forward For: {forward_for}, Request URL: {request_url}, Request Method: {request_method}")
    return request_id
