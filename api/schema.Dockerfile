# ベースイメージ
FROM python:3.11-slim

# 必要なツールをインストール
WORKDIR /app
COPY openapi/openapi.json /app/openapi.json
