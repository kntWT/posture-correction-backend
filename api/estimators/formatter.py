from scipy.spatial.transform import Rotation
import numpy as np
import torch
import pandas as pd


def unify_rotation_order(alpha, beta, gamma):
    rots = np.array([Rotation.from_euler("zyx", [a, b, g], degrees=True).as_euler(
        "yxz", degrees=True) for a, b, g in zip(alpha, beta, gamma)])
    beta = rots[:, 0]
    gamma = rots[:, 1]
    alpha = rots[:, 2]
    return {"alpha": alpha, "beta": beta, "gamma": gamma}


def parse_np(data):
    set_id = np.array([float(d.get("set_id", d.get("set_num", 0)))
                      for d in data])
    neck_to_nose = np.array([float(d.get("neck_to_nose", 0)) for d in data])
    standard_dist = np.array(
        [float(d.get("standard_dist", d.get("standard_distance"))) for d in data])
    normalized_dist = neck_to_nose / standard_dist
    neck_to_nose_standard = np.array([float(
        d.get("neck_to_nose_standard", 0)) if "neck_to_nose_standard" in d and d.get("neck_to_nose_standard", 0) is not None else 2.5 for d in data])
    normalized_ratio = normalized_dist / neck_to_nose_standard
    orientation_alpha = np.array(
        [float(d.get("orientation_alpha", d.get("sensor_alpha", d.get("alpha", 0)))) for d in data])
    orientation_beta = np.array(
        [float(d.get("orientation_beta", d.get("sensor_beta", d.get("beta", 0)))) for d in data])
    orientation_gamma = np.array(
        [float(d.get("orientation_gamma", d.get("sensor_gamma", d.get("gamma", 0)))) for d in data])
    rots = unify_rotation_order(
        orientation_alpha, orientation_beta, orientation_gamma)
    alpha = rots["alpha"]
    beta = 90 - rots["beta"]
    gamma = rots["gamma"]
    pitch = np.array([float(d.get("pitch", d.get("face_pitch", 0)))
                     for d in data])
    yaw = np.array([float(d.get("yaw", d.get("face_pitch", 0))) for d in data])
    roll = np.array([float(d.get("roll", d.get("face_pitch", 0)))
                    for d in data])
    nose_x = np.array([float(d.get("nose_x", 0)) for d in data])
    nose_y = np.array([float(d.get("nose_y", 0)) for d in data])
    neck_x = np.array([float(d.get("neck_x", 0)) for d in data])
    neck_y = np.array([float(d.get("neck_y", 0)) for d in data])

    neck_angle = np.array(
        [float(d.get("neck_angle", 0) if "neck_angle" in d else 0) for d in data])
    neck_angle_offset = np.array(
        [float(d.get("neck_angle_offset", 0) if "neck_angle_offset" in d else 0) for d in data])

    thres = 45

    def filter(i):
        return beta[i] <= 100 and \
            beta[i] >= -10 and \
            abs(pitch[i]) <= 100 and \
            abs(alpha[i]) <= thres and \
            abs(gamma[i]) <= thres and \
            abs(yaw[i]) <= thres and \
            abs(roll[i]) <= thres
    x_ = []
    y_ = []
    for i in range(len(data)):
        if filter(i):
            x_.append(np.array([
                # set_id[i],
                #   neck_to_nose[i], # lightGBM
                #   standard_dist[i], # lightGBM
                #   neck_to_nose_standard[i], # lightGBM
                normalized_ratio[i],  # trees
                #   alpha[i], # lightGBM
                beta[i],  # trees, lightGBM
                #   gamma[i], # lightGBM
                pitch[i],  # trees, lightGBM
                #   yaw[i], # lightGBM
                #   roll[i], # lightGBM
                #   math.sin(math.radians(pitch[i])), # lightGBM
                #   math.sin(math.radians(yaw[i])), # lightGBM
                #   pitch[i] - beta[i],
                #   yaw[i] - alpha[i],
                #   roll[i] - gamma[i],
                #   nose_x[i], # lightGBM
                #   nose_y[i], # lightGBM
                #   neck_x[i], # lightGBM
                #   neck_y[i], # lightGBM
            ]))
            y_.append(np.array(neck_angle[i] - neck_angle_offset[i]))
    x = np.array(x_).T
    y = np.array(y_)
    return x, y


def parse_torch(data):
    x_, y_ = parse_np(data)
    return parse_torch_from_np(x_, y_)


def parse_torch_from_np(x_, y_):
    x = torch.from_numpy(x_).float()
    y = torch.from_numpy(y_).float()
    return x, y


def parse_pd(data):
    x_, y_ = parse_np(data)
    return parse_pd_from_np(x_, y_)


def parse_pd_from_np(x_, y_):
    col_n, row_n = x_.shape
    x = pd.DataFrame(data=x_.T, columns=[i for i in range(col_n)])
    y = pd.DataFrame(data=y_.T, columns=[0])
    return x, y


def try_parse_float(data):
    ret_data = []
    for _d in data:
        d = {}
        for key, value in _d.items():
            try:
                d[key] = float(value)
            except ValueError:
                d[key] = value
        ret_data.append(d)
    return ret_data
