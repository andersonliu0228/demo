@echo off
chcp 65001 >nul
echo 檢查容器內的 Dashboard.jsx...
echo.

echo [1] 檢查文件是否存在...
docker exec ea_trading_frontend ls -la /app/src/components/Dashboard.jsx
echo.

echo [2] 檢查文件開頭（前 15 行）...
docker exec ea_trading_frontend head -15 /app/src/components/Dashboard.jsx
echo.

echo [3] 檢查文件末尾（最後 15 行）...
docker exec ea_trading_frontend tail -15 /app/src/components/Dashboard.jsx
echo.

echo [4] 檢查文件行數...
docker exec ea_trading_frontend wc -l /app/src/components/Dashboard.jsx
echo.

echo [5] 搜索 export default...
docker exec ea_trading_frontend grep -n "export default" /app/src/components/Dashboard.jsx
echo.

pause
