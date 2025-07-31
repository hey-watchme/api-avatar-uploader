#!/usr/bin/env python3
"""
本番環境にユーザーアバターをアップロードするスクリプト
"""
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# 設定
API_URL = "http://3.24.16.82:8014"  # EC2直接アクセス（Nginxが未設定のため）
USER_ID = "71958203-e43a-4510-bdfd-a9459388e830"

def create_test_avatar():
    """User 1 Avatarテスト画像を作成"""
    # ピンク背景に白文字でUser 1 Avatarと書かれた画像を作成
    width, height = 600, 600
    image = Image.new('RGB', (width, height), color='#FFC0CB')  # ピンク色
    draw = ImageDraw.Draw(image)
    
    # テキストを描画（中央に配置）
    text = "User 1\nAvatar"
    # デフォルトフォントを使用
    try:
        # より大きなフォントサイズを試す
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
    except:
        # フォントが見つからない場合はデフォルトを使用
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

def upload_avatar():
    """アバターをアップロード"""
    print(f"=== ユーザー {USER_ID} のアバターアップロード ===")
    
    # テスト画像を作成
    image_data = create_test_avatar()
    
    # ファイルとして送信
    files = {
        'file': ('user1_avatar.jpg', image_data, 'image/jpeg')
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
            return result
        else:
            print("❌ アップロード失敗")
            print(f"レスポンス: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return None

def verify_upload():
    """アップロードを確認"""
    print("\n=== アップロード確認 ===")
    
    # ヘルスチェック
    try:
        health_response = requests.get(f"{API_URL}/health")
        if health_response.status_code == 200:
            print("✅ APIは正常に動作しています")
        else:
            print("⚠️  APIの状態を確認してください")
    except:
        print("❌ APIに接続できません")

if __name__ == "__main__":
    # APIの状態を確認
    verify_upload()
    
    # アバターをアップロード
    result = upload_avatar()
    
    if result:
        print("\n=== 完了 ===")
        print(f"ユーザー {USER_ID} のアバターが正常にアップロードされました。")
        print(f"S3 URL: {result.get('avatarUrl', 'N/A')}")
    else:
        print("\nアップロードに失敗しました。ログを確認してください。")