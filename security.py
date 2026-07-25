"""
security.py — hashing password e token di sessione firmati.

Nessuna dipendenza esterna: usa solo la libreria standard di Python
(hashlib, hmac, secrets, base64, json, time). Pensato per essere semplice
da leggere e da sostituire con soluzioni più robuste (es. Argon2, JWT con
libreria dedicata) quando l'app va davvero in produzione.
"""
import hashlib
import hmac
import secrets
import base64
import json
import time

PBKDF2_ITERATIONS = 260_000
TOKEN_TTL_SECONDS = 60 * 60 * 12  # 12 ore


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Restituisce (salt_hex, hash_hex) per la password data."""
    if salt is None:
        salt = secrets.token_hex(16)
    salt_bytes = bytes.fromhex(salt)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, PBKDF2_ITERATIONS)
    return salt, digest.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    _, computed = hash_password(password, salt)
    return hmac.compare_digest(computed, expected_hash)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def make_token(payload: dict, secret: str) -> str:
    body = dict(payload)
    body['exp'] = int(time.time()) + TOKEN_TTL_SECONDS
    body_json = json.dumps(body, separators=(',', ':')).encode('utf-8')
    body_b64 = _b64url(body_json)
    sig = hmac.new(secret.encode('utf-8'), body_b64.encode('ascii'), hashlib.sha256).digest()
    sig_b64 = _b64url(sig)
    return f"{body_b64}.{sig_b64}"


def verify_token(token: str, secret: str) -> dict | None:
    try:
        body_b64, sig_b64 = token.split('.', 1)
    except ValueError:
        return None
    expected_sig = _b64url(hmac.new(secret.encode('utf-8'), body_b64.encode('ascii'), hashlib.sha256).digest())
    if not hmac.compare_digest(expected_sig, sig_b64):
        return None
    try:
        payload = json.loads(_b64url_decode(body_b64))
    except Exception:
        return None
    if payload.get('exp', 0) < time.time():
        return None
    return payload
