# 🚀 EA Trading System - 快速參考

## 一鍵啟動

```powershell
# 啟動所有服務
.\docker-start.ps1

# 測試前端開發模式
.\test-docker-frontend.ps1
```

## 訪問地址

| 服務 | 地址 | 說明 |
|------|------|------|
| 前端應用 | http://localhost:3000 | React 儀表板 |
| 後端 API | http://localhost:8000 | FastAPI 服務 |
| API 文檔 | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | API 文檔 |

## 常用命令

### 服務管理
```powershell
# 啟動
docker-compose up -d

# 停止
docker-compose stop

# 重啟
docker-compose restart

# 查看狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 前端開發
```powershell
# 重啟前端（熱更新模式）
.\docker-restart-frontend.ps1

# 查看前端日誌
docker-compose logs -f frontend

# 進入前端容器
docker-compose exec frontend sh
```

### 後端開發
```powershell
# 查看後端日誌
docker-compose logs -f backend

# 執行資料庫遷移
docker-compose exec backend alembic upgrade head

# 進入後端容器
docker-compose exec backend sh
```

### 資料庫操作
```powershell
# 進入 PostgreSQL
docker-compose exec postgres psql -U postgres -d ea_trading

# 備份資料庫
docker-compose exec postgres pg_dump -U postgres ea_trading > backup.sql

# 還原資料庫
docker-compose exec -T postgres psql -U postgres ea_trading < backup.sql
```

## 開發工作流程

### 1. 啟動系統
```powershell
docker-compose up -d
```

### 2. 開發前端
- 修改 `frontend/src/` 下的檔案
- 保存後自動熱更新（1-2 秒）
- 瀏覽器自動刷新

### 3. 開發後端
- 修改 `backend/app/` 下的檔案
- 重啟後端：`docker-compose restart backend`

### 4. 測試 API
- 訪問 http://localhost:8000/docs
- 使用 Swagger UI 測試端點

### 5. 查看日誌
```powershell
# 所有服務
docker-compose logs -f

# 特定服務
docker-compose logs -f frontend
docker-compose logs -f backend
```

## 故障排除

### 前端無法訪問
```powershell
# 檢查容器狀態
docker-compose ps frontend

# 查看日誌
docker-compose logs frontend

# 重啟前端
docker-compose restart frontend
```

### 後端 API 錯誤
```powershell
# 檢查容器狀態
docker-compose ps backend

# 查看日誌
docker-compose logs backend

# 重啟後端
docker-compose restart backend
```

### 資料庫連接失敗
```powershell
# 檢查 PostgreSQL
docker-compose ps postgres

# 查看日誌
docker-compose logs postgres

# 重啟資料庫
docker-compose restart postgres

# 重新執行遷移
docker-compose exec backend alembic upgrade head
```

### 完全重置
```powershell
# 停止並刪除所有容器和資料
docker-compose down -v

# 重新啟動
docker-compose up -d --build

# 執行遷移
docker-compose exec backend alembic upgrade head
```

## API 測試流程

### 1. 註冊用戶
```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"username":"testuser","password":"testpass123","email":"test@example.com"}'
```

### 2. 登入
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=testuser&password=testpass123"
```

### 3. 獲取儀表板數據
```powershell
curl http://localhost:8000/api/v1/dashboard/summary `
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 前端功能測試

### 1. 登入系統
- 訪問 http://localhost:3000
- 使用註冊的帳號登入

### 2. 檢查 API 連接
- 查看右上角狀態指示器
- 應顯示「後端連線：成功 ✅」

### 3. 配置跟單
- 在儀表板中設定跟單比例
- 啟用跟單功能

### 4. 測試跟單
- 使用右側測試控制台
- 觸發 Master 訂單
- 觀察跟單效果

## 熱更新測試

### 測試前端熱更新
1. 修改 `frontend/src/App.jsx`
2. 改變任何文字或樣式
3. 保存檔案
4. 瀏覽器應在 1-2 秒內自動更新

### 測試後端更新
1. 修改 `backend/app/routes/dashboard_routes.py`
2. 保存檔案
3. 重啟後端：`docker-compose restart backend`
4. 測試 API 端點

## 效能監控

```powershell
# 查看容器資源使用
docker stats

# 查看磁碟使用
docker system df

# 清理未使用的資源
docker system prune -a
```

## 環境變數

### 必需設定
```bash
ENCRYPTION_KEY=your-base64-encoded-key
JWT_SECRET_KEY=your-secret-key
```

### 生成加密金鑰
```powershell
python scripts/generate_encryption_key.py
```

## 快速鍵

| 操作 | 命令 |
|------|------|
| 啟動 | `.\docker-start.ps1` |
| 測試 | `.\test-docker-frontend.ps1` |
| 重啟前端 | `.\docker-restart-frontend.ps1` |
| 查看日誌 | `.\docker-logs.ps1` |
| 停止 | `.\docker-stop.ps1` |
| 清理 | `.\docker-clean.ps1` |

## 相關文檔

| 文檔 | 說明 |
|------|------|
| [README.md](./README.md) | 專案總覽 |
| [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) | Docker 部署指南 |
| [前端Docker開發模式測試指南.md](./前端Docker開發模式測試指南.md) | 開發模式指南 |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系統架構 |

## 技術支援

遇到問題？
1. 查看相關文檔
2. 檢查日誌：`docker-compose logs`
3. 重啟服務：`docker-compose restart`
4. 完全重置：`docker-compose down -v && docker-compose up -d`

---

**提示**: 將此文件加入書籤，方便快速查閱！
