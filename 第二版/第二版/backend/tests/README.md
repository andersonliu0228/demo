# 測試文檔

## 概述

本專案採用雙重測試策略，結合**單元測試**和**屬性測試**以確保全面的代碼覆蓋和正確性驗證。

## 測試類型

### 1. 單元測試（Unit Tests）

單元測試驗證特定的功能、邊緣情況和錯誤處理：

- **位置**：`backend/tests/services/test_*.py`（不含 `_properties` 後綴）
- **框架**：pytest + pytest-asyncio
- **用途**：
  - 測試具體的業務邏輯
  - 驗證錯誤處理
  - 測試邊緣情況
  - 驗證整合點

**範例**：
```python
def test_decrypt_with_wrong_key_raises_error(crypto_service):
    """測試使用錯誤金鑰解密會拋出異常"""
    plaintext = "secret_api_key"
    encrypted = crypto_service.encrypt(plaintext)
    
    wrong_service = CryptoService(Fernet.generate_key().decode())
    
    with pytest.raises(InvalidToken):
        wrong_service.decrypt(encrypted)
```

### 2. 屬性測試（Property-Based Tests）

屬性測試使用隨機生成的輸入驗證通用屬性：

- **位置**：`backend/tests/services/test_*_properties.py`
- **框架**：Hypothesis
- **配置**：最少 100 次迭代（CI 環境 200 次）
- **用途**：
  - 驗證跨所有輸入的通用屬性
  - 發現邊緣情況和意外行為
  - 確保系統在各種輸入下的正確性

**範例**：
```python
@given(st.text(min_size=1, max_size=1000))
def test_encryption_decryption_roundtrip(crypto_service, plaintext):
    """
    Feature: ea-trading-backend, Property 1: 加密解密往返一致性
    
    對於任何明文，加密後解密應該得到原始值
    """
    encrypted = crypto_service.encrypt(plaintext)
    decrypted = crypto_service.decrypt(encrypted)
    assert decrypted == plaintext
```

## 已實作的屬性測試

### Crypto Service
- ✅ **屬性 1**：加密解密往返一致性
- ✅ **屬性 3**：錯誤金鑰拒絕解密

### Cache Service
- ✅ **屬性 18**：快取失效機制
- ✅ **屬性 19**：Redis 降級處理

### Exchange Service
- ✅ **屬性 11**：無效憑證驗證失敗

### Credential Service
- ✅ **屬性 2**：資料庫中不存儲明文 Secret
- ✅ **屬性 7**：API Key 明文存儲與查詢一致性
- ✅ **屬性 12**：有效憑證驗證成功並存儲
- ✅ **屬性 13**：API Key 遮蔽顯示
- ✅ **屬性 14**：刪除憑證後無法查詢
- ✅ **屬性 15**：更新憑證值正確保存
- ✅ **屬性 16**：更新時重新驗證憑證

### Repository Layer
- ✅ **屬性 5**：用戶名和電子郵件唯一性
- ✅ **屬性 10**：防止重複綁定相同憑證

## 運行測試

### 方法 1：使用測試腳本（推薦）

**Linux/Mac**：
```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

**Windows**：
```cmd
scripts\run_tests.bat
```

### 方法 2：使用 Docker Compose

```bash
# 在後端容器中運行測試
docker-compose exec backend pytest backend/tests/ -v

# 運行屬性測試
docker-compose exec backend pytest backend/tests/ -v -k "property"

# 運行單元測試
docker-compose exec backend pytest backend/tests/ -v -k "not property"

# 生成覆蓋率報告
docker-compose exec backend pytest backend/tests/ --cov=backend/app --cov-report=html
```

### 方法 3：直接使用 pytest

```bash
# 設定環境變數
export ENCRYPTION_KEY="test_key_for_testing_only"
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export REDIS_URL="redis://localhost:6379/1"

# 運行所有測試
pytest backend/tests/ -v

# 運行特定測試文件
pytest backend/tests/services/test_crypto_service_properties.py -v

# 運行特定測試
pytest backend/tests/services/test_crypto_service_properties.py::test_property_1_encryption_decryption_roundtrip -v

# 生成覆蓋率報告
pytest backend/tests/ --cov=backend/app --cov-report=term-missing --cov-report=html
```

## 測試配置

### Hypothesis 配置

在 `conftest.py` 中配置：

```python
settings.register_profile(
    "default",
    max_examples=100,  # 每個屬性測試運行 100 次
    verbosity=Verbosity.normal,
    deadline=None  # 禁用超時
)
```

### Pytest 配置

在 `pytest.ini` 中配置：

```ini
[pytest]
testpaths = backend/tests
asyncio_mode = auto
addopts = -v --tb=short --strict-markers
```

## 測試結構

```
backend/tests/
├── conftest.py                          # 共用 fixtures 和配置
├── README.md                            # 本文件
├── repositories/                        # Repository 層測試
│   ├── test_user_repository.py
│   └── test_credential_repository.py
└── services/                            # Service 層測試
    ├── test_crypto_service.py           # 單元測試
    ├── test_crypto_service_properties.py # 屬性測試
    ├── test_cache_service_properties.py
    ├── test_exchange_service.py
    └── test_credential_service_properties.py
```

## 測試覆蓋率目標

- **整體覆蓋率**：> 80%
- **關鍵路徑**（加密、認證、憑證驗證）：> 90%

## 常見問題

### Q: 為什麼屬性測試運行時間較長？

A: 屬性測試會生成大量隨機輸入（預設 100 次），每次都要執行完整的測試邏輯。這是正常的，確保了全面的測試覆蓋。

### Q: 如何調試失敗的屬性測試？

A: Hypothesis 會自動縮小失敗的輸入。查看測試輸出中的 "Falsifying example"，它會顯示導致失敗的最小輸入。

### Q: 測試需要真實的資料庫嗎？

A: 不需要。測試使用 SQLite 記憶體資料庫（`:memory:`），每次測試後自動清理。

### Q: 測試需要 Redis 嗎？

A: 不需要。快取服務測試使用 Mock，不需要真實的 Redis 實例。

## 持續整合

在 CI/CD 環境中，測試會自動運行：

```yaml
# .github/workflows/test.yml 範例
- name: Run tests
  run: |
    export HYPOTHESIS_PROFILE=ci
    pytest backend/tests/ --cov=backend/app --cov-report=xml
```

## 貢獻指南

添加新測試時：

1. **單元測試**：測試具體功能和邊緣情況
2. **屬性測試**：驗證通用屬性和不變量
3. **標記屬性測試**：使用標準格式的文檔字串
4. **使用 fixtures**：重用 `conftest.py` 中的共用 fixtures
5. **異步測試**：使用 `@pytest.mark.asyncio` 裝飾器

## 參考資源

- [pytest 文檔](https://docs.pytest.org/)
- [pytest-asyncio 文檔](https://pytest-asyncio.readthedocs.io/)
- [Hypothesis 文檔](https://hypothesis.readthedocs.io/)
- [屬性測試介紹](https://hypothesis.works/articles/what-is-property-based-testing/)
