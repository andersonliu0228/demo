@echo off
chcp 65001 >nul
echo ========================================
echo   檢查環境變數配置
echo ========================================
echo.

echo [1] 檢查 .env 文件...
if exist ".env" (
    echo ✅ .env 文件存在
    echo.
    echo 內容：
    type .env
) else (
    echo ❌ .env 文件不存在！
    echo.
    echo 請從 .env.example 複製：
    echo   copy .env.example .env
)
echo.

echo [2] 檢查後端容器環境變數...
echo ----------------------------------------
docker exec ea_trading_backend env | findstr /I "SECRET DATABASE REDIS ENCRYPTION JWT"
echo ----------------------------------------
echo.

echo [3] 測試配置驗證...
docker exec ea_trading_backend python -c "from backend.app.config import settings; settings.validate_settings(); print('✅ 配置驗證通過')"
echo.

pause
