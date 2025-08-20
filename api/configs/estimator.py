import os

train_method = "lightGBM" # "trees"
dataset_file_name = "estimators/data/dataset.csv"
use_under_sampling = True
dataset_type = "union"
dataset_split_column = "user_id"
dataset_split_min_index = 11
dataset_split_num = 4
data_range = (0, 61, 15)
data_range_margin = 5
trees_params = {
    "bootstrap": True,
    "ccp_alpha": 0.0,
    "max_depth": 20,
    "max_features": 1.0,
    "min_impurity_decrease": 0.01,
    "min_samples_leaf": 1,
    "min_samples_split": 3,
    "n_estimators": 100,
    "n_jobs": 1
}
lgb_params = {
    'objective': 'regression',
    'boosting_type': 'gbdt',
    'metric': 'rmse',
    "device": "cpu",
    'verbosity': -1,
    'learning_rate': 0.09686737182522671,
    'num_leaves': 73,
    'max_depth': 13,
    'feature_fraction': 0.8694096287219913,
    'bagging_fraction': 0.6227147380713965,
    'bagging_freq': 9,
    'lambda_l1': 0.024450887804406532,
    'lambda_l2': 2.625370263087402e-06
}
lgb_columns = [
    "首から鼻",
    "目と目",
    "基準姿勢",
    "スマホalpha",
    "スマホbeta",
    "スマホgamma",
    "顔pitch",
    "顔yaw",
    "顔roll",
    "sin(pitch)",
    "sin(yaw)",
    "鼻X",
    "鼻Y",
    "首X",
    "首Y"
]
model_file_name = "estimator.onnx"
scaler_file_name = "scaler.pkl"
image_size = 384
train_data_resized = False

model_dir = "estimators/model"
evaluate_output_dir = "estimators/figures"
train_data_dir = "estimators/data"

os.makedirs(model_dir, exist_ok=True)
os.makedirs(evaluate_output_dir, exist_ok=True)
os.makedirs(train_data_dir, exist_ok=True)

guest_neck_to_nose_standard = 3.0
