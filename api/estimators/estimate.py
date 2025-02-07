import numpy as np
import joblib
import onnxruntime as ort
from onnxruntime.capi.onnxruntime_pybind11_state import NoSuchFile
import cv2
import os

from estimators.features.estimate import estimate as estimate_feature, estimate_from_image as estimate_feature_from_image
from estimators.formatter import parse_np
from estimators.train import train
from configs.env import model_dir

try:
    sess = ort.InferenceSession(f"{model_dir}/extra_trees.onnx", providers=[
                                "CPUExecutionProvider"])
    sess.set_providers(["CPUExecutionProvider"], [{"input_op_num_threads": 6}])
    scaler = joblib.load(f"{model_dir}/scaler.pkl")
except NoSuchFile:
    train()
    sess = ort.InferenceSession(f"{model_dir}/extra_trees.onnx", providers=[
                                "CPUExecutionProvider"])
    sess.set_providers(["CPUExecutionProvider"], [{"input_op_num_threads": 6}])
    scaler = joblib.load(f"{model_dir}/scaler.pkl")

async def estimate_from_image(image: np.ndarray, user_id: int, file_name: str, features: dict):
    face_feature, head_feature = await estimate_feature_from_image(image, user_id, file_name)
    if face_feature is None or head_feature is None:
        return None
    x, _ = parse_np([{
        **face_feature,
        **head_feature,
        **features
    }])
    X = scaler.transform(x)
    pred = sess.run(None, {"input": X.astype(np.float32)})[0]
    return pred[0]


async def estimate_from_path(path: str, sub_path: int, file_name: str, features: dict):
    try:
        image = cv2.imread(os.path.join(
            path, f"{sub_path}", "original", file_name))
        return await estimate_from_image(image, sub_path, file_name, features)
    except FileNotFoundError as e:
        print(e)
        return


async def estimate_from_features(features: dict):
    x, _ = parse_np([features])
    X = scaler.transform(x)
    pred = sess.run(None, {"input": X.astype(np.float32)})[0]
    return pred[0]
