#!/bin/bash
# systemd用の起動スクリプト
set -e

ECR_REPOSITORY="754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-avatar-uploader"
AWS_REGION="ap-southeast-2"

# 環境変数ファイルを読み込む
if [ -f /home/ubuntu/.env.avatar-uploader ]; then
    export $(cat /home/ubuntu/.env.avatar-uploader | xargs)
fi

# ECRから最新イメージをプル
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com
docker pull $ECR_REPOSITORY:latest

# 既存のコンテナを停止・削除
docker-compose -f /home/ubuntu/docker-compose.prod.yml down || true

# 本番環境でコンテナを起動
docker-compose -f /home/ubuntu/docker-compose.prod.yml up -d