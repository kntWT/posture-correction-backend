import multiprocessing as mp
from estimators.features.face import estimate_head_pose, init_head_pose_estimator
from estimators.features.body import estimate_body_pose, init_body_pose_estimator
# from helpers.synchronize import run_async_in_sync
import os
from configs.env import estimate_body_pose_pool_count, estimate_head_pose_pool_count

estimate_head_pose_pool = None
estimate_body_pose_pool = None

# モジュールの初期化時に実行される
def init_multiprocessing():
    #if mp.get_start_method(allow_none=True) != "spawn":
    #    mp.set_start_method("spawn", force=True)
    print(f"init_multiprocessing, pid:{os.getpid()}")
    global estimate_head_pose_pool
    global estimate_body_pose_pool
    if estimate_head_pose_pool != None or estimate_body_pose_pool != None:
        print("init_multiprocessing: already initialized")
        return
    try:
        estimate_head_pose_pool = mp.Pool(estimate_head_pose_pool_count, initializer=init_head_pose_estimator, maxtasksperchild=100)
        estimate_body_pose_pool = mp.Pool(estimate_body_pose_pool_count, initializer=init_body_pose_estimator, maxtasksperchild=100)
    except Exception as e:
        print(e)

def estimate_head_pose_in_process(*args):
    result = estimate_head_pose_pool.apply(estimate_head_pose, args)
    return result

def estimate_body_pose_in_process(*args):
    result = estimate_body_pose_pool.apply(estimate_body_pose, args)
    return result
