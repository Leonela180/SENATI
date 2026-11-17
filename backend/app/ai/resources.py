"""Comprobaciones de memoria antes de cargar el motor local; sin dependencias pesadas."""
import ctypes
import os

from .interface import EngineError


def available_ram_gib():
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                (name, ctypes.c_ulonglong) for name in
                ("total", "available", "page_total", "page_available", "virtual_total", "virtual_available", "extended")
            ]
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
        return status.available / 1024 ** 3
    try:
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 1024 ** 3
    except (AttributeError, OSError, ValueError):
        return None


def require_memory(minimum_gib=6.0):
    available = available_ram_gib()
    if available is not None and available < minimum_gib:
        raise EngineError("memoria_insuficiente")
    return available
