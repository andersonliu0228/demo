@echo off
chcp 65001 >nul
echo ========================================
echo   前端問題診斷工具
echo ========================================
echo.

echo [1] 檢查 Docker 容器狀態...
docker ps --filter "name=frontend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo [2] 檢查前端容器日誌（最後 50 行）...
echo ----------------------------------------
docker logs --tail=50 ea_trading_frontend
echo ----------------------------------------
echo.

echo [3] 測試前端是否可訪問...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:3000
echo.

echo [4] 測試後端 API 是否可訪問...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:8000/health
echo.

echo [5] 檢查前端文件是否正確掛載...
docker exec ea_trading_frontend ls -la /app/src/
echo.

echo [6] 檢查 App.jsx 是否存在...
docker exec ea_trading_frontend cat /app/src/App.jsx | findstr "AppContent"
echo.

echo ========================================
echo   診斷完成
echo ========================================
echo.
echo 請提供以下資訊：
echo 1. 瀏覽器訪問 http://localhost:3000 看到什麼？
echo 2. 按 F12 打開控制台，Console 標籤有什麼錯誤？
echo 3. Network 標籤中，哪些請求失敗了？
echo.
pause
