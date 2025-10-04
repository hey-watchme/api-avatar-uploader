# Avatar Uploader API - 変更履歴

## 2025-10-04
### 修正
- docker-compose.prod.ymlに`watchme-network`設定を追加
- run-avatar-uploader.shに`--env-file`オプションを追加して環境変数を正しく読み込むように修正
- 環境変数の読み込み問題により発生していたS3アップロードエラー（NoSuchBucket）を解決

## 2025-08-16
### 更新
- **HTTPS化完了**: Nginx経由で`https://api.hey-watch.me/avatar/`でアクセス可能に
- **S3バケット名を統一**: `watchme-vault` → `watchme-avatars`に変更
- **S3リージョンを正しく設定**: `us-east-1` → `ap-southeast-2`に修正
- **S3パブリックアクセス設定**: アップロードされた画像が正しく表示されるよう設定
- **本番環境へのデプロイ完了**: EC2インスタンス（3.24.16.82）で稼働中

## 2025-07-31
### 変更
- 開発・テスト用に認証機能を一時無効化
- エンドポイントのパスを変更:
  - `/v1/users/me/avatar` → `/v1/users/{user_id}/avatar`
  - パラメータでuser_idとsubject_idを直接指定する形式に変更
- データベース連携の実装:
  - Supabaseのusersテーブルとsubjectsテーブルのavatar_urlカラムを自動更新
  - S3アップロード後、失敗時は自動ロールバック
