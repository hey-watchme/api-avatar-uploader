# WatchMe Avatar Management API

iOS、Android、Webアプリケーション共通で使用するアバター管理APIです。

## 🔴 重要なセキュリティ警告

**このAPIは現在、認証機能が無効化されており、深刻なセキュリティリスクがあります。**

### 現在の問題点
- ❌ **誰でもアクセス可能**: 認証なしで全てのエンドポイントにアクセス可能
- ❌ **他人のアバター変更可能**: 悪意のある第三者が任意のユーザーIDを指定してアバターを変更できる
- ❌ **データ改ざんリスク**: user_idやsubject_idを知っていれば誰でもデータを変更可能

**本番環境移行前に認証機能の有効化が必須です。**

---

## 📋 概要

このAPIは、ユーザーおよび観測対象者（Subject）のアバター画像をAWS S3に安全にアップロード・管理する機能を提供します。

### 主な機能

- ユーザーアバターのアップロード/更新/削除
- 観測対象者アバターのアップロード/更新/削除
- 画像の自動リサイズと最適化（512x512px）
- Supabaseデータベースとの自動連携（avatar_url更新）

### 技術スタック

- **FastAPI** - Webフレームワーク
- **AWS S3** - 画像ストレージ（リージョン: ap-southeast-2）
- **Supabase** - データベース
- **Pillow** - 画像処理
- **Boto3** - AWS SDK

---

## 🚀 デプロイプロセス

### 前提条件
- AWS ECRリポジトリ: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-avatar-uploader`
- EC2インスタンス: `3.24.16.82`
- ポート: `8014`
- SSH鍵: `/Users/kaya.matsumoto/watchme-key.pem`

### デプロイフロー

```
┌─────────────────┐
│  ローカル環境    │
└────────┬────────┘
         │
         │ 1. コード変更時のみ
         ▼
   ./deploy-ecr.sh ─────► ECRにイメージをプッシュ
                          (754724220380.dkr.ecr...watchme-api-avatar-uploader:latest)
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────┐
│  EC2サーバー (3.24.16.82)            │
│                                     │
│  2. サービス再起動                    │
│  sudo systemctl restart             │
│    watchme-avatar-uploader          │
│         │                           │
│         ▼                           │
│  run-avatar-uploader.sh             │
│    - ECRから最新イメージをPULL       │
│    - 環境変数を読み込み              │
│    - コンテナを起動                  │
└─────────────────────────────────────┘
```

### Step 1: ローカルでコード変更（コード変更時のみ）

```bash
cd /Users/kaya.matsumoto/projects/watchme/api/avatar-uploader

# ECRにDockerイメージをプッシュ
./deploy-ecr.sh
```

**このステップが行うこと：**
1. ECRにログイン
2. `Dockerfile.prod`を使ってイメージをビルド
3. イメージにタグ付け（`latest`とタイムスタンプ）
4. ECRにプッシュ

### Step 2: EC2でサービス再起動

```bash
# EC2にSSH接続
ssh -i /Users/kaya.matsumoto/watchme-key.pem ubuntu@3.24.16.82

# サービスを再起動（推奨）
sudo systemctl restart watchme-avatar-uploader

# または、手動でスクリプトを実行
./watchme-avatar-uploader/run-avatar-uploader.sh
```

**このステップが行うこと：**
1. ECRから最新のイメージをPULL
2. `.env.avatar-uploader`から環境変数を読み込み
3. 既存のコンテナを停止・削除
4. 新しいコンテナを起動

### 設定ファイルのみ変更した場合

**docker-compose.prod.ymlやrun-avatar-uploader.shのみ変更した場合：**

```bash
# ローカルから設定ファイルをアップロード
scp -i /Users/kaya.matsumoto/watchme-key.pem \
  docker-compose.prod.yml \
  ubuntu@3.24.16.82:/home/ubuntu/docker-compose.prod.yml

# EC2でサービス再起動
ssh -i /Users/kaya.matsumoto/watchme-key.pem ubuntu@3.24.16.82
sudo systemctl restart watchme-avatar-uploader
```

---

## ⚙️ 環境設定

### 環境変数ファイル（EC2: `/home/ubuntu/.env.avatar-uploader`）

```env
# Supabase Configuration
SUPABASE_URL=https://qvtlwotzuzbavrzqhyvt.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=watchme-avatars
AWS_REGION=ap-southeast-2

# API Configuration
API_PORT=8014
API_HOST=0.0.0.0
```

### 重要な設定項目

| 項目 | 値 | 説明 |
|-----|-----|------|
| S3バケット名 | `watchme-avatars` | ⚠️ `watchme-vault`ではない |
| AWSリージョン | `ap-southeast-2` | ⚠️ `us-east-1`ではない |
| ポート | `8014` | Nginx経由で公開 |

---

## 📡 APIエンドポイント

### ヘルスチェック
```
GET /health
```

### ユーザーアバター管理

#### アップロード/更新
```
POST /v1/users/{user_id}/avatar
```
- **認証**: 現在無効
- **Body**: multipart/form-data
  - `file`: 画像ファイル（必須）
- **対応形式**: JPG, JPEG, PNG, WebP
- **最大サイズ**: 10MB
- **出力**: 512x512px JPEG

#### 削除
```
DELETE /v1/users/{user_id}/avatar
```

### 観測対象者アバター管理

#### アップロード/更新
```
POST /v1/subjects/{subject_id}/avatar
```

#### 削除
```
DELETE /v1/subjects/{subject_id}/avatar
```

### アクセスURL

| 用途 | URL |
|-----|-----|
| **内部アクセス** | `http://localhost:8014/` |
| **外部アクセス** | `https://api.hey-watch.me/avatar/` |

---

## 🔍 トラブルシューティング

### サービスが起動しない

```bash
# ログを確認
sudo journalctl -u watchme-avatar-uploader -n 100 --no-pager

# コンテナのログを確認
docker logs watchme-avatar-uploader --tail 50
```

### 環境変数が読み込まれない

```bash
# コンテナ内の環境変数を確認
docker exec watchme-avatar-uploader env | grep -E '^AWS_|^S3_'

# 期待される出力:
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...
# S3_BUCKET_NAME=watchme-avatars
# AWS_REGION=ap-southeast-2
```

**解決方法:**
- `run-avatar-uploader.sh`に`--env-file`オプションがあるか確認
- `.env.avatar-uploader`ファイルが存在し、正しい内容か確認

### S3アップロードエラー（NoSuchBucket / 403 Forbidden）

**原因:**
1. 環境変数が読み込まれていない
2. AWSアクセスキーが無効
3. バケット名が間違っている

**確認手順:**
```bash
# 1. 環境変数を確認
docker exec watchme-avatar-uploader env | grep S3_BUCKET_NAME
# 出力: S3_BUCKET_NAME=watchme-avatars であること

# 2. AWSアクセスキーを確認
docker exec watchme-avatar-uploader python3 -c "
import boto3
sts = boto3.client('sts')
identity = sts.get_caller_identity()
print(f'Account: {identity[\"Account\"]}')
"
# 出力: Account: 754724220380
```

### 画像が表示されない

**確認項目:**
1. S3バケットのパブリックアクセス設定
2. 返却されるURLの形式が正しいか
   - 正: `https://watchme-avatars.s3.ap-southeast-2.amazonaws.com/users/{user_id}/avatar.jpg`
   - 誤: `watchme-vault`が含まれている

---

## 🧪 テスト

### ローカルテスト
```bash
python3 test_api.py
```

### 本番環境テスト
```bash
# EC2にSSH接続後
python3 test_after_deploy.py
```

### 手動テスト
```bash
# ヘルスチェック
curl https://api.hey-watch.me/avatar/health

# アップロードテスト
curl -X POST https://api.hey-watch.me/avatar/v1/users/{user_id}/avatar \
  -F "file=@test_avatar.jpg"
```

---

## 📁 S3バケット構造

```
watchme-avatars/
├── users/
│   └── {user_id}/
│       └── avatar.jpg
└── subjects/
    └── {subject_id}/
        └── avatar.jpg
```

---

## 📝 開発時の注意事項

1. **UUIDの使用**: user_id/subject_idは必ずUUID形式
2. **multipart/form-data**: ファイルアップロード時は必須
3. **エンドポイントパス**: `/v1/`プレフィックスが必要
4. **画像形式**: JPG, JPEG, PNG, WebP のみ対応
5. **アトミック性**: S3アップロード後のDB更新失敗時は自動ロールバック

---

## 🔗 関連ドキュメント

- [DEPLOYMENT.md](./DEPLOYMENT.md) - 詳細なデプロイ手順とトラブルシューティング
- [CHANGELOG.md](./CHANGELOG.md) - 変更履歴
- [Server Configs README](../../server-configs/README.md) - サーバー全体の構成

---

## ⚠️ 本番環境移行前の必須対応

1. **認証機能の有効化**
   - app.pyに認証処理を追加
   - JWTトークンの検証を実装
   - 権限チェックを有効化

2. **エンドポイントの変更**
   - `/v1/users/{user_id}/avatar` → `/v1/users/me/avatar`
   - URLパラメータではなくトークンからユーザーIDを取得

3. **セキュリティの強化**
   - CORS設定の見直し
   - レート制限の実装
   - ログ監視の設定
