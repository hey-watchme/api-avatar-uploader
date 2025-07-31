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

print("=== Supabaseテーブル確認 ===\n")

# Usersテーブルの確認
print("1. Usersテーブルの確認:")
try:
    # 全カラムを取得（1行だけ）
    result = supabase.table('users').select('*').limit(1).execute()
    if result.data:
        print("  カラム一覧:")
        for key in result.data[0].keys():
            print(f"    - {key}")
    else:
        print("  データなし（カラム情報を取得できません）")
except Exception as e:
    print(f"  エラー: {e}")

print("\n2. Subjectsテーブルの確認:")
try:
    # 全カラムを取得（1行だけ）
    result = supabase.table('subjects').select('*').limit(1).execute()
    if result.data:
        print("  カラム一覧:")
        for key in result.data[0].keys():
            print(f"    - {key}")
    else:
        print("  データなし（カラム情報を取得できません）")
except Exception as e:
    print(f"  エラー: {e}")

# 指定されたIDのレコード確認
print(f"\n3. 指定されたユーザーID (164cba5a-dba6-4cbc-9b39-4eea28d98fa5) の確認:")
try:
    # user_idでの検索を試みる
    result = supabase.table('users').select('*').eq('user_id', '164cba5a-dba6-4cbc-9b39-4eea28d98fa5').execute()
    if result.data:
        print(f"  ✅ ユーザーが見つかりました: {result.data[0]}")
    else:
        print("  ❌ ユーザーが見つかりません")
except Exception as e:
    print(f"  エラー: {e}")

print(f"\n4. 指定されたサブジェクトID (f394486f-bd07-4fcc-8afe-eab38b4ebb0f) の確認:")
try:
    # subject_idでの検索を試みる
    result = supabase.table('subjects').select('*').eq('subject_id', 'f394486f-bd07-4fcc-8afe-eab38b4ebb0f').execute()
    if result.data:
        print(f"  ✅ サブジェクトが見つかりました: {result.data[0]}")
    else:
        print("  ❌ サブジェクトが見つかりません")
except Exception as e:
    print(f"  エラー: {e}")