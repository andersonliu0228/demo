@echo off
chcp 65001 >nul
echo ========================================
echo   測試完整認證流程
echo ========================================
echo.

echo [1] 測試後端登入 API...
echo.
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=testuser&password=testpass123"
echo.
echo.

echo [2] 重啟前端容器...
docker-compose restart frontend
timeout /t 10 /nobreak >nul
echo.

echo ========================================
echo   修復說明
echo ========================================
echo.
echo ✅ 已修復的問題：
echo   1. Login.jsx 在登入前清除 localStorage
echo   2. 添加詳細的 console.log 便於調試
echo   3. 使用 replace: true 跳轉到 Dashboard
echo   4. 正確儲存用戶資訊（只儲存 username）
echo   5. API 使用正確的 URL: http://localhost:8000
echo.
echo 📋 測試步驟：
echo   1. 打開瀏覽器訪問 http://localhost:3000
echo   2. 按 F12 打開開發者工具
echo   3. 切換到 Console 標籤
echo   4. 輸入用戶名：testuser
echo   5. 輸入密碼：testpass123
echo   6. 點擊登入
echo   7. 查看 Console 日誌：
echo      - 應該看到 "🧹 已清除舊的 localStorage 數據"
echo      - 應該看到 "🔐 嘗試登入"
echo      - 應該看到 "✅ 登入成功"
echo      - 應該看到 "💾 已儲存 Token 和用戶資訊"
echo      - 應該看到 "🚀 跳轉到 Dashboard"
echo   8. 切換到 Application 標籤 -^> Local Storage
echo      - 應該看到 token
echo      - 應該看到 user: {"username":"testuser"}
echo.
echo 🔍 如果登入失敗，查看：
echo   1. Console 的錯誤訊息
echo   2. Network 標籤的請求詳情
echo   3. 後端日誌：docker logs ea_trading_backend
echo.
pause
