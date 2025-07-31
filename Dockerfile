FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 非rootユーザーを作成
RUN useradd -m -u 1000 apiuser && chown -R apiuser:apiuser /app
USER apiuser

# ポートを公開
EXPOSE 8014

# アプリケーションを起動
CMD ["python", "app.py"]