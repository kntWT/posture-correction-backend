import numpy as np
import re
import pandas as pd
import os
import torch

from estimators.formatter import parse_np, try_parse_float, parse_torch, parse_pd


def load_data_from_csvs(dir: str = "data", mode: str = "torch", filter_reg=re.compile(r".\.csv"), remove_reg=None):
    x = None
    y = None
    for file_name in os.listdir(dir):
        if not file_name.endswith(".csv"):
            continue
        elif not filter_reg.search(file_name):
            continue
        elif remove_reg is not None and remove_reg.search(file_name):
            continue

        x_, y_ = load_data_from_csv(f"{dir}/{file_name}", mode)
        # x.extend(x_)
        # y.extend(y_)
        if x is None or y is None:
            x = x_
            y = y_
        else:
            if mode == "torch":
                x = torch.cat((x, x_), 0)
                y = torch.cat((y, y_), 0)
            elif mode == "np" or mode == "numpy":
                # print(x.shape, x_.shape)
                x = np.concatenate((x, x_), axis=1)
                # print(y.shape, y_.shape)
                y = np.concatenate((y, y_))
            elif mode == "pd" or mode == "pandas":
                x = pd.concat([x, x_], ignore_index=True)
                y = pd.concat([y, y_], ignore_index=True)
            else:
                return None
    return x, y


def load_data_from_csv(file_name: str, mode: str = "torch"):
    data = []
    with open(file_name) as f:
        lines = f.readlines()
        cols = lines[0].replace('"', "").replace("\n", "").split(",")
        for line in lines[1:]:
            data_list = line.replace('"', "").replace("\n", "").split(",")
            data.append({cols[i]: data_list[i] for i in range(len(cols))})

    if mode == "torch":
        return parse_torch(data)
    elif mode == "np" or mode == "numpy":
        return parse_np(data)
    elif mode == "pd" or mode == "pandas":
        return parse_pd(data)
    elif mode == "list":
        return try_parse_float(data)
    else:
        return None


def load_data_from_joined_csv(file_name: str, shuffle=True):
    joined_list = load_data_from_csv(file_name, "list")
    joined = split_data(joined_list, "set_id", 1)
    # [set_id][dimension]
    joined_nps = [parse_np(j) for j in joined]
    if shuffle:
        np.random.shuffle(joined_nps)
    return joined_nps


def split_data(data, key: str, min_index: int = 0, split_num: int = 5):
    data_list = [[] for _ in range(split_num)]
    for d in data:
        index = int(d[key]) - min_index
        if index < 0 or index >= split_num:
            continue
        data_list[index].append(d)

    return data_list


def flatten(arr):
    ret_arr = []
    for v in arr:
        ret_arr.extend(v)
    return ret_arr


def concat_data(data_list):
    # [user_id][set_id][x, y] -> [set_id][dims][x
    user_num = len(data_list)
    set_num = len(data_list[0])
    cols = [data_list[0][0][i].shape[0] if len(
        data_list[0][0][i].shape) > 1 else 1 for i in range(len(data_list[0][0]))]
    row_nums = [sum([d[i][0].shape[1] for d in data_list])
                for i in range(set_num)]
    data = [[np.empty((cols[0], row_nums[i])), np.empty((row_nums[i],))]
            for i in range(set_num)]
    for i in range(len(data_list[0])):
        for j in range(len(data_list[0][i])):
            axis = 1 if len(data_list[0][i][j].shape) > 1 else 0
            data[i][j] = np.concatenate([d[i][j]
                                        for d in data_list], axis=axis)
    return data


def load(path: str = "estimators/data"):
    joined_nps_all = np.array([])
    for file_name in os.listdir(path):
        if not file_name.endswith(".csv"):
            continue
        joined_np = load_data_from_joined_csv(os.path.join(path, file_name), False)
        joined_nps_all = [*joined_nps_all, joined_np]
    return np.array(concat_data(joined_nps_all), dtype=object)
