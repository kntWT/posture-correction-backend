import torch.multiprocessing as mp
# from helpers.synchronize import run_async_in_sync

# モジュールの初期化時に実行される
def init_multiprocessing():
    if mp.get_start_method(allow_none=True) != "spawn":
        mp.set_start_method("spawn", force=True)

def run_in_process(func, initializer, *args):
    with mp.Pool(1, initializer=initializer) as pool:
        result = pool.apply(func, args)
    return result

# def run_async_in_process(func, *args):
#     with mp.Pool(1) as pool:
#         result = pool.apply(run_async_in_sync, (func, *args))
#     return result

def run_in_single_process(func, *args, **kwds):
    return func(*args, **kwds)
