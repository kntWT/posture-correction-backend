import os
from dotenv import load_dotenv

load_dotenv(".env")

user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
db_name = os.environ.get("MYSQL_DATABASE")
host = os.environ.get("MYSQL_HOST")

# secret_key = os.environ.get("JWT_SECRET_KEY")
# public_key = os.environ.get("JWT_PUBLIC_KEY")
with open("./configs/keys/secret_key", "r") as f:
    secret_key = f.read()
with open("./configs/keys/public_key.pub", "r") as f:
    public_key = f.read()

cookie_token_key = os.environ.get("COOKIE_TOKEN_KEY") or "token"

image_dir = os.environ.get("IMAGE_DIR")
original_image_dir = os.environ.get("ORIGINAL_IMAGE_DIR")

model_dir = "estimators/model"
evaluate_output_dir = "estimators/figures"
train_data_dir = "estimators/data"

os.makedirs(image_dir, exist_ok=True)
os.makedirs(original_image_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)
os.makedirs(evaluate_output_dir, exist_ok=True)
os.makedirs(train_data_dir, exist_ok=True)
