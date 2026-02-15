@echo off
chcp 65001 >nul
echo ========================================
echo   修復 Dashboard.jsx Export 錯誤
echo ========================================
echo.

echo ✅ 已修復問題：
echo   - Dashboard.jsx 文件被截斷
echo   - 重新創建完整的 Dashboard.jsx
echo   - 確保 export default 正確
echo.

echo [1] 檢查文件是否存在...
if exist "frontend\src\components\Dashboard.jsx" (
    echo ✅ Dashboard.jsx 存在
) else (
    echo ❌ Dashboard.jsx 不存在
    pause
    exit /b 1
)
echo.

echo [2] 重啟前端容器以應用修復...
docker-compose restart frontend
echo.

echo [3] 等待前端啟動（20秒）...
timeout /t 20 /nobreak
echo.

echo [4] 檢查前端日誌...
docker logs --tail=20 ea_trading_frontend
echo.

echo ========================================
echo   修復完成！
echo ========================================
echo.
echo 請在瀏覽器中測試：
echo   1. 訪問 http://localhost:3000
echo   2. 按 F12 查看 Console
echo   3. 應該不再有 "does not provide an export named 'default'" 錯誤
echo   4. 應該能看到登入頁面
echo.
pause
