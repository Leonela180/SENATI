import secrets
from pathlib import Path
from flask import current_app

KINDS = ("originals", "results")


def new_key(ext: str) -> str:
    return f"{secrets.token_hex(16)}.{ext}"            # nombre aleatorio, sin datos del usuario (RF-08)


def path_for(kind: str, key: str) -> Path:
    if kind not in KINDS or not key or "/" in key or "\\" in key or ".." in key:
        raise ValueError("clave de almacenamiento inválida")   # evita path traversal
    return current_app.config["PRIVATE_STORAGE_ROOT"] / kind / key


def save_bytes(kind: str, key: str, data: bytes) -> None:
    path_for(kind, key).write_bytes(data)
