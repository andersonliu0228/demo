# 🚀 開始使用 EA 自動化跟單系統後端

歡迎！這份指南將幫助你在 5 分鐘內啟動並運行系統。

## 📋 前置需求

確保你的系統已安裝：
- ✅ Docker Desktop（或 Docker + Docker Compose）
- ✅ Python 3.11+（如果要本地開發）

## 🎯 三步驟快速啟動

### 步驟 1：生成加密金鑰

打開終端機，執行：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

你會看到類似這樣的輸出：
```
b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx='
```

**複製這個金鑰！**

### 步驟 2：設定環境變數

在專案根目錄創建 `.env` 檔案：

```bash
echo "ENCRYPTION_KEY=你剛才複製的金鑰" > .env
```

或手動創建 `.env` 檔案，內容如下：

```env
ENCRYPTION_KEY=你的金鑰
```

### 步驟 3：啟動所有服務

```bash
docker-compose up -d
```

等待幾秒鐘，讓服務啟動完成。

## ✅ 驗證安裝

### 1. 檢查服務狀態

```bash
docker-compose ps
```

你應該看到三個服務都在運行：
- `ea_trading_postgres` - 資料庫
- `ea_trading_redis` - 快取
- `ea_trading_backend` - API 服務

### 2. 訪問 API 文檔

打開瀏覽器，訪問：

**Swagger UI**: http://localhost:8000/docs

你應該看到完整的 API 文檔介面。

### 3. 測試健康檢查

```bash
curl http://localhost:8000/health
```

應該返回：
```json
{"status":"healthy"}
```

## 🎮 試用 API

### 1. 獲取支援的交易所列表

```bash
curl http://localhost:8000/api/v1/exchange/supported
```

應該返回：
```json
["binance","okx","bybit","huobi","kucoin","gate","bitget","mexc"]
```

### 2. 驗證 API 憑證（測試用）

```bash
curl -X POST http://localhost:8000/api/v1/exchange/verify \
  -H "Content-Type: application/json" \
  -d '{
    "exchange_name": "binance",
    "api_key": "test_key",
    "api_secret": "test_secret"
  }'
```

**注意**：這會返回驗證失敗（因為是測試憑證），但證明 API 正常工作。

### 3. 創建憑證（使用真實憑證）

如果你有真實的交易所 API Key：

```bash
curl -X POST http://localhost:8000/api/v1/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "exchange_name": "binance",
    "api_key": "你的API_KEY",
    "api_secret": "你的API_SECRET",
    "verify": true
  }'
```

### 4. 查看所有憑證

```bash
curl http://localhost:8000/api/v1/credentials
```

## 📚 探索更多

### 使用 Swagger UI

訪問 http://localhost:8000/docs，你可以：

1. **查看所有 API 端點**
2. **直接在瀏覽器中測試 API**
3. **查看請求/響應格式**
4. **下載 OpenAPI 規範**

### 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs -f

# 只查看後端日誌
docker-compose logs -f backend

# 只查看最近 100 行
docker-compose logs --tail=100 backend
```

### 進入容器

```bash
# 進入後端容器
docker-compose exec backend bash

# 進入資料庫容器
docker-compose exec postgres psql -U postgres -d ea_trading
```

## 🔧 常見操作

### 重啟服務

```bash
docker-compose restart backend
```

### 停止所有服務

```bash
docker-compose down
```

### 清理並重新開始

```bash
# 停止並刪除所有容器和卷
docker-compose down -v

# 重新啟動
docker-compose up -d
```

### 查看資料庫

```bash
docker-compose exec postgres psql -U postgres -d ea_trading

# 在 psql 中執行：
\dt                    # 列出所有表
SELECT * FROM users;   # 查看用戶
SELECT * FROM api_credentials;  # 查看憑證
\q                     # 退出
```

## 🐛 故障排查

### 問題：容器無法啟動

**解決方案**：
```bash
# 查看詳細日誌
docker-compose logs backend

# 檢查配置
docker-compose config
```

### 問題：加密金鑰錯誤

**解決方案**：
```bash
# 重新生成金鑰
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 更新 .env 檔案
echo "ENCRYPTION_KEY=新金鑰" > .env

# 重啟服務
docker-compose restart backend
```

### 問題：資料庫連接失敗

**解決方案**：
```bash
# 檢查 PostgreSQL 狀態
docker-compose ps postgres

# 測試連接
docker-compose exec postgres pg_isready -U postgres

# 重啟資料庫
docker-compose restart postgres
```

### 問題：Redis 連接失敗

**解決方案**：
```bash
# 檢查 Redis 狀態
docker-compose ps redis

# 測試連接
docker-compose exec redis redis-cli ping

# 重啟 Redis
docker-compose restart redis
```

## 📖 下一步

### 1. 閱讀完整文檔

- **README.md** - 完整功能說明
- **IMPLEMENTATION_SUMMARY.md** - 架構詳解
- **PROJECT_STATUS.md** - 專案狀態

### 2. 了解 API

訪問 http://localhost:8000/docs 探索所有 API 端點。

### 3. 查看代碼

```
backend/app/
├── models/       # 資料模型
├── repositories/ # 資料存取層
├── routes/       # API 路由
├── schemas/      # 請求/響應格式
├── services/     # 業務邏輯
└── main.py       # 應用程式入口
```

### 4. 執行測試

```bash
# 在容器中執行測試
docker-compose exec backend pytest

# 查看測試覆蓋率
docker-compose exec backend pytest --cov=backend/app
```

## 💡 實用技巧

### 1. 使用環境變數

你可以在 `.env` 檔案中自定義更多設定：

```env
ENCRYPTION_KEY=你的金鑰
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/ea_trading
REDIS_URL=redis://redis:6379/0
DEBUG=True
LOG_LEVEL=INFO
```

### 2. 開發模式

如果要本地開發（不使用 Docker）：

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動資料庫和 Redis
docker-compose up -d postgres redis

# 執行遷移
alembic upgrade head

# 啟動開發伺服器
uvicorn backend.app.main:app --reload
```

### 3. 生產環境

生產環境建議：
- 使用強密碼
- 啟用 HTTPS
- 設定防火牆
- 配置備份
- 實作監控

## 🎓 學習資源

- **FastAPI 教程**: https://fastapi.tiangolo.com/tutorial/
- **SQLAlchemy 文檔**: https://docs.sqlalchemy.org/
- **CCXT 文檔**: https://docs.ccxt.com/
- **Docker 教程**: https://docs.docker.com/get-started/

## 🆘 需要幫助？

1. **查看文檔**：README.md, QUICK_START.md
2. **查看日誌**：`docker-compose logs -f backend`
3. **檢查狀態**：`docker-compose ps`
4. **測試連接**：訪問 http://localhost:8000/health

## ✅ 檢查清單

完成以下步驟，確保系統正常運行：

- [ ] Docker 已安裝
- [ ] 已生成加密金鑰
- [ ] 已創建 `.env` 檔案
- [ ] 已執行 `docker-compose up -d`
- [ ] 可以訪問 http://localhost:8000/docs
- [ ] 健康檢查返回 `{"status":"healthy"}`
- [ ] 可以獲取支援的交易所列表

**恭喜！你已經成功啟動 EA 自動化跟單系統後端！** 🎉

---

**提示**：如果遇到任何問題，請查看 [QUICK_START.md](QUICK_START.md) 或 [README.md](README.md) 獲取更詳細的說明。
