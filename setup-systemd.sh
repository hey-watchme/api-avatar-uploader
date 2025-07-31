#!/bin/bash
# systemdサービスのセットアップスクリプト
# EC2インスタンス上で実行する

set -e

echo "=== systemdサービスのセットアップ ==="

# サービスファイルをコピー
sudo cp watchme-avatar-uploader.service /etc/systemd/system/

# 実行権限を付与
chmod +x run-avatar-uploader.sh

# systemdをリロード
sudo systemctl daemon-reload

# サービスを有効化
sudo systemctl enable watchme-avatar-uploader.service

echo "=== セットアップ完了 ==="
echo ""
echo "使用方法:"
echo "  起動: sudo systemctl start watchme-avatar-uploader"
echo "  停止: sudo systemctl stop watchme-avatar-uploader"
echo "  状態確認: sudo systemctl status watchme-avatar-uploader"
echo "  ログ確認: sudo journalctl -u watchme-avatar-uploader -f"
echo ""
echo "自動起動が有効になりました。サーバー再起動時に自動的に起動します。"