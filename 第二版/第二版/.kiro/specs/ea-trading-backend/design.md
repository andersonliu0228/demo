# 設計文件

## 概述

EA 自動化跟單系統後端採用現代化的非同步架構，基於 FastAPI 框架構建。系統的核心功能是安全地管理用戶的交易所 API 憑證，使用 Fernet AES-256 加密演算法保護敏感資訊，並透過 CCXT 函式庫驗證憑證的有效性。

### 設計目標

1. **安全性優先**：所有敏感資訊必須加密存儲，加密金鑰與應用程式分離
2. **高效能**：使用非同步 I/O 處理資料庫和外部 API 呼叫
3. **可擴展性**：模組化設計，易於添加新的交易所支援
4. **可維護性**：清晰的分層架構，完整的測試覆蓋

### 技術選型理由

- **FastAPI**：原生支援異步、自動生成 API 文件、優秀的型別檢查
- **SQLAlchemy Async**：成熟的 ORM，支援非同步操作
- **PostgreSQL**：可靠的關聯式資料庫，支援 ACID 事務
- **Redis**：高效能快取，減少資料庫負載
- **CCXT**：統一的交易所 API 介面，支援 100+ 交易所
- **Fernet (cryptography)**：對稱加密，簡單安全，適合加密存儲

## 架構

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                    (Frontend / API Client)                   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Auth       │  │  Credential  │  │  Exchange    │      │
│  │  Middleware  │  │   Routes     │  │   Routes     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Crypto     │  │  Credential  │  │  Exchange    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                          │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │     User     │  │     API      │                         │
│  │  Repository  │  │  Credential  │                         │
│  │              │  │  Repository  │                         │
│  └──────────────┘  └──────────────┘                         │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │     CCXT     │
│   Database   │    │    Cache     │    │  (Exchanges) │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 分層架構說明

1. **API Layer（路由層）**
   - 處理 HTTP 請求和響應
   - 請求驗證和參數解析
   - 身份認證和授權檢查

2. **Service Layer（服務層）**
   - 業務邏輯實作
   - 協調多個 Repository 的操作
   - 加密/解密、外部 API 呼叫

3. **Repository Layer（資料存取層）**
   - 資料庫 CRUD 操作
   - 快取管理
   - 資料模型轉換

4. **Infrastructure Layer（基礎設施層）**
   - 資料庫連接管理
   - Redis 連接管理
   - 配置管理

## 元件與介面

### 1. 資料模型（Models）

#### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    api_credentials: Mapped[List["ApiCredential"]] = relationship(back_populates="user")
```

#### ApiCredential Model

```python
class ApiCredential(Base):
    __tablename__ = "api_credentials"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exchange_name: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_api_secret: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_passphrase: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="api_credentials")
    
    # Unique constraint: one user can only have one credential per exchange
    __table_args__ = (
        UniqueConstraint('user_id', 'exchange_name', 'api_key', name='uq_user_exchange_key'),
    )
```

### 2. Crypto Service（加密服務）

```python
class CryptoService:
    """
    負責 API 憑證的加密和解密
    使用 Fernet (AES-256) 對稱加密
    """
    
    def __init__(self, encryption_key: str):
        """
        初始化加密服務
        
        Args:
            encryption_key: Base64 編碼的 Fernet 金鑰（從環境變數讀取）
        """
        self.fernet = Fernet(encryption_key.encode())
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文字串
        
        Args:
            plaintext: 要加密的明文（如 API Secret）
            
        Returns:
            加密後的密文（Base64 編碼）
        """
        encrypted_bytes = self.fernet.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文字串
        
        Args:
            ciphertext: 加密的密文
            
        Returns:
            解密後的明文
            
        Raises:
            InvalidToken: 如果密文無效或金鑰錯誤
        """
        decrypted_bytes = self.fernet.decrypt(ciphertext.encode())
        return decrypted_bytes.decode()
    
    @staticmethod
    def generate_key() -> str:
        """
        生成新的 Fernet 金鑰（用於初始化設定）
        
        Returns:
            Base64 編碼的金鑰字串
        """
        return Fernet.generate_key().decode()
```

### 3. Exchange Service（交易所服務）

```python
class ExchangeService:
    """
    負責與交易所 API 互動
    使用 CCXT 函式庫統一介面
    """
    
    def __init__(self, crypto_service: CryptoService):
        self.crypto_service = crypto_service
    
    async def verify_credentials(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        驗證 API 憑證是否有效且具備交易權限
        
        Args:
            exchange_name: 交易所名稱（如 'binance', 'okx'）
            api_key: API Key
            api_secret: API Secret
            passphrase: API Passphrase（某些交易所需要）
            
        Returns:
            驗證結果字典，包含：
            - is_valid: bool - 憑證是否有效
            - has_trading_permission: bool - 是否具備交易權限
            - account_info: dict - 帳戶基本資訊（如有）
            - error_message: str - 錯誤訊息（如有）
            
        Raises:
            ExchangeNotSupportedError: 不支援的交易所
            NetworkError: 網路連接錯誤
        """
        pass
    
    async def get_account_balance(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ) -> Dict[str, float]:
        """
        獲取帳戶餘額（用於驗證憑證）
        
        Returns:
            幣種餘額字典 {'BTC': 0.5, 'USDT': 1000.0, ...}
        """
        pass
    
    def get_supported_exchanges(self) -> List[str]:
        """
        獲取支援的交易所列表
        
        Returns:
            交易所名稱列表
        """
        return ccxt.exchanges
```

### 4. Credential Service（憑證服務）

```python
class CredentialService:
    """
    負責 API 憑證的業務邏輯
    """
    
    def __init__(
        self,
        credential_repo: CredentialRepository,
        crypto_service: CryptoService,
        exchange_service: ExchangeService,
        cache_service: CacheService
    ):
        self.credential_repo = credential_repo
        self.crypto_service = crypto_service
        self.exchange_service = exchange_service
        self.cache_service = cache_service
    
    async def create_credential(
        self,
        user_id: int,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None,
        verify: bool = True
    ) -> ApiCredential:
        """
        創建新的 API 憑證
        
        Args:
            user_id: 用戶 ID
            exchange_name: 交易所名稱
            api_key: API Key
            api_secret: API Secret
            passphrase: API Passphrase（可選）
            verify: 是否在創建前驗證憑證
            
        Returns:
            創建的 ApiCredential 物件
            
        Raises:
            CredentialVerificationError: 憑證驗證失敗
            DuplicateCredentialError: 憑證已存在
        """
        pass
    
    async def get_user_credentials(
        self,
        user_id: int,
        include_inactive: bool = False
    ) -> List[ApiCredential]:
        """
        獲取用戶的所有憑證
        
        Args:
            user_id: 用戶 ID
            include_inactive: 是否包含已停用的憑證
            
        Returns:
            憑證列表
        """
        pass
    
    async def update_credential(
        self,
        credential_id: int,
        user_id: int,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        passphrase: Optional[str] = None,
        verify: bool = True
    ) -> ApiCredential:
        """
        更新現有憑證
        """
        pass
    
    async def delete_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> bool:
        """
        刪除憑證
        """
        pass
    
    async def get_decrypted_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> Dict[str, str]:
        """
        獲取解密後的憑證（用於實際交易）
        
        Returns:
            包含 api_key, api_secret, passphrase 的字典
        """
        pass
```

### 5. API 路由（Routes）

#### Credential Routes

```python
router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])

@router.post("/", response_model=CredentialResponse, status_code=201)
async def create_credential(
    request: CreateCredentialRequest,
    current_user: User = Depends(get_current_user),
    credential_service: CredentialService = Depends()
):
    """
    綁定新的 API 憑證
    
    Request Body:
    {
        "exchange_name": "binance",
        "api_key": "xxx",
        "api_secret": "yyy",
        "passphrase": "zzz",  // optional
        "verify": true  // optional, default true
    }
    """
    pass

@router.get("/", response_model=List[CredentialResponse])
async def list_credentials(
    current_user: User = Depends(get_current_user),
    credential_service: CredentialService = Depends()
):
    """
    獲取當前用戶的所有憑證
    """
    pass

@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    credential_service: CredentialService = Depends()
):
    """
    獲取特定憑證的詳細資訊
    """
    pass

@router.put("/{credential_id}", response_model=CredentialResponse)
async def update_credential(
    credential_id: int,
    request: UpdateCredentialRequest,
    current_user: User = Depends(get_current_user),
    credential_service: CredentialService = Depends()
):
    """
    更新現有憑證
    """
    pass

@router.delete("/{credential_id}", status_code=204)
async def delete_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    credential_service: CredentialService = Depends()
):
    """
    刪除憑證
    """
    pass
```

#### Exchange Routes

```python
router = APIRouter(prefix="/api/v1/exchange", tags=["exchange"])

@router.post("/verify", response_model=VerifyCredentialResponse)
async def verify_credential(
    request: VerifyCredentialRequest,
    current_user: User = Depends(get_current_user),
    exchange_service: ExchangeService = Depends()
):
    """
    驗證 API 憑證但不儲存
    
    Request Body:
    {
        "exchange_name": "binance",
        "api_key": "xxx",
        "api_secret": "yyy",
        "passphrase": "zzz"  // optional
    }
    
    Response:
    {
        "is_valid": true,
        "has_trading_permission": true,
        "account_info": {...},
        "error_message": null
    }
    """
    pass

@router.get("/supported", response_model=List[str])
async def get_supported_exchanges(
    exchange_service: ExchangeService = Depends()
):
    """
    獲取支援的交易所列表
    """
    pass
```

### 6. 資料傳輸物件（DTOs）

```python
# Request DTOs
class CreateCredentialRequest(BaseModel):
    exchange_name: str = Field(..., min_length=1, max_length=50)
    api_key: str = Field(..., min_length=1)
    api_secret: str = Field(..., min_length=1)
    passphrase: Optional[str] = None
    verify: bool = True

class UpdateCredentialRequest(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    verify: bool = True

class VerifyCredentialRequest(BaseModel):
    exchange_name: str
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None

# Response DTOs
class CredentialResponse(BaseModel):
    id: int
    exchange_name: str
    api_key_masked: str  # 只顯示前4位和後4位
    is_active: bool
    last_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VerifyCredentialResponse(BaseModel):
    is_valid: bool
    has_trading_permission: bool
    account_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
```

## 資料模型

### 資料庫 Schema

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Credentials Table
CREATE TABLE api_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exchange_name VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    encrypted_api_secret TEXT NOT NULL,
    encrypted_passphrase TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_exchange_key UNIQUE (user_id, exchange_name, api_key)
);

-- Indexes
CREATE INDEX idx_api_credentials_user_id ON api_credentials(user_id);
CREATE INDEX idx_api_credentials_exchange ON api_credentials(exchange_name);
CREATE INDEX idx_users_email ON users(email);
```

### Redis 快取結構

```
# 用戶憑證列表快取
Key: user:{user_id}:credentials
Type: List
Value: [credential_id_1, credential_id_2, ...]
TTL: 300 seconds (5 minutes)

# 單個憑證快取
Key: credential:{credential_id}
Type: Hash
Value: {
    "id": "123",
    "user_id": "456",
    "exchange_name": "binance",
    "api_key": "xxx",
    "encrypted_api_secret": "yyy",
    "is_active": "true",
    ...
}
TTL: 300 seconds (5 minutes)

# 交易所支援列表快取
Key: exchanges:supported
Type: Set
Value: {"binance", "okx", "bybit", ...}
TTL: 3600 seconds (1 hour)
```


## 正確性屬性

屬性（Property）是一種特徵或行為，應該在系統的所有有效執行中保持為真——本質上是關於系統應該做什麼的正式陳述。屬性作為人類可讀規範和機器可驗證正確性保證之間的橋樑。

### 屬性 1：加密解密往返一致性

*對於任何* 有效的明文字串（API Secret），使用 Crypto_Service 加密後再解密，應該得到與原始明文相同的值。

**驗證需求：2.1, 2.3**

### 屬性 2：資料庫中不存儲明文 Secret

*對於任何* 存儲在資料庫中的 ApiCredential 記錄，encrypted_api_secret 欄位的值應該與原始 API Secret 明文不同，且無法直接讀取為有意義的明文。

**驗證需求：2.2, 3.3**

### 屬性 3：錯誤金鑰拒絕解密

*對於任何* 使用正確金鑰加密的密文，如果使用錯誤的金鑰嘗試解密，Crypto_Service 應該拋出異常並拒絕解密操作。

**驗證需求：2.5**

### 屬性 4：電子郵件格式驗證

*對於任何* 字串，系統應該正確識別其是否為有效的電子郵件格式，接受有效格式（如 user@example.com）並拒絕無效格式（如 "not-an-email"、"@example.com"、"user@"）。

**驗證需求：1.2**

### 屬性 5：用戶名和電子郵件唯一性

*對於任何* 已存在的用戶，嘗試創建具有相同用戶名或相同電子郵件的新用戶時，系統應該拒絕操作並返回唯一性約束錯誤。

**驗證需求：1.3**

### 屬性 6：查詢結果不包含敏感資訊

*對於任何* 用戶查詢操作（查詢用戶資訊或憑證列表），返回的結果中不應包含 API Secret（加密或明文形式）、密碼雜湊等敏感欄位。

**驗證需求：1.4, 5.2**

### 屬性 7：API Key 明文存儲與查詢一致性

*對於任何* 創建的 ApiCredential，存儲後查詢得到的 api_key 欄位應該與創建時提供的原始 API Key 完全相同（明文存儲）。

**驗證需求：3.2**

### 屬性 8：時間戳自動記錄

*對於任何* 新創建的 ApiCredential 或 User 記錄，created_at 和 updated_at 欄位應該自動設定為創建時的時間戳，且 created_at 應該小於或等於 updated_at。

**驗證需求：3.4**

### 屬性 9：用戶可綁定多個交易所憑證

*對於任何* 用戶，系統應該允許該用戶創建多個 ApiCredential 記錄，只要這些憑證的交易所名稱或 API Key 不完全相同。

**驗證需求：3.5**

### 屬性 10：防止重複綁定相同憑證

*對於任何* 用戶和交易所組合，如果該用戶已經綁定了特定交易所的特定 API Key，嘗試再次綁定相同的組合時，系統應該拒絕操作並返回重複錯誤。

**驗證需求：3.6**

### 屬性 11：無效憑證驗證失敗

*對於任何* 無效的 API 憑證（錯誤的 API Key 或 Secret），當透過 Exchange Service 驗證時，應該返回 is_valid=false 並包含具體的錯誤訊息。

**驗證需求：4.4, 4.5**

### 屬性 12：有效憑證驗證成功並存儲

*對於任何* 有效的 API 憑證，當驗證成功後進行綁定操作，系統應該將憑證存儲到資料庫，並且後續可以查詢到該憑證。

**驗證需求：4.6**

### 屬性 13：API Key 遮蔽顯示

*對於任何* 查詢憑證的操作，返回的 api_key_masked 欄位應該只顯示 API Key 的前 4 位和後 4 位字元，中間部分用星號或其他字元遮蔽。

**驗證需求：5.1**

### 屬性 14：刪除憑證後無法查詢

*對於任何* 已刪除的 ApiCredential，刪除操作完成後，嘗試查詢該憑證應該返回「不存在」錯誤或空結果。

**驗證需求：5.3**

### 屬性 15：更新憑證值正確保存

*對於任何* 已存在的 ApiCredential，當更新其 API Key 或 Secret 時，更新後查詢得到的值應該與更新時提供的新值一致。

**驗證需求：5.4**

### 屬性 16：更新時重新驗證憑證

*對於任何* 憑證更新操作，如果提供的新憑證無效，系統應該拒絕更新並保持原有憑證不變。

**驗證需求：5.5**

### 屬性 17：資料庫事務回滾

*對於任何* 資料庫操作序列，如果其中任何一步失敗，整個事務應該回滾，資料庫狀態應該恢復到操作開始前的狀態。

**驗證需求：6.5**

### 屬性 18：快取失效機制

*對於任何* 憑證的更新或刪除操作，完成後相關的 Redis 快取應該被清除或失效，下次查詢時應該從資料庫重新載入最新資料。

**驗證需求：7.2**

### 屬性 19：Redis 降級處理

*對於任何* 查詢操作，當 Redis 連接失敗或不可用時，系統應該自動降級到直接從資料庫讀取，並且仍能正確返回資料。

**驗證需求：7.4**

### 屬性 20：標準化錯誤響應格式

*對於任何* 發生錯誤的 API 請求，系統應該返回統一格式的錯誤響應，包含錯誤碼、錯誤訊息和時間戳等標準欄位。

**驗證需求：8.1**

### 屬性 21：日誌遮蔽敏感資訊

*對於任何* 涉及 API Secret、密碼或其他敏感資訊的操作，記錄的日誌中應該將這些敏感資訊遮蔽或替換為佔位符，不應出現明文。

**驗證需求：8.3**

### 屬性 22：異常處理返回通用錯誤

*對於任何* 未預期的異常（如空指標、類型錯誤等），系統應該捕獲異常、記錄完整堆疊追蹤到日誌，並向客戶端返回通用的 500 錯誤訊息（不洩露內部細節）。

**驗證需求：8.4**

### 屬性 23：HTTP 狀態碼正確分類

*對於任何* API 錯誤響應，客戶端錯誤（如參數驗證失敗、資源不存在）應該返回 4xx 狀態碼，伺服器錯誤（如資料庫連接失敗、未捕獲異常）應該返回 5xx 狀態碼。

**驗證需求：8.5**

### 屬性 24：未認證請求被拒絕

*對於任何* 需要認證的 API 端點，如果請求未包含有效的認證令牌或憑證，系統應該返回 401 Unauthorized 錯誤並拒絕處理請求。

**驗證需求：9.7**

## 錯誤處理

### 錯誤類型定義

系統定義以下自定義異常類型：

```python
class BaseAPIException(Exception):
    """基礎 API 異常類"""
    def __init__(self, message: str, error_code: str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class CredentialVerificationError(BaseAPIException):
    """憑證驗證失敗"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CREDENTIAL_VERIFICATION_FAILED",
            status_code=400
        )

class DuplicateCredentialError(BaseAPIException):
    """重複的憑證"""
    def __init__(self, message: str = "此 API Key 已經綁定"):
        super().__init__(
            message=message,
            error_code="DUPLICATE_CREDENTIAL",
            status_code=409
        )

class CredentialNotFoundError(BaseAPIException):
    """憑證不存在"""
    def __init__(self, credential_id: int):
        super().__init__(
            message=f"憑證 ID {credential_id} 不存在",
            error_code="CREDENTIAL_NOT_FOUND",
            status_code=404
        )

class ExchangeNotSupportedError(BaseAPIException):
    """不支援的交易所"""
    def __init__(self, exchange_name: str):
        super().__init__(
            message=f"不支援的交易所: {exchange_name}",
            error_code="EXCHANGE_NOT_SUPPORTED",
            status_code=400
        )

class EncryptionError(BaseAPIException):
    """加密/解密錯誤"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="ENCRYPTION_ERROR",
            status_code=500
        )

class NetworkError(BaseAPIException):
    """網路連接錯誤"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            status_code=503
        )
```

### 全域異常處理器

```python
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """處理自定義 API 異常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """處理未預期的異常"""
    # 記錄完整堆疊追蹤
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # 返回通用錯誤訊息（不洩露內部細節）
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "伺服器發生內部錯誤，請稍後再試",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """處理請求驗證錯誤"""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "請求參數驗證失敗",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

### 錯誤處理策略

1. **加密錯誤**
   - 金鑰無效：返回 500 錯誤，記錄日誌，建議檢查環境變數
   - 解密失敗：返回 500 錯誤，可能是資料損壞或金鑰變更

2. **憑證驗證錯誤**
   - API Key 無效：返回 400 錯誤，提示檢查憑證
   - 權限不足：返回 400 錯誤，提示需要交易權限
   - 網路錯誤：返回 503 錯誤，建議重試

3. **資料庫錯誤**
   - 連接失敗：返回 503 錯誤，記錄日誌
   - 唯一性約束違反：返回 409 錯誤，提示資源已存在
   - 事務失敗：自動回滾，返回 500 錯誤

4. **快取錯誤**
   - Redis 連接失敗：降級到資料庫，記錄警告日誌
   - 快取資料損壞：清除快取，從資料庫重新載入

5. **認證授權錯誤**
   - 未認證：返回 401 錯誤
   - 權限不足：返回 403 錯誤
   - 令牌過期：返回 401 錯誤，提示重新登入

## 測試策略

### 測試方法

系統採用雙重測試方法，結合單元測試和屬性測試以確保全面覆蓋：

1. **單元測試（Unit Tests）**
   - 用於驗證特定範例、邊緣情況和錯誤條件
   - 測試具體的業務邏輯和整合點
   - 使用 pytest 框架和 pytest-asyncio 支援非同步測試

2. **屬性測試（Property-Based Tests）**
   - 用於驗證跨所有輸入的通用屬性
   - 透過隨機化實現全面的輸入覆蓋
   - 每個屬性測試最少執行 100 次迭代
   - 使用 Hypothesis 函式庫進行屬性測試

### 測試配置

```python
# conftest.py
import pytest
import pytest_asyncio
from hypothesis import settings, Verbosity

# 配置 Hypothesis
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=200, verbosity=Verbosity.verbose)
settings.load_profile("default")

@pytest_asyncio.fixture
async def db_session():
    """提供測試資料庫會話"""
    # 創建測試資料庫連接
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def crypto_service():
    """提供測試用的加密服務"""
    test_key = Fernet.generate_key().decode()
    return CryptoService(test_key)

@pytest_asyncio.fixture
async def test_user(db_session):
    """創建測試用戶"""
    user = User(username="testuser", email="test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

### 測試覆蓋範圍

#### 1. Crypto Service 測試

```python
# 屬性測試範例
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_encryption_decryption_roundtrip(crypto_service, plaintext):
    """
    Feature: ea-trading-backend, Property 1: 加密解密往返一致性
    
    對於任何明文，加密後解密應該得到原始值
    """
    encrypted = crypto_service.encrypt(plaintext)
    decrypted = crypto_service.decrypt(encrypted)
    assert decrypted == plaintext

# 單元測試範例
def test_decrypt_with_wrong_key_raises_error(crypto_service):
    """測試使用錯誤金鑰解密會拋出異常"""
    plaintext = "secret_api_key"
    encrypted = crypto_service.encrypt(plaintext)
    
    # 使用不同的金鑰
    wrong_service = CryptoService(Fernet.generate_key().decode())
    
    with pytest.raises(InvalidToken):
        wrong_service.decrypt(encrypted)
```

#### 2. Credential Service 測試

```python
@pytest.mark.asyncio
@given(
    exchange=st.sampled_from(["binance", "okx", "bybit"]),
    api_key=st.text(min_size=10, max_size=100),
    api_secret=st.text(min_size=10, max_size=100)
)
async def test_create_credential_stores_encrypted_secret(
    credential_service, test_user, db_session, exchange, api_key, api_secret
):
    """
    Feature: ea-trading-backend, Property 2: 資料庫中不存儲明文 Secret
    
    對於任何憑證，資料庫中存儲的應該是加密後的值
    """
    # Mock 驗證成功
    with patch.object(credential_service.exchange_service, 'verify_credentials') as mock_verify:
        mock_verify.return_value = {"is_valid": True, "has_trading_permission": True}
        
        credential = await credential_service.create_credential(
            user_id=test_user.id,
            exchange_name=exchange,
            api_key=api_key,
            api_secret=api_secret
        )
    
    # 驗證資料庫中的值不是明文
    assert credential.encrypted_api_secret != api_secret
    assert credential.api_key == api_key  # API Key 應該是明文

@pytest.mark.asyncio
async def test_duplicate_credential_raises_error(credential_service, test_user):
    """測試重複綁定相同憑證會拋出錯誤"""
    exchange = "binance"
    api_key = "test_key"
    api_secret = "test_secret"
    
    # 第一次創建
    with patch.object(credential_service.exchange_service, 'verify_credentials') as mock_verify:
        mock_verify.return_value = {"is_valid": True, "has_trading_permission": True}
        await credential_service.create_credential(
            user_id=test_user.id,
            exchange_name=exchange,
            api_key=api_key,
            api_secret=api_secret
        )
    
    # 第二次創建應該失敗
    with pytest.raises(DuplicateCredentialError):
        await credential_service.create_credential(
            user_id=test_user.id,
            exchange_name=exchange,
            api_key=api_key,
            api_secret=api_secret
        )
```

#### 3. API 端點測試

```python
@pytest.mark.asyncio
async def test_create_credential_endpoint(client, auth_headers):
    """測試創建憑證端點"""
    response = await client.post(
        "/api/v1/credentials",
        json={
            "exchange_name": "binance",
            "api_key": "test_key",
            "api_secret": "test_secret",
            "verify": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["exchange_name"] == "binance"
    assert "api_key_masked" in data
    assert "encrypted_api_secret" not in data  # 不應返回加密的 secret

@pytest.mark.asyncio
async def test_unauthenticated_request_returns_401(client):
    """
    Feature: ea-trading-backend, Property 24: 未認證請求被拒絕
    
    測試未認證的請求應該返回 401
    """
    response = await client.get("/api/v1/credentials")
    assert response.status_code == 401
```

#### 4. Exchange Service 測試

```python
@pytest.mark.asyncio
async def test_verify_invalid_credentials_returns_false(exchange_service):
    """測試驗證無效憑證返回 false"""
    result = await exchange_service.verify_credentials(
        exchange_name="binance",
        api_key="invalid_key",
        api_secret="invalid_secret"
    )
    
    assert result["is_valid"] is False
    assert "error_message" in result

@pytest.mark.asyncio
async def test_network_error_handling(exchange_service):
    """測試網路錯誤處理"""
    with patch('ccxt.binance') as mock_exchange:
        mock_exchange.return_value.fetch_balance.side_effect = NetworkError("Connection timeout")
        
        with pytest.raises(NetworkError):
            await exchange_service.verify_credentials(
                exchange_name="binance",
                api_key="test_key",
                api_secret="test_secret"
            )
```

### 測試標籤規範

每個屬性測試必須包含標籤註解，格式如下：

```python
"""
Feature: ea-trading-backend, Property {編號}: {屬性描述}

{詳細說明}
"""
```

### 持續整合

- 所有測試在 CI/CD 管道中自動執行
- 屬性測試在 CI 環境中使用更高的迭代次數（200 次）
- 測試覆蓋率目標：> 80%
- 關鍵路徑（加密、認證、憑證驗證）要求 > 90% 覆蓋率
