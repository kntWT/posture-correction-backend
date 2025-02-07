import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesRegressor
import skl2onnx
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort
import joblib

from estimators.loader import flatten
from estimators.plot import plot_diff_by_y
from estimators.loader import load
from configs.env import model_dir


def root_mean_square_error(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def root_mean_squared_log_error(y_true, y_pred):
    return np.sqrt(mean_squared_log_error(y_true, y_pred))


def calc_accuracy_with_buffer(y_true, y_pred, buffer):
    if len(y_true) <= 0 or len(y_pred) <= 0 or len(y_true) != len(y_pred):
        return 0
    answers = []
    for true, pred in zip(y_true, y_pred):
        ans = 1 if abs(true - pred) <= buffer else 0
        answers.append(ans)
    return sum(answers) / len(answers)


def accuracy_each(y_true, y_pred, _range=(-10, 81, 10)):
    accuracy = [[0 for _ in range(*_range)] for key in range(*_range)]
    _min = int(_range[0] / _range[2])
    _max = int(_range[1] / _range[2])
    offset = _min
    for yt, yp in zip(y_true, y_pred):
        _yt = int((yt + _range[2]/2) / _range[2])
        _yt = max(_min, min(_max, _yt)) - offset
        _yp = int((yp + _range[2]/2) / _range[2])
        _yp = max(_min, min(_max, _yp)) - offset
        # if _yt == 1 and _yp == 1:
        #   print(yt, yp)
        accuracy[_yt][_yp] += 1
    _accuracy = np.array(accuracy)
    # return np.array([np.where(a.sum() > 0, a/a.sum(), np.zeros(a.shape)) for a in _accuracy])
    return np.array([a/a.sum() for a in _accuracy])


def fold5_cross_val_score(estimator, xs, ys_, margin=5, _range=(0, 81, 10), show_plot=True):
    scores = {
        "MAE(train)": np.array([]),
        "MAE(test)": np.array([]),
        "RMSE(train)": np.array([]),
        "RMSE(test)": np.array([]),
        # "RMSLE(train)": np.array([]),
        # "RMSLE(test)": np.array([]),
        "R2(train)": np.array([]),
        "R2(test)": np.array([]),
        "Accuracy5(train)": np.array([]),
        "Accuracy5(test)": np.array([]),
        "Accuracy7(train)": np.array([]),
        "Accuracy7(test)": np.array([]),
        "Accuracy10(train)": np.array([]),
        "Accuracy10(test)": np.array([]),
        "Accuracy15(train)": np.array([]),
        "Accuracy15(test)": np.array([]),
    }
    _len = int((_range[1] - _range[0]) / _range[2]) + 1
    print(_len)
    accuracy = {
        "train": np.empty((len(xs), _len, _len)),
        "test": np.empty((len(xs), _len, _len)),
    }
    # ys = [y - x[1] for x, y in zip(xs, ys_)]
    ys = np.array(ys_, dtype=object)
    # ss = StandardScaler()
    # pca = get_pca(np.concatenate(xs, axis=1), np.concatenate(ys, axis=0))
    # Xs = [pca.transform(ss.fit_transform(x.T)) for x in xs]

    Xs = np.array([x.T for x in xs], dtype=object)
    for i in range(5):
        # test_X = Xs[i]
        # test_y = ys[i]
        # if test_X.shape[0] <= 1:
        #     continue
        # train_X = np.array(flatten(np.delete(Xs, i, 0)))
        # train_y = np.array(flatten(np.delete(ys, i, 0)))

        test_x = Xs[i]
        test_y = ys[i]
        # test_y = ys[i] - (test_x[:, 2] - test_x[:, 1])
        if test_x.shape[0] <= 1:
            continue

        train_x = np.array(flatten(np.delete(Xs, i, 0)))
        # train_x_eliminated = np.delete(train_x, [1, 2], 1)
        # test_x_eliminated = np.delete(test_x, [1, 2], 1)
        train_y = np.array(flatten(np.delete(ys, i, 0)))
        # train_y = np.array(flatten(np.delete(ys, i, 0))) - (train_x[:, 2] - train_x[:, 1])
        ss = StandardScaler()
        train_X = ss.fit_transform(train_x)
        test_X = ss.fit_transform(test_x)
        # train_X = ss.fit_transform(train_x_eliminated)
        # test_X = ss.fit_transform(test_x_eliminated)

        # for y in np.delete(ys, i, 0):
        #   train_y.extend(y)
        # train_y = np.array(train_y)

        estimator.fit(train_X, train_y)

        train_y_pred = estimator.predict(train_X)
        # train_y_pred = estimator.predict(train_X) - (train_x[:, 2] - train_x[:, 1])
        train_mae = mean_absolute_error(train_y, train_y_pred)
        train_rmse = root_mean_square_error(train_y, train_y_pred)
        # train_rmsle = root_mean_squared_log_error(train_y, train_y_pred)
        train_r2 = r2_score(train_y, train_y_pred)
        train_accuracy = accuracy_each(train_y, train_y_pred, _range)
        train_accuracy_5 = calc_accuracy_with_buffer(train_y, train_y_pred, 5)
        train_accuracy_7 = calc_accuracy_with_buffer(train_y, train_y_pred, 7)
        train_accuracy_10 = calc_accuracy_with_buffer(
            train_y, train_y_pred, 10)
        train_accuracy_15 = calc_accuracy_with_buffer(
            train_y, train_y_pred, 15)

        test_y_pred = estimator.predict(test_X)
        # test_y_pred = estimator.predict(test_X) - (test_x[:, 2] - test_x[:, 1])
        test_mae = mean_absolute_error(test_y, test_y_pred)
        test_rmse = root_mean_square_error(test_y, test_y_pred)
        # test_rmsle = root_mean_squared_log_error(test_y, test_y_pred)
        test_r2 = r2_score(test_y, test_y_pred)
        test_accuracy = accuracy_each(test_y, test_y_pred, _range)
        test_accuracy_5 = calc_accuracy_with_buffer(test_y, test_y_pred, 5)
        test_accuracy_7 = calc_accuracy_with_buffer(test_y, test_y_pred, 7)
        test_accuracy_10 = calc_accuracy_with_buffer(test_y, test_y_pred, 10)
        test_accuracy_15 = calc_accuracy_with_buffer(test_y, test_y_pred, 15)

        scores["MAE(train)"] = np.append(scores["MAE(train)"], train_mae)
        scores["MAE(test)"] = np.append(scores["MAE(test)"], test_mae)
        scores["RMSE(train)"] = np.append(scores["RMSE(train)"], train_rmse)
        scores["RMSE(test)"] = np.append(scores["RMSE(test)"], test_rmse)
        # scores["RMSLE(train)"] = np.append(scores["RMSLE(train)"], train_rmsle)
        # scores["RMSLE(test)"] = np.append(scores["RMSLE(test)"], test_rmsle)
        scores["R2(train)"] = np.append(scores["R2(train)"], train_r2)
        scores["R2(test)"] = np.append(scores["R2(test)"], test_r2)
        accuracy["train"][i] = train_accuracy
        accuracy["test"][i] = test_accuracy
        scores["Accuracy5(test)"] = np.append(
            scores["Accuracy5(test)"], test_accuracy_5)
        scores["Accuracy7(train)"] = np.append(
            scores["Accuracy7(train)"], train_accuracy_7)
        scores["Accuracy7(test)"] = np.append(
            scores["Accuracy7(test)"], test_accuracy_7)
        scores["Accuracy10(train)"] = np.append(
            scores["Accuracy10(train)"], train_accuracy_10)
        scores["Accuracy10(test)"] = np.append(
            scores["Accuracy10(test)"], test_accuracy_10)
        scores["Accuracy15(train)"] = np.append(
            scores["Accuracy15(train)"], train_accuracy_15)
        scores["Accuracy15(test)"] = np.append(
            scores["Accuracy15(test)"], test_accuracy_15)
        print(f"MAE(train): {train_mae}")
        print(f"MAE(test): {test_mae}")
        print(f"RMSE(train): {train_rmse}")
        print(f"RMSE(test): {test_rmse}")
        # print(f"RMSLE(train): {train_rmsle}")
        # print(f"RMSLE(test): {test_rmsle}")
        print(f"R2(train): {train_r2}")
        print(f"R2(test): {test_r2}")
        print(f"Accuracy(train): {[train_accuracy[j][j]for j in range(_len)]}")
        print(f"Accuracy(test): {[test_accuracy[j][j] for j in range(_len)]}")
        print(f"Accuracy5(train): {train_accuracy_5}")
        print(f"Accuracy5(test): {test_accuracy_5}")
        print(f"Accuracy7(train): {train_accuracy_7}")
        print(f"Accuracy7(test): {test_accuracy_7}")
        print(f"Accuracy10(train): {train_accuracy_10}")
        print(f"Accuracy10(test): {test_accuracy_10}")
        print(f"Accuracy15(train): {train_accuracy_15}")
        print(f"Accuracy15(test): {test_accuracy_15}")

        if show_plot:
            plot_diff_by_y(train_y, train_y_pred, test_y, test_y_pred)

#   if show_plot:
#     ss = StandardScaler()
#     Xs = [ss.fit_transform(x.T) for x in xs]
#     plot_diff_by_x(np.concatenate(xs, axis=1).T, np.concatenate(Xs, axis=0), np.concatenate(ys, axis=0), estimator)

    _scores = dict(map(lambda x: (x[0], np.mean(x[1])), scores.items()))
    _accuracy = {key: np.nanmean(values, axis=0)
                 for key, values in accuracy.items()}
    return _scores, _accuracy


def train(evaluate=False, output_figure=False):
    data = load()
    xs = [d[0] for d in data]
    ys = [d[1] for d in data]
    estimator = ExtraTreesRegressor(
        bootstrap=True,
        ccp_alpha=0.0,
        max_depth=20,
        max_features=1.0,
        min_impurity_decrease=0.01,
        min_samples_leaf=1,
        min_samples_split=3,
        n_estimators=100,
        n_jobs=1
    )
    if evaluate:
        scores, accuracy = fold5_cross_val_score(
            estimator, xs, ys, _range=(0, 61, 10), show_plot=output_figure)
        print(scores)
        print(accuracy)
    Xs = np.array([x.T for x in xs], dtype=object)
    Ys = np.concatenate(np.array(ys, dtype=object))
    scaler = StandardScaler()
    Xs = scaler.fit_transform(np.concatenate(Xs))
    estimator.fit(Xs, Ys)
    initial_type = [('input', FloatTensorType([None, Xs.shape[1]]))]
    onnx_model = skl2onnx.convert_sklearn(
        estimator, initial_types=initial_type)

    # 保存
    with open(f"{model_dir}/extra_trees.onnx", "wb") as f:
        f.write(onnx_model.SerializeToString())
    joblib.dump(scaler, f"{model_dir}/scaler.pkl")
    print("model trained")
