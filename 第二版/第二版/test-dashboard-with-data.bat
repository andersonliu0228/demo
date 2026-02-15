@echo off
chcp 65001 >nul
echo ========================================
echo   測試 Dashboard（含數據載入）
echo ========================================
echo.

echo 現在使用 Dashboard-test.jsx
echo 這個版本會：
echo   - 使用 useDashboard hook
echo   - 載入真實數據
echo   - 但不渲染複雜的子組件
echo.

echo [1] 重啟前端容器...
docker-compose restart frontend
echo.

echo [2] 等待啟動（15秒）...
timeout /t 15 /nobreak
echo.

echo ========================================
echo   測試步驟
echo ========================================
echo.
echo 1. 訪問 http://localhost:3000
echo 2. 登入：testuser / testpass123
echo 3. 查看結果：
echo.
echo    如果看到綠色提示框和數據：
echo      ✅ useDashboard hook 正常
echo      ✅ API 請求正常
echo      ✅ 問題在於某個子組件
echo.
echo    如果仍然白屏或錯誤：
echo      ❌ 問題在於 useDashboard 或 API
echo      請查看瀏覽器 Console 的錯誤訊息
echo.
pause
