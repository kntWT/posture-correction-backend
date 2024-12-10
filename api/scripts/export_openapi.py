from fastapi.openapi.utils import get_openapi
import json
import os
import sys

api_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(api_dir)

from app import app

def export_openapi_scheme():
    if not os.path.exists('openapi'):
        os.makedirs('openapi')
    with open(os.path.join(api_dir, 'openapi/openapi.json'), 'w') as file:
        json.dump(get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ), file)


if __name__ == "__main__":
    export_openapi_scheme()
