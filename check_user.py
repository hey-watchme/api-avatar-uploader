from supabase import create_client, Client
from dotenv import load_dotenv
import os

# 環境変数を読み込む
load_dotenv()

# Supabase設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabaseクライアント初期化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 指定されたユーザーIDを確認
USER_ID = "71958203-e43a-4510-bdfd-a9459388e830"

print(f"=== ユーザー {USER_ID} の確認 ===\n")

try:
    result = supabase.table('users').select('*').eq('user_id', USER_ID).execute()
    
    if result.data:
        user = result.data[0]
        print("✅ ユーザーが見つかりました:")
        print(f"  - user_id: {user.get('user_id')}")
        print(f"  - name: {user.get('name')}")
        print(f"  - email: {user.get('email')}")
        print(f"  - avatar_url: {user.get('avatar_url', '(空)')}")
        print(f"  - created_at: {user.get('created_at')}")
    else:
        print("❌ ユーザーが見つかりません")
        print("\n既存のユーザー一覧（最初の5件）:")
        users = supabase.table('users').select('user_id, name, avatar_url').limit(5).execute()
        for u in users.data:
            print(f"  - {u['user_id']}: {u['name']} (avatar: {u.get('avatar_url', '空')})")
            
except Exception as e:
    print(f"エラー: {str(e)}")