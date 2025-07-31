import requests
import sys
from pathlib import Path

# テスト用のID
USER_ID = "164cba5a-dba6-4cbc-9b39-4eea28d98fa5"
SUBJECT_ID = "f394486f-bd07-4fcc-8afe-eab38b4ebb0f"
BASE_URL = "http://localhost:8014"

def test_user_avatar_upload(image_path):
    """指定されたユーザーIDでアバターをアップロード"""
    url = f"{BASE_URL}/v1/users/{USER_ID}/avatar"
    
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        response = requests.post(url, files=files)
    
    print(f"ユーザーアバターアップロード:")
    print(f"User ID: {USER_ID}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Avatar URL: {data['avatarUrl']}")
        print("✅ アップロード成功!\n")
        return data['avatarUrl']
    else:
        print(f"Error: {response.text}\n")
        return None

def test_subject_avatar_upload(image_path):
    """指定されたサブジェクトIDでアバターをアップロード"""
    url = f"{BASE_URL}/v1/subjects/{SUBJECT_ID}/avatar"
    
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        response = requests.post(url, files=files)
    
    print(f"サブジェクトアバターアップロード:")
    print(f"Subject ID: {SUBJECT_ID}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Avatar URL: {data['avatarUrl']}")
        print("✅ アップロード成功!\n")
        return data['avatarUrl']
    else:
        print(f"Error: {response.text}\n")
        return None

def check_s3_files():
    """S3に保存されたファイルを確認"""
    import boto3
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "ap-southeast-2")
    )
    
    bucket_name = os.getenv("S3_BUCKET_NAME", "watchme-avatars")
    
    print("S3バケット内のファイル:")
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"  - {obj['Key']} (Size: {obj['Size']} bytes)")
    else:
        print("  （ファイルなし）")

if __name__ == "__main__":
    print("=== アバター管理APIテスト ===\n")
    
    # ユーザーアバターのテスト
    print("1. ユーザーアバターのアップロード")
    user_avatar_path = Path("test_avatar_1.jpg")
    if user_avatar_path.exists():
        user_url = test_user_avatar_upload(user_avatar_path)
    else:
        print(f"テスト画像が見つかりません: {user_avatar_path}\n")
    
    # サブジェクトアバターのテスト
    print("2. サブジェクトアバターのアップロード")
    subject_avatar_path = Path("test_avatar_3.jpg")
    if subject_avatar_path.exists():
        subject_url = test_subject_avatar_upload(subject_avatar_path)
    else:
        print(f"テスト画像が見つかりません: {subject_avatar_path}\n")
    
    # S3ファイルの確認
    print("\n3. S3バケットの確認")
    check_s3_files()
    
    print("\n=== テスト完了 ===")