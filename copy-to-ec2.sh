#!/bin/bash
# EC2へ必要なファイルをコピーするスクリプト

EC2_HOST="ubuntu@3.24.16.82"
KEY_PATH="~/watchme-key.pem"

echo "=== EC2へファイルをコピー ==="

# 環境変数ファイル
echo "1. 環境変数ファイルをコピー..."
scp -i $KEY_PATH .env $EC2_HOST:~/.env.avatar-uploader

# Docker Compose設定
echo "2. Docker Compose設定をコピー..."
scp -i $KEY_PATH docker-compose.prod.yml $EC2_HOST:~/

# 実行スクリプト
echo "3. 実行スクリプトをコピー..."
scp -i $KEY_PATH run-prod.sh $EC2_HOST:~/
scp -i $KEY_PATH run-avatar-uploader.sh $EC2_HOST:~/

# systemd関連
echo "4. systemdファイルをコピー..."
scp -i $KEY_PATH watchme-avatar-uploader.service $EC2_HOST:~/
scp -i $KEY_PATH setup-systemd.sh $EC2_HOST:~/

echo ""
echo "=== コピー完了 ==="
echo ""
echo "次のステップ:"
echo "1. Docker Desktopを起動"
echo "2. ./deploy-ecr.sh を実行"
echo "3. EC2にSSH接続: ssh -i $KEY_PATH $EC2_HOST"
echo "4. EC2で実行:"
echo "   chmod +x *.sh"
echo "   ./setup-systemd.sh  # 初回のみ"
echo "   sudo systemctl restart watchme-avatar-uploader"