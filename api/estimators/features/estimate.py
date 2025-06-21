import os
import sys
import cv2
import asyncio
from typing import List, Dict, Any, NoReturn
import numpy as np
import datetime
from configs.env import image_dir, timestamp_format
from helpers.multiprocessing import estimate_head_pose_in_process, estimate_body_pose_in_process

# from estimators.body import estimate_body_pose
# from estimators.face import estimate_head_pose
from estimators.features.face import estimate_head_pose, init_head_pose_estimator
from estimators.features.body import estimate_body_pose, init_body_pose_estimator


def init_feature_estimators():
    init_body_pose_estimator()
    init_head_pose_estimator()


async def estimate(path: str, sub_path: int, file_name: str):
    try:
        image = cv2.imread(os.path.join(
            path, f"{sub_path}", "original", file_name))
        face_feature, head_pose = await estimate_from_image(image, sub_path, file_name)
        if face_feature is None or head_pose is None:
            return None, None
        return face_feature, head_pose
    except FileNotFoundError as e:
        print(e)
        return


async def estimate_from_image(image: np.ndarray, user_id: int, file_name: str):
    # face_feature = estimate_body_pose(
    #     image.copy(), user_id, file_name
    # )
    # head_pose = estimate_head_pose(
    #     image.copy(), user_id, file_name
    # )
    # return face_feature, {
    #         "face_pitch": head_pose["pitch"],
    #         "face_roll": head_pose["roll"],
    #         "face_yaw": head_pose["yaw"]
    #     }
    loop = asyncio.get_event_loop()
    # # async with asyncio.Lock():
    base_args = {
        "img": image,
        "sub_path": user_id,
        "file_name": file_name
    }
    print(f"estimate start: {datetime.datetime.now().strftime(timestamp_format)}")
    
    tasks: List[Any] = [
        loop.run_in_executor(
            None,
            lambda: estimate_body_pose_in_process(
                base_args["img"],
                base_args["sub_path"],
                base_args["file_name"]
            )
        ),
        loop.run_in_executor(
            None,
            lambda: estimate_head_pose_in_process(
                base_args["img"],
                base_args["sub_path"],
                base_args["file_name"]
            )
        ),
    ]
    face_feature, head_pose = await asyncio.gather(*tasks)
    return [
        face_feature,
        None if head_pose is None else {
            "face_pitch": head_pose["pitch"],
            "face_roll": head_pose["roll"],
            "face_yaw": head_pose["yaw"]
        }]
    # tasks.append(estimate_body_pose(image, user_id, file_name))
    # tasks.append(estimate_head_pose(image, user_id, file_name))
    # return await asyncio.gather(*tasks)
    # head_pose = await estimate_head_pose(image.copy(), user_id, file_name)
    # face_feature = await estimate_body_pose(image, user_id, file_name)
    # return face_feature, head_pose


if __name__ == "__main__":
    init_feature_estimators()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(estimate(f"images/内カメラ", "original", sys.argv[1]))
