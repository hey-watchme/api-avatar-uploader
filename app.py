from fastapi import FastAPI, UploadFile, File, HTTPException, status, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from supabase import create_client, Client
from PIL import Image
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# 環境変数の読み込み
load_dotenv()

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="WatchMe Avatar Management API",
    description="アバター画像を管理するための共通API",
    version="1.0.0"
)

# 環境変数から設定を読み込み
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "watchme-avatars")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

# S3クライアント初期化
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Supabaseクライアント初期化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# レスポンスモデル
class AvatarUploadResponse(BaseModel):
    avatarUrl: str

# 画像処理設定
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
AVATAR_SIZE = (512, 512)  # リサイズ後のサイズ
JPEG_QUALITY = 85

# 認証機能は削除（開発・テスト用）

def check_subject_exists(subject_id: str) -> bool:
    """
    指定されたSubjectが存在するか確認
    """
    try:
        result = supabase.table('subjects').select('subject_id').eq('subject_id', subject_id).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Subject existence check failed: {str(e)}")
        return False

def validate_image(file: UploadFile) -> None:
    """
    アップロードされた画像ファイルを検証
    """
    # ファイル拡張子の確認
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が指定されていません")
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"許可されていないファイル形式です。対応形式: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Content-Typeの確認
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="画像ファイルではありません")

def process_image(file_content: bytes) -> bytes:
    """
    画像をリサイズして最適化
    """
    try:
        # 画像を開く
        image = Image.open(io.BytesIO(file_content))
        
        # RGBに変換（透過画像対応）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # アスペクト比を保ちながらリサイズ
        image.thumbnail(AVATAR_SIZE, Image.Resampling.LANCZOS)
        
        # 正方形にクロップ
        width, height = image.size
        if width != height:
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            right = left + size
            bottom = top + size
            image = image.crop((left, top, right, bottom))
        
        # JPEGとして保存
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        output.seek(0)
        
        return output.getvalue()
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(status_code=400, detail="画像の処理に失敗しました")

def upload_to_s3(file_content: bytes, s3_key: str) -> str:
    """
    S3に画像をアップロード
    """
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType='image/jpeg',
            CacheControl='public, max-age=31536000'
        )
        
        # S3のURLを生成
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return s3_url
    except ClientError as e:
        logger.error(f"S3 upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="画像のアップロードに失敗しました")

def delete_from_s3(s3_key: str) -> None:
    """
    S3から画像を削除
    """
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
    except ClientError as e:
        logger.error(f"S3 deletion failed: {str(e)}")
        # 削除の失敗は致命的ではないので、ログのみ

def update_database(table: str, record_id: str, avatar_url: Optional[str]) -> None:
    """
    データベースのavatar_urlを更新
    """
    try:
        if table == "users":
            supabase.table(table).update(
                {"avatar_url": avatar_url}
            ).eq("user_id", record_id).execute()
        elif table == "subjects":
            supabase.table(table).update(
                {"avatar_url": avatar_url}
            ).eq("subject_id", record_id).execute()
    except Exception as e:
        logger.error(f"Database update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="データベースの更新に失敗しました")

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "avatar-management-api"
    }

@app.post("/v1/users/{user_id}/avatar", response_model=AvatarUploadResponse)
async def upload_user_avatar(
    user_id: str,
    file: UploadFile = File(...)
):
    """
    ユーザーのアバターをアップロード/更新
    """
    
    # 画像の検証
    validate_image(file)
    
    # ファイルサイズチェック
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="ファイルサイズが大きすぎます（最大10MB）")
    
    # 画像処理
    processed_image = process_image(file_content)
    
    # S3キー
    s3_key = f"users/{user_id}/avatar.jpg"
    
    # S3にアップロード
    s3_url = upload_to_s3(processed_image, s3_key)
    
    # データベース更新
    try:
        update_database("users", user_id, s3_url)
    except HTTPException:
        # DB更新失敗時はS3からも削除
        delete_from_s3(s3_key)
        raise
    
    logger.info(f"User avatar uploaded: user_id={user_id}, url={s3_url}")
    return AvatarUploadResponse(avatarUrl=s3_url)

@app.delete("/v1/users/{user_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_avatar(user_id: str):
    """
    ユーザーのアバターを削除
    """
    s3_key = f"users/{user_id}/avatar.jpg"
    
    # S3から削除
    delete_from_s3(s3_key)
    
    # データベース更新
    update_database("users", user_id, None)
    
    logger.info(f"User avatar deleted: user_id={user_id}")

@app.post("/v1/subjects/{subject_id}/avatar", response_model=AvatarUploadResponse)
async def upload_subject_avatar(
    subject_id: str,
    file: UploadFile = File(...)
):
    """
    観測対象者のアバターをアップロード/更新
    """
    # Subject存在確認
    if not check_subject_exists(subject_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたSubjectが見つかりません"
        )
    
    # 画像の検証
    validate_image(file)
    
    # ファイルサイズチェック
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="ファイルサイズが大きすぎます（最大10MB）")
    
    # 画像処理
    processed_image = process_image(file_content)
    
    # S3キー
    s3_key = f"subjects/{subject_id}/avatar.jpg"
    
    # S3にアップロード
    s3_url = upload_to_s3(processed_image, s3_key)
    
    # データベース更新
    try:
        update_database("subjects", subject_id, s3_url)
    except HTTPException:
        # DB更新失敗時はS3からも削除
        delete_from_s3(s3_key)
        raise
    
    logger.info(f"Subject avatar uploaded: subject_id={subject_id}, url={s3_url}")
    return AvatarUploadResponse(avatarUrl=s3_url)

@app.delete("/v1/subjects/{subject_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject_avatar(
    subject_id: str
):
    """
    観測対象者のアバターを削除
    """
    # Subject存在確認
    if not check_subject_exists(subject_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定されたSubjectが見つかりません"
        )
    
    s3_key = f"subjects/{subject_id}/avatar.jpg"
    
    # S3から削除
    delete_from_s3(s3_key)
    
    # データベース更新
    update_database("subjects", subject_id, None)
    
    logger.info(f"Subject avatar deleted: subject_id={subject_id}")

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """全般的なエラーハンドリング"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部サーバーエラーが発生しました"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8014))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("app:app", host=host, port=port, reload=True)