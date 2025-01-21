# import time
# import math
# import re
# import sys
from config.env import image_dir
from sixdrepnet import utils
from sixdrepnet.model import SixDRepNet
from huggingface_hub import hf_hub_download
from PIL import Image
from face_detection import RetinaFace
from torchvision import transforms
# import torchvision
# import torch.nn.functional as F
from torch.backends import cudnn
# from torch.utils.data import DataLoader
# import torch.nn as nn
import torch
import cv2
import numpy as np
import os
from typing import Dict


os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

_image_dir = image_dir if image_dir is not None else "images"

transformations = transforms.Compose([transforms.Resize(224),
                                      transforms.CenterCrop(224),
                                      transforms.ToTensor(),
                                      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

gpu = 0
cam = 0
cudnn.enabled = True
if (gpu < 0):
    device = torch.device('cpu')
else:
    device = torch.device('cuda:%d' % gpu)
    # device = torch.device("mps")
snapshot_path = hf_hub_download(
    repo_id="osanseviero/6DRepNet_300W_LP_AFLW2000", filename="model.pth")
model = SixDRepNet(backbone_name='RepVGG-B1g2',
                   backbone_file='',
                   deploy=True,
                   pretrained=False)

print('Loading data.')

detector = RetinaFace(0)

# Load snapshot
saved_state_dict = torch.load(os.path.join(
    snapshot_path), map_location='cpu')

if 'model_state_dict' in saved_state_dict:
    model.load_state_dict(saved_state_dict['model_state_dict'])
else:
    model.load_state_dict(saved_state_dict)
model.to(device)

# Test the Model
model.eval()  # Change model to 'eval' mode (BN uses moving mean/var).


async def estimate_head_pose(img=None, user_id: int = 1, file_name: str = "no_name") -> Dict | None:
    if img is None:
        return None

    faces = sorted(detector(img), key=lambda x: x[2], reverse=True)
    if len(faces) <= 0:
        # print("face cannot detected")
        return None
    box, landmarks, score = faces[0]
    # Print the location of each face in this image
    if score < .95:
        # print(f"face cannot detected (score: {score})")
        return None
    x_min = int(box[0])
    y_min = int(box[1])
    x_max = int(box[2])
    y_max = int(box[3])
    bbox_width = abs(x_max - x_min)
    bbox_height = abs(y_max - y_min)

    x_min = max(0, x_min-int(0.2*bbox_height))
    y_min = max(0, y_min-int(0.2*bbox_width))
    x_max = x_max+int(0.2*bbox_height)
    y_max = y_max+int(0.2*bbox_width)

    canvas = img[y_min:y_max, x_min:x_max]
    canvas = Image.fromarray(canvas)
    canvas = canvas.convert('RGB')
    canvas = transformations(canvas)

    canvas = torch.Tensor(canvas[None, :]).to(device)

    R_pred = model(canvas)

    euler = utils.compute_euler_angles_from_rotation_matrices(
        R_pred)*180/np.pi
    pitch = euler[:, 0].cpu()
    yaw = euler[:, 1].cpu()
    roll = euler[:, 2].cpu()

    # utils.draw_axis(frame, y_pred_deg, p_pred_deg, r_pred_deg, left+int(.5*(right-left)), top, size=100)
    utils.plot_pose_cube(img,  yaw, pitch, roll, x_min + int(.5*(
        x_max-x_min)), y_min + int(.5*(y_max-y_min)), size=bbox_width)
    save_dir: str = f"{_image_dir}/{user_id}/head"
    os.makedirs(save_dir, exist_ok=True)
    cv2.imwrite(f"{save_dir}/{file_name}", img)
    return {
        "pitch": float(pitch),
        "yaw": float(yaw),
        "roll": float(roll)
    }
