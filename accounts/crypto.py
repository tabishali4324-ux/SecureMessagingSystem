import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings

ITERATIONS = 120_000
KEY_LENGTH_BYTES = 32
SALT_LENGTH = 16
IV_LENGTH = 12

def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH_BYTES,
        salt=salt,
        iterations=ITERATIONS,

    )
    return kdf.derive(password.encode("utf-8"))

def encrypt_message(plain_text: str, password: str) -> str:
    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(IV_LENGTH)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plain_text.encode("utf-8"), None)
    return ":".join([
        base64.b64encode(salt).decode(),
        base64.b64encode(iv).decode(),
        base64.b64encode(ciphertext).decode(),
    ])

def decrypt_message(encrypted_text: str, password: str) -> str:
    parts = encrypted_text.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid encrypted message.")
    salt = base64.b64decode(parts[0])
    iv = base64.b64decode(parts[1])
    ciphertext = base64.b64decode(parts[2])
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")