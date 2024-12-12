import os
from dotenv import load_dotenv

load_dotenv(".env")

user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
db_name = os.environ.get("MYSQL_DATABASE")
host = os.environ.get("MYSQL_OUTSIDE_HOST")

secret_key = os.environ.get("JWT_SECRET_KEY")

image_dir = os.environ.get("IMAGE_DIR")
original_image_dir = os.environ.get("ORIGINAL_IMAGE_DIR")
