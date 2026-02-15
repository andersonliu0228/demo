# 🐳 Docker 完整部署總結

## ✅ 已完成的工作

### 1. 前端 Docker 化

#### 創建的檔案
- `frontend/Dockerfile` - 多階段構建配置
  - 階段 1: Node.js 構建 React 應用
  - 階段 2: Nginx 提供靜態檔案服務
- `frontend/nginx.conf` - Nginx 配置
  - SPA 路由支援
  - API 代理到後端
  - 靜態資源快取
  - Gzip 壓縮
- `frontend/.dockerignore` - 排除不必要的檔案
- `frontend/.env.production` - 生產環境配置
- `frontend/.env.development` - 開發環境配置

#### 前端配置優化
- 更新 `frontend/src/lib/api.js`
  - 支援環境變數配置 API URL
  - Docker 環境使用相對路徑（通過 nginx 代理）
  - 本地開發使用完整 URL

### 2. Docker Compose 更新

#### 新增服務
在 `docker-compose.yml` 中添加了 `frontend` 服務：
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  container_name: ea_trading_frontend
  ports:
    - "3000:80"
  depends_on:
    - backend
  networks:
    - ea_trading_network
  restart: unless-stopped
```

#### 後端配置增強
添加了 JWT 相關環境變數：
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`

### 3. 管理腳本（PowerShell）

創建了 4 個 PowerShell 腳本，簡化 Docker 操作：

#### `docker-start.ps1`
- 檢查 Docker 狀態
- 檢查 .env 檔案
- 停止現有容器
- 構建並啟動所有服務
- 等待服務啟動
- 執行資料庫遷移
- 顯示訪問資訊
- 可選擇自動打開瀏覽器

#### `docker-stop.ps1`
- 停止所有容器
- 顯示重啟提示

#### `docker-logs.ps1`
- 查看所有服務日誌
- 支援查看特定服務日誌
- 支援指定顯示行數
- 實時跟蹤日誌

#### `docker-clean.ps1`
- 完全清理系統
- 刪除容器、網路、卷
- 需要確認操作（防止誤刪）

### 4. 文檔

#### `DOCKER_DEPLOYMENT.md`
完整的 Docker 部署指南，包含：
- 系統架構圖
- 快速開始步驟
- 服務說明
- 開發工作流程
- 常用命令
- 故障排除
- 監控與日誌
- 安全最佳實踐
- 生產部署建議
- 效能優化

#### `啟動Docker完整系統.md`
快速啟動指南，包含：
- 前置需求
- 快速啟動步驟
- 服務訪問地址
- 常用命令
- 開發模式說明
- 測試系統步驟
- 故障排除
- 清理與重新開始

#### 更新 `README.md`
- 添加 Docker 快速開始說明
- 更新專案結構（包含前端）
- 添加使用指南
- 更新核心功能說明
- 添加 Docker 管理命令
- 更新開發狀態
- 添加相關文檔連結

## 🏗️ 系統架構

```
┌──────────────────────────────────────────────────────────┐
│                      Docker Network                       │
│                   (ea_trading_network)                    │
│                                                           │
│  ┌─────────────┐                                         │
│  │   Browser   │                                         │
│  └──────┬──────┘                                         │
│         │ http://localhost:3000                          │
│         ▼                                                 │
│  ┌──────────────┐                                        │
│  │   Frontend   │                                        │
│  │   (Nginx)    │                                        │
│  │   Port: 80   │                                        │
│  └──────┬───────┘                                        │
│         │                                                 │
│         │ /api/* → http://backend:8000                   │
│         ▼                                                 │
│  ┌──────────────┐                                        │
│  │   Backend    │                                        │
│  │  (FastAPI)   │                                        │
│  │  Port: 8000  │                                        │
│  └───┬──────┬───┘                                        │
│      │      │                                             │
│      │      └─────────────┐                              │
│      ▼                    ▼                              │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  PostgreSQL  │  │    Redis     │                     │
│  │  Port: 5432  │  │  Port: 6379  │                     │
│  └──────────────┘  └──────────────┘                     │
│                                                           │
└──────────────────────────────────────────────────────────┘

外部訪問:
- Frontend: localhost:3000 → Container:80
- Backend:  localhost:8000 → Container:8000
- Postgres: localhost:5432 → Container:5432
- Redis:    localhost:6379 → Container:6379
```

## 📦 容器說明

### Frontend Container
- **基礎映像**: nginx:alpine
- **構建方式**: 多階段構建
  1. Node.js 18 Alpine - 構建 React 應用
  2. Nginx Alpine - 提供靜態檔案服務
- **端口映射**: 3000:80
- **功能**:
  - 提供 React SPA
  - 代理 /api/* 到後端
  - 處理 React Router 路由
  - 靜態資源快取
  - Gzip 壓縮

### Backend Container
- **基礎映像**: python:3.11-slim
- **端口映射**: 8000:8000
- **功能**:
  - FastAPI 應用
  - JWT 認證
  - 跟單引擎
  - API 端點
- **卷掛載**: 
  - `./backend:/app/backend`
  - `./alembic:/app/alembic`

### PostgreSQL Container
- **映像**: postgres:15-alpine
- **端口映射**: 5432:5432
- **資料持久化**: postgres_data volume
- **健康檢查**: pg_isready

### Redis Container
- **映像**: redis:7-alpine
- **端口映射**: 6379:6379
- **資料持久化**: redis_data volume
- **健康檢查**: redis-cli ping

## 🚀 使用流程

### 1. 首次啟動

```powershell
# Windows 用戶
.\docker-start.ps1

# Linux/Mac 用戶
docker-compose up --build -d
docker-compose exec backend alembic upgrade head
```

### 2. 訪問系統

1. 打開瀏覽器訪問 http://localhost:3000
2. 註冊新帳號
3. 登入系統
4. 配置 API 憑證
5. 設定跟單參數
6. 啟動跟單引擎

### 3. 測試系統

1. 使用右側測試控制台
2. 選擇交易對和方向
3. 輸入數量
4. 觸發 Master 訂單
5. 觀察儀表板變化

### 4. 日常使用

```powershell
# 啟動系統
docker-compose start

# 查看日誌
.\docker-logs.ps1

# 停止系統
docker-compose stop
```

## 🔧 開發模式

### 前端本地開發

```powershell
# 1. 只啟動後端服務
docker-compose up -d postgres redis backend

# 2. 本地運行前端
cd frontend
npm install
npm run dev
```

前端會在 http://localhost:5173 運行，Vite 會自動代理 API 請求。

### 後端本地開發

```powershell
# 1. 啟動資料庫和 Redis
docker-compose up -d postgres redis

# 2. 本地運行後端
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

## 🐛 常見問題

### 問題 1: 端口衝突

**症狀**: 容器啟動失敗，提示端口已被佔用

**解決方案**:
```powershell
# 檢查端口佔用
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 修改 docker-compose.yml 中的端口映射
# 例如: "3001:80" 代替 "3000:80"
```

### 問題 2: 前端無法連接後端

**症狀**: 前端顯示網路錯誤

**解決方案**:
```powershell
# 1. 檢查後端是否運行
docker-compose ps backend

# 2. 檢查網路連接
docker-compose exec frontend ping backend

# 3. 查看 nginx 日誌
docker-compose logs frontend

# 4. 重啟前端
docker-compose restart frontend
```

### 問題 3: 資料庫遷移失敗

**症狀**: 後端啟動失敗，提示資料庫錯誤

**解決方案**:
```powershell
# 1. 檢查 PostgreSQL 狀態
docker-compose ps postgres

# 2. 手動執行遷移
docker-compose exec backend alembic upgrade head

# 3. 如果還是失敗，重置資料庫
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### 問題 4: 容器無法啟動

**症狀**: docker-compose up 失敗

**解決方案**:
```powershell
# 1. 查看詳細日誌
docker-compose logs

# 2. 檢查 .env 檔案
# 確保 ENCRYPTION_KEY 已設定

# 3. 清理並重新構建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 📊 監控與維護

### 查看資源使用

```powershell
# 查看容器資源使用
docker stats

# 查看磁碟使用
docker system df
```

### 備份資料庫

```powershell
# 備份
docker-compose exec postgres pg_dump -U postgres ea_trading > backup.sql

# 還原
docker-compose exec -T postgres psql -U postgres ea_trading < backup.sql
```

### 清理未使用的資源

```powershell
# 清理未使用的映像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理所有未使用的資源
docker system prune -a
```

## 🔐 安全建議

### 生產環境配置

1. **修改預設密碼**
```yaml
environment:
  POSTGRES_PASSWORD: strong-password-here
  JWT_SECRET_KEY: secure-random-key-here
```

2. **禁用 DEBUG 模式**
```yaml
environment:
  APP_ENV: production
  DEBUG: "False"
  LOG_LEVEL: WARNING
```

3. **限制端口暴露**
```yaml
# 只暴露前端端口
ports:
  - "3000:80"
# 移除後端、資料庫、Redis 的端口映射
```

4. **使用 Secrets**
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  encryption_key:
    file: ./secrets/encryption_key.txt
```

5. **添加資源限制**
```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
```

## 🎯 下一步

- ✅ 系統已完全 Docker 化
- ✅ 前後端分離部署
- ✅ 資料持久化配置
- ✅ 管理腳本完成
- ⬜ 添加 CI/CD 流程
- ⬜ 配置監控告警
- ⬜ 實施備份策略
- ⬜ 負載測試與優化
- ⬜ Kubernetes 部署配置

## 📚 相關文檔

- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - 詳細部署指南
- [啟動Docker完整系統.md](./啟動Docker完整系統.md) - 快速啟動
- [README.md](./README.md) - 專案總覽
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 系統架構

## ✨ 總結

Docker 部署已完全配置完成，包括：

1. **前端容器化**: 使用 Nginx 提供 React SPA 服務
2. **後端容器化**: FastAPI 應用與跟單引擎
3. **資料庫**: PostgreSQL 與 Redis
4. **網路配置**: 所有服務在同一網路中通信
5. **管理工具**: PowerShell 腳本簡化操作
6. **完整文檔**: 詳細的使用和故障排除指南

系統現在可以通過一個命令啟動所有服務，非常適合開發、測試和生產部署！
