# WatchMe Avatar Management API

iOS、Android、Webアプリケーション共通で使用するアバター管理APIです。

## 📅 更新履歴

### 2025-08-16 更新
- **S3バケット名を統一**: `watchme-vault` → `watchme-avatars`に変更
- **S3リージョンを正しく設定**: `us-east-1` → `ap-southeast-2`に修正
- **S3パブリックアクセス設定**: アップロードされた画像が正しく表示されるよう設定
- **本番環境へのデプロイ完了**: EC2インスタンス（3.24.16.82）で稼働中

## ⚠️ 重要な注意事項

**このAPIは現在、開発・テスト用に認証機能を無効化しています。**
- 本番環境で使用する前に、必ず認証機能を有効化してください
- 認証なしの状態では、誰でもアバターを変更できてしまいます

## 概要

このAPIは、ユーザーおよび観測対象者（Subject）のアバター画像をAWS S3に安全にアップロード・管理する機能を提供します。

## 主な機能

- ユーザーアバターのアップロード/更新/削除
- 観測対象者アバターのアップロード/更新/削除
- 画像の自動リサイズと最適化（512x512px）
- ~~JWT認証による安全なアクセス制御~~ （現在無効化中）
- ~~権限に基づくアクセス制御（観測対象者の編集権限確認）~~ （現在無効化中）
- Supabaseデータベースとの自動連携（avatar_url更新）

## 技術スタック

- **FastAPI** - Webフレームワーク
- **AWS S3** - 画像ストレージ（リージョン: ap-southeast-2）
- **Supabase** - 認証とデータベース
- **Pillow** - 画像処理
- **Boto3** - AWS SDK

## セットアップ

### 1. 依存関係のインストール

```bash
pip3 install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルに以下の環境変数を設定してください：

```env
# Supabase Configuration
SUPABASE_URL=https://qvtlwotzuzbavrzqhyvt.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# AWS S3 Configuration（2025-08-16更新）
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=watchme-avatars  # 重要: watchme-vaultではなくwatchme-avatarsを使用
AWS_REGION=ap-southeast-2        # 重要: us-east-1ではなくap-southeast-2を使用

# API Configuration
API_PORT=8014
API_HOST=0.0.0.0
```

### 3. APIの起動

```bash
python3 app.py
```

または

```bash
uvicorn app:app --host 0.0.0.0 --port 8014 --reload
```

## APIエンドポイント

### ヘルスチェック

```
GET /health
```

### ユーザーアバター管理

#### アップロード/更新
```
POST /v1/users/{user_id}/avatar
```
- 認証: ~~必須（Bearer Token）~~ **現在無効**
- Body: multipart/form-data
  - `file`: 画像ファイル（必須）
- パラメータ:
  - `user_id`: ユーザーID（URLパス内で指定）

#### 削除
```
DELETE /v1/users/{user_id}/avatar
```
- 認証: ~~必須（Bearer Token）~~ **現在無効**
- パラメータ:
  - `user_id`: ユーザーID（URLパス内で指定）

### 観測対象者アバター管理

#### アップロード/更新
```
POST /v1/subjects/{subject_id}/avatar
```
- 認証: ~~必須（Bearer Token）~~ **現在無効**
- 権限: ~~ユーザーがSubjectの編集権限を持っている必要があります~~ **現在無効**
- Body: multipart/form-data
  - `file`: 画像ファイル（必須）
- パラメータ:
  - `subject_id`: サブジェクトID（URLパス内で指定）

#### 削除
```
DELETE /v1/subjects/{subject_id}/avatar
```
- 認証: ~~必須（Bearer Token）~~ **現在無効**
- 権限: ~~ユーザーがSubjectの編集権限を持っている必要があります~~ **現在無効**
- パラメータ:
  - `subject_id`: サブジェクトID（URLパス内で指定）

## S3バケット構造

```
watchme-avatars/
├── users/
│   └── {user_id}/
│       └── avatar.jpg
└── subjects/
    └── {subject_id}/
        └── avatar.jpg
```

## 画像処理仕様

- 対応形式: JPG, JPEG, PNG, WebP
- 最大ファイルサイズ: 10MB
- 出力形式: JPEG（品質85%）
- 出力サイズ: 512x512px（正方形、アスペクト比保持）

## エラーレスポンス

| ステータスコード | 説明 |
|----------------|------|
| 400 | 不正なリクエスト（画像形式エラー、ファイルサイズ超過など） |
| 401 | 認証エラー |
| 403 | 権限エラー（Subjectの編集権限なし） |
| 404 | リソースが見つからない |
| 500 | サーバーエラー |

## 開発時の注意事項

1. S3とデータベースの操作は可能な限りアトミックに行う
2. S3アップロード後のDB更新失敗時は、S3のファイルを削除する
3. 画像は常に`avatar.jpg`という固定名で保存（上書き更新）
4. トークン検証はSupabaseのauth.get_user()を使用

## 変更履歴

### 2025年7月31日 - 認証機能の一時無効化
- 開発・テスト用に認証機能を無効化
- エンドポイントのパスを変更:
  - `/v1/users/me/avatar` → `/v1/users/{user_id}/avatar`
  - パラメータでuser_idとsubject_idを直接指定する形式に変更
- データベース連携の実装:
  - Supabaseのusersテーブルとsubjectsテーブルのavatar_urlカラムを自動更新
  - S3アップロード後、失敗時は自動ロールバック

## テスト

### 基本的なテスト
```bash
python3 test_api.py
```

### 実際のIDを使用したテスト
```bash
python3 test_with_ids.py
```

### テスト用のユーザーID/サブジェクトID
- ユーザーID: `164cba5a-dba6-4cbc-9b39-4eea28d98fa5`
- サブジェクトID: `f394486f-bd07-4fcc-8afe-eab38b4ebb0f`

## 本番環境情報

### デプロイ状況
- **稼働環境**: EC2インスタンス（3.24.16.82）
- **ポート**: 8014
- **Dockerイメージ**: ECR（754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-avatar-uploader）
- **S3バケット**: `watchme-avatars`（ap-southeast-2リージョン）

### S3バケット設定
- **パブリックアクセス**: 有効（画像の読み取りのみ）
- **バケットポリシー**: GetObject許可
- **CORS**: すべてのオリジンからのGET/HEADを許可

## 本番環境への移行時の注意事項

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

## トラブルシューティング

### 画像が表示されない場合
1. **S3バケットのパブリックアクセス設定を確認**
   - バケットポリシーでGetObjectが許可されているか
   - パブリックアクセスブロックが適切に設定されているか

2. **URLフォーマットを確認**
   - 正しい形式: `https://watchme-avatars.s3.ap-southeast-2.amazonaws.com/users/{user_id}/avatar.jpg`
   - 誤った形式: `watchme-vault`や`us-east-1`が含まれている場合は古い設定

3. **APIレスポンスを確認**
   ```bash
   curl http://3.24.16.82:8014/health
   ```

### デプロイ後の確認
```bash
# テストスクリプトを実行
python3 test_after_deploy.py
```