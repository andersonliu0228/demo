@echo off
chcp 65001 >nul
echo ========================================
echo   測試簡化版 Dashboard
echo ========================================
echo.

echo 已創建簡化版 Dashboard 用於測試
echo App.jsx 已修改為使用 Dashboard-simple.jsx
echo.

echo [1] 重啟前端容器...
docker-compose restart frontend
echo.

echo [2] 等待啟動（15秒）...
timeout /t 15 /nobreak
echo.

echo [3] 檢查前端日誌...
docker logs --tail=20 ea_trading_frontend
echo.

echo ========================================
echo   測試步驟
echo ========================================
echo.
echo 1. 訪問 http://localhost:3000
echo 2. 登入：testuser / testpass123
echo 3. 如果看到 "Dashboard 測試" 頁面，說明：
echo    - 路由正常
echo    - 組件導入正常
echo    - 問題在於完整版 Dashboard 的某個依賴
echo.
echo 4. 如果仍然白屏，說明：
echo    - 問題在於 App.jsx 或路由配置
echo    - 或者其他基礎組件有問題
echo.
pause
