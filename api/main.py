from gunicorn.app.base import Application
from app import app  # app.pyに定義されたアプリケーションをインポート
import signal
from multiprocessing import Process
from helpers.multiprocessing import init_multiprocessing
import sys
from estimators.features.estimate import init_feature_estimators


class AppWrapper(Application):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        # 設定ファイルを読み込む
        self.load_config_from_file("gunicorn_config_prod.py")

    def load(self):
        return self.application


def handle_shutdown(signum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)


def start_gunicorn():
    AppWrapper(app).run()


if __name__ == "__main__":
    init_multiprocessing()
    init_feature_estimators()
    start_gunicorn()
    # # シグナルハンドラを設定
    # signal.signal(signal.SIGINT, handle_shutdown)  # Ctrl + C
    # signal.signal(signal.SIGTERM, handle_shutdown)  # Kill signal

    # # # Gunicornを別プロセスで実行
    # gunicorn_process = Process(target=start_gunicorn)
    # gunicorn_process.start()

    # try:
    #     # メインプロセスをブロック
    #     gunicorn_process.join()
    # except KeyboardInterrupt:
    #     print("Received KeyboardInterrupt")
    #     gunicorn_process.terminate()
    #     gunicorn_process.join()
