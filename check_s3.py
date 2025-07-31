import boto3
from dotenv import load_dotenv
import os

# 環境変数を読み込む
load_dotenv()

# AWS設定
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "watchme-avatars")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

# S3クライアント初期化
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

print(f"S3バケット確認: {S3_BUCKET_NAME}")
print(f"リージョン: {AWS_REGION}")
print("-" * 50)

try:
    # バケットの存在確認
    response = s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
    print(f"✅ バケット '{S3_BUCKET_NAME}' が存在します")
    
    # バケット内のオブジェクトをリスト（最大10個）
    print("\nバケット内のオブジェクト（最大10個）:")
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, MaxKeys=10)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"  - {obj['Key']} (Size: {obj['Size']} bytes)")
    else:
        print("  （空のバケット）")
        
except Exception as e:
    print(f"❌ エラー: {str(e)}")
    print("\nバケットが存在しない場合は作成が必要です。")