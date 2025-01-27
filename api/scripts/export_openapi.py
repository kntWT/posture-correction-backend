from fastapi.openapi.utils import get_openapi
import json
import os
from . import api_dir
from app import app

def export_openapi_scheme():
    target_dir = os.path.join(api_dir, 'openapi')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    with open(os.path.join(target_dir, 'openapi.json'), 'w') as file:
        json.dump(get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ), file)


if __name__ == "__main__":
    export_openapi_scheme()
