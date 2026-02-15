#!/bin/bash
# 測試運行腳本

set -e

echo "=========================================="
echo "運行 EA Trading Backend 測試套件"
echo "=========================================="

# 設定測試環境變數
export ENCRYPTION_KEY="test_key_for_testing_only_do_not_use_in_production"
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export REDIS_URL="redis://localhost:6379/1"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}1. 運行所有測試...${NC}"
pytest backend/tests/ -v

echo ""
echo -e "${YELLOW}2. 運行屬性測試...${NC}"
pytest backend/tests/ -v -k "property"

echo ""
echo -e "${YELLOW}3. 運行單元測試...${NC}"
pytest backend/tests/ -v -k "not property"

echo ""
echo -e "${YELLOW}4. 生成測試覆蓋率報告...${NC}"
pytest backend/tests/ --cov=backend/app --cov-report=term-missing --cov-report=html

echo ""
echo -e "${GREEN}=========================================="
echo "測試完成！"
echo "==========================================${NC}"
echo ""
echo "覆蓋率報告已生成到 htmlcov/index.html"
