from scipy.spatial.transform import Rotation
import numpy as np
import torch
import pandas as pd
import datetime
import math


def unify_rotation_order(_alpha, _beta, _gamma):
    # NOTE: alphaとgammaが逆転しているが、特徴量に入れる入れない問わず順番を変えるとおかしくなる
    quat = Rotation.from_euler(
        "zxy", np.column_stack([_alpha, _beta, _gamma]), degrees=True
    )
    # mat = quat.as_matrix()
    # .as_euler(
    #     "xyz", degrees=True
    # )
    # beta = rots[:, 0]
    # gamma = rots[:, 1]
    # alpha = rots[:, 2]
    alpha = quat.as_euler("zxy", degrees=True)[:, 0]
    beta = quat.as_euler("xzy", degrees=True)[:, 0]
    gamma = quat.as_euler("yxz", degrees=True)[:, 0]
    return {"alpha": alpha, "beta": beta, "gamma": gamma}
    # """
    # デバイスの向きを、垂直持ちを基準とした角度に変換する。

    # Args:
    #     alpha_in: センサーから取得したalpha値の配列
    #     beta_in: センサーから取得したbeta値の配列
    #     gamma_in: センサーから取得したgamma値の配列

    # Returns:
    #     垂直状態を基準とした 'yaw', 'pitch', 'roll' のndarrayを含む辞書
    # """
    # #
    # # --- ステップ1: 理想の「ゼロ姿勢」を定義 ---
    # #
    # # スマートフォンを垂直に立てた状態（X軸で-90度回転）
    # r_zero_pose = Rotation.from_euler('x', -90, degrees=True)

    # #
    # # --- ステップ2: 現在のセンサー値からRotationオブジェクトを生成 ---
    # #
    # # 入力をNumPy配列に変換
    # alpha_np = np.asarray(_alpha)
    # beta_np = np.asarray(_beta)
    # gamma_np = np.asarray(_gamma)

    # # Scipyが扱いやすいように、(N, 3)の配列にスタックする
    # euler_angles_raw = np.stack([alpha_np, beta_np, gamma_np], axis=-1)
    
    # # 現在のセンサー値から、デバイス全体の向きを表現
    # r_current = Rotation.from_euler('ZXY', euler_angles_raw, degrees=True)

    # #
    # # --- ステップ3: 「ゼロ姿勢」からの相対的な変化を計算 ---
    # #
    # # 垂直状態を基準とした場合の、現在の傾きを計算
    # r_relative = r_current * r_zero_pose.inv()

    # #
    # # --- ステップ4: 相対的な向きから、新しいオイラー角を抽出 ---
    # #
    # # 'YXZ'の順で、直感的な[ロール, ピッチ, ヨー]を取得
    # new_angles = r_relative.as_euler('YXZ', degrees=True)

    # # 結果を分かりやすいキーで辞書に格納して返す
    # # new_anglesは (N, 3) の形状なので、各列を抽出する
    # result = {
    #     "gamma": new_angles[..., 0],  # 左右のひねり
    #     "beta": new_angles[..., 1], # 前後の傾き
    #     "alpha": new_angles[..., 2],   # 左右の向き
    # }
    
    # return result


def parse_np(data, mode="trees"):
    set_id = np.array([float(d.get("set_id", d.get("set_num", 0)))
                      for d in data])
    width = np.array([float(d.get("width", d.get("image_width", 310))) for d in data])
    height = np.array([float(d.get("height", d.get("image_height", 414))) for d in data])
    nose_x = np.array([float(d["nose_x"]) for d in data]) / width
    nose_y = np.array([float(d["nose_y"]) for d in data]) / height
    neck_x = np.array([float(d["neck_x"]) for d in data]) / width
    neck_y = np.array([float(d["neck_y"]) for d in data]) / height
    _neck_to_nose = np.array([float(d.get("neck_to_nose", 0)) for d in data])
    # 正規化された距離は1より小さい
    # 鼻と首は元座標をとっているので正確に計算できる
    neck_to_nose = _neck_to_nose if _neck_to_nose[0] < 1 else np.array([float(math.dist([nose_x[i], nose_y[i]], [neck_x[i], neck_y[i]])) for i in range(len(data))])
    _standard_dist = np.array(
        [float(d.get("standard_dist", d.get("standard_distance"))) for d in data])
    # 目と目の距離は各座標を取得していなかったので、y方向の差分を０と仮定してdistをwidthで割ることで近似的に正規化する
    standard_dist = _standard_dist if _standard_dist[0] < 1 else _standard_dist / width
    normalized_dist = neck_to_nose / standard_dist
    neck_to_nose_standard = np.array([float(
        d.get("neck_to_nose_standard", 0)) if "neck_to_nose_standard" in d and d.get("neck_to_nose_standard", 0) is not None else 2.5 for d in data])
    normalized_ratio = normalized_dist / neck_to_nose_standard
    # user_id = np.array([float(d.get("user_id")) for d in data])
    # ref_neck_to_nose = np.array([REF_POSTURE[u]["neck_to_nose"] for u in user_id])
    # ref_standard_dist = np.array([REF_POSTURE[u]["standard_dist"] for u in user_id])
    # ref_normalized_dist = ref_neck_to_nose / ref_standard_dist
    # normalized_ratio = normalized_dist / ref_normalized_dist
    orientation_alpha = np.array(
        [float(d.get("orientation_alpha", d.get("sensor_alpha", d.get("alpha")))) for d in data])
    orientation_beta = np.array(
        [float(d.get("orientation_beta", d.get("sensor_beta", d.get("beta")))) for d in data])
    orientation_gamma = np.array(
        [float(d.get("orientation_gamma", d.get("sensor_gamma", d.get("gamma")))) for d in data])
    rots = unify_rotation_order(orientation_alpha, orientation_beta, orientation_gamma)
    alpha = rots["alpha"]
    beta = 90 - rots["beta"]
    gamma = rots["gamma"]
    print(alpha[0], beta[0], gamma[0])
    pitch = np.array([float(d.get("pitch", d.get("face_pitch"))) for d in data])
    yaw = np.array([float(d.get("yaw", d.get("face_yaw"))) for d in data])
    roll = np.array([float(d.get("roll", d.get("face_roll"))) for d in data])

    neck_angle = np.array([float(d.get("neck_angle", 0)) for d in data])
    # neck_angle_offset = np.array([float(d["neck_angle_offset"] if "neck_angle_offset" in d else 0) for d in data])
    # neck_angle_offset = np.array([REF_POSTURE[u]["neck_angle_offset"] for u in user_id])
    # timestamp = np.array([datetime.datetime.strptime(d['in_created_at'] + (".000000" if len(d["in_created_at"]) == 19 else ""), "%Y-%m-%d %H:%M:%S.%f") for d in data])

    thres = 45
    def filter(i):
        return True
        # return beta[i] <= 100 and \
        #         beta[i] >= -10 and \
        #         abs(pitch[i]) <= 100 and \
        #         abs(gamma[i]) <= thres and \
        #         abs(yaw[i]) <= thres and \
        #         abs(roll[i]) <= thres
                # abs(alpha[i]) <= thres and \
                #  user_id[i] > 10
    x_ = []
    y_ = []
    for i in range(len(data)):
        if filter(i):
            content = [
                normalized_ratio[i], # trees
                beta[i], # trees, lightGBM
                pitch[i], # trees, lightGBM
                #   neck_angle_offset[i],
            ] if mode == "trees" else [
                # set_id[i],
                neck_to_nose[i], # lightGBM
                standard_dist[i], # lightGBM
                # normalized_ratio[i],
                neck_to_nose_standard[i], # lightGBM
                #   ref_normalized_dist[i], # lightGBM
                # ref_neck_to_nose[i], # lightGBM
                # ref_standard_dist[i], # lightGBM
                # normalized_ratio[i], # trees
                # alpha[i], # lightGBM
                beta[i], # trees, lightGBM
                # gamma[i], # lightGBM
                pitch[i], # trees, lightGBM
                yaw[i], # lightGBM
                roll[i], # lightGBM
                #   math.sin(math.radians(pitch[i])), # lightGBM
                #   math.sin(math.radians(yaw[i])), # lightGBM
                #   pitch[i] - beta[i],
                #   yaw[i] - alpha[i],
                #   roll[i] - gamma[i],
                nose_x[i], # lightGBM
                nose_y[i], # lightGBM
                neck_x[i], # lightGBM
                neck_y[i], # lightGBM
                # neck_angle_offset[i],
                #   _id[i],
                #   timestamp[i],
            ]
            x_.append(np.array(content))
            # y_.append([np.array(neck_angle[i], neck_angle_offset[i]]))
            y_.append(np.array(neck_angle[i]))
        else:
            print("features filtered")
    x = np.array(x_).T
    y = np.array(y_).T
    # y = np.array(y_)
    return x, y


def parse_torch(data):
    x_, y_ = parse_np(data)
    return parse_torch_from_np(x_, y_)


def parse_torch_from_np(x_, y_):
    x = torch.from_numpy(x_).float()
    y = torch.from_numpy(y_).float()
    return x, y


def parse_pd(data, feat_mode: str = "trees"):
    x_, y_ = parse_np(data, feat_mode)
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
