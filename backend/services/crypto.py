"""NBLM — AES-256-GCM encryption for credentials."""
import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from backend.config import settings

def _get_key() -> bytes:
    key = settings.ENCRYPTION_KEY
    if not key:
        raise ValueError("ENCRYPTION_KEY not set in .env")
    return bytes.fromhex(key)

def encrypt_value(plaintext: str) -> dict:
    key = _get_key()
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(iv, plaintext.encode(), None)
    return {"encrypted": base64.b64encode(ct).decode(), "iv": iv.hex()}

def decrypt_value(encrypted_b64: str, iv_hex: str) -> str:
    key = _get_key()
    iv = bytes.fromhex(iv_hex)
    ct = base64.b64decode(encrypted_b64)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ct, None).decode()
