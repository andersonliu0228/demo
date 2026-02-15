"""
Crypto Service 單元測試
測試特定範例、邊緣情況和錯誤條件
"""
import pytest
from cryptography.fernet import Fernet, InvalidToken

from backend.app.services.crypto_service import CryptoService


@pytest.fixture
def crypto_service():
    """提供測試用的加密服務"""
    test_key = Fernet.generate_key().decode()
    return CryptoService(test_key)


@pytest.fixture
def another_crypto_service():
    """提供另一個使用不同金鑰的加密服務"""
    another_key = Fernet.generate_key().decode()
    return CryptoService(another_key)


class TestCryptoServiceInitialization:
    """測試 CryptoService 初始化"""
    
    def test_valid_key_initialization(self):
        """測試使用有效金鑰初始化"""
        key = Fernet.generate_key().decode()
        service = CryptoService(key)
        assert service is not None
        assert service.fernet is not None
    
    def test_invalid_key_raises_error(self):
        """測試使用無效金鑰初始化會拋出錯誤"""
        with pytest.raises(ValueError, match="無效的加密金鑰"):
            CryptoService("invalid-key")
    
    def test_empty_key_raises_error(self):
        """測試使用空金鑰初始化會拋出錯誤"""
        with pytest.raises(ValueError):
            CryptoService("")


class TestEncryption:
    """測試加密功能"""
    
    def test_encrypt_simple_text(self, crypto_service):
        """測試加密簡單文本"""
        plaintext = "my_secret_api_key"
        encrypted = crypto_service.encrypt(plaintext)
        
        assert encrypted is not None
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        assert len(encrypted) > 0
    
    def test_encrypt_empty_string_raises_error(self, crypto_service):
        """測試加密空字串會拋出錯誤"""
        with pytest.raises(ValueError, match="明文不能為空"):
            crypto_service.encrypt("")
    
    def test_encrypt_special_characters(self, crypto_service):
        """測試加密包含特殊字元的文本"""
        plaintext = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_unicode_characters(self, crypto_service):
        """測試加密 Unicode 字元"""
        plaintext = "測試中文字符 🔐🔑"
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_long_text(self, crypto_service):
        """測試加密長文本"""
        plaintext = "a" * 10000
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext


class TestDecryption:
    """測試解密功能"""
    
    def test_decrypt_valid_ciphertext(self, crypto_service):
        """測試解密有效的密文"""
        plaintext = "secret_value"
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_decrypt_empty_string_raises_error(self, crypto_service):
        """測試解密空字串會拋出錯誤"""
        with pytest.raises(ValueError, match="密文不能為空"):
            crypto_service.decrypt("")
    
    def test_decrypt_invalid_ciphertext_raises_error(self, crypto_service):
        """測試解密無效密文會拋出錯誤"""
        with pytest.raises(InvalidToken):
            crypto_service.decrypt("invalid_ciphertext")
    
    def test_decrypt_with_wrong_key_raises_error(
        self, crypto_service, another_crypto_service
    ):
        """
        Feature: ea-trading-backend, Property 3: 錯誤金鑰拒絕解密
        
        測試使用錯誤金鑰解密會拋出異常
        
        對於任何使用正確金鑰加密的密文，如果使用錯誤的金鑰嘗試解密，
        Crypto_Service 應該拋出異常並拒絕解密操作。
        
        驗證需求：2.5
        """
        plaintext = "secret_api_key"
        
        # 使用第一個服務加密
        encrypted = crypto_service.encrypt(plaintext)
        
        # 使用第二個服務（不同金鑰）嘗試解密應該失敗
        with pytest.raises(InvalidToken):
            another_crypto_service.decrypt(encrypted)


class TestGenerateKey:
    """測試金鑰生成功能"""
    
    def test_generate_key_returns_valid_key(self):
        """測試生成的金鑰是有效的"""
        key = CryptoService.generate_key()
        
        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 0
        
        # 驗證生成的金鑰可以用於初始化 CryptoService
        service = CryptoService(key)
        assert service is not None
    
    def test_generate_key_produces_different_keys(self):
        """測試每次生成的金鑰都不同"""
        key1 = CryptoService.generate_key()
        key2 = CryptoService.generate_key()
        
        assert key1 != key2
    
    def test_generated_key_can_encrypt_and_decrypt(self):
        """測試生成的金鑰可以正常加密和解密"""
        key = CryptoService.generate_key()
        service = CryptoService(key)
        
        plaintext = "test_message"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == plaintext


class TestEdgeCases:
    """測試邊緣情況"""
    
    def test_encrypt_decrypt_whitespace(self, crypto_service):
        """測試加密和解密空白字元"""
        plaintext = "   "
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_newlines(self, crypto_service):
        """測試加密和解密換行符"""
        plaintext = "line1\nline2\nline3"
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_tabs(self, crypto_service):
        """測試加密和解密製表符"""
        plaintext = "col1\tcol2\tcol3"
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
