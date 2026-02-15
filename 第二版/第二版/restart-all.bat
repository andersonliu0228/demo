@echo off
REM EA Trading System - 完整重啟腳本

echo ========================================
echo   EA Trading System - 完整重啟
echo ========================================
echo.

REM 1. 停止所有容器
echo [1/5] 停止所有容器...
docker compose stop
if %ERRORLEVEL% EQU 0 (
    echo ✅ 容器已停止
) else (
    echo ⚠️  停止容器時出現警告
)
echo.

REM 2. 移除容器
echo [2/5] 移除容器...
docker compose down
if %ERRORLEVEL% EQU 0 (
    echo ✅ 容器已移除
) else (
    echo ⚠️  移除容器時出現警告
)
echo.

REM 3. 清理未使用的資源
echo [3/5] 清理未使用的 Docker 資源...
docker system prune -f
echo ✅ 清理完成
echo.

REM 4. 重新啟動所有服務
echo [4/5] 啟動所有服務...
docker compose up -d
if %ERRORLEVEL% EQU 0 (
    echo ✅ 服務啟動成功
) else (
    echo ❌ 服務啟動失敗
    exit /b 1
)
echo.

REM 5. 等待服務就緒
echo [5/5] 等待服務就緒...
echo    等待 30 秒讓服務完全啟動...
timeout /t 30 /nobreak >nul
echo.

REM 檢查容器狀態
echo 📊 容器狀態:
docker ps
echo.

REM 完成
echo ========================================
echo   重啟完成！
echo ========================================
echo.
echo 🌐 訪問地址:
echo    前端: http://localhost:5173
echo    後端: http://localhost:8000
echo    API 文檔: http://localhost:8000/docs
echo.
echo 📋 下一步:
echo    1. 訪問前端: http://localhost:5173
echo    2. 登入測試帳號:
echo       用戶名: testuser
echo       密碼: testpass123
echo    3. 檢查 Navbar 是否正常顯示
echo.
echo 🔧 管理命令:
echo    查看日誌: docker compose logs -f
echo    停止服務: docker compose stop
echo    查看狀態: docker ps
echo.

pause
