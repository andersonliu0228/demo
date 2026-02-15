@echo off
chcp 65001 >nul
echo ========================================
echo   修復後端 500 錯誤
echo ========================================
echo.

echo [步驟 1] 停止所有容器...
docker-compose down
echo.

echo [步驟 2] 清理舊的 volume（可選）...
echo 注意：這會刪除所有數據！
choice /C YN /M "是否清理 volume？"
if errorlevel 2 goto skip_volume
docker volume rm ea-trading_postgres_data ea-trading_redis_data 2>nul
echo ✅ Volume 已清理
:skip_volume
echo.

echo [步驟 3] 重新構建後端容器...
docker-compose build backend
echo.

echo [步驟 4] 啟動數據庫服務...
docker-compose up -d postgres redis
echo 等待數據庫啟動（15秒）...
timeout /t 15 /nobreak >nul
echo.

echo [步驟 5] 檢查數據庫連接...
docker exec ea_trading_postgres pg_isready -U postgres
echo.

echo [步驟 6] 啟動後端服務...
docker-compose up -d backend
echo 等待後端啟動（20秒）...
timeout /t 20 /nobreak >nul
echo.

echo [步驟 7] 檢查後端日誌...
echo ----------------------------------------
docker logs --tail=50 ea_trading_backend
echo ----------------------------------------
echo.

echo [步驟 8] 測試健康檢查...
curl -s http://localhost:8000/health
echo.
echo.

echo [步驟 9] 初始化測試數據...
docker exec ea_trading_backend python scripts/init_test_data.py
echo.

echo [步驟 10] 測試登入 API...
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=testuser&password=testpass123"
echo.
echo.

echo [步驟 11] 啟動前端...
docker-compose up -d frontend
echo.

echo ========================================
echo   修復完成！
echo ========================================
echo.
echo ✅ 已完成的修復：
echo   1. 重新構建後端容器
echo   2. 執行數據庫遷移（alembic upgrade head）
echo   3. 初始化測試數據
echo   4. 驗證配置（JWT_SECRET_KEY, ENCRYPTION_KEY）
echo   5. 強化錯誤處理和日誌
echo   6. 驗證 bcrypt 密碼加密
echo.
echo 📋 測試步驟：
echo   1. 訪問 http://localhost:3000
echo   2. 登入：testuser / testpass123
echo   3. 如果仍有問題，查看：
echo      - docker logs ea_trading_backend
echo      - 瀏覽器 Console（F12）
echo.
pause
