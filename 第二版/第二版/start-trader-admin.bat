@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 啟動交易員管理面板
echo ========================================
echo.

echo 📦 重啟前端容器...
docker-compose restart frontend

echo.
echo ⏳ 等待容器啟動 (15秒)...
timeout /t 15 /nobreak >nul

echo.
echo ✅ 啟動完成!
echo.
echo 📍 訪問地址:
echo    http://localhost:3000
echo.
echo 💡 功能說明:
echo    - 查看所有客戶列表
echo    - 搜尋客戶（名稱或郵箱）
echo    - 篩選客戶狀態
echo    - 管理客戶狀態（啟用/封鎖）
echo    - 查看即時統計數據
echo.
echo 🎨 特色:
echo    - 即時變色狀態標籤
echo    - 脈動動畫效果
echo    - 響應式設計
echo.
echo ========================================
echo.

start http://localhost:3000

pause
