# 🐳 Docker 完整系統啟動指南

## 📋 前置需求

- Docker Desktop 已安裝並運行
- 已設定 `.env` 檔案中的 `ENCRYPTION_KEY`

## 🚀 快速啟動

### 1. 構建並啟動所有服務

```powershell
# 構建並啟動所有容器（首次啟動或更新代碼後）
docker-compose up --build -d

# 或者只啟動（不重新構建）
docker-compose up -d
```

### 2. 檢查服務狀態

```powershell
# 查看所有容器狀態
docker-compose ps

# 查看容器日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 3. 初始化資料庫

```powershell
# 執行資料庫遷移
docker-compose exec backend alembic upgrade head
```

### 4. 訪問服務

- **前端應用**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🛠️ 常用命令

### 服務管理

```powershell
# 停止所有服務
docker-compose stop

# 啟動已停止的服務
docker-compose start

# 重啟服務
docker-compose restart

# 停止並移除所有容器
docker-compose down

# 停止並移除所有容器、網路、卷
docker-compose down -v
```

### 重新構建

```powershell
# 重新構建特定服務
docker-compose build backend
docker-compose build frontend

# 重新構建並啟動
docker-compose up --build -d backend
docker-compose up --build -d frontend
```

### 進入容器

```powershell
# 進入後端容器
docker-compose exec backend sh

# 進入前端容器
docker-compose exec frontend sh

# 進入 PostgreSQL 容器
docker-compose exec postgres psql -U postgres -d ea_trading
```

### 查看資源使用

```powershell
# 查看容器資源使用情況
docker stats

# 查看磁碟使用
docker system df
```

## 🔧 開發模式

如果你想在開發時使用熱重載：

### 前端開發模式

```powershell
# 停止 Docker 中的前端服務
docker-compose stop frontend

# 在本地運行前端（需要 Node.js）
cd frontend
npm install
npm run dev
```

前端會在 http://localhost:5173 運行，並自動代理 API 請求到 http://localhost:8000

### 後端開發模式

後端已經配置了卷掛載，代碼更改會自動反映（但需要重啟 uvicorn）：

```powershell
# 重啟後端服務
docker-compose restart backend
```

## 📊 測試系統

### 1. 註冊測試用戶

訪問 http://localhost:3000，點擊「註冊」按鈕：
- 用戶名: testuser
- 密碼: testpass123

### 2. 登入系統

使用剛才註冊的帳號登入

### 3. 配置 API 憑證

在儀表板中配置 Master 和 Follower 的 API 憑證（使用 Mock Exchange）

### 4. 啟動跟單引擎

在儀表板中啟動跟單引擎

### 5. 觸發測試訂單

使用右側的「測試控制台」觸發 Master 訂單，觀察跟單效果

## 🐛 故障排除

### 容器無法啟動

```powershell
# 查看詳細日誌
docker-compose logs backend
docker-compose logs frontend

# 檢查容器狀態
docker-compose ps
```

### 資料庫連接失敗

```powershell
# 檢查 PostgreSQL 是否健康
docker-compose ps postgres

# 重啟 PostgreSQL
docker-compose restart postgres

# 重新執行遷移
docker-compose exec backend alembic upgrade head
```

### 前端無法連接後端

1. 確認後端服務正在運行: `docker-compose ps backend`
2. 檢查 nginx 配置是否正確代理到 backend:8000
3. 查看前端日誌: `docker-compose logs frontend`

### 清理並重新開始

```powershell
# 停止並移除所有容器和卷
docker-compose down -v

# 重新構建並啟動
docker-compose up --build -d

# 重新執行遷移
docker-compose exec backend alembic upgrade head
```

## 📦 生產部署建議

1. **環境變數**: 使用 `.env` 檔案管理敏感資訊
2. **加密金鑰**: 生成安全的 `ENCRYPTION_KEY` 和 `JWT_SECRET_KEY`
3. **資料庫**: 使用外部託管的 PostgreSQL（如 AWS RDS）
4. **Redis**: 使用外部託管的 Redis（如 AWS ElastiCache）
5. **反向代理**: 在前端前面加上 Nginx 或 Traefik
6. **HTTPS**: 配置 SSL 證書
7. **監控**: 添加日誌聚合和監控工具

## 🔐 安全注意事項

- 修改 `.env` 中的預設密碼和金鑰
- 在生產環境中禁用 DEBUG 模式
- 限制 CORS 允許的來源
- 使用強密碼策略
- 定期更新依賴套件

## 📝 架構說明

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ :3000
       ▼
┌─────────────┐
│   Nginx     │ (Frontend Container)
│  (React)    │
└──────┬──────┘
       │ /api/* → backend:8000
       ▼
┌─────────────┐
│   FastAPI   │ (Backend Container)
└──┬────────┬─┘
   │        │
   ▼        ▼
┌────┐  ┌─────┐
│ PG │  │Redis│
└────┘  └─────┘
```

所有服務都在同一個 Docker 網路中，可以通過服務名稱互相通信。
