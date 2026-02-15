@echo off
REM 測試運行腳本 (Windows)

echo ==========================================
echo 運行 EA Trading Backend 測試套件
echo ==========================================

REM 設定測試環境變數
set ENCRYPTION_KEY=test_key_for_testing_only_do_not_use_in_production
set DATABASE_URL=sqlite+aiosqlite:///:memory:
set REDIS_URL=redis://localhost:6379/1

echo.
echo 1. 運行所有測試...
pytest backend/tests/ -v

echo.
echo 2. 運行屬性測試...
pytest backend/tests/ -v -k "property"

echo.
echo 3. 運行單元測試...
pytest backend/tests/ -v -k "not property"

echo.
echo 4. 生成測試覆蓋率報告...
pytest backend/tests/ --cov=backend/app --cov-report=term-missing --cov-report=html

echo.
echo ==========================================
echo 測試完成！
echo ==========================================
echo.
echo 覆蓋率報告已生成到 htmlcov/index.html

pause
