# EA 自動化跟單系統後端 - 快速開始指南

## 🚀 5 分鐘快速啟動

### 前置需求

- Docker 和 Docker Compose
- Python 3.11+（如果要本地開發）

### 步驟 1：生成加密金鑰

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

複製輸出的金鑰。

### 步驟 2：設定環境變數

創建 `.env` 檔案：

```bash
echo "ENCRYPTION_KEY=你的金鑰" > .env
```

### 步驟 3：啟動服務

```bash
docker-compose up -d
```

### 步驟 4：驗證服務

訪問 http://localhost:8000/docs 查看 API 文檔。

## 📝 測試 API

### 1. 獲取支援的交易所列表

```bash
curl http://localhost:8000/api/v1/exchange/supported
```

### 2. 驗證 API 憑證（不儲存）

```bash
curl -X POST http://localhost:8000/api/v1/exchange/verify \
  -H "Content-Type: application/json" \
  -d '{
    "exchange_name": "binance",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
  }'
```

### 3. 創建憑證

```bash
curl -X POST http://localhost:8000/api/v1/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "exchange_name": "binance",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "verify": true
  }'
```

### 4. 獲取所有憑證

```bash
curl http://localhost:8000/api/v1/credentials
```

## 🔧 常用命令

### 查看日誌

```bash
# 所有服務
docker-compose logs -f

# 只看後端
docker-compose logs -f backend

# 只看資料庫
docker-compose logs -f postgres
```

### 重啟服務

```bash
docker-compose restart backend
```

### 停止服務

```bash
docker-compose down
```

### 清理並重新開始

```bash
docker-compose down -v
docker-compose up -d --build
```

### 執行資料庫遷移

```bash
docker-compose exec backend alembic upgrade head
```

### 進入容器

```bash
# 進入後端容器
docker-compose exec backend bash

# 進入資料庫容器
docker-compose exec postgres psql -U postgres -d ea_trading
```

## 🧪 執行測試

### 在容器中執行測試

```bash
docker-compose exec backend pytest
```

### 本地執行測試

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行測試
pytest

# 查看覆蓋率
pytest --cov=backend/app --cov-report=html
```

## 📊 監控服務狀態

### 檢查服務健康狀態

```bash
docker-compose ps
```

### 檢查 API 健康

```bash
curl http://localhost:8000/health
```

## 🐛 故障排除

### 問題：容器無法啟動

```bash
# 查看詳細日誌
docker-compose logs backend

# 檢查環境變數
docker-compose config
```

### 問題：資料庫連接失敗

```bash
# 確認 PostgreSQL 正在運行
docker-compose ps postgres

# 測試資料庫連接
docker-compose exec postgres pg_isready -U postgres
```

### 問題：Redis 連接失敗

```bash
# 確認 Redis 正在運行
docker-compose ps redis

# 測試 Redis 連接
docker-compose exec redis redis-cli ping
```

### 問題：加密金鑰錯誤

確保 `.env` 檔案中的 `ENCRYPTION_KEY` 是有效的 Fernet 金鑰。重新生成：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 📚 下一步

1. 閱讀完整的 [README.md](README.md)
2. 查看 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) 了解架構
3. 訪問 http://localhost:8000/docs 探索 API
4. 查看 `backend/tests/` 了解測試範例

## 🔐 安全提示

⚠️ **重要**：
- 不要在生產環境中使用預設的加密金鑰
- 不要將 `.env` 檔案提交到版本控制
- 在生產環境中使用強密碼
- 啟用 HTTPS
- 實作身份認證和授權

## 💡 提示

- 使用 `docker-compose up -d` 在背景執行服務
- 使用 `docker-compose logs -f backend` 即時查看日誌
- API 文檔會自動更新（訪問 /docs）
- 修改代碼後容器會自動重新載入（開發模式）
