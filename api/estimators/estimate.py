import os
import sys
import cv2
import asyncio
from typing import List, Dict, Any, NoReturn
import numpy as np
import datetime
from configs.env import image_dir, original_image_dir

# from estimators.body import estimate_body_pose
# from estimators.face import estimate_head_pose
from estimators.face import estimate_head_pose
from estimators.body import estimate_body_pose
    
async def estimate(path: str, sub_path: int, file_name: str):
    try:
        image = cv2.imread(os.path.join(path, f"{sub_path}", "original", file_name))
        face_feature, head_pose = await estimate_from_image(image, sub_path, file_name)
        if face_feature is None or head_pose is None:
            return
        
        pass
    except FileNotFoundError as e:
        print(e)
        return

async def estimate_from_image(image: np.ndarray, user_id: int, file_name: str):
    tasks: List[Any] = []
    tasks.append(estimate_body_pose(image, user_id, file_name))
    tasks.append(estimate_head_pose(image, user_id, file_name))
    return await asyncio.gather(*tasks)
    # head_pose = await estimate_head_pose(image.copy(), user_id, file_name)
    # face_feature = await estimate_body_pose(image, user_id, file_name)
    # return face_feature, head_pose


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(estimate(f"images/内カメラ", "original", sys.argv[1]))
