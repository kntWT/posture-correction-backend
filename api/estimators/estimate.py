import numpy as np
import joblib
import onnxruntime as ort
from onnxruntime.capi.onnxruntime_pybind11_state import NoSuchFile
import cv2
import os

from estimators.features.estimate import estimate as estimate_feature, estimate_from_image as estimate_feature_from_image
from estimators.formatter import parse_np
from estimators.train import train
from configs.env import train_if_not_exist
import configs.estimator as config

try:
    sess = ort.InferenceSession(f"{config.model_dir}/{config.model_file_name}", providers=[
                                "CPUExecutionProvider"])
    sess.set_providers(["CPUExecutionProvider"], [{"input_op_num_threads": 1}])
    scaler = joblib.load(f"{config.model_dir}/{config.scaler_file_name}")
except Exception as e:
    print(e)
    if train_if_not_exist:
        train()
        sess = ort.InferenceSession(f"{config.model_dir}/{config.model_file_name}", providers=[
                                    "CPUExecutionProvider"])
        sess.set_providers(["CPUExecutionProvider"], [{"input_op_num_threads": 1}])
        scaler = joblib.load(f"{config.model_dir}/{config.scaler_file_name}")

async def estimate_from_image(image: np.ndarray, user_id: int, file_name: str, features: dict):
    face_feature, head_feature = await estimate_feature_from_image(image, user_id, file_name)
    if face_feature is None or head_feature is None:
        return None
    return estimate_from_features({**face_feature, **head_feature, **features})


async def estimate_from_path(path: str, sub_path: int, file_name: str, features: dict):
    try:
        image = cv2.imread(os.path.join(
            path, f"{sub_path}", "original", file_name))
        return await estimate_from_image(image, sub_path, file_name, features)
    except FileNotFoundError as e:
        print(e)
        return


async def estimate_from_features(features: dict):
    x, _ = parse_np([features], mode=config.train_method)
    X = scaler.transform(x.T)
    pred = sess.run(None, {"input": X.astype(np.float32)})[0]
    return pred[0][0]
