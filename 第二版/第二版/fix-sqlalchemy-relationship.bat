@echo off
chcp 65001 >nul
echo ========================================
echo   修復 SQLAlchemy 關聯錯誤
echo ========================================
echo.

echo [步驟 1] 檢查模型文件...
echo.
echo 檢查 PositionSnapshot 模型...
if exist "backend\app\models\position_snapshot.py" (
    echo ✅ position_snapshot.py 存在
) else (
    echo ❌ position_snapshot.py 不存在！
    pause
    exit /b 1
)
echo.

echo 檢查 __init__.py 導入...
findstr /C:"PositionSnapshot" backend\app\models\__init__.py >nul
if %errorlevel% == 0 (
    echo ✅ PositionSnapshot 已在 __init__.py 中導入
) else (
    echo ❌ PositionSnapshot 未在 __init__.py 中導入！
)
echo.

echo [步驟 2] 重啟後端容器...
docker-compose restart backend
echo 等待後端啟動（20秒）...
timeout /t 20 /nobreak >nul
echo.

echo [步驟 3] 檢查後端日誌...
echo ----------------------------------------
docker logs --tail=50 ea_trading_backend
echo ----------------------------------------
echo.

echo [步驟 4] 測試模型導入...
docker exec ea_trading_backend python -c "from backend.app.models import PositionSnapshot; print('✅ PositionSnapshot 導入成功')"
echo.

echo [步驟 5] 測試 User 模型關聯...
docker exec ea_trading_backend python -c "from backend.app.models import User; print('✅ User 模型載入成功'); print(f'關聯: {[r.key for r in User.__mapper__.relationships]}')"
echo.

echo [步驟 6] 測試登入 API...
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=testuser&password=testpass123"
echo.
echo.

echo ========================================
echo   修復完成！
echo ========================================
echo.
echo ✅ 已修復的問題：
echo   1. 在 __init__.py 中添加 PositionSnapshot 導入
echo   2. 在 __init__.py 中添加其他缺失的模型導入
echo   3. 確保所有模型在 Base 註冊表中
echo.
echo 📋 驗證步驟：
echo   1. 後端日誌無 SQLAlchemy 錯誤
echo   2. 模型導入測試通過
echo   3. 登入 API 返回 200（不是 500）
echo.
pause
