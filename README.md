# AI Hedge Fund API

## 🚀 項目介紹
本專案基於 `virattt/ai-hedge-fund` 和 `KRSHH/ritadel`，並進一步擴展，
**提供 Web API 介面**，可讓其他應用直接調用 AI 分析師的投資建議。

**主要改動：**
- ✅ **使用 Python 3.12，棄用 Poetry，改用 Pip 管理依賴**
- ✅ **內建 Flask API 服務（預設運行於 `6000` 端口）**
- ✅ **支援多種 LLM（GPT-4o、Claude 3、LLaMA3、Gemini）**
- ✅ **支援金融數據 API（Alpha Vantage、StockData、Finnhub 等）**
- ✅ **支援 Docker 部署，可直接 `docker run` 啟動 API 服務**

網頁版 Web Page
<img width="1516" alt="image" src="https://github.com/user-attachments/assets/e2d443f9-0a48-44ee-a9f4-a61bdfe60e96" />

telegram bot 
https://github.com/tbdavid2019/telegram-bot-stock2
![image](https://github.com/user-attachments/assets/26d173d0-cc64-4d11-b70b-7735a07c30e0)


## 📌 環境安裝

### **1️⃣ Clone 本專案**
```bash
git clone https://github.com/tbdavid2019/ai-hedge-fund-API.git
cd ai-hedge-fund-API
```

### **2️⃣ 創建虛擬環境 & 安裝依賴**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows 則使用 venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### **3️⃣ 設定環境變數**
請在專案根目錄創建 `.env` 檔案，並填入 API Keys：

```ini
# LLM API Keys（至少設定一個）
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key

# 金融數據 API Keys（至少設定一個）
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
STOCKDATA_API_KEY=your-stockdata-key
FINNHUB_API_KEY=your-finnhub-key
EODHD_API_KEY=your-eodhd-key

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB_NAME=ai_hedge_fund_db
```

### **4️⃣ Database Setup (MySQL)**

This project now uses MySQL to store user information, analysis requests, results, and system logs.

1.  **Install MySQL Server:**
    *   Ensure you have a MySQL server instance running. You can install it locally or use a cloud-based MySQL service.
2.  **Create Database and User:**
    *   Connect to your MySQL server and create a database, for example, `ai_hedge_fund_db`.
        ```sql
        CREATE DATABASE ai_hedge_fund_db;
        ```
    *   Create a dedicated user and grant privileges to this database. Replace `your_mysql_user` and `your_mysql_password` with secure credentials.
        ```sql
        CREATE USER 'your_mysql_user'@'localhost' IDENTIFIED BY 'your_mysql_password';
        GRANT ALL PRIVILEGES ON ai_hedge_fund_db.* TO 'your_mysql_user'@'localhost';
        FLUSH PRIVILEGES;
        ```
3.  **Database Schema:**
    The application expects the following tables. You may need to create these manually if the application doesn't create them automatically on first run. (Clarification: Current implementation does not auto-create tables).

    *   **`users`**: Stores user credentials.
        ```sql
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
    *   **`analysis_requests`**: Stores details of analysis requests.
        ```sql
        CREATE TABLE analysis_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            tickers TEXT NOT NULL,
            selected_analysts TEXT NOT NULL,
            model_name VARCHAR(255),
            start_date DATE,
            end_date DATE,
            request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        ```
    *   **`analysis_results`**: Stores the outcomes of analyses.
        ```sql
        CREATE TABLE analysis_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT NOT NULL,
            raw_response_json LONGTEXT,
            decisions_json LONGTEXT,
            analyst_signals_json LONGTEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES analysis_requests(id) ON DELETE CASCADE
        );
        ```
    *   **`system_logs`**: General system logs, API calls, errors.
        ```sql
        CREATE TABLE system_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level VARCHAR(50),
            event_type VARCHAR(100),
            message TEXT,
            details_json LONGTEXT
        );
        ```

## 🚀 5️⃣ 啟動 API 服務

```bash
python webui2.py --api
```
預設 API 會運行於 `http://localhost:6000`


## 📡 6️⃣ **Docker 部署**

### **1️⃣ 建立 Docker 映像**
```bash
docker build -t ai-hedge-fund-api .
```

### **2️⃣ 啟動容器**
```bash
docker run --env-file .env -p 6000:6000 ai-hedge_fund_api
```

## 🔍 7️⃣ **API 調用方式**

### **1️⃣ 股票分析 API**

#### **📥 請求方式**
```bash
curl -X POST "http://localhost:6000/api/analysis" \
     -H "Content-Type: application/json" \
     -d '{
           "tickers": "tsla",
           "selectedAnalysts": ["ben_graham"],
           "modelName": "gpt-4o",
           "user_id": 123 
         }'
```
*(Note: `user_id` is optional. If provided, associates the analysis with a registered user.)*

#### **📤 回應範例**
```json
{
  "analyst_signals": {
    "ben_graham_agent": {
      "tsla": {
        "confidence": 80.0,
        "reasoning": "Tesla's financial assessment reveals several weaknesses from a Graham perspective...",
        "signal": "bearish"
      }
    },
    "risk_management_agent": {
      "tsla": {
        "current_price": 236.25,
        "reasoning": {
          "available_cash": 100000.0,
          "current_position": 0.0,
          "portfolio_value": 100000.0,
          "position_limit": 20000.0,
          "remaining_limit": 20000.0
        },
        "remaining_position_limit": 20000.0
      }
    }
  },
  "decisions": {
    "tsla": {
      "action": "short",
      "confidence": 80.0,
      "quantity": 84,
      "reasoning": "The analysis by the ben_graham_agent indicates a strong bearish signal..."
    }
  }
}
```

### **2️⃣ User Management API**

#### Register User
*   **Endpoint:** `POST /api/register`
*   **Payload:** `{"username": "testuser", "password": "password123", "email": "test@example.com"}`
*   **Response:** Success message with `user_id` or error.

#### Login User
*   **Endpoint:** `POST /api/login`
*   **Payload:** `{"username": "testuser", "password": "password123"}`
*   **Response:** Success message with `user_id` and `username` or error. (Note: Full session management/tokens are not yet implemented).

### **3️⃣ Data Retrieval API**

#### Get User's Analyses
*   **Endpoint:** `GET /api/users/<user_id>/analyses`
*   **Description:** Retrieves a list of past analysis requests for the specified user.
*   **Response:** JSON array of analysis request objects.

#### Get Analysis Details
*   **Endpoint:** `GET /api/analyses/<analysis_id>`
*   **Description:** Retrieves detailed information for a specific analysis, including request parameters and results.
*   **Response:** JSON object with analysis details.

#### Get System Logs
*   **Endpoint:** `GET /api/logs`
*   **Description:** Retrieves system logs.
*   **Query Parameters (optional):**
    *   `level`: Filter by log level (e.g., INFO, ERROR).
    *   `event_type`: Filter by event type (e.g., API_CALL, AI_DECISION).
    *   `limit`: Number of logs to return (default 100).
    *   `offset`: Offset for pagination.
*   **Response:** JSON array of log objects.

---

# AI Hedge Fund API (English)

## 🚀 Project Overview
This project extends `virattt/ai-hedge-fund` and `KRSHH/ritadel`,
providing a **RESTful API** for external applications to query AI-driven investment insights.

**Major Improvements:**
- ✅ **Python 3.12 (Switched from Poetry to Pip)**
- ✅ **Built-in Flask API (default port: `6000`)**
- ✅ **Supports multiple LLMs (GPT-4o, Claude 3, LLaMA3, Gemini)**
- ✅ **Financial Data APIs (Alpha Vantage, StockData, Finnhub, etc.)**
- ✅ **Docker-ready, deploy via `docker run`**

Web
<img width="1516" alt="image" src="https://github.com/user-attachments/assets/e2d443f9-0a48-44ee-a9f4-a61bdfe60e96" />

## 📌 Installation

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/tbdavid2019/ai-hedge-fund-API.git
cd ai-hedge-fund-API
```

### **2️⃣ Set Up Virtual Environment & Install Dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### **3️⃣ Configure `.env` File**
```ini
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
STOCKDATA_API_KEY=your-stockdata-key
FINNHUB_API_KEY=your-finnhub-key
EODHD_API_KEY=your-eodhd-key

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB_NAME=ai_hedge_fund_db
```

### **4️⃣ Database Setup (MySQL)**

This project now uses MySQL to store user information, analysis requests, results, and system logs.

1.  **Install MySQL Server:**
    *   Ensure you have a MySQL server instance running. You can install it locally or use a cloud-based MySQL service.
2.  **Create Database and User:**
    *   Connect to your MySQL server and create a database, for example, `ai_hedge_fund_db`.
        ```sql
        CREATE DATABASE ai_hedge_fund_db;
        ```
    *   Create a dedicated user and grant privileges to this database. Replace `your_mysql_user` and `your_mysql_password` with secure credentials.
        ```sql
        CREATE USER 'your_mysql_user'@'localhost' IDENTIFIED BY 'your_mysql_password';
        GRANT ALL PRIVILEGES ON ai_hedge_fund_db.* TO 'your_mysql_user'@'localhost';
        FLUSH PRIVILEGES;
        ```
3.  **Database Schema:**
    The application expects the following tables. You may need to create these manually if the application doesn't create them automatically on first run. (Clarification: Current implementation does not auto-create tables).

    *   **`users`**: Stores user credentials.
        ```sql
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
    *   **`analysis_requests`**: Stores details of analysis requests.
        ```sql
        CREATE TABLE analysis_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            tickers TEXT NOT NULL,
            selected_analysts TEXT NOT NULL,
            model_name VARCHAR(255),
            start_date DATE,
            end_date DATE,
            request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        ```
    *   **`analysis_results`**: Stores the outcomes of analyses.
        ```sql
        CREATE TABLE analysis_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT NOT NULL,
            raw_response_json LONGTEXT,
            decisions_json LONGTEXT,
            analyst_signals_json LONGTEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES analysis_requests(id) ON DELETE CASCADE
        );
        ```
    *   **`system_logs`**: General system logs, API calls, errors.
        ```sql
        CREATE TABLE system_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level VARCHAR(50),
            event_type VARCHAR(100),
            message TEXT,
            details_json LONGTEXT
        );
        ```

## 🚀 5️⃣ Start API Server
```bash
python webui2.py --api
```
(Default API runs on `http://localhost:6000`)

## 📡 6️⃣ Docker Deployment

### **1️⃣ Build Docker Image**
```bash
docker build -t ai-hedge_fund_api .
```

### **2️⃣ Run Container**
```bash
docker run --env-file .env -p 6000:6000 ai-hedge_fund_api
```

## 🔍 7️⃣ API Usage

### **1️⃣ Stock Analysis API**
#### **📥 Request**
```bash
curl -X POST "http://localhost:6000/api/analysis" \
     -H "Content-Type: application/json" \
     -d '{
           "tickers": "tsla",
           "selectedAnalysts": ["ben_graham"],
           "modelName": "gpt-4o",
           "user_id": 123
         }'
```
*(Note: `user_id` is optional. If provided, associates the analysis with a registered user.)*

#### **📤 Response Example** *(Real-time financial data required!)*
_(See JSON example in Chinese section)_

### **2️⃣ User Management API**

#### Register User
*   **Endpoint:** `POST /api/register`
*   **Payload:** `{"username": "testuser", "password": "password123", "email": "test@example.com"}`
*   **Response:** Success message with `user_id` or error.

#### Login User
*   **Endpoint:** `POST /api/login`
*   **Payload:** `{"username": "testuser", "password": "password123"}`
*   **Response:** Success message with `user_id` and `username` or error. (Note: Full session management/tokens are not yet implemented).

### **3️⃣ Data Retrieval API**

#### Get User's Analyses
*   **Endpoint:** `GET /api/users/<user_id>/analyses`
*   **Description:** Retrieves a list of past analysis requests for the specified user.
*   **Response:** JSON array of analysis request objects.

#### Get Analysis Details
*   **Endpoint:** `GET /api/analyses/<analysis_id>`
*   **Description:** Retrieves detailed information for a specific analysis, including request parameters and results.
*   **Response:** JSON object with analysis details.

#### Get System Logs
*   **Endpoint:** `GET /api/logs`
*   **Description:** Retrieves system logs.
*   **Query Parameters (optional):**
    *   `level`: Filter by log level (e.g., INFO, ERROR).
    *   `event_type`: Filter by event type (e.g., API_CALL, AI_DECISION).
    *   `limit`: Number of logs to return (default 100).
    *   `offset`: Offset for pagination.
*   **Response:** JSON array of log objects.


<img width="1601" alt="image" src="https://github.com/user-attachments/assets/0c2157e0-071c-4c9d-a15a-04c02912242a" />


