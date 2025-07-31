#!/bin/bash
set -e

# 変数設定
AWS_REGION="ap-southeast-2"
ECR_REPOSITORY="754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-avatar-uploader"
IMAGE_TAG="latest"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "=== ECRへのデプロイを開始します ==="
echo "リポジトリ: $ECR_REPOSITORY"

# ECRにログイン
echo "ECRにログイン中..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com

# Dockerイメージをビルド（本番用）
echo "Dockerイメージをビルド中..."
docker build -f Dockerfile.prod -t watchme-api-avatar-uploader .

# ECR用のタグを付与
echo "タグを付与中..."
docker tag watchme-api-avatar-uploader:latest $ECR_REPOSITORY:$IMAGE_TAG
docker tag watchme-api-avatar-uploader:latest $ECR_REPOSITORY:$TIMESTAMP

# ECRにプッシュ
echo "ECRにプッシュ中..."
docker push $ECR_REPOSITORY:$IMAGE_TAG
docker push $ECR_REPOSITORY:$TIMESTAMP

echo "=== デプロイが完了しました ==="
echo "ECRリポジトリ: $ECR_REPOSITORY"
echo "イメージタグ: $IMAGE_TAG および $TIMESTAMP"
echo ""
echo "次のステップ:"
echo "1. EC2インスタンスにSSH接続: ssh -i ~/watchme-key.pem ubuntu@3.24.16.82"
echo "2. デプロイスクリプトを実行: ./run-prod.sh"