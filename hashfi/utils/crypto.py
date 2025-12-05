import hashlib
import secrets
import base64
from cryptography.fernet import Fernet


def generate_salt(length: int = 16) -> str:
    """Generates a random salt."""
    return secrets.token_hex(length)


def generate_session_hash(salt: str, entropy: str) -> str:
    """Generates a SHA-256 hash from salt and entropy."""
    data = f"{salt}{entropy}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def derive_key(session_hash: str) -> bytes:
    """Derives a Fernet-compatible key from the session hash."""
    # Fernet requires a 32-byte url-safe base64-encoded key.
    # We take the SHA256 of the session hash (which is already hex) to get 32 bytes,
    # then base64 encode it.
    digest = hashlib.sha256(session_hash.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_data(key: bytes, plaintext: str) -> bytes:
    """Encrypts plaintext using the provided key."""
    f = Fernet(key)
    return f.encrypt(plaintext.encode())


def decrypt_data(key: bytes, ciphertext: bytes) -> str:
    """Decrypts ciphertext using the provided key."""
    f = Fernet(key)
    return f.decrypt(ciphertext).decode()


def secure_wipe(data: bytearray):
    """Overwrites a bytearray with zeros."""
    for i in range(len(data)):
        data[i] = 0
