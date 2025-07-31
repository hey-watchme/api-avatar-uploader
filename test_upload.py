import requests
import sys
from pathlib import Path

def test_upload_without_auth(image_path):
    """認証なしでのアップロードテスト（エラーになるはず）"""
    url = "http://localhost:8014/v1/users/me/avatar"
    
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        response = requests.post(url, files=files)
    
    print(f"認証なしテスト:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    
    return response

def test_health_check():
    """ヘルスチェック"""
    response = requests.get("http://localhost:8014/health")
    print(f"Health check: {response.json()}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_upload.py <image_path>")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"Testing with image: {image_path}\n")
    
    # ヘルスチェック
    test_health_check()
    
    # 認証なしでのアップロードテスト
    test_upload_without_auth(image_path)
    
    print("\n注意: 実際のアップロードには有効なSupabase JWTトークンが必要です。")
    print("トークンは以下の方法で取得できます:")
    print("1. Supabaseダッシュボードからユーザーを作成")
    print("2. Supabase Authを使ってログイン")
    print("3. 取得したアクセストークンをAuthorizationヘッダーに設定")