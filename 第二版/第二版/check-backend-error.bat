@echo off
chcp 65001 >nul
echo ========================================
echo   檢查後端錯誤
echo ========================================
echo.

echo [1] 檢查後端容器狀態...
docker ps --filter "name=backend"
echo.

echo [2] 檢查後端日誌（最後 100 行）...
echo ----------------------------------------
docker logs --tail=100 ea_trading_backend
echo ----------------------------------------
echo.

echo [3] 測試後端健康檢查...
curl -s http://localhost:8000/health
echo.
echo.

echo [4] 測試登入 API...
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=testuser&password=testpass123"
echo.
echo.

pause
