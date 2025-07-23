import numpy as np
import re
import pandas as pd
import os
import torch
from random import sample

from estimators.formatter import parse_np, try_parse_float, parse_torch, parse_pd
import configs.estimator as config


def load_data_from_csvs(dir: str = "data", mode: str = "torch", filter_reg=re.compile(r".\.csv"), remove_reg=None, feat_mode: str = "trees"):
    x = None
    y = None
    for file_name in os.listdir(dir):
        if not file_name.endswith(".csv"):
            continue
        elif not filter_reg.search(file_name):
            continue
        elif remove_reg is not None and remove_reg.search(file_name):
            continue

        x_, y_ = load_data_from_csv(f"{dir}/{file_name}", mode, feat_mode)
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


def load_data_from_csv(file_name: str, mode: str = "torch", feat_mode: str = "trees"):
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
        return parse_np(data, feat_mode)
    elif mode == "pd" or mode == "pandas":
        return parse_pd(data)
    elif mode == "list":
        return try_parse_float(data)
    else:
        return None


def load_data_from_joined_csv(file_name: str, shuffle=True, feat_mode: str = "trees"):
    joined_list = load_data_from_csv(file_name, "list", feat_mode)
    joined = split_data(joined_list, "set_id", 1)
    # [set_id][dimension]
    joined_nps = [parse_np(j, feat_mode) for j in joined]
    if shuffle:
        np.random.shuffle(joined_nps)
    return joined_nps

def load_data_from_joined_all_member_csv(file_name, shuffle=True, feat_mode="trees"):
    joined_list = load_data_from_csv(file_name, "list", feat_mode=feat_mode)
    if config.dataset_split_column is not None:
        joined = split_data(joined_list, config.dataset_split_column, config.dataset_split_min_index, config.dataset_split_num)
    
    #   joined = [split_data(j, "set_id", 1) for j in joined_list]
    # [set_id][dimension]
    print([len(d) for d in joined])
    joined_nps = [parse_np(j, mode=feat_mode) for j in joined]
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


def concat_to_section_data(data_list):
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

# [user_id][x, y] -> [dims]
def concat_to_single_section_data(data_list):
    cols = [data_list[0][i].shape[0] if len(data_list[0][i].shape) > 1 else 1 for i in range(len(data_list[0]))]
    row_num = sum([d[0].shape[1] for d in data_list])
    data = [ np.empty((cols[0], row_num)), np.empty((row_num,)) ]
    # data = [[ np.empty((cols[0], row_nums[i])), np.empty((2, row_nums[i])) ] for i in range(set_num)]
    for i in range(len(data_list[0])):
          axis = 1 if len(data_list[0][i].shape) > 1 else 0
          data[i] = np.concatenate([d[i] for d in data_list], axis=axis)
    return data

# input: [data_type][data] as numpy array
def resample_to_equal_size(data_list: np.ndarray, group_range=(0, 61, 10), margin=5):
    if margin > group_range[2] / 2:
        raise ValueError("Margin should be less than or equal to half of the group range.")
    grouped = [[] for _ in range(*group_range)]
    for i, _y in enumerate(data_list[1]):
        x = data_list[0].T[i]
        y = int((_y+margin) / group_range[2])
        if 0 <= y < len(grouped) and abs(y*group_range[2] - _y) <= margin:
            grouped[y].append(np.array([x, _y], dtype=object))

    print([len(g) for g in grouped])
    min_size = min([len(g) for g in grouped])
    if min_size <= 0:
       return np.array([[], []])
    balanced = [[] for _ in range(len(grouped))]
    for i, group in enumerate(grouped):
          balanced[i].extend(sample(group, min_size))
    for i, b in enumerate(balanced):
        x = np.array(np.array(b).T[0].tolist()).T
        y = np.array(b).T[1]
        balanced[i] = np.array([x, y], dtype=object)

    print([len(b[1]) for b in balanced])
    return np.array(concat_to_single_section_data(balanced), dtype=object)


def load_from_separated_data(path: str = "estimators/data", mode: str = "trees"):
    joined_nps_all = np.array([])
    for file_name in os.listdir(path):
        if not file_name.endswith(".csv"):
            continue
        joined_np = load_data_from_joined_csv(os.path.join(path, file_name), False, mode)
        joined_nps_all = [*joined_nps_all, joined_np]
    return np.array(concat_to_section_data(joined_nps_all), dtype=object)

def load_from_unioned_data(file_name: str, mode: str = "trees", under_sample: bool = False, _range = (0, 61, 15), margin: int = 5):
    if not file_name.endswith(".csv"):
        raise ValueError("only csv format is accepted")
    print("data load")
    joined_np = load_data_from_joined_all_member_csv(file_name, False, feat_mode=mode)
    joined_np_all_user = np.array(concat_to_single_section_data(joined_np), dtype=object)
    if under_sample:
        joined_np_all_user = resample_to_equal_size(joined_np_all_user, _range, margin)
    return joined_np_all_user
    
