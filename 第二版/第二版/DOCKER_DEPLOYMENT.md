# 🐳 EA Trading System - Docker 部署完整指南

## 📋 系統架構

```
┌──────────────────────────────────────────────────────────┐
│                      Docker Network                       │
│                                                           │
│  ┌─────────────┐         ┌──────────────┐               │
│  │   Browser   │────────▶│   Frontend   │               │
│  │             │  :3000  │   (Nginx)    │               │
│  └─────────────┘         └──────┬───────┘               │
│                                  │                        │
│                                  │ /api/* proxy          │
│                                  ▼                        │
│                          ┌──────────────┐                │
│                          │   Backend    │                │
│                          │  (FastAPI)   │                │
│                          └───┬──────┬───┘                │
│                              │      │                     │
│                    ┌─────────┘      └─────────┐          │
│                    ▼                           ▼          │
│            ┌──────────────┐          ┌──────────────┐    │
│            │  PostgreSQL  │          │    Redis     │    │
│            │   :5432      │          │    :6379     │    │
│            └──────────────┘          └──────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 步驟 1: 準備環境變數

確保 `.env` 檔案已設定：

```bash
# 生成加密金鑰
python scripts/generate_encryption_key.py

# 或在 PowerShell 中直接設定
$env:ENCRYPTION_KEY="your-generated-key-here"
```

### 步驟 2: 啟動所有服務

```powershell
# 構建並啟動所有容器
docker-compose up --build -d

# 等待服務啟動（約 10-15 秒）
Start-Sleep -Seconds 15

# 檢查服務狀態
docker-compose ps
```

### 步驟 3: 初始化資料庫

```powershell
# 執行資料庫遷移
docker-compose exec backend alembic upgrade head
```

### 步驟 4: 訪問系統

- **前端應用**: http://localhost:3000
- **後端 API 文檔**: http://localhost:8000/docs
- **後端 ReDoc**: http://localhost:8000/redoc

## 📦 服務說明

### Frontend (Port 3000)
- **技術**: React 18 + Vite + Tailwind CSS
- **容器**: Nginx Alpine
- **功能**: 
  - 用戶登入/註冊
  - 儀表板顯示
  - 跟單設定管理
  - 交易歷史查看
  - 測試控制台

### Backend (Port 8000)
- **技術**: FastAPI + SQLAlchemy Async + asyncpg
- **容器**: Python 3.11 Slim
- **功能**:
  - RESTful API
  - JWT 認證
  - 加密服務
  - 交易所整合 (CCXT)
  - 跟單引擎
  - 快取服務

### PostgreSQL (Port 5432)
- **版本**: PostgreSQL 15 Alpine
- **資料庫**: ea_trading
- **持久化**: Docker Volume

### Redis (Port 6379)
- **版本**: Redis 7 Alpine
- **用途**: 快取、會話管理
- **持久化**: Docker Volume

## 🔧 開發工作流程

### 本地開發 + Docker 後端

如果你想在本地開發前端，但使用 Docker 運行後端：

```powershell
# 1. 啟動後端服務（不包含前端）
docker-compose up -d postgres redis backend

# 2. 在本地運行前端
cd frontend
npm install
npm run dev
```

前端會在 http://localhost:5173 運行，並通過 Vite 代理連接到 http://localhost:8000

### 熱重載開發

後端代碼已經通過 volume 掛載，修改後需要重啟：

```powershell
# 重啟後端服務
docker-compose restart backend

# 查看日誌
docker-compose logs -f backend
```

### 前端代碼更新

前端使用多階段構建，修改代碼後需要重新構建：

```powershell
# 重新構建前端
docker-compose build frontend

# 重啟前端服務
docker-compose up -d frontend
```

## 🛠️ 常用命令

### 服務管理

```powershell
# 查看所有服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止所有服務
docker-compose stop

# 啟動服務
docker-compose start

# 重啟服務
docker-compose restart

# 停止並移除容器
docker-compose down

# 停止並移除容器、網路、卷（清空資料庫）
docker-compose down -v
```

### 資料庫操作

```powershell
# 執行遷移
docker-compose exec backend alembic upgrade head

# 回滾遷移
docker-compose exec backend alembic downgrade -1

# 查看遷移歷史
docker-compose exec backend alembic history

# 進入 PostgreSQL
docker-compose exec postgres psql -U postgres -d ea_trading

# 備份資料庫
docker-compose exec postgres pg_dump -U postgres ea_trading > backup.sql

# 還原資料庫
docker-compose exec -T postgres psql -U postgres ea_trading < backup.sql
```

### 容器操作

```powershell
# 進入後端容器
docker-compose exec backend sh

# 進入前端容器
docker-compose exec frontend sh

# 執行 Python 腳本
docker-compose exec backend python scripts/init_db.py

# 執行測試
docker-compose exec backend pytest
```

### 清理與重建

```powershell
# 完全清理並重新開始
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## 🧪 測試系統

### 1. 健康檢查

```powershell
# 檢查後端健康狀態
curl http://localhost:8000/health

# 檢查前端
curl http://localhost:3000
```

### 2. API 測試

訪問 http://localhost:8000/docs 使用 Swagger UI 測試 API

### 3. 完整流程測試

```powershell
# 使用 PowerShell 腳本測試
.\test_auth_system.ps1
.\test_dashboard.ps1
.\test_follower_engine.ps1
```

## 🐛 故障排除

### 問題 1: 容器無法啟動

```powershell
# 查看詳細日誌
docker-compose logs backend
docker-compose logs frontend

# 檢查容器狀態
docker-compose ps

# 重新構建
docker-compose build --no-cache
docker-compose up -d
```

### 問題 2: 資料庫連接失敗

```powershell
# 檢查 PostgreSQL 健康狀態
docker-compose ps postgres

# 查看 PostgreSQL 日誌
docker-compose logs postgres

# 重啟 PostgreSQL
docker-compose restart postgres

# 等待健康檢查通過
Start-Sleep -Seconds 10

# 重新執行遷移
docker-compose exec backend alembic upgrade head
```

### 問題 3: 前端無法連接後端

**症狀**: 前端顯示網路錯誤或 API 請求失敗

**解決方案**:

1. 檢查後端是否運行:
```powershell
docker-compose ps backend
curl http://localhost:8000/docs
```

2. 檢查 nginx 配置:
```powershell
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

3. 檢查網路連接:
```powershell
docker-compose exec frontend ping backend
```

4. 重啟前端:
```powershell
docker-compose restart frontend
```

### 問題 4: 端口衝突

**症狀**: 容器啟動失敗，提示端口已被佔用

**解決方案**:

```powershell
# 檢查端口佔用
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# 修改 docker-compose.yml 中的端口映射
# 例如: "3001:80" 代替 "3000:80"
```

### 問題 5: 資料持久化問題

**症狀**: 重啟後資料消失

**解決方案**:

```powershell
# 檢查 volume
docker volume ls

# 查看 volume 詳情
docker volume inspect ea-trading-backend_postgres_data

# 確保使用 docker-compose down 而不是 docker-compose down -v
docker-compose down
docker-compose up -d
```

## 📊 監控與日誌

### 實時監控

```powershell
# 查看容器資源使用
docker stats

# 持續查看日誌
docker-compose logs -f --tail=100

# 只看錯誤日誌
docker-compose logs | Select-String "ERROR"
```

### 日誌管理

```powershell
# 導出日誌
docker-compose logs > logs.txt

# 清理日誌（重啟容器）
docker-compose restart
```

## 🔐 安全最佳實踐

### 1. 環境變數管理

```bash
# .env 檔案範例
ENCRYPTION_KEY=your-secure-base64-key
JWT_SECRET_KEY=your-secure-jwt-secret
POSTGRES_PASSWORD=strong-password-here
```

### 2. 生產環境配置

修改 `docker-compose.yml`:

```yaml
environment:
  APP_ENV: production
  DEBUG: "False"
  LOG_LEVEL: WARNING
```

### 3. 網路隔離

```yaml
# 只暴露必要的端口
ports:
  - "3000:80"  # 只暴露前端
# 移除後端、資料庫、Redis 的端口映射
```

### 4. 使用 Secrets

```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  encryption_key:
    file: ./secrets/encryption_key.txt
```

## 🚀 生產部署建議

### 1. 使用外部資料庫

```yaml
environment:
  DATABASE_URL: postgresql+asyncpg://user:pass@external-db:5432/ea_trading
  REDIS_URL: redis://external-redis:6379/0
```

### 2. 添加反向代理

使用 Nginx 或 Traefik 作為入口點：

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
```

### 3. 配置 HTTPS

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
    }
}
```

### 4. 健康檢查與自動重啟

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
restart: always
```

### 5. 資源限制

```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## 📈 效能優化

### 1. 使用 Redis 快取

已在系統中實現，確保 Redis 正常運行

### 2. 資料庫連接池

在 `backend/app/database.py` 中已配置：

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
)
```

### 3. Nginx 快取

在 `frontend/nginx.conf` 中已配置靜態資源快取

### 4. 壓縮

Nginx 已啟用 Gzip 壓縮

## 🎯 下一步

1. ✅ 系統已完全 Docker 化
2. ✅ 前後端分離部署
3. ✅ 資料持久化配置
4. ⬜ 添加 CI/CD 流程
5. ⬜ 配置監控告警
6. ⬜ 實施備份策略
7. ⬜ 負載測試與優化

## 📚 相關文檔

- [啟動Docker完整系統.md](./啟動Docker完整系統.md) - 快速啟動指南
- [啟動完整系統.md](./啟動完整系統.md) - 本地開發指南
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 系統架構說明
- [README.md](./README.md) - 專案總覽

## 💡 提示

- 首次啟動需要等待約 15-20 秒讓所有服務完全啟動
- 使用 `docker-compose logs -f` 可以實時查看所有服務的日誌
- 開發時建議使用本地前端 + Docker 後端的模式以獲得更好的開發體驗
- 生產環境務必修改所有預設密碼和金鑰
