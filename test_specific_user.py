#!/usr/bin/env python3
"""
特定のユーザーIDでアバターをテストアップロード
"""
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# 設定
API_URL = "http://3.24.16.82:8014"
USER_ID = "164CBA5A-DBA6-4CBC-9B39-4EEA28D98FA5"  # 実際のユーザーID

def create_test_avatar():
    """テスト用アバター画像を作成"""
    width, height = 600, 600
    image = Image.new('RGB', (width, height), color='#4A90E2')  # 青色背景
    draw = ImageDraw.Draw(image)
    
    # テキストを描画
    text = "Test\nAvatar"
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
    except:
        font = ImageFont.load_default()
    
    # テキストのバウンディングボックスを取得
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # テキストを中央に配置
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font, align='center')
    
    # 画像をバイト列に変換
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr

def test_upload():
    """アバターアップロードテスト"""
    print(f"=== ユーザー {USER_ID} のアバターアップロードテスト ===")
    
    # ヘルスチェック
    try:
        health_response = requests.get(f"{API_URL}/health")
        print(f"ヘルスチェック: {health_response.status_code}")
        if health_response.status_code != 200:
            print("APIが応答しません")
            return
    except Exception as e:
        print(f"APIへの接続エラー: {e}")
        return
    
    # テスト画像を作成
    image_data = create_test_avatar()
    
    # ファイルとして送信
    files = {
        'file': ('test_avatar.jpg', image_data, 'image/jpeg')
    }
    data = {
        'avatar_type': 'main'
    }
    
    # アップロードリクエスト
    url = f"{API_URL}/v1/users/{USER_ID}/avatar"
    print(f"アップロード先: {url}")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ アップロード成功！")
            print(f"Avatar URL: {result.get('avatarUrl', 'N/A')}")
            
            # URLアクセステスト
            avatar_url = result.get('avatarUrl')
            if avatar_url:
                print(f"\n=== S3 URLアクセステスト ===")
                print(f"URL: {avatar_url}")
                
                # HEADリクエストでアクセス可能か確認
                head_response = requests.head(avatar_url, allow_redirects=True)
                print(f"HEADリクエスト: {head_response.status_code}")
                print(f"Content-Type: {head_response.headers.get('Content-Type', 'N/A')}")
                print(f"Content-Length: {head_response.headers.get('Content-Length', 'N/A')}")
                
                if head_response.status_code in [200, 301, 302]:
                    print("✅ 画像にアクセス可能です")
                else:
                    print("❌ 画像にアクセスできません")
                    
            return result
        else:
            print("❌ アップロード失敗")
            print(f"レスポンス: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return None

if __name__ == "__main__":
    test_upload()