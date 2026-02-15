# 前端 Docker 開發模式測試指南

## ✨ 新功能

### 1. 開發模式 Docker 配置
- 支援熱更新（Hot Reload）
- Volume 掛載，本地修改即時生效
- API 連接狀態指示器

### 2. 檔案說明

#### `frontend/Dockerfile.dev`
開發環境專用 Dockerfile：
- 使用 Node.js 18 Alpine
- 安裝依賴後啟動 Vite 開發伺服器
- 監聽 0.0.0.0:3000

#### `docker-compose.yml` 更新
前端服務配置：
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev  # 使用開發版 Dockerfile
  ports:
    - "3000:3000"  # Vite 開發伺服器端口
  volumes:
    - ./frontend:/app  # 掛載整個前端目錄
    - /app/node_modules  # 排除 node_modules
  environment:
    - VITE_API_BASE_URL=  # 使用相對路徑
```

#### `frontend/vite.config.js` 更新
```javascript
server: {
  host: '0.0.0.0',  # 允許外部訪問
  port: 3000,
  watch: {
    usePolling: true,  # Docker 環境需要輪詢
  },
  proxy: {
    '/api': {
      target: 'http://backend:8000',  # 代理到後端容器
      changeOrigin: true,
    },
  },
}
```

#### `frontend/src/App.jsx` 更新
新增 API 連接測試：
- 自動測試 `/api/v1/dashboard/summary` 端點
- 顯示連接狀態指示器（右上角）
- 三種狀態：連接中、成功、失敗

## 🚀 啟動步驟

### 方法 1: 使用腳本（推薦）

```powershell
# 重啟前端容器
.\docker-restart-frontend.ps1
```

### 方法 2: 手動命令

```powershell
# 1. 停止並移除前端容器
docker-compose rm -sf frontend

# 2. 重新構建並啟動
docker-compose up -d --build frontend

# 3. 查看日誌
docker-compose logs -f frontend
```

### 方法 3: 完整重啟

```powershell
# 重啟所有服務
docker-compose down
docker-compose up -d --build
```

## 🧪 測試步驟

### 1. 檢查容器狀態

```powershell
docker-compose ps
```

應該看到：
```
NAME                  STATUS        PORTS
ea_trading_frontend   Up X seconds  0.0.0.0:3000->3000/tcp
ea_trading_backend    Up X minutes  0.0.0.0:8000->8000/tcp
ea_trading_postgres   Up X minutes  0.0.0.0:5432->5432/tcp
ea_trading_redis      Up X minutes  0.0.0.0:6379->6379/tcp
```

### 2. 查看前端日誌

```powershell
docker-compose logs -f frontend
```

應該看到：
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: http://172.x.x.x:3000/
```

### 3. 訪問前端

打開瀏覽器訪問: http://localhost:3000

### 4. 檢查 API 連接狀態

在頁面右上角應該看到：
- 🟡 **連接中...** （初始狀態）
- 🟢 **後端連線：成功 ✅** （連接成功）
- 🔴 **後端連線：失敗 ❌** （連接失敗）

### 5. 測試熱更新

1. 修改 `frontend/src/App.jsx` 中的任何文字
2. 保存檔案
3. 瀏覽器應該自動刷新並顯示更改

例如，修改 API 狀態指示器的文字：
```javascript
<span className="text-sm font-medium">後端連線：成功 🎉</span>
```

保存後，頁面應該立即更新。

## 🔍 故障排除

### 問題 1: 前端無法啟動

**症狀**: 容器啟動失敗

**解決方案**:
```powershell
# 查看詳細日誌
docker-compose logs frontend

# 檢查是否端口衝突
netstat -ano | findstr :3000

# 重新構建
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### 問題 2: API 連接失敗

**症狀**: 顯示「後端連線：失敗」

**解決方案**:
```powershell
# 1. 檢查後端是否運行
docker-compose ps backend

# 2. 測試後端 API
curl http://localhost:8000/health

# 3. 檢查網路連接
docker-compose exec frontend ping backend

# 4. 查看前端網路請求
# 在瀏覽器開發者工具 > Network 標籤查看請求
```

### 問題 3: 熱更新不工作

**症狀**: 修改代碼後頁面不自動刷新

**解決方案**:
```powershell
# 1. 確認 volume 掛載正確
docker-compose exec frontend ls -la /app

# 2. 檢查 Vite 配置
docker-compose exec frontend cat /app/vite.config.js

# 3. 重啟容器
docker-compose restart frontend
```

### 問題 4: node_modules 問題

**症狀**: 缺少依賴或版本衝突

**解決方案**:
```powershell
# 重新安裝依賴
docker-compose exec frontend npm install

# 或重新構建容器
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## 📊 API 連接測試詳情

### 測試邏輯

```javascript
// 在 App.jsx 中
useEffect(() => {
  const testApiConnection = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/dashboard/summary', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      
      if (response.ok) {
        // 200 OK - 連接成功
        setApiStatus({ connected: true, error: null });
      } else if (response.status === 401) {
        // 401 Unauthorized - 後端正常，但需要登入
        setApiStatus({ connected: true, error: '需要登入' });
      } else {
        // 其他錯誤
        setApiStatus({ connected: false, error: `HTTP ${response.status}` });
      }
    } catch (error) {
      // 網路錯誤或後端未運行
      setApiStatus({ connected: false, error: error.message });
    }
  };

  testApiConnection();
}, []);
```

### 預期結果

| 情況 | 狀態 | 顯示 |
|------|------|------|
| 後端運行 + 已登入 | ✅ 成功 | 後端連線：成功 |
| 後端運行 + 未登入 | ✅ 成功 | 後端連線：成功 |
| 後端未運行 | ❌ 失敗 | 後端連線：失敗 |
| 網路錯誤 | ❌ 失敗 | 後端連線：失敗 |

## 🎯 開發工作流程

### 日常開發

1. **啟動系統**
```powershell
docker-compose up -d
```

2. **開始開發**
- 修改 `frontend/src/` 下的任何檔案
- 保存後自動熱更新
- 在瀏覽器中查看變化

3. **查看日誌**
```powershell
# 前端日誌
docker-compose logs -f frontend

# 後端日誌
docker-compose logs -f backend
```

4. **停止系統**
```powershell
docker-compose stop
```

### 添加新依賴

```powershell
# 1. 進入容器
docker-compose exec frontend sh

# 2. 安裝依賴
npm install <package-name>

# 3. 退出容器
exit

# 4. 更新 package.json 後重新構建
docker-compose build frontend
docker-compose up -d frontend
```

### 調試技巧

1. **瀏覽器開發者工具**
   - F12 打開開發者工具
   - Console 標籤查看日誌
   - Network 標籤查看 API 請求

2. **容器內調試**
```powershell
# 進入容器
docker-compose exec frontend sh

# 查看檔案
ls -la /app

# 查看環境變數
env | grep VITE

# 查看進程
ps aux
```

3. **網路調試**
```powershell
# 測試後端連接
docker-compose exec frontend wget -O- http://backend:8000/health

# 查看網路配置
docker-compose exec frontend ifconfig
```

## 📝 下一步

- [ ] 完成登入功能測試
- [ ] 測試儀表板 API 整合
- [ ] 測試跟單引擎控制
- [ ] 測試交易歷史顯示
- [ ] 添加更多 API 端點測試

## 🔗 相關文檔

- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - Docker 部署指南
- [前端實作總結.md](./前端實作總結.md) - 前端開發說明
- [README.md](./README.md) - 專案總覽

## ✨ 總結

現在前端已經配置為開發模式：
- ✅ 支援熱更新
- ✅ Volume 掛載
- ✅ API 連接測試
- ✅ 狀態指示器
- ✅ 完整的開發工作流程

修改代碼後會自動更新，無需重啟容器！
