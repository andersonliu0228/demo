# 需求文件

## 簡介

EA 自動化跟單系統後端是一個基於 FastAPI 的服務，允許用戶安全地綁定交易所 API 憑證，並透過加密方式存儲這些敏感資訊。系統將使用 CCXT 函式庫來驗證 API Key 的有效性，並支援多個交易所的整合。

### 技術棧

- **後端框架**: FastAPI
- **資料庫**: PostgreSQL (使用 asyncpg 驅動)
- **ORM**: SQLAlchemy (Async)
- **快取**: Redis
- **交易所整合**: CCXT
- **加密**: cryptography (Fernet AES-256)
- **資料庫遷移**: Alembic
- **測試**: pytest (異步測試)
- **容器化**: Docker + docker-compose

### 目錄結構

- `backend/app`: 核心應用程式碼
- `backend/tests`: 測試程式碼
- `docker`: Docker 配置檔案

## 術語表

- **System**: EA 自動化跟單系統後端
- **User**: 使用系統的交易者（包含帳號、權限資訊）
- **ApiCredential**: 交易所 API 憑證（包含 API Key 和 Secret，加密存儲）
- **Exchange**: 加密貨幣交易所（如 Binance、OKX 等）
- **Crypto_Service**: 負責加密和解密 API 憑證的服務（使用 Fernet AES-256）
- **CCXT**: 統一的加密貨幣交易所 API 函式庫
- **Database**: PostgreSQL 資料庫（使用 asyncpg 驅動）
- **Cache**: Redis 快取系統
- **Alembic**: 資料庫遷移工具

## 需求

### 需求 1：用戶管理

**用戶故事：** 作為系統管理員，我想要管理用戶帳戶，以便追蹤哪些用戶綁定了哪些交易所憑證。

#### 驗收標準

1. THE System SHALL 儲存用戶的唯一識別碼、用戶名稱和電子郵件
2. WHEN 創建新用戶時，THE System SHALL 驗證電子郵件格式的有效性
3. THE System SHALL 確保每個用戶的電子郵件和用戶名稱是唯一的
4. WHEN 查詢用戶資訊時，THE System SHALL 返回用戶的基本資訊但不包含敏感憑證

### 需求 2：API 憑證加密存儲

**用戶故事：** 作為用戶，我想要安全地存儲我的交易所 API 憑證，以便系統可以代表我執行交易操作而不會洩露我的密鑰。

#### 驗收標準

1. WHEN 儲存 API Secret 時，THE Crypto_Service SHALL 使用 Fernet AES-256 對稱加密演算法進行加密
2. THE System SHALL 在資料庫中僅儲存加密後的 API Secret，嚴禁明碼存儲
3. WHEN 需要使用 API Secret 時，THE Crypto_Service SHALL 解密並返回原始值
4. THE System SHALL 從環境變數（.env 檔案）讀取加密金鑰
5. IF 加密金鑰遺失或損壞，THEN THE System SHALL 拒絕解密操作並返回錯誤
6. THE Crypto_Service SHALL 實作為獨立的服務模組（crypto.service）

### 需求 3：API 憑證綁定

**用戶故事：** 作為用戶，我想要綁定我的交易所 API Key，以便系統可以訪問我的交易所帳戶。

#### 驗收標準

1. WHEN 用戶提交 API 憑證時，THE System SHALL 接收交易所名稱、API Key、API Secret 和可選的 Passphrase
2. THE System SHALL 儲存 API Key 的明文形式以供查詢使用
3. THE System SHALL 加密存儲 API Secret 和 Passphrase
4. WHEN 綁定 API 憑證時，THE System SHALL 記錄創建時間和最後更新時間
5. THE System SHALL 允許一個用戶綁定多個不同交易所的 API 憑證
6. THE System SHALL 防止同一用戶在同一交易所重複綁定相同的 API Key

### 需求 4：API 憑證驗證

**用戶故事：** 作為用戶，我想要在綁定 API Key 時驗證其有效性，以便確保憑證正確且具有必要的交易權限。

#### 驗收標準

1. WHEN 用戶綁定新的 API 憑證時，THE System SHALL 使用 CCXT 函式庫連接到指定的交易所
2. THE System SHALL 提供 /api/v1/exchange/verify 路由端點用於驗證 API Key
3. THE System SHALL 嘗試執行基本的 API 呼叫（如獲取帳戶餘額）來驗證憑證
4. THE System SHALL 驗證 API Key 是否具備交易權限
5. IF API 憑證無效或權限不足，THEN THE System SHALL 拒絕綁定並返回具體的錯誤訊息
6. IF API 憑證驗證成功，THEN THE System SHALL 儲存憑證並返回成功狀態
7. WHEN 驗證過程中發生網路錯誤，THE System SHALL 返回適當的錯誤訊息並建議重試

### 需求 5：API 憑證查詢與管理

**用戶故事：** 作為用戶，我想要查看和管理我已綁定的 API 憑證，以便了解當前的綁定狀態。

#### 驗收標準

1. WHEN 用戶查詢已綁定的憑證時，THE System SHALL 返回交易所名稱、API Key（部分遮蔽）和綁定時間
2. THE System SHALL 不在查詢結果中返回 API Secret 的任何形式（加密或明文）
3. WHEN 用戶請求刪除憑證時，THE System SHALL 從資料庫中永久刪除該憑證
4. THE System SHALL 允許用戶更新已存在的 API 憑證
5. WHEN 更新憑證時，THE System SHALL 重新驗證新的憑證有效性

### 需求 6：資料庫操作與遷移

**用戶故事：** 作為系統架構師，我想要使用非同步資料庫操作和版本控制的遷移機制，以便提高系統的並發處理能力和維護資料庫結構的一致性。

#### 驗收標準

1. THE System SHALL 使用 SQLAlchemy 的非同步引擎進行所有資料庫操作
2. THE System SHALL 使用 asyncpg 作為 PostgreSQL 的驅動程式
3. WHEN 執行資料庫查詢時，THE System SHALL 使用非同步會話管理
4. THE System SHALL 正確處理資料庫連接池和會話生命週期
5. IF 資料庫操作失敗，THEN THE System SHALL 回滾事務並返回錯誤
6. THE System SHALL 使用 Alembic 處理資料庫遷移和資料表初始化
7. THE System SHALL 提供遷移腳本來創建 User 和 ApiCredential 資料表

### 需求 7：快取機制

**用戶故事：** 作為系統架構師，我想要使用 Redis 快取頻繁訪問的資料，以便減少資料庫負載並提高響應速度。

#### 驗收標準

1. WHERE 快取功能啟用時，THE System SHALL 使用 Redis 快取用戶的 API 憑證列表
2. WHEN 憑證被更新或刪除時，THE System SHALL 使相關的快取失效
3. THE System SHALL 為快取項目設定合理的過期時間
4. IF Redis 連接失敗，THEN THE System SHALL 降級到直接從資料庫讀取

### 需求 8：錯誤處理與日誌

**用戶故事：** 作為開發人員，我想要完善的錯誤處理和日誌記錄，以便快速診斷和解決問題。

#### 驗收標準

1. WHEN 發生錯誤時，THE System SHALL 返回標準化的錯誤響應格式
2. THE System SHALL 記錄所有 API 請求和關鍵操作的日誌
3. THE System SHALL 在日誌中遮蔽敏感資訊（如 API Secret）
4. IF 發生未預期的異常，THEN THE System SHALL 記錄完整的堆疊追蹤並返回通用錯誤訊息
5. THE System SHALL 區分客戶端錯誤（4xx）和伺服器錯誤（5xx）

### 需求 9：API 端點設計

**用戶故事：** 作為前端開發人員，我想要清晰且符合 RESTful 原則的 API 端點，以便輕鬆整合前端應用。

#### 驗收標準

1. THE System SHALL 提供 POST /api/credentials 端點用於綁定新的 API 憑證
2. THE System SHALL 提供 GET /api/credentials 端點用於查詢用戶的所有憑證
3. THE System SHALL 提供 GET /api/credentials/{credential_id} 端點用於查詢特定憑證
4. THE System SHALL 提供 PUT /api/credentials/{credential_id} 端點用於更新憑證
5. THE System SHALL 提供 DELETE /api/credentials/{credential_id} 端點用於刪除憑證
6. THE System SHALL 提供 POST /api/credentials/validate 端點用於驗證憑證而不儲存
7. WHEN API 端點被呼叫時，THE System SHALL 驗證請求的身份認證和授權

### 需求 10：容器化與部署

**用戶故事：** 作為 DevOps 工程師，我想要使用 Docker 容器化應用程式，以便簡化部署流程和環境一致性。

#### 驗收標準

1. THE System SHALL 提供 docker-compose.yml 檔案用於啟動完整的開發環境
2. THE docker-compose.yml SHALL 包含 PostgreSQL 服務配置
3. THE docker-compose.yml SHALL 包含 Redis 服務配置
4. THE System SHALL 提供 Dockerfile 用於構建後端應用程式映像
5. THE System SHALL 在容器啟動時自動執行資料庫遷移
6. THE System SHALL 透過環境變數配置所有外部依賴的連接資訊

### 需求 11：測試要求

**用戶故事：** 作為開發人員，我想要完整的測試覆蓋，以便確保系統的可靠性和正確性。

#### 驗收標準

1. THE System SHALL 使用 pytest 作為測試框架
2. THE System SHALL 支援異步測試（pytest-asyncio）
3. THE System SHALL 測試資料庫連線的正確性
4. THE System SHALL 測試加密和解密邏輯的正確性
5. THE System SHALL 測試 CCXT 整合和 API 驗證邏輯
6. THE System SHALL 達到合理的測試覆蓋率（建議 > 80%）

