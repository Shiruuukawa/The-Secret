import json
import os
import base64
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from resources import data_dir

DB_FILE   = os.path.join(data_dir(), "vault.enc")
SALT_FILE = os.path.join(data_dir(), "vault.salt")


def _get_salt() -> bytes:
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
    with open(SALT_FILE, "rb") as f:
        return f.read()


def _derive_key(password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_get_salt(),
        iterations=390000
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def load_vault(password: str) -> dict:
    if not os.path.exists(DB_FILE):
        return {"main_password": None, "backup_password": None, "categories": {}}
    try:
        cipher = Fernet(_derive_key(password))
        with open(DB_FILE, "rb") as f:
            return json.loads(cipher.decrypt(f.read()))
    except Exception:
        return None


def save_vault(password: str, data: dict) -> None:
    cipher = Fernet(_derive_key(password))
    with open(DB_FILE, "wb") as f:
        f.write(cipher.encrypt(json.dumps(data).encode()))


def vault_exists() -> bool:
    return os.path.exists(DB_FILE)
