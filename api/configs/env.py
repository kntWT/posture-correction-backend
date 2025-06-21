import os
from dotenv import load_dotenv

load_dotenv(".env")

user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
db_name = os.environ.get("MYSQL_DATABASE")
host = os.environ.get("MYSQL_HOST")

# secret_key = os.environ.get("JWT_SECRET_KEY")
# public_key = os.environ.get("JWT_PUBLIC_KEY")
mock_secret_key = os.environ.get("MOCK_SECRET_KEY", "false") == "true"
if not mock_secret_key:
    with open("./configs/keys/secret_key", "r") as f:
        secret_key = f.read()
    with open("./configs/keys/public_key.pub", "r") as f:
        public_key = f.read()
else:
    secret_key = None
    public_key = None

cookie_token_key = os.environ.get("COOKIE_TOKEN_KEY") or "token"

image_dir = os.environ.get("IMAGE_DIR") or "images"

model_dir = "estimators/model"
evaluate_output_dir = "estimators/figures"
train_data_dir = "estimators/data"

guest_id = 0

# process_pool_count = os.environ.get("PROCESS_POOL_COUNT", 2)
estimate_body_pose_pool_count = int(os.environ.get("ESTIMATE_BODY_POSE_POOL_COUNT", 4))
estimate_head_pose_pool_count = int(os.environ.get("ESTIMATE_HEAD_POSE_POOL_COUNT", 4))

os.makedirs(image_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)
os.makedirs(evaluate_output_dir, exist_ok=True)
os.makedirs(train_data_dir, exist_ok=True)

timestamp_format = "%Y-%m-%d_%H:%M:%S.%f"
