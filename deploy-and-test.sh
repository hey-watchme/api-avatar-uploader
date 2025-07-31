#!/bin/bash
# 本番環境へのデプロイとテストを一括実行

set -e

echo "=== Avatar Uploader API 本番デプロイ ==="
echo ""

# 1. Docker Desktopの起動確認
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker Desktopが起動していません"
    echo "Docker Desktopを起動してから再実行してください"
    exit 1
fi

echo "✅ Docker実行環境: OK"
echo ""

# 2. ECRへのプッシュ
echo "📦 ECRへイメージをプッシュしています..."
if ./deploy-ecr.sh; then
    echo "✅ ECRプッシュ: 完了"
else
    echo "❌ ECRプッシュ: 失敗"
    exit 1
fi

echo ""
echo "=== 次のステップ ==="
echo ""
echo "1. EC2にSSH接続:"
echo "   ssh -i ~/watchme-key.pem ubuntu@3.24.16.82"
echo ""
echo "2. 初回セットアップの場合:"
echo "   # ファイルが存在しない場合のみ実行"
echo "   ./setup-systemd.sh"
echo ""
echo "3. サービスを再起動:"
echo "   sudo systemctl restart watchme-avatar-uploader"
echo "   sudo systemctl status watchme-avatar-uploader"
echo ""
echo "4. ローカルから本番環境をテスト:"
echo "   python3 test_production.py"
echo ""
echo "=== デプロイ準備完了 ==="