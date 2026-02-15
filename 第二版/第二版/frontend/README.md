# EA Trading Frontend

React + Vite 前端專案，用於 EA 自動跟單系統。

## 功能特色

- ✅ 儀表板總覽（總持倉、跟單設定、引擎狀態）
- ✅ 實時數據更新（每 5 秒自動刷新）
- ✅ Master 倉位追蹤
- ✅ 交易歷史記錄
- ✅ 測試控制台（模擬 Master 下單）
- ✅ JWT 認證
- ✅ 響應式設計

## 技術棧

- **React 18** - UI 框架
- **Vite** - 構建工具
- **Tailwind CSS** - 樣式框架
- **Axios** - HTTP 客戶端
- **Lucide React** - 圖標庫

## 快速開始

### 1. 安裝依賴

```bash
cd frontend
npm install
```

### 2. 啟動開發伺服器

```bash
npm run dev
```

前端將運行在 http://localhost:5173

### 3. 構建生產版本

```bash
npm run build
```

## 專案結構

```
frontend/
├── src/
│   ├── components/          # React 組件
│   │   ├── Dashboard.jsx    # 主儀表板
│   │   ├── StatusBar.jsx    # 頂部狀態欄
│   │   ├── FollowSettings.jsx  # 跟單設定
│   │   ├── TradeHistory.jsx    # 交易歷史
│   │   ├── TestConsole.jsx     # 測試控制台
│   │   └── Login.jsx           # 登入頁面
│   ├── hooks/               # 自定義 Hooks
│   │   └── useDashboard.js  # 儀表板數據 Hook
│   ├── lib/                 # 工具庫
│   │   └── api.js           # API 客戶端
│   ├── App.jsx              # 主應用組件
│   ├── main.jsx             # 入口文件
│   └── index.css            # 全局樣式
├── index.html               # HTML 模板
├── vite.config.js           # Vite 配置
├── tailwind.config.js       # Tailwind 配置
└── package.json             # 依賴配置
```

## API 端點

前端連接到後端 API：`http://localhost:8000`

主要端點：
- `GET /api/v1/dashboard/summary` - 獲取儀表板摘要
- `POST /api/v1/auth/login` - 用戶登入
- `POST /api/v1/test/trigger-master-order` - 觸發 Master 訂單（測試用）

## 環境變數

創建 `.env` 文件：

```
VITE_API_URL=http://localhost:8000
```

## 測試帳號

- 用戶名：`testuser`
- 密碼：`testpass123`

## 開發說明

### 自動刷新

儀表板每 5 秒自動刷新一次數據，可以在 `useDashboard` Hook 中調整刷新間隔。

### 測試控制台

點擊右下角的閃電圖標可以開啟測試控制台，用於模擬 Master 下單：

1. 設定交易參數（交易對、倉位大小、價格）
2. 點擊「模擬 Master 下單」
3. 系統會立即更新 Master 倉位
4. 3 秒後跟單引擎會執行對帳並更新跟隨者倉位

### API Key 遮罩

跟單設定中的 API Key 預設為遮罩狀態，點擊眼睛圖標可以切換顯示/隱藏。

## 常見問題

### Q: 為什麼看不到數據？

A: 確認：
1. 後端服務是否運行（http://localhost:8000）
2. 是否已登入（檢查 localStorage 中的 token）
3. 瀏覽器控制台是否有錯誤訊息

### Q: CORS 錯誤怎麼辦？

A: 確認後端 CORS 設定包含 `http://localhost:5173`

### Q: 如何修改刷新間隔？

A: 編輯 `src/components/Dashboard.jsx`：

```javascript
const { dashboard, loading, error, refresh } = useDashboard(5000); // 5000ms = 5秒
```

## 部署

### 構建

```bash
npm run build
```

構建產物在 `dist/` 目錄。

### 預覽

```bash
npm run preview
```

## License

MIT
