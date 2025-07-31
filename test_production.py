import requests
import sys
from pathlib import Path

# 本番環境の設定
PRODUCTION_URL = "https://api.hey-watch.me/avatar"
USER_ID = "71958203-e43a-4510-bdfd-a9459388e830"

def test_production_upload(image_path):
    """本番環境へのアップロードテスト"""
    url = f"{PRODUCTION_URL}/v1/users/{USER_ID}/avatar"
    
    print(f"本番環境へのアップロードテスト")
    print(f"URL: {url}")
    print(f"User ID: {USER_ID}")
    print(f"画像: {image_path}")
    print("-" * 50)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ アップロード成功!")
            print(f"Avatar URL: {data['avatarUrl']}")
            return data['avatarUrl']
        else:
            print(f"❌ エラー: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        return None

def check_health():
    """ヘルスチェック"""
    url = f"{PRODUCTION_URL}/health"
    try:
        response = requests.get(url, timeout=10)
        print(f"ヘルスチェック: {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("✅ APIは正常に動作しています\n")
            return True
        else:
            print(f"❌ APIが応答しません: {response.text}\n")
            return False
    except Exception as e:
        print(f"❌ 接続エラー: {str(e)}\n")
        return False

if __name__ == "__main__":
    print("=== 本番環境アップロードテスト ===\n")
    
    # ヘルスチェック
    if not check_health():
        print("APIが利用できません。デプロイ状況を確認してください。")
        sys.exit(1)
    
    # テスト画像を使用
    test_image = Path("test_avatar_1.jpg")
    
    if not test_image.exists():
        print(f"テスト画像が見つかりません: {test_image}")
        print("test_avatar_1.jpg を作成してください")
        sys.exit(1)
    
    # アップロード実行
    avatar_url = test_production_upload(test_image)
    
    if avatar_url:
        print(f"\n=== アップロード完了 ===")
        print(f"ユーザーID: {USER_ID}")
        print(f"アバターURL: {avatar_url}")
        print(f"\nブラウザでアクセス可能か確認してください:")
        print(f"{avatar_url}")