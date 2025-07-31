import requests
import os
from dotenv import load_dotenv
import json

# 環境変数読み込み
load_dotenv()

# テスト設定
BASE_URL = "http://localhost:8014"
# テスト用のトークン（実際のテストでは有効なトークンに置き換える必要があります）
TEST_TOKEN = "your_test_token_here"

def test_health_check():
    """ヘルスチェックのテスト"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed\n")

def test_user_avatar_upload():
    """ユーザーアバターアップロードのテスト"""
    print("Testing user avatar upload...")
    
    # テスト用画像を作成（実際のテストでは本物の画像ファイルを使用）
    # ここでは簡単のため、小さな画像データを生成
    from PIL import Image
    import io
    
    # 100x100の赤い画像を作成
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    files = {
        "file": ("test_avatar.jpg", img_bytes, "image/jpeg")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/users/me/avatar",
            headers=headers,
            files=files
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("✅ User avatar upload test passed\n")
        else:
            print(f"Error: {response.text}")
            print("❌ User avatar upload test failed\n")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("❌ User avatar upload test failed\n")

def test_subject_avatar_upload():
    """観測対象者アバターアップロードのテスト"""
    print("Testing subject avatar upload...")
    
    # テスト用のsubject_id（実際のテストでは有効なIDに置き換える）
    subject_id = "test_subject_123"
    
    from PIL import Image
    import io
    
    # 100x100の青い画像を作成
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    files = {
        "file": ("test_subject_avatar.jpg", img_bytes, "image/jpeg")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/subjects/{subject_id}/avatar",
            headers=headers,
            files=files
        )
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 403, 404]:
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                print("✅ Subject avatar upload test passed\n")
            else:
                print(f"Expected error: {response.text}")
                print("✅ Subject avatar upload permission test passed\n")
        else:
            print(f"Unexpected error: {response.text}")
            print("❌ Subject avatar upload test failed\n")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("❌ Subject avatar upload test failed\n")

def test_user_avatar_delete():
    """ユーザーアバター削除のテスト"""
    print("Testing user avatar delete...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.delete(
            f"{BASE_URL}/v1/users/me/avatar",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 204:
            print("✅ User avatar delete test passed\n")
        else:
            print(f"Error: {response.text}")
            print("❌ User avatar delete test failed\n")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("❌ User avatar delete test failed\n")

def test_invalid_file_format():
    """無効なファイル形式のテスト"""
    print("Testing invalid file format...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    # テキストファイルをアップロード
    files = {
        "file": ("test.txt", b"This is not an image", "text/plain")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/users/me/avatar",
            headers=headers,
            files=files
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            print(f"Expected error: {response.text}")
            print("✅ Invalid file format test passed\n")
        else:
            print("❌ Invalid file format test failed - should return 400\n")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("❌ Invalid file format test failed\n")

def test_no_auth():
    """認証なしのリクエストテスト"""
    print("Testing request without authentication...")
    
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {
        "file": ("test_avatar.jpg", img_bytes, "image/jpeg")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/users/me/avatar",
            files=files
        )
        print(f"Status: {response.status_code}")
        if response.status_code in [401, 403]:
            print(f"Expected error: {response.text}")
            print("✅ No auth test passed\n")
        else:
            print("❌ No auth test failed - should return 401 or 403\n")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("❌ No auth test failed\n")

if __name__ == "__main__":
    print("=== Avatar Management API Tests ===\n")
    
    # APIが起動していることを確認
    try:
        test_health_check()
    except:
        print("❌ API is not running. Please start the API first.")
        exit(1)
    
    print("Note: To run full tests, you need to:")
    print("1. Set a valid TEST_TOKEN in this script")
    print("2. Have valid subject_id for subject tests")
    print("3. Make sure the API is running on port 8014\n")
    
    # 各テストを実行（実際のテストでは有効なトークンが必要）
    # test_user_avatar_upload()
    # test_subject_avatar_upload()
    # test_user_avatar_delete()
    test_invalid_file_format()
    test_no_auth()
    
    print("\n=== Tests completed ===")
    print("\nTo run authenticated tests, update TEST_TOKEN with a valid JWT token.")