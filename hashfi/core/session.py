import secrets
import time
import tempfile
import shutil
import os
import hashlib
import base64
from typing import Optional, List, Dict
from hashfi.utils.crypto import (
    generate_salt,
    generate_session_hash,
    derive_key,
    encrypt_data,
    decrypt_data,
)


class SessionManager:
    def __init__(self):
        self._session_hash: Optional[str] = None
        self._salt: Optional[str] = None
        self._start_time: Optional[float] = None
        self.sandbox_path: Optional[str] = None
        self.vault_key: Optional[bytes] = None
        self.is_active = False

    def start_session(self):
        """Starts a new secure session."""
        self._salt = generate_salt()
        # Use system time and random bytes as entropy
        entropy = f"{time.time()}{secrets.token_hex(32)}"
        self._session_hash = generate_session_hash(self._salt, entropy)
        self._start_time = time.time()

        # Derive encryption key from session hash
        self.vault_key = derive_key(self._session_hash)

        # Create a secure sandbox directory
        self.sandbox_path = tempfile.mkdtemp(prefix="hashfi_session_")

        self.is_active = True
        print(f"[SessionManager] Session started. Hash: {self._session_hash[:8]}...")
        print(f"[SessionManager] Secure Workspace: {self.sandbox_path}")

    def store_secret(self, name: str, content: str) -> bool:
        """Encrypts and stores a secret in the sandbox."""
        if not self.is_active or not self.sandbox_path or not self.vault_key:
            return False

        try:
            encrypted_data = encrypt_data(self.vault_key, content)
            file_path = os.path.join(self.sandbox_path, f"{name}.enc")
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"[SessionManager] Failed to store secret: {e}")
            return False

    def get_secrets_list(self) -> List[str]:
        """Returns a list of stored secret names."""
        if not self.is_active or not self.sandbox_path:
            return []
        try:
            files = [
                f.replace(".enc", "")
                for f in os.listdir(self.sandbox_path)
                if f.endswith(".enc")
            ]
            return files
        except:
            return []

    def retrieve_secret(self, name: str) -> Optional[str]:
        """Retrieves and decrypts a secret."""
        if not self.is_active or not self.sandbox_path or not self.vault_key:
            return None

        file_path = os.path.join(self.sandbox_path, f"{name}.enc")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
            return decrypt_data(self.vault_key, encrypted_data)
        except Exception as e:
            print(f"[SessionManager] Failed to retrieve secret: {e}")
            return None

    def get_hash(self) -> Optional[str]:
        """Returns the current session hash."""
        return self._session_hash

    def get_sandbox(self) -> Optional[str]:
        return self.sandbox_path

    def derive_service_credential(
        self, service_name: str, length: int = 16
    ) -> Optional[str]:
        """Generates a deterministic password for a service based on the session hash."""
        if not self.is_active or not self._session_hash:
            return None

        # Combine session hash and service name
        data = f"{self._session_hash}:{service_name}".encode("utf-8")
        # Hash it
        digest = hashlib.sha256(data).digest()
        # Encode to base64 to make it printable
        b64 = base64.urlsafe_b64encode(digest).decode("utf-8")
        # Return the first 'length' characters
        return b64[:length]

    def burn_session(self):
        """Securely wipes the session hash."""
        if self._session_hash:
            # In a real low-level language, we'd overwrite memory.
            # In Python, we just dereference and hope GC picks it up,
            # but we can conceptually 'wipe' it.
            self._session_hash = None
            self._salt = None
            self._start_time = None
            self.vault_key = None  # Lose the key!

            # Nuke the sandbox
            if self.sandbox_path and os.path.exists(self.sandbox_path):
                try:
                    shutil.rmtree(self.sandbox_path)
                    print(f"[SessionManager] Sandbox {self.sandbox_path} INCINERATED.")
                except Exception as e:
                    print(f"[SessionManager] Failed to incinerate sandbox: {e}")
            self.sandbox_path = None

            self.is_active = False
            print("[SessionManager] Session BURNED.")

    def regenerate_session(self):
        """Burns the current session and starts a new one."""
        self.burn_session()
        self.start_session()
