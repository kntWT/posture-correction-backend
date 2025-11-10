import cv2
import numpy as np
import math
import torch
import torch.multiprocessing as mp
import sys
import os
from typing import Dict
import copy
import random
import string

from configs.env import image_dir, timestamp_format
from configs.estimator import image_size
import datetime
from helpers.resize_image import resize_and_pad

_image_dir = image_dir if image_dir is not None else "images"

Point = Dict[str, float]
# x: x_coord
# y: y_coord
# score: score

sys.path.append("pytorch-openpose")

from src import util
from src.body import Body

body_estimation = None

def init_body_pose_estimator():
    global body_estimation
    body_estimation = Body("pytorch-openpose/model/body_pose_model.pth")
    gpu = 0
    # デバイス取得
    if (gpu < 0):
        device = torch.device('cpu')
    else:
        device = torch.device('cuda:%d' % gpu)
        # device = torch.device("mps")


def parse_point(cand) -> Point:
    return {
        "x": cand[0],
        "y": cand[1],
        "score": cand[2],
    }


def estimate_body_pose(
        img: np.ndarray | None = None, sub_path: str = "1", file_name: str = "no_name", size: int = image_size, request_id: str = "no_request_id"
) -> Dict | None:
    """
    入力画像をリサイズして鼻、首、両目の座標を取得する
    """
    if img is None:
        return None
    img = resize_and_pad(img, size)
    candidate, subset = body_estimation(img)
    canvas: np.ndarray = copy.deepcopy(img)
    canvas = util.draw_bodypose(canvas, candidate, subset)
    save_path: str = f"{_image_dir}/{sub_path}/neck"
    if len(subset) <= 0:
        # print("cannot detected")
        return None
    # if len(subset) >= 2:
    #     print("othre people detected")
    #     return None

    nose_index: int = int(subset[0][0])
    neck_index: int = int(subset[0][1])
    right_eye_index: int = int(subset[0][14])
    left_eye_index: int = int(subset[0][15])
    if nose_index == -1 or neck_index == -1 or right_eye_index == -1 or left_eye_index == -1:
        # print(f"nose({nose_index}) or neck({neck_index}) or eyes([{right_eye_index}, {left_eye_index}]) cannot detected")
        cv2.imwrite(f"{save_path}/_{file_name}", canvas)
        return None

    nose: Point = parse_point(candidate[nose_index])
    neck: Point = parse_point(candidate[neck_index])
    right_eye: Point = parse_point(candidate[right_eye_index])
    left_eye: Point = parse_point(candidate[left_eye_index])
    # _subset: np.ndarray = np.array([[s if i < 2 else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    # _subset: np.ndarray = np.array([[s if (i < 2 or i > 17) else -1 for i, s in enumerate(subset[n])] for n in range(1)])
    os.makedirs(save_path, exist_ok=True)
    if nose["score"] < 0.7 or \
            neck["score"] < 0.2 or \
            right_eye["score"] < 0.7 or \
            left_eye["score"] < 0.7:
        # print(f"nose: {nose['score']}, neck: {neck['score']}, right eye: {right_eye['score']}, {left_eye['score']}")
        cv2.imwrite(f"{save_path}/_{file_name}", canvas)
        return None

    cv2.imwrite(f"{save_path}/{file_name}", canvas)
    neck_to_nose: float = math.dist(
        [nose["x"], nose["y"]], [neck["x"], neck["y"]])
    standard_dist: float = math.dist(
        [right_eye["x"], right_eye["y"]],
        [left_eye["x"], left_eye["y"]])
    print(f"[{request_id}] face estimated: {datetime.datetime.now().strftime(timestamp_format)}")
    return {
        "nose_x": nose["x"],
        "nose_y": nose["y"],
        "neck_x": neck["x"],
        "neck_y": neck["y"],
        "left_eye_x": left_eye["x"],
        "left_eye_y": left_eye["y"],
        "right_eye_x": right_eye["x"],
        "right_eye_y": right_eye["y"],
        "neck_to_nose": float(neck_to_nose),
        "standard_distance": float(standard_dist)
    }
