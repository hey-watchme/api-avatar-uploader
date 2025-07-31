# Avatar Uploader API デプロイメント手順

## 📋 前提条件

- AWS ECRリポジトリ: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-avatar-uploader`
- EC2インスタンス: 3.24.16.82
- ポート: 8014

## 🚀 デプロイ手順

### 1. ECRへのイメージプッシュ（ローカル環境）

```bash
# デプロイスクリプトを実行
./deploy-ecr.sh
```

### 2. EC2へ必要なファイルをコピー（初回のみ）

```bash
# 環境変数ファイルをEC2に配置
scp -i ~/watchme-key.pem .env ubuntu@3.24.16.82:~/.env.avatar-uploader

# Docker Compose設定ファイル
scp -i ~/watchme-key.pem docker-compose.prod.yml ubuntu@3.24.16.82:~/

# 起動スクリプト
scp -i ~/watchme-key.pem run-prod.sh ubuntu@3.24.16.82:~/
scp -i ~/watchme-key.pem run-avatar-uploader.sh ubuntu@3.24.16.82:~/

# systemdサービスファイル
scp -i ~/watchme-key.pem watchme-avatar-uploader.service ubuntu@3.24.16.82:~/
scp -i ~/watchme-key.pem setup-systemd.sh ubuntu@3.24.16.82:~/
```

### 3. EC2上でのセットアップ（初回のみ）

```bash
# EC2にSSH接続
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82

# 実行権限を付与
chmod +x run-prod.sh
chmod +x run-avatar-uploader.sh
chmod +x setup-systemd.sh

# systemdサービスをセットアップ
./setup-systemd.sh
```

### 4. サービスの起動

#### 手動起動（テスト用）
```bash
./run-prod.sh
```

#### systemdによる起動（本番用）
```bash
# サービスを起動
sudo systemctl start watchme-avatar-uploader

# 状態確認
sudo systemctl status watchme-avatar-uploader

# ログ確認
sudo journalctl -u watchme-avatar-uploader -f
```

### 5. Nginx設定（初回のみ）

```bash
# Nginx設定ファイルを編集
sudo nano /etc/nginx/sites-available/api.hey-watch.me

# 以下の設定を追加:
location /avatar/ {
    proxy_pass http://localhost:8014/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # ファイルアップロード設定
    client_max_body_size 10M;
    
    # CORS設定
    add_header "Access-Control-Allow-Origin" "*";
    add_header "Access-Control-Allow-Methods" "GET, POST, DELETE, OPTIONS";
    add_header "Access-Control-Allow-Headers" "Content-Type, Authorization";
    
    if ($request_method = "OPTIONS") {
        return 204;
    }
}

# Nginx設定をリロード
sudo nginx -t
sudo systemctl reload nginx
```

## 🔄 更新時の手順

1. ローカルでコード変更
2. `./deploy-ecr.sh` でECRにプッシュ
3. EC2で:
   ```bash
   # 方法1: systemdを使用している場合
   sudo systemctl restart watchme-avatar-uploader
   
   # 方法2: 直接run-prod.shを使用する場合
   ./run-prod.sh
   ```

## ⚠️ 注意事項と間違いやすいポイント

### 1. UUID形式の必須要件
**重要**: user_idとsubject_idは必ずUUID形式である必要があります。

```python
# ✅ 正しい例
user_id = "71958203-e43a-4510-bdfd-a9459388e830"  # UUID形式

# ❌ 間違った例
user_id = "test-user-001"  # 文字列形式はエラーになる
user_id = "123"  # 数値文字列もエラー
```

エラーメッセージ例:
```
"invalid input syntax for type uuid: "test-user-001""
```

### 2. Dockerfile.prodのユーザー権限
非rootユーザー（apiuser）で実行するため、Pythonパスの設定に注意:

```dockerfile
# ✅ 正しい設定
COPY --from=builder /root/.local /home/apiuser/.local
ENV PATH=/home/apiuser/.local/bin:$PATH

# ❌ 間違った設定（rootのパスを参照してしまう）
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
```

### 3. systemdとDockerの併用
- systemdサービスはDockerコンテナの起動/停止を管理
- WorkingDirectoryは`/home/ubuntu`を指定
- run-avatar-uploader.shはホームディレクトリに配置必要

### 4. 環境変数ファイルの配置
```bash
# EC2上での正しい配置場所
~/.env.avatar-uploader

# 必要な環境変数
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxxxx
S3_BUCKET_NAME=watchme-vault
AWS_REGION=ap-southeast-2  # S3バケットのリージョンに注意
```

### 5. APIエンドポイントの形式
エンドポイントは`/v1/`プレフィックスが必要:

```bash
# ✅ 正しいエンドポイント
POST /v1/users/{user_id}/avatar
GET /v1/users/{user_id}/avatar

# ❌ 間違ったエンドポイント
POST /upload  # このエンドポイントは存在しない
POST /users/{user_id}/avatar  # v1が抜けている
```

### 6. ファイルアップロード形式
multipart/form-dataで送信する必要があります:

```python
# ✅ 正しい送信方法
files = {
    'file': ('avatar.jpg', file_data, 'image/jpeg')
}
data = {
    'avatar_type': 'main'  # または 'sub'
}
response = requests.post(url, files=files, data=data)

# ❌ 間違った送信方法（JSONで送信）
data = {
    'user_id': user_id,
    'avatar_type': 'main',
    'image_data': base64_string
}
response = requests.post(url, json=data)
```

### 7. S3バケットのリージョン
- バケット名: `watchme-vault`
- リージョン: `ap-southeast-2` （us-east-1ではない）
- 返却されるURLはus-east-1形式だが、実際はap-southeast-2にリダイレクトされる

### 8. Nginx設定の注意点
locationブロックは必ずserverブロック内に配置:

```nginx
server {
    listen 443 ssl;
    # ... 他の設定 ...
    
    # ✅ 正しい位置
    location /avatar/ {
        proxy_pass http://localhost:8014/;
        # ...
    }
}

# ❌ serverブロックの外に配置するとエラー
location /avatar/ {
    # ...
}
```

## 📍 エンドポイント

### 内部アクセス
- http://localhost:8014/health
- http://localhost:8014/v1/users/{user_id}/avatar
- http://localhost:8014/v1/subjects/{subject_id}/avatar

### 外部アクセス
- https://api.hey-watch.me/avatar/health
- https://api.hey-watch.me/avatar/v1/users/{user_id}/avatar
- https://api.hey-watch.me/avatar/v1/subjects/{subject_id}/avatar

## 🔍 トラブルシューティング

### コンテナが起動しない場合
```bash
# ログを確認
docker logs watchme-avatar-uploader

# 環境変数を確認
cat ~/.env.avatar-uploader

# よくあるエラー: "No module named uvicorn"
# → Dockerfile.prodでPythonパスが正しく設定されているか確認
```

### systemdサービスが起動しない場合
```bash
# サービスの詳細ログを確認
sudo journalctl -u watchme-avatar-uploader -n 100 --no-pager

# よくあるエラー: "Failed to execute /home/ubuntu/run-avatar-uploader.sh: Exec format error"
# → 実行権限を確認: chmod +x ~/run-avatar-uploader.sh
```

### ECRアクセスエラーの場合
```bash
# IAMロールを確認
aws sts get-caller-identity

# ECRログイン再試行
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com
```

### データベースエラーの場合
```
ERROR: invalid input syntax for type uuid: "test-user-001"
```
→ user_idがUUID形式でない。必ずUUID形式（例: 71958203-e43a-4510-bdfd-a9459388e830）を使用すること。

### アップロードエラーの場合
```
422 Unprocessable Entity - Field 'file' required
```
→ multipart/form-data形式で送信していない。files=とdata=パラメータを使用すること。

## 🚨 デプロイ時の確認チェックリスト

1. [ ] Dockerfile.prodのPATH設定が`/home/apiuser/.local/bin`を指している
2. [ ] user_id/subject_idにUUID形式を使用している
3. [ ] APIエンドポイントに`/v1/`プレフィックスを含めている
4. [ ] multipart/form-data形式でファイルをアップロードしている
5. [ ] EC2上に必要なファイル（docker-compose.prod.yml、run-prod.sh等）が配置されている
6. [ ] 環境変数ファイル（~/.env.avatar-uploader）が正しく設定されている
7. [ ] Nginx設定がserverブロック内に正しく配置されている
8. [ ] S3バケットのリージョンがap-southeast-2であることを理解している

## 📝 デプロイ成功の確認方法

```bash
# 1. ヘルスチェック
curl http://localhost:8014/health

# 2. テストアップロード（UUID形式のIDを使用）
curl -X POST http://localhost:8014/v1/users/550e8400-e29b-41d4-a716-446655440000/avatar \
  -F "file=@test_avatar.jpg" \
  -F "avatar_type=main"

# 3. コンテナログ確認
docker logs watchme-avatar-uploader --tail 20
```