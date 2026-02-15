@echo off
echo ========================================
echo   客戶管理系統 - 最終測試
echo ========================================
echo.

echo 檢查前端容器狀態...
docker ps --filter "name=ea_trading_frontend" --format "table {{.Names}}\t{{.Status}}"
echo.

echo 檢查前端日誌（最後 10 行）...
docker logs ea_trading_frontend --tail 10
echo.

echo ========================================
echo   訪問資訊
echo ========================================
echo.
echo 主要地址: http://localhost:3000
echo 備用地址: http://localhost:3000/admin/customers
echo.
echo ========================================
echo   測試步驟
echo ========================================
echo.
echo 1. 打開瀏覽器訪問上述網址
echo 2. 查看客戶管理表格
echo 3. 點擊「核准」按鈕（Tester01）
echo 4. 觀察狀態標籤立即變為綠色
echo 5. 觀察統計卡片數字立即更新
echo 6. 點擊「停止」按鈕（Wilson Chen）
echo 7. 觀察狀態標籤立即變為紅色
echo 8. 確認頁面沒有重新整理
echo.
echo ========================================
echo.
echo 如果頁面無法顯示，執行以下命令：
echo   docker-compose restart frontend
echo.
echo 完成！
pause
