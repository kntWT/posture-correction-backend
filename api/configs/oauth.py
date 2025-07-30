import os
from dotenv import load_dotenv

load_dotenv(".env")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:5555")
GOOGLE_REDIRECT_URI = f"{SERVER_URL}/user/login/google/callback"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"