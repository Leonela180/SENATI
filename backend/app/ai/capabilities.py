"""Disponibilidad de funciones sin cargar los motores de inferencia."""
from pathlib import Path


def realistic_available(config):
    return (config.get("AI_REALISTIC_ENABLED", False)
            and config.get("AI_ENGINE") == "local"
            and config.get("AI_LOCAL_RUNTIME") == "cpp"
            and Path(config.get("AI_REALISTIC_MODEL_PATH", "")).is_file())
