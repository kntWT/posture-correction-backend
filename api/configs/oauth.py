import os
from dotenv import load_dotenv

load_dotenv(".env")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
ROOT_SERVICE_ORIGIN = os.environ.get("ROOT_SERVICE_ORIGIN", "http://localhost:5555")
ROOT_SERVICE_PATH = os.environ.get("ROOT_SERVICE_PATH", "")
GOOGLE_ROOT_REDIRECT_URI = f"{ROOT_SERVICE_ORIGIN}{ROOT_SERVICE_PATH}/user/login/google/callback"
GOOGLE_INSTANCE_REDIRECT_PATH = "/posture-api/user/login/google/callback"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
