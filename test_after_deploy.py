#!/usr/bin/env python3
"""
デプロイ後の動作確認テスト
"""

import requests
import json
from PIL import Image
import io
from datetime import datetime

# APIエンドポイント
BASE_URL = "http://3.24.16.82:8014"

# テスト用ユーザーID（実際のユーザー）
TEST_USER_ID = "164cba5a-dba6-4cbc-9b39-4eea28d98fa5"

def test_deployment():
    """デプロイ確認テスト"""
    print("=" * 60)
    print("Avatar Uploader API デプロイ確認")
    print(f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"エンドポイント: {BASE_URL}")
    print("=" * 60)
    
    # 1. ヘルスチェック
    print("\n1. ヘルスチェック...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ APIは正常に動作しています")
            print(f"   サービス: {health.get('service')}")
            print(f"   タイムスタンプ: {health.get('timestamp')}")
        else:
            print(f"   ❌ ステータス: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 接続エラー: {e}")
        return False
    
    # 2. テストアップロード
    print(f"\n2. テストアップロード (user_id: {TEST_USER_ID})...")
    
    # テスト画像を作成（100x100の青い画像）
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {
        "file": ("test_deploy.jpg", img_bytes, "image/jpeg")
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/users/{TEST_USER_ID}/avatar",
            files=files,
            timeout=10
        )
        
        print(f"   ステータスコード: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            avatar_url = result.get('avatarUrl')
            print(f"   ✅ アップロード成功")
            print(f"   返却URL: {avatar_url}")
            
            # S3バケット名とリージョンを確認
            if avatar_url:
                if "watchme-avatars" in avatar_url:
                    print("   ✅ 正しいバケット名 (watchme-avatars)")
                elif "watchme-vault" in avatar_url:
                    print("   ⚠️ 古いバケット名が使用されています (watchme-vault)")
                
                if "ap-southeast-2" in avatar_url:
                    print("   ✅ 正しいリージョン (ap-southeast-2)")
                elif "us-east-1" in avatar_url:
                    print("   ⚠️ 誤ったリージョンが設定されています (us-east-1)")
            
            return True
        else:
            print(f"   ❌ アップロード失敗")
            print(f"   レスポンス: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

def main():
    success = test_deployment()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ デプロイ確認完了 - APIは正常に動作しています")
    else:
        print("❌ デプロイ確認失敗 - 設定を確認してください")
    print("=" * 60)

if __name__ == "__main__":
    main()