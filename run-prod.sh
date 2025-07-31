#!/bin/bash
set -e

ECR_REPOSITORY="754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-avatar-uploader"
AWS_REGION="ap-southeast-2"
CONTAINER_NAME="watchme-avatar-uploader"

echo "=== watchme-api-avatar-uploader 本番環境起動 ==="

# ECRから最新イメージをプル
echo "ECRから最新イメージをプル中..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com
docker pull $ECR_REPOSITORY:latest

# 既存のコンテナを停止・削除
echo "既存のコンテナを停止中..."
docker-compose -f docker-compose.prod.yml down || true

# 本番環境でコンテナを起動
echo "新しいコンテナを起動中..."
docker-compose -f docker-compose.prod.yml up -d

# 起動確認
echo "起動確認中..."
sleep 5
if docker ps | grep -q $CONTAINER_NAME; then
    echo "✅ コンテナが正常に起動しました"
    docker logs $CONTAINER_NAME --tail 20
else
    echo "❌ コンテナの起動に失敗しました"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo "=== 起動完了 ==="
echo "アプリケーションURL: http://localhost:8014"
echo "ヘルスチェック: http://localhost:8014/health"
echo ""
echo "外部公開URL: https://api.hey-watch.me/avatar/"