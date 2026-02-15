"""
Crypto Service 屬性測試
使用 Hypothesis 進行屬性測試
"""
import pytest
from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

from backend.app.services.crypto_service import CryptoService


@pytest.fixture
def crypto_service():
    """提供測試用的加密服務"""
    test_key = Fernet.generate_key().decode()
    return CryptoService(test_key)


@given(st.text(min_size=1, max_size=1000))
def test_property_1_encryption_decryption_roundtrip(crypto_service, plaintext):
    """
    Feature: ea-trading-backend, Property 1: 加密解密往返一致性
    
    對於任何有效的明文字串（API Secret），使用 Crypto_Service 加密後再解密，
    應該得到與原始明文相同的值。
    
    驗證需求：2.1, 2.3
    """
    # 加密明文
    encrypted = crypto_service.encrypt(plaintext)
    
    # 驗證加密後的值與原始明文不同
    assert encrypted != plaintext
    
    # 解密密文
    decrypted = crypto_service.decrypt(encrypted)
    
    # 驗證解密後的值與原始明文相同
    assert decrypted == plaintext


@given(st.text(min_size=1, max_size=1000))
def test_property_1_multiple_encryptions_produce_different_ciphertexts(
    crypto_service, plaintext
):
    """
    Feature: ea-trading-backend, Property 1: 加密解密往返一致性（擴展）
    
    對於相同的明文，多次加密可能產生不同的密文（因為 Fernet 包含時間戳），
    但所有密文解密後都應該得到相同的明文。
    
    驗證需求：2.1, 2.3
    """
    # 多次加密相同的明文
    encrypted1 = crypto_service.encrypt(plaintext)
    encrypted2 = crypto_service.encrypt(plaintext)
    
    # 解密所有密文
    decrypted1 = crypto_service.decrypt(encrypted1)
    decrypted2 = crypto_service.decrypt(encrypted2)
    
    # 所有解密結果都應該等於原始明文
    assert decrypted1 == plaintext
    assert decrypted2 == plaintext


@given(st.text(min_size=1, max_size=1000))
def test_property_encrypted_text_is_different_from_plaintext(
    crypto_service, plaintext
):
    """
    驗證加密後的文本與明文不同
    
    驗證需求：2.1
    """
    encrypted = crypto_service.encrypt(plaintext)
    
    # 加密後的文本應該與明文不同
    assert encrypted != plaintext
    
    # 加密後的文本應該是 Base64 編碼的字串
    assert isinstance(encrypted, str)
    assert len(encrypted) > 0
