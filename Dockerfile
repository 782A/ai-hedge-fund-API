# 使用 Python 3.12 官方映像
FROM python:3.12

# 設置工作目錄
WORKDIR /app

# 複製專案檔案
COPY . .

# 建立虛擬環境並安裝依賴
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=webui2.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=6000
ENV MYSQL_HOST=db
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=password
ENV MYSQL_DB_NAME=ai_hedge_fund_db

# 告知 Docker 這個容器將使用 6000 端口
EXPOSE 6000

# 啟動 Flask 服務
CMD ["venv/bin/python", "webui2.py", "--api", "--port=6000"]