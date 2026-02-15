# 測試結果報告

## 測試執行時間
2026-02-03 21:12:00 (UTC+8)

## 測試環境
- Docker 容器環境
- Python 3.11.14
- pytest 7.4.4
- Hypothesis 6.98.3
- SQLite 記憶體資料庫

## 測試文件
`backend/tests/services/test_credential_service_properties.py`

## 測試結果摘要

### 通過的測試 (2/7)
✅ **屬性 13：API Key 遮蔽顯示** - PASSED
- 驗證 API Key 只顯示前 4 位和後 4 位，中間部分被遮蔽
- 測試運行 100 次迭代，全部通過

✅ **屬性 14：刪除憑證後無法查詢** - PASSED  
- 驗證刪除憑證後無法再查詢到該憑證
- 測試運行 100 次迭代，全部通過

### 失敗的測試 (5/7)

❌ **屬性 2：資料庫中不存儲明文 Secret** - FAILED
- **失敗原因**：資料庫會話在 Hypothesis 多次迭代之間沒有正確清理
- **錯誤**：`UNIQUE constraint failed: api_credentials.user_id, api_credentials.exchange_name, api_credentials.api_key`
- **根本原因**：測試 fixture 設計問題，需要為每次 Hypothesis 迭代創建獨立的資料庫會話

❌ **屬性 7：API Key 明文存儲與查詢一致性** - FAILED
- **失敗原因**：Hypothesis 檢測到測試結果不一致（Flaky test）
- **錯誤**：第一次運行通過，第二次運行因 UNIQUE 約束失敗
- **根本原因**：同屬性 2，資料庫狀態在迭代之間未清理

❌ **屬性 12：有效憑證驗證成功並存儲** - FAILED
- **失敗原因**：Hypothesis 檢測到測試結果不一致
- **錯誤**：不同迭代產生不同的錯誤（AssertionError vs IntegrityError）
- **根本原因**：資料庫狀態污染 + Mock 狀態未重置

❌ **屬性 15：更新憑證值正確保存** - FAILED
- **失敗原因**：更新操作觸發 UNIQUE 約束衝突
- **錯誤**：`UNIQUE constraint failed` 在 UPDATE 語句中
- **根本原因**：測試數據在迭代之間累積，導致約束衝突

❌ **屬性 16：更新時重新驗證憑證** - FAILED
- **失敗原因**：創建憑證時 UNIQUE 約束失敗
- **錯誤**：`UNIQUE constraint failed` 在 INSERT 語句中
- **根本原因**：資料庫會話未在迭代之間清理

## 問題分析

### 核心問題
所有失敗的測試都源於同一個根本問題：**資料庫會話在 Hypothesis 的多次迭代之間沒有正確隔離和清理**。

### 技術細節
1. **Hypothesis 行為**：每個屬性測試會運行 100 次（預設配置），每次使用不同的隨機輸入
2. **Fixture 作用域**：當前的 `db_session` fixture 在整個測試函數期間保持同一個實例
3. **資料累積**：每次 Hypothesis 迭代都會向資料庫插入數據，但沒有清理
4. **約束衝突**：當隨機生成的數據碰巧重複時（或在後續迭代中），觸發 UNIQUE 約束

### 解決方案

需要修改測試架構，確保每次 Hypothesis 迭代都使用乾淨的資料庫狀態。有幾種可能的方法：

#### 方案 1：使用事務回滾（推薦）
```python
@pytest_asyncio.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session
            # 自動回滾
```

#### 方案 2：在每次迭代後清理數據
```python
# 在測試函數中
async def cleanup_db(db_session):
    await db_session.execute(text("DELETE FROM api_credentials"))
    await db_session.execute(text("DELETE FROM users"))
    await db_session.commit()
```

#### 方案 3：使用 Hypothesis 的 stateful testing
```python
from hypothesis.stateful import RuleBasedStateMachine
# 更複雜但更強大的測試方法
```

#### 方案 4：為每個測試使用獨立的記憶體資料庫
```python
# 每次測試都創建新的 engine
@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # ...
```

## 測試覆蓋的正確性屬性

### 已驗證（部分）
- ✅ 屬性 13：API Key 遮蔽機制正確
- ✅ 屬性 14：刪除操作正確執行

### 待修復
- ⏳ 屬性 2：加密存儲驗證
- ⏳ 屬性 7：明文 API Key 一致性
- ⏳ 屬性 12：憑證驗證和存儲
- ⏳ 屬性 15：更新操作正確性
- ⏳ 屬性 16：更新時重新驗證

## 建議的下一步

1. **立即修復**：實作方案 1（事務回滾），這是最簡單且最有效的方法
2. **驗證修復**：重新運行所有測試，確保全部通過
3. **增加測試**：考慮添加更多邊緣情況測試
4. **文檔更新**：更新測試文檔，說明 Hypothesis 測試的特殊要求

## 測試質量評估

### 優點
- ✅ 使用 Hypothesis 進行屬性測試，覆蓋範圍廣
- ✅ 測試邏輯清晰，文檔完整
- ✅ Mock 使用得當，隔離外部依賴
- ✅ 測試命名規範，易於理解

### 需要改進
- ⚠️ 資料庫會話管理需要優化
- ⚠️ 需要更好的測試隔離機制
- ⚠️ 考慮添加測試輔助函數減少重複代碼

## 結論

測試框架和測試邏輯本身是正確的，問題在於測試基礎設施（fixture 設計）。修復資料庫會話管理後，預期所有測試都能通過。這是屬性測試常見的挑戰，因為它們會運行大量迭代，對測試隔離的要求更高。
