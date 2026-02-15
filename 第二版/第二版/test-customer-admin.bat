@echo off
echo ========================================
echo   客戶管理系統原型測試
echo ========================================
echo.

echo 1. 檢查 Docker 容器狀態...
docker ps --filter "name=ea_trading_frontend"
echo.

echo 2. 重啟前端容器...
docker-compose restart frontend
timeout /t 5 /nobreak >nul
echo.

echo 3. 檢查前端日誌...
docker logs ea_trading_frontend --tail 20
echo.

echo ========================================
echo   測試資訊
echo ========================================
echo.
echo 直接訪問（無需登入）:
echo   http://localhost:3000/admin/customers
echo.
echo 需要登入後訪問:
echo   http://localhost:3000/trader-admin
echo.
echo ========================================
echo   測試步驟
echo ========================================
echo 1. 打開瀏覽器訪問上述網址
echo 2. 查看客戶列表表格
echo 3. 點擊「核准」或「啟動」按鈕
echo 4. 觀察狀態標籤顏色立即改變（綠色）
echo 5. 點擊「停止」或「封鎖」按鈕
echo 6. 觀察狀態標籤顏色立即改變（紅色）
echo 7. 確認頁面沒有重新整理
echo.
echo 完成！
pause
