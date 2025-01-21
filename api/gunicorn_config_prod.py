# 実行するPythonがあるパス
pythonpath = './'

# ワーカー数
workers = 4

wsgi_app = "app:app"

# ワーカーのクラス、*2 にあるようにUvicornWorkerを指定 (Uvicornがインストールされている必要がある)
worker_class = 'uvicorn.workers.UvicornWorker'

# IPアドレスとポート
bind = '0.0.0.0:5555'

# プロセスIDを保存するファイル名
pidfile = 'prod.pid'

# Pythonアプリに渡す環境変数
raw_env = ['MODE=PROD']

# デーモン化する場合はTrue
# daemon = True

reload = True

# エラーログ
errorlog = './logs/error_log.txt'

# プロセスの名前
proc_name = 'posture_correction_api'

# アクセスログ
accesslog = './logs/access_log.txt'

loglevel = 'debug'
