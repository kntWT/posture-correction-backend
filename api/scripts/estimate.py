import sys
from configs.env import image_dir
from estimators.features.estimate import estimate

if __name__ == "__main__":
    estimate(f"{image_dir}/内カメラ", "original", sys.argv[1])
