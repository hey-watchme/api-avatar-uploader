from PIL import Image, ImageDraw, ImageFont
import os

# 4つのテスト画像を作成（提供された画像の代わり）
def create_test_images():
    colors = [
        ("#FFB6C1", "User 1"),     # ピンク
        ("#87CEEB", "User 2"),     # スカイブルー
        ("#98FB98", "Subject 1"),  # ペールグリーン
        ("#FFE4B5", "Subject 2")   # モカシン
    ]
    
    for i, (color, label) in enumerate(colors):
        # 600x600の画像を作成
        img = Image.new('RGB', (600, 600), color=color)
        draw = ImageDraw.Draw(img)
        
        # テキストを追加
        text = f"{label}\nAvatar"
        # フォントサイズを大きく
        try:
            # システムフォントを試す
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except:
            font = None
        
        # テキストを中央に配置
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = 200, 100  # デフォルト
            
        x = (600 - text_width) // 2
        y = (600 - text_height) // 2
        
        draw.text((x, y), text, fill="white", font=font, align="center")
        
        # 画像を保存
        filename = f"test_avatar_{i+1}.jpg"
        img.save(filename)
        print(f"Created: {filename}")

if __name__ == "__main__":
    create_test_images()
    print("\nテスト画像を作成しました。")