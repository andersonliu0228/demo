# EA 自動化跟單系統

完整的加密貨幣自動跟單系統，包含後端 API、前端儀表板和 Docker 部署配置。

## ✨ 功能特色

- 🔐 **安全的憑證管理**: API Secret 使用 Fernet AES-256 加密存儲
- 🤖 **自動跟單引擎**: 實時監控 Master 帳戶並自動執行跟單
- 📊 **即時儀表板**: React 前端顯示持倉、交易歷史和引擎狀態
- 🔄 **對帳系統**: 自動計算並執行補單/平倉操作
- 🎯 **靈活配置**: 支援自定義跟單比例和開關控制
- 🐳 **完整 Docker 化**: 一鍵啟動所有服務

## 🚀 快速開始

### 使用 Docker（推薦）

```powershell
# 1. 啟動所有服務（首次運行會自動構建）
.\docker-start.ps1

# 2. 訪問系統
# 前端: http://localhost:3000
# 後端 API: http://localhost:8000/docs
```

就這麼簡單！腳本會自動：
- 檢查 Docker 狀態
- 構建並啟動所有容器
- 執行資料庫遷移
- 顯示訪問地址

### 其他 Docker 命令

```powershell
# 查看日誌
.\docker-logs.ps1

# 查看特定服務日誌
.\docker-logs.ps1 -Service backend

# 停止服務
.\docker-stop.ps1

# 完全清理（會刪除資料）
.\docker-clean.ps1
```

## 📋 系統架構

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ :3000
       ▼
┌──────────────┐
│   Frontend   │ (React + Nginx)
│  Dashboard   │
└──────┬───────┘
       │ /api/* → :8000
       ▼
┌──────────────┐
│   Backend    │ (FastAPI)
│   API + 引擎  │
└───┬──────┬───┘
    │      │
    ▼      ▼
┌────┐  ┌─────┐
│ PG │  │Redis│
└────┘  └─────┘
```

## 技術棧

### 後端
- **框架**: FastAPI
- **資料庫**: PostgreSQL (asyncpg)
- **ORM**: SQLAlchemy (Async)
- **快取**: Redis
- **交易所**: CCXT
- **加密**: Fernet AES-256
- **遷移**: Alembic
- **測試**: pytest + hypothesis

### 前端
- **框架**: React 18
- **構建工具**: Vite
- **樣式**: Tailwind CSS
- **圖標**: Lucide React
- **HTTP**: Axios

### 部署
- **容器化**: Docker + docker-compose
- **Web 伺服器**: Nginx (前端)
- **反向代理**: Nginx (API 代理)

## 專案結構

```
.
├── backend/              # 後端應用程式
│   ├── app/
│   │   ├── models/       # 資料模型
│   │   ├── repositories/ # 資料存取層
│   │   ├── routes/       # API 路由
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # 業務邏輯層
│   │   │   ├── follower_engine_v2.py  # 跟單引擎
│   │   │   ├── crypto_service.py      # 加密服務
│   │   │   ├── cache_service.py       # 快取服務
│   │   │   └── exchange_service.py    # 交易所整合
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 資料庫配置
│   │   └── main.py       # FastAPI 入口
│   └── tests/            # 測試代碼
├── frontend/             # 前端應用程式
│   ├── src/
│   │   ├── components/   # React 組件
│   │   │   ├── Dashboard.jsx
│   │   │   ├── StatusBar.jsx
│   │   │   ├── FollowSettings.jsx
│   │   │   ├── TradeHistory.jsx
│   │   │   └── TestConsole.jsx
│   │   ├── hooks/        # 自定義 Hooks
│   │   ├── lib/          # API 客戶端
│   │   └── main.jsx      # React 入口
│   ├── Dockerfile        # 前端 Docker 配置
│   └── nginx.conf        # Nginx 配置
├── alembic/              # 資料庫遷移
├── scripts/              # 輔助腳本
├── docker-compose.yml    # Docker Compose 配置
├── Dockerfile            # 後端 Docker 配置
└── .env                  # 環境變數
```

## 快速開始

### 方法 1：使用 Docker（推薦）

這是最簡單的方式，適合所有用戶。

#### Windows 用戶

```powershell
# 一鍵啟動
.\docker-start.ps1
```

#### Linux/Mac 用戶

```bash
# 構建並啟動
docker-compose up --build -d

# 執行遷移
docker-compose exec backend alembic upgrade head
```

#### 訪問系統

- **前端應用**: http://localhost:3000
- **後端 API 文檔**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 方法 2：本地開發

適合需要修改代碼的開發者。

#### 後端（使用 Docker 資料庫）

```bash
# 1. 啟動資料庫和 Redis
docker-compose up -d postgres redis

# 2. 安裝 Python 依賴
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env 並設定 ENCRYPTION_KEY

# 4. 執行遷移
alembic upgrade head

# 5. 啟動後端
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端（本地開發）

```bash
# 1. 進入前端目錄
cd frontend

# 2. 安裝依賴
npm install

# 3. 啟動開發伺服器
npm run dev
```

前端會在 http://localhost:5173 運行，並自動代理 API 請求到後端。

## 📖 使用指南

### 1. 註冊新帳號

1. 訪問 http://localhost:3000
2. 點擊「尚未註冊？點此註冊」
3. 填寫註冊表單：
   - 用戶名（至少 3 個字元）
   - Email
   - 密碼（至少 6 個字元）
   - 確認密碼
4. 點擊「註冊」按鈕
5. 註冊成功後自動跳轉到登入頁面

### 2. 登入系統

1. 在登入頁面輸入帳號密碼
2. 點擊「登入」按鈕
3. 成功登入後進入儀表板

**測試帳號**:
- 用戶名: testuser
- 密碼: testpass123

### 2. 配置 API 憑證

1. 在儀表板中點擊「API 憑證管理」
2. 添加 Master 帳戶憑證（用於監控）
3. 添加 Follower 帳戶憑證（用於跟單）
4. 系統會自動驗證憑證有效性

### 3. 設定跟單參數

1. 在「跟單設定」區域配置：
   - **跟單比例**: 例如 0.5 表示 50% 的倉位
   - **啟用狀態**: 開啟/關閉跟單功能
2. 點擊「儲存設定」

### 4. 啟動跟單引擎

1. 點擊「啟動引擎」按鈕
2. 引擎會每 3 秒檢查一次 Master 持倉
3. 自動執行跟單和對帳操作

### 5. 測試系統

使用右側的「測試控制台」：
1. 選擇交易對（如 BTC/USDT）
2. 選擇方向（買入/賣出）
3. 輸入數量
4. 點擊「觸發 Master 訂單」
5. 觀察儀表板變化

## 🔧 Docker 管理命令

### Windows PowerShell

```powershell
# 啟動系統
.\docker-start.ps1

# 測試前端開發模式
.\test-docker-frontend.ps1

# 重啟前端（開發模式）
.\docker-restart-frontend.ps1

# 查看所有日誌
.\docker-logs.ps1

# 查看特定服務日誌
.\docker-logs.ps1 -Service backend
.\docker-logs.ps1 -Service frontend

# 停止系統
.\docker-stop.ps1

# 完全清理（刪除所有資料）
.\docker-clean.ps1
```

### 開發模式特點

前端使用開發模式運行，支援：
- ✅ **熱更新（Hot Reload）**: 修改代碼自動刷新
- ✅ **Volume 掛載**: 本地修改即時生效
- ✅ **API 狀態指示器**: 右上角顯示連接狀態
- ✅ **快速迭代**: 無需重啟容器

修改 `frontend/src/` 下的任何檔案，保存後 1-2 秒內自動更新！

### 通用命令

```bash
# 查看服務狀態
docker-compose ps

# 重啟服務
docker-compose restart

# 重新構建
docker-compose build

# 進入容器
docker-compose exec backend sh
docker-compose exec frontend sh

# 執行資料庫遷移
docker-compose exec backend alembic upgrade head

# 查看資料庫
docker-compose exec postgres psql -U postgres -d ea_trading
```

## 🧪 測試

### 執行所有測試

```bash
# 在 Docker 中執行
docker-compose exec backend pytest

# 本地執行
pytest
```

### 執行特定測試

```bash
# 測試加密服務
pytest backend/tests/services/test_crypto_service.py

# 測試屬性
pytest backend/tests/services/test_crypto_service_properties.py

# 查看覆蓋率
pytest --cov=backend/app --cov-report=html
```

### 屬性測試

系統使用 Hypothesis 進行屬性測試，確保核心功能的正確性：

- **Property 1**: 加密解密往返一致性
- **Property 3**: 錯誤金鑰拒絕解密
- **Property 5**: 用戶名和電子郵件唯一性
- **Property 10**: 防止重複綁定相同憑證
- **Property 11**: 無效憑證驗證失敗
- **Property 18**: 快取失效機制
- **Property 19**: Redis 降級處理

## 📚 API 端點

### 認證
- `POST /api/v1/auth/register` - 註冊新用戶
- `POST /api/v1/auth/login` - 用戶登入
- `GET /api/v1/auth/me` - 獲取當前用戶資訊

### 憑證管理
- `POST /api/v1/credentials` - 創建新憑證
- `GET /api/v1/credentials` - 獲取用戶所有憑證
- `GET /api/v1/credentials/{id}` - 獲取特定憑證
- `PUT /api/v1/credentials/{id}` - 更新憑證
- `DELETE /api/v1/credentials/{id}` - 刪除憑證

### 跟單配置
- `GET /api/v1/follow-config/settings` - 獲取跟單設定
- `PUT /api/v1/follow-config/settings` - 更新跟單設定
- `GET /api/v1/follow-config/status` - 獲取引擎狀態
- `POST /api/v1/follow-config/start` - 啟動跟單引擎
- `POST /api/v1/follow-config/stop` - 停止跟單引擎

### 交易歷史
- `GET /api/v1/trades/history` - 獲取交易歷史
- `GET /api/v1/trades/positions` - 獲取當前持倉

### 儀表板
- `GET /api/v1/dashboard/summary` - 獲取儀表板摘要（一次返回所有資訊）

### 測試端點
- `POST /api/v1/test/trigger-master-order` - 觸發 Master 測試訂單

完整的 API 文檔請訪問: http://localhost:8000/docs

## ⚙️ 核心功能

### 1. 安全的憑證存儲
- API Secret 使用 Fernet AES-256 加密
- 加密金鑰與應用程式分離
- API Key 自動遮蔽顯示
- 用戶級別權限隔離

### 2. 自動跟單引擎
- 實時監控 Master 帳戶持倉（3 秒輪詢）
- 自動計算跟單數量（支援自定義比例）
- 智能對帳系統（補單/平倉）
- 完整的錯誤處理和日誌記錄

### 3. 交易所整合
支援的交易所：
- Binance
- OKX
- Bybit
- Huobi
- KuCoin
- Gate.io
- Bitget
- MEXC

### 4. 快取機制
- 用戶憑證列表快取（TTL: 5 分鐘）
- 單個憑證快取（TTL: 5 分鐘）
- 交易所列表快取（TTL: 1 小時）
- Redis 失敗時自動降級到資料庫

### 5. 對帳系統
- 自動比對 Master 和 Follower 持倉
- 計算差異並執行補單或平倉
- 記錄所有對帳操作
- 支援手動觸發對帳

### 6. 即時儀表板
- 顯示當前持倉和總價值
- 實時交易歷史
- 引擎運行狀態監控
- 錯誤日誌查看
- 測試控制台

## 🔐 環境變數

創建 `.env` 檔案並設定以下變數：

```bash
# 資料庫配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ea_trading
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ea_trading

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 加密金鑰（使用 scripts/generate_encryption_key.py 生成）
ENCRYPTION_KEY=your-base64-encoded-fernet-key-here

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 應用程式設定
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1
```

### 生成加密金鑰

```bash
# 方法 1: 使用腳本
python scripts/generate_encryption_key.py

# 方法 2: 使用 Python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 🐳 Docker 管理

### 快速命令（Windows）

```powershell
# 啟動系統
.\docker-start.ps1

# 查看日誌
.\docker-logs.ps1

# 停止系統
.\docker-stop.ps1

# 完全清理
.\docker-clean.ps1
```

### 通用命令

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 重啟服務
docker-compose restart

# 停止服務
docker-compose stop

# 停止並移除容器
docker-compose down

# 停止並移除容器和資料
docker-compose down -v

# 重新構建
docker-compose build

# 執行資料庫遷移
docker-compose exec backend alembic upgrade head

# 進入容器
docker-compose exec backend sh
docker-compose exec frontend sh
docker-compose exec postgres psql -U postgres -d ea_trading
```

詳細的 Docker 部署指南請參考 [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

## 📝 開發狀態

### ✅ 已完成

#### 後端
- [x] 專案結構和基礎配置
- [x] Crypto Service（加密服務）+ 屬性測試
- [x] 資料庫模型和遷移（6 個遷移檔案）
- [x] Repository 層 + 單元測試
- [x] Redis 快取服務 + 屬性測試
- [x] Exchange Service（CCXT 整合）+ 測試
- [x] Credential Service（業務邏輯層）+ 屬性測試
- [x] 用戶認證系統（JWT）
- [x] 跟單引擎 V2（用戶級配置）
- [x] 對帳系統（補單/平倉）
- [x] 儀表板聚合 API
- [x] 完整的 API 路由層
- [x] Docker 容器化配置

#### 前端
- [x] React + Vite 專案結構
- [x] Tailwind CSS 樣式系統
- [x] 用戶登入/註冊頁面
- [x] 儀表板主頁
- [x] 狀態欄組件
- [x] 跟單設定組件
- [x] 交易歷史組件
- [x] 測試控制台組件
- [x] API 客戶端（Axios + JWT）
- [x] 自定義 Hooks（useDashboard）
- [x] Docker 部署配置

#### 部署
- [x] Docker Compose 配置
- [x] 前端 Nginx 配置
- [x] 環境變數管理
- [x] 健康檢查配置
- [x] PowerShell 管理腳本

### 🚧 可選優化

- [ ] WebSocket 實時推送（目前使用輪詢）
- [ ] 更多交易所支援
- [ ] 進階風控功能
- [ ] 多語言支援
- [ ] 移動端適配
- [ ] 效能監控和告警
- [ ] 自動化測試 CI/CD

## 🔒 安全性

### 已實現
- ✅ API Secret 加密存儲（Fernet AES-256）
- ✅ 加密金鑰與應用程式分離
- ✅ API Key 遮蔽顯示
- ✅ 用戶級別權限隔離
- ✅ JWT Token 認證
- ✅ 密碼 bcrypt 雜湊
- ✅ CORS 配置

### 生產環境建議
- 🔐 使用強密碼和金鑰
- 🔐 啟用 HTTPS
- 🔐 限制 CORS 允許的來源
- 🔐 定期更新依賴套件
- 🔐 實施 API 速率限制
- 🔐 添加日誌監控和告警

## 📖 相關文檔

- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - Docker 部署完整指南
- [註冊功能測試指南.md](./註冊功能測試指南.md) - 註冊功能使用指南
- [註冊功能完成總結.md](./註冊功能完成總結.md) - 註冊功能說明
- [前端Docker開發模式測試指南.md](./前端Docker開發模式測試指南.md) - 開發模式使用指南
- [前端Docker開發模式完成總結.md](./前端Docker開發模式完成總結.md) - 開發模式功能說明
- [啟動Docker完整系統.md](./啟動Docker完整系統.md) - Docker 快速啟動
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 系統架構說明
- [QUICK_START.md](./QUICK_START.md) - 快速開始指南
- [前端實作總結.md](./前端實作總結.md) - 前端開發說明
- [儀表板API實作總結.md](./儀表板API實作總結.md) - API 說明
- [對帳系統實作總結.md](./對帳系統實作總結.md) - 對帳系統說明

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License
