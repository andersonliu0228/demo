@echo off
chcp 65001 >nul
echo ========================================
echo   修復並測試前端白屏問題
echo ========================================
echo.

echo [步驟 1] 檢查當前容器狀態...
docker ps --filter "name=ea_trading" --format "table {{.Names}}\t{{.Status}}"
echo.

echo [步驟 2] 重啟前端容器...
echo 正在重啟...
docker-compose restart frontend
timeout /t 5 /nobreak >nul
echo ✅ 前端容器已重啟
echo.

echo [步驟 3] 等待前端啟動（15秒）...
timeout /t 15 /nobreak
echo.

echo [步驟 4] 檢查前端日誌...
echo ----------------------------------------
docker logs --tail=30 ea_trading_frontend
echo ----------------------------------------
echo.

echo [步驟 5] 測試前端訪問...
curl -s -o nul -w "前端狀態碼: %%{http_code}\n" http://localhost:3000
echo.

echo [步驟 6] 測試後端 API...
curl -s -o nul -w "後端狀態碼: %%{http_code}\n" http://localhost:8000/health
echo.

echo ========================================
echo   修復說明
echo ========================================
echo.
echo ✅ 已修復的問題：
echo   1. 用戶狀態現在使用 useState 管理，響應式更新
echo   2. 監聽路由變化自動重新載入用戶資訊
echo   3. 監聽 localStorage 變化（跨標籤頁同步）
echo   4. Navbar 只在已登入且非認證頁面時顯示
echo   5. 用戶名使用預設值防止 undefined
echo   6. 添加詳細的 console.log 便於調試
echo.
echo 📋 測試步驟：
echo   1. 打開瀏覽器訪問 http://localhost:3000
echo   2. 按 F12 打開開發者工具，查看 Console 標籤
echo   3. 應該看到登入頁面（不是白屏）
echo   4. 使用測試帳號登入：testuser / testpass123
echo   5. 登入後應該看到：
echo      - Dashboard 頁面
echo      - 頂部有 Navbar
echo      - Navbar 顯示用戶名 "testuser"
echo      - 右上角有登出按鈕
echo   6. 點擊登出按鈕
echo   7. 應該返回登入頁面
echo.
echo 🔍 如果仍有問題，請檢查：
echo   1. Console 標籤的錯誤訊息
echo   2. Network 標籤的請求狀態
echo   3. Application 標籤 -^> Local Storage
echo      - 登入後應該有 token 和 user
echo      - 登出後應該被清除
echo.
echo ========================================
pause
