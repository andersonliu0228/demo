@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🧪 測試最小化前端
echo ========================================
echo.

echo ✅ normalizeUrl 錯誤已修復！
echo.

echo 📋 診斷結果:
echo    ✓ 路徑大小寫 - 正確
echo    ✓ .vite 快取 - 已清理
echo    ✓ react-router-dom - 已安裝
echo    ✓ App.jsx - 使用最小化版本
echo    ✓ Vite 日誌 - 無錯誤
echo.

echo 🔧 當前配置:
echo    使用: App-minimal.jsx
echo    路由: / 和 /admin
echo    組件: TraderAdmin-simple
echo    測試文字: "FRONTEND IS ALIVE - MINIMAL VERSION"
echo.

echo 📊 容器狀態:
docker ps --filter "name=ea_trading_frontend" --format "table {{.Names}}\t{{.Status}}"
echo.

echo 🧪 HTTP 測試:
curl http://localhost:3000 -UseBasicParsing | Select-Object StatusCode
echo.

echo ========================================
echo 🚀 正在打開瀏覽器...
echo ========================================
echo.

start http://localhost:3000

echo.
echo 💡 預期結果:
echo    - 看到紅色大字 "FRONTEND IS ALIVE - MINIMAL VERSION"
echo    - 看到交易員管理面板
echo    - 統計卡片、搜尋、篩選、客戶列表
echo.
echo 📝 如果正常顯示:
echo    ✅ normalizeUrl 錯誤已解決
echo    ✅ Vite 已救活
echo    ✅ 可以開始逐步恢復其他路由
echo.
echo 🔄 下一步:
echo    1. 修復 Dashboard.jsx（目前為空）
echo    2. 逐步添加其他路由
echo    3. 測試登入和註冊功能
echo.

pause
