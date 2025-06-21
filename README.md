# posture-correction-backend
姿勢矯正システムのバックエンド\
- スマートフォンのセンサ情報と内カメラの画像からユーザの首の角度を推定します
- システムを利用したい場合は[利用方法](#利用方法)を参照してください
- システムをローカルでセットアップしたい場合は[セットアップ方法](#セットアップ方法)を参照してください

# 構成
- Docker Composeにapi(FastAPI)とdb(MySQL)を配置
- ローカルのGPUを使用して推論を行う（nvidia/cuda:12.1.1）


**開発で使用するポート一覧**

| サービス名 | ポート番号 | 備考 |
| --- | --- | --- |
| FastAPI | 3330 | API |
| MySQL | 3331 | データベース |
| PHPMyAdmin | 3332 | データベース管理 |


## API

### OpenAPI
[DockerHub](https://hub.docker.com/repository/docker/kntwt/posture-correction-schema/general)でpublicになっているので適宜参照してください（APIを立ち上げたら`http://localhost:3330/docs`でも参照できます）
フロントエンド開発時にpullすると型安全にAPIを呼び出すことができます

### ユーザ周り
- ユーザの登録
  - Basic認証またはメールアドレスで新規作成できます（それぞれエンドポイントが異なります）
- キャリブレーション
  - ユーザごとにより正確な推定を行うためキャリブレーションが必要です
  - なるべくスマートフォンの角度、ユーザの顔の角度がずれないように首をまっすぐにした状態でキャリブレーションを行ってください
- 情報へのアクセス
  - ユーザに関する情報にアクセスするにはログイン後に発行されるJWT TokenをCookieに含めてリクエストする必要があります
  - ログイン時にCookieに埋め込むのでそれをそのまま利用してください

### 姿勢推定
- 姿勢推定にはスマートフォンのジャイロセンサと内カメラの画像を含める必要があります
- ログインしたユーザの姿勢推定には事前にキャリブレーションが必要で、CookieにJWT Tokenが含まれている必要があります
- ゲストユーザ用のエンドポイント（`/posture/estimate/guest`）ではキャリブレーションが不要です
- キャリブレーションする前にユーザの顔の角度のみフィードバックしたい場合は`/posture/estimate/feature`を使用してください

## データベース
- データベースにはMySQLを使用しています
- テーブルのスキーマは`db/init/1_create_table.sql`を参照してください


# 利用方法
- 利用先のサーバ（またはローカル）で[Tailscale](https://tailscale.com/)などを用いてVPN接続してください
- 利用先のHTTPサーバでプロキシし、`<接続先のIP>:3330/`につなぐことでAPIが利用できます
- [APIの構成](#api)を参照し適切にAPIを呼び出してください（SSLやCORSに注意してください）
- 接続先（このバックエンドが動いているホストマシン）が長時間操作されないとDockerが落ちる場合があるので注意してください

# セットアップ方法
## 環境変数
`.env.sample`をコピーし、値が`<>`で囲われているものを適当な値に変更して利用してください
```sh
cp .env.sample .env
```
- `ESTIMATE_BODY_POSE_POOL_COUNT`と`ESTIMATE_HEAD_POSE_POOL_COUNT`はそれぞれ首の角度推定に用いる特徴量抽出（骨格推定と頭部姿勢推定）に割り当てるプロセス数です。動作環境に合わせて適切な値を設定してください
- `MOCK_SECRET_KEY`と`TRAIN_IF_NOT_EXIST`はworkflow用の変数なので、開発段階では既定の値から変更しないでください

## 姿勢推定
- 姿勢推定に用いる骨格推定ライブラリとして[Pytorch-OpenPose](https://github.com/Hzzone/pytorch-openpose)を利用しています。`git submodule init`、`git submodule update`を実行後、リポジトリのREADMEに従いmodelを`api/pytorch-openpose/model`配下に配置してください
- 起動時に首の角度推定モデルがない場合に学習が走るので、`api/estimators/data`配下に[学習に必要なデータ](https://drive.google.com/drive/u/0/folders/1DCPd7bjqo80g9JaEFJEANtliDxzXwIs_)を配置してください（ファイル名は変更しないでください）
- 姿勢推定実行後、元画像、頭部姿勢推定結果、骨格推定結果がそれぞれ`api/images(または環境変数で指定したディレクトリ)/:userId/(original|head|neck)`に出力されます

## ユーザ認証
- JWTの署名に公開鍵と秘密鍵を利用しています。`EdDSA`形式で暗号化した鍵を`api/configs/keys`に配置してください（`secret_key`、`publick_key.pub`）
- Cookieに署名するkeyは環境変数で変更できます
