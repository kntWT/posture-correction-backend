import cv2
import numpy as np
import os


def save_image(image: np.ndarray, path: str, sub_path: str, file_name: str) -> None:
    save_dir: str = os.path.join(path, sub_path)
    os.makedirs(save_dir, exist_ok=True)
    cv2.imwrite(f"{save_dir}/{file_name}", image)


def save_file(file: bytes, path: str, sub_path: str, file_name: str) -> None:
    save_dir: str = os.path.join(path, sub_path)
    os.makedirs(save_dir, exist_ok=True)
    file_path: str = os.path.join(save_dir, file_name.replace("/", "-").replace(" ", "_"))
    try:
        with open(file_path, "wb") as f:
            f.write(file.read())
            f.close()
        return file_path
    except Exception as e:
        print(e)
        return None
