"""
生成加密金鑰腳本
用於生成 Fernet 加密金鑰
"""
from cryptography.fernet import Fernet


def generate_key():
    """生成新的 Fernet 加密金鑰"""
    key = Fernet.generate_key().decode()
    print("生成的加密金鑰：")
    print(key)
    print("\n請將此金鑰添加到 .env 檔案中的 ENCRYPTION_KEY 變數")
    return key


if __name__ == "__main__":
    generate_key()
