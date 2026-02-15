@echo off
echo ========================================
echo   重啟前端容器以應用白屏修復
echo ========================================
echo.

echo [1] 重啟前端容器...
docker-compose restart frontend
timeout /t 3 /nobreak >nul
echo.

echo [2] 檢查前端容器狀態...
docker ps --filter "name=frontend"
echo.

echo [3] 查看前端日誌（最後 20 行）...
docker-compose logs --tail=20 frontend
echo.

echo ========================================
echo   修復完成！
echo ========================================
echo.
echo 已修復的問題：
echo   1. 路由配置：/ 重定向到 /login
echo   2. Navbar 移到 App.jsx 層級
echo   3. 用戶資訊使用安全語法
echo   4. 登出邏輯使用 replace: true
echo.
echo 請在瀏覽器中測試：
echo   1. 訪問 http://localhost:3000
echo   2. 應該看到登入頁面（不是白屏）
echo   3. 登入後測試登出功能
echo.
pause
