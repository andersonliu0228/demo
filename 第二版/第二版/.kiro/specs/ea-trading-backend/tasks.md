# 實作計畫：EA 自動化跟單系統後端

## 概述

本實作計畫將 EA 自動化跟單系統後端的設計轉換為可執行的編碼任務。系統使用 FastAPI + SQLAlchemy Async + PostgreSQL + Redis + CCXT 技術棧，重點是安全的 API 憑證管理和加密存儲。

實作將採用增量方式，每個任務都建立在前一個任務的基礎上，確保核心功能儘早通過代碼驗證。

## 任務

- [x] 1. 設定專案結構和基礎配置
  - 創建目錄結構：backend/app、backend/tests、docker
  - 設定 pyproject.toml 或 requirements.txt（包含 FastAPI、SQLAlchemy、asyncpg、Redis、CCXT、cryptography、pytest、hypothesis）
  - 創建 .env.example 檔案定義環境變數（DATABASE_URL、REDIS_URL、ENCRYPTION_KEY）
  - 設定 FastAPI 應用程式入口點（main.py）
  - _需求：10.6_

- [x] 2. 實作 Crypto Service（加密服務）
  - [x] 2.1 創建 crypto_service.py 模組
    - 實作 CryptoService 類別，使用 Fernet 進行加密/解密
    - 實作 encrypt() 方法
    - 實作 decrypt() 方法
    - 實作 generate_key() 靜態方法
    - 從環境變數讀取加密金鑰
    - _需求：2.1, 2.3, 2.4_
  
  - [x] 2.2 撰寫 Crypto Service 的屬性測試
    - **屬性 1：加密解密往返一致性**
    - **驗證需求：2.1, 2.3**
  
  - [x] 2.3 撰寫 Crypto Service 的單元測試
    - 測試使用錯誤金鑰解密拋出異常（屬性 3）
    - 測試空字串和特殊字元的加密
    - _需求：2.5_

- [x] 3. 設定資料庫連接和模型
  - [x] 3.1 配置 SQLAlchemy 非同步引擎
    - 創建 database.py 模組
    - 設定 asyncpg 驅動的非同步引擎
    - 實作非同步會話管理（get_db 依賴）
    - 配置連接池參數
    - _需求：6.1, 6.2, 6.3, 6.4_
  
  - [x] 3.2 定義資料模型
    - 創建 models/user.py：定義 User 模型
    - 創建 models/api_credential.py：定義 ApiCredential 模型
    - 設定模型關係（User.api_credentials）
    - 設定唯一性約束（uq_user_exchange_key）
    - _需求：1.1, 3.1, 3.4_
  
  - [x] 3.3 設定 Alembic 資料庫遷移
    - 初始化 Alembic 配置
    - 創建初始遷移腳本（創建 users 和 api_credentials 資料表）
    - 配置自動遷移支援
    - _需求：6.6, 6.7_

- [x] 4. 實作 Repository 層（資料存取）
  - [x] 4.1 創建 User Repository
    - 實作 create_user() 方法
    - 實作 get_user_by_id() 方法
    - 實作 get_user_by_email() 方法
    - 處理唯一性約束違反
    - _需求：1.2, 1.3_
  
  - [x] 4.2 創建 Credential Repository
    - 實作 create_credential() 方法
    - 實作 get_credential_by_id() 方法
    - 實作 get_user_credentials() 方法
    - 實作 update_credential() 方法
    - 實作 delete_credential() 方法
    - 處理唯一性約束違反
    - _需求：3.2, 3.5, 3.6, 5.3, 5.4_
  
  - [x] 4.3 撰寫 Repository 層的單元測試
    - 測試用戶創建和查詢
    - 測試憑證 CRUD 操作
    - 測試唯一性約束（屬性 5, 10）
    - _需求：1.3, 3.6_

- [ ] 5. 實作 Redis 快取服務
  - [x] 5.1 創建 Cache Service
    - 實作 Redis 連接管理
    - 實作 get_user_credentials_cache() 方法
    - 實作 set_user_credentials_cache() 方法
    - 實作 invalidate_credential_cache() 方法
    - 設定 TTL（5 分鐘）
    - 實作降級邏輯（Redis 失敗時直接查詢資料庫）
    - _需求：7.1, 7.2, 7.3, 7.4_
  
  - [x] 5.2 撰寫快取服務的屬性測試
    - **屬性 18：快取失效機制**
    - **屬性 19：Redis 降級處理**
    - **驗證需求：7.2, 7.4**

- [x] 6. 實作 Exchange Service（交易所整合）
  - [x] 6.1 創建 Exchange Service
    - 實作 verify_credentials() 方法（使用 CCXT）
    - 實作 get_account_balance() 方法
    - 實作 get_supported_exchanges() 方法
    - 處理 CCXT 異常（AuthenticationError、NetworkError）
    - 驗證交易權限
    - _需求：4.1, 4.3, 4.4_
  
  - [x] 6.2 撰寫 Exchange Service 的單元測試
    - 測試有效憑證驗證成功
    - 測試無效憑證驗證失敗（屬性 11）
    - 測試網路錯誤處理
    - 使用 Mock 模擬 CCXT 呼叫
    - _需求：4.5, 4.7_

- [ ] 7. 實作 Credential Service（業務邏輯層）
  - [x] 7.1 創建 Credential Service
    - 注入 CredentialRepository、CryptoService、ExchangeService、CacheService
    - 實作 create_credential() 方法（包含驗證和加密）
    - 實作 get_user_credentials() 方法（使用快取）
    - 實作 get_credential_by_id() 方法
    - 實作 update_credential() 方法（重新驗證）
    - 實作 delete_credential() 方法（清除快取）
    - 實作 get_decrypted_credential() 方法（用於交易）
    - 實作 API Key 遮蔽邏輯
    - _需求：3.3, 4.5, 4.6, 5.1, 5.4, 5.5_
  
  - [x] 7.2 撰寫 Credential Service 的屬性測試
    - **屬性 2：資料庫中不存儲明文 Secret**
    - **屬性 7：API Key 明文存儲與查詢一致性**
    - **屬性 12：有效憑證驗證成功並存儲**
    - **屬性 13：API Key 遮蔽顯示**
    - **屬性 14：刪除憑證後無法查詢**
    - **屬性 15：更新憑證值正確保存**
    - **屬性 16：更新時重新驗證憑證**
    - **驗證需求：2.2, 3.2, 3.3, 4.6, 5.1, 5.3, 5.4, 5.5**
  
  - [ ] 7.3 撰寫 Credential Service 的單元測試
    - 測試重複憑證拋出錯誤（屬性 10）
    - 測試多個憑證綁定（屬性 9）
    - 測試事務回滾（屬性 17）
    - _需求：3.5, 3.6, 6.5_

- [ ] 8. Checkpoint - 確保核心服務測試通過
  - 執行所有測試，確保 Crypto、Repository、Cache、Exchange、Credential Service 正常運作
  - 如有問題請詢問用戶

- [ ] 9. 實作 API 路由層
  - [x] 9.1 創建 Credential Routes
    - 實作 POST /api/v1/credentials（創建憑證）
    - 實作 GET /api/v1/credentials（列出用戶憑證）
    - 實作 GET /api/v1/credentials/{credential_id}（獲取單個憑證）
    - 實作 PUT /api/v1/credentials/{credential_id}（更新憑證）
    - 實作 DELETE /api/v1/credentials/{credential_id}（刪除憑證）
    - 定義請求和響應 DTO（Pydantic models）
    - _需求：9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 9.2 創建 Exchange Routes
    - 實作 POST /api/v1/exchange/verify（驗證憑證但不儲存）
    - 實作 GET /api/v1/exchange/supported（獲取支援的交易所列表）
    - _需求：4.2, 9.6_
  
  - [ ] 9.3 實作身份認證中間件
    - 創建簡單的 JWT 認證（或使用 OAuth2）
    - 實作 get_current_user 依賴
    - 保護所有需要認證的端點
    - _需求：9.7_
  
  - [ ] 9.4 撰寫 API 端點的整合測試
    - 測試所有端點的正常流程
    - 測試未認證請求返回 401（屬性 24）
    - 測試參數驗證錯誤
    - _需求：9.7_

- [ ] 10. 實作錯誤處理和日誌
  - [ ] 10.1 定義自定義異常類別
    - 創建 BaseAPIException
    - 創建 CredentialVerificationError、DuplicateCredentialError 等
    - _需求：8.1_
  
  - [ ] 10.2 實作全域異常處理器
    - 實作 api_exception_handler（處理自定義異常）
    - 實作 general_exception_handler（處理未預期異常）
    - 實作 validation_exception_handler（處理參數驗證錯誤）
    - 確保錯誤響應格式統一
    - _需求：8.1, 8.4, 8.5_
  
  - [ ] 10.3 配置日誌系統
    - 設定結構化日誌（JSON 格式）
    - 實作敏感資訊遮蔽（API Secret、密碼）
    - 記錄所有 API 請求和關鍵操作
    - _需求：8.2, 8.3_
  
  - [ ] 10.4 撰寫錯誤處理的屬性測試
    - **屬性 20：標準化錯誤響應格式**
    - **屬性 21：日誌遮蔽敏感資訊**
    - **屬性 22：異常處理返回通用錯誤**
    - **屬性 23：HTTP 狀態碼正確分類**
    - **驗證需求：8.1, 8.3, 8.4, 8.5**

- [ ] 11. 實作資料驗證和安全性
  - [ ] 11.1 加強輸入驗證
    - 實作電子郵件格式驗證（使用 Pydantic EmailStr）
    - 實作交易所名稱白名單驗證
    - 實作 API Key 格式基本驗證
    - _需求：1.2_
  
  - [ ] 11.2 撰寫驗證邏輯的屬性測試
    - **屬性 4：電子郵件格式驗證**
    - **驗證需求：1.2**
  
  - [ ] 11.3 實作查詢結果過濾
    - 確保查詢用戶資訊時不返回敏感欄位
    - 確保查詢憑證時不返回 encrypted_api_secret
    - _需求：1.4, 5.2_
  
  - [ ] 11.4 撰寫安全性的屬性測試
    - **屬性 6：查詢結果不包含敏感資訊**
    - **驗證需求：1.4, 5.2**

- [ ] 12. Docker 容器化配置
  - [x] 12.1 創建 Dockerfile
    - 使用 Python 3.11+ 基礎映像
    - 安裝依賴
    - 配置啟動命令（執行遷移後啟動 FastAPI）
    - _需求：10.4, 10.5_
  
  - [x] 12.2 創建 docker-compose.yml
    - 配置 PostgreSQL 服務
    - 配置 Redis 服務
    - 配置後端服務（依賴 PostgreSQL 和 Redis）
    - 設定環境變數
    - 設定網路和卷
    - _需求：10.1, 10.2, 10.3_

- [ ] 13. 撰寫測試配置和輔助工具
  - [ ] 13.1 創建 conftest.py
    - 配置 pytest 和 pytest-asyncio
    - 配置 Hypothesis（最少 100 次迭代）
    - 創建測試資料庫 fixture
    - 創建測試用戶 fixture
    - 創建 mock 服務 fixture
    - _需求：11.2, 11.3_
  
  - [ ] 13.2 創建測試輔助工具
    - 實作測試資料生成器（使用 Hypothesis strategies）
    - 實作 API 測試客戶端
    - _需求：11.4, 11.5_

- [ ] 14. 最終整合和驗證
  - [ ] 14.1 執行完整測試套件
    - 執行所有單元測試
    - 執行所有屬性測試
    - 執行所有整合測試
    - 檢查測試覆蓋率（目標 > 80%）
    - _需求：11.6_
  
  - [ ] 14.2 驗證 Docker 環境
    - 使用 docker-compose up 啟動完整環境
    - 驗證資料庫遷移自動執行
    - 驗證 API 端點可訪問
    - 測試端到端流程（創建用戶 → 綁定憑證 → 查詢憑證）
    - _需求：10.5_
  
  - [ ] 14.3 創建 README.md
    - 說明專案結構
    - 說明如何設定環境變數
    - 說明如何啟動開發環境（docker-compose）
    - 說明如何執行測試
    - 說明 API 端點文檔（或指向 FastAPI 自動生成的文檔）

- [ ] 15. Final Checkpoint - 確保所有測試通過
  - 確保所有測試通過，如有問題請詢問用戶

## 注意事項

- 每個任務都引用了具體的需求編號以便追溯
- Checkpoint 任務確保增量驗證
- 屬性測試驗證通用正確性屬性
- 單元測試驗證特定範例和邊緣情況
- 兩種測試方法互補，共同確保全面覆蓋
- 所有測試任務都是必需的，以確保系統的可靠性和正確性
