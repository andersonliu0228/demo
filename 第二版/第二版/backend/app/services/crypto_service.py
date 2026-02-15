"""
Crypto Service - 負責 API 憑證的加密和解密
使用 Fernet (AES-256) 對稱加密
"""
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional


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
            
        Raises:
            ValueError: 如果金鑰格式無效
        """
        try:
            self.fernet = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"無效的加密金鑰: {str(e)}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文字串
        
        Args:
            plaintext: 要加密的明文（如 API Secret）
            
        Returns:
            加密後的密文（Base64 編碼）
            
        Raises:
            ValueError: 如果明文為空或無效
        """
        if not plaintext:
            raise ValueError("明文不能為空")
        
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"加密失敗: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文字串
        
        Args:
            ciphertext: 加密的密文
            
        Returns:
            解密後的明文
            
        Raises:
            InvalidToken: 如果密文無效或金鑰錯誤
            ValueError: 如果密文為空或格式無效
        """
        if not ciphertext:
            raise ValueError("密文不能為空")
        
        try:
            decrypted_bytes = self.fernet.decrypt(ciphertext.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            raise InvalidToken("解密失敗：密文無效或金鑰錯誤")
        except Exception as e:
            raise ValueError(f"解密失敗: {str(e)}")
    
    @staticmethod
    def generate_key() -> str:
        """
        生成新的 Fernet 金鑰（用於初始化設定）
        
        Returns:
            Base64 編碼的金鑰字串
        """
        return Fernet.generate_key().decode('utf-8')


# 全域實例（從配置中初始化）
_crypto_service_instance: Optional[CryptoService] = None


def get_crypto_service(encryption_key: str) -> CryptoService:
    """
    獲取 CryptoService 單例實例
    
    Args:
        encryption_key: 加密金鑰
        
    Returns:
        CryptoService 實例
    """
    global _crypto_service_instance
    if _crypto_service_instance is None:
        _crypto_service_instance = CryptoService(encryption_key)
    return _crypto_service_instance
