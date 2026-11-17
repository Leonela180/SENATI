"""Copia Safetensors a FP16 por bloques, sin cargar el modelo completo."""
import json
import math
from pathlib import Path
import shutil
import struct
import uuid

from .interface import EngineError
from .resources import available_ram_gib


def compact_safetensors(source, destination):
    import numpy as np
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise ValueError("El destino ya existe; no se sobrescribe.")
    lowest = available_ram_gib()
    if lowest is None or lowest < 1.2:
        raise EngineError("memoria_insuficiente")
    partial = destination.with_name(destination.name + f".{uuid.uuid4().hex}.partial")
    try:
        with source.open("rb") as original:
            header_length = struct.unpack("<Q", original.read(8))[0]
            if header_length > 16 * 1024**2:
                raise ValueError("Cabecera demasiado grande.")
            header = json.loads(original.read(header_length))
            data_start = 8 + header_length
            tensors = sorted(((name, item) for name, item in header.items() if name != "__metadata__"),
                             key=lambda entry: entry[1]["data_offsets"][0])
            new_header, offset = {}, 0
            if "__metadata__" in header:
                new_header["__metadata__"] = header["__metadata__"]
            for name, item in tensors:
                lo, hi = item["data_offsets"]
                if not 0 <= lo <= hi <= source.stat().st_size - data_start:
                    raise ValueError("Offsets inválidos.")
                length = hi - lo
                if item["dtype"] == "F32":
                    if length != math.prod(item["shape"]) * 4:
                        raise ValueError("Forma de tensor inválida.")
                    length //= 2
                new_header[name] = {**item, "dtype": "F16" if item["dtype"] == "F32" else item["dtype"],
                                    "data_offsets": [offset, offset + length]}
                offset += length
            if shutil.disk_usage(destination.parent).free < offset + 512 * 1024**2:
                raise EngineError("espacio_insuficiente")
            encoded = json.dumps(new_header, separators=(",", ":")).encode("utf-8")
            encoded += b" " * (-len(encoded) % 8)
            with partial.open("xb") as output:
                output.write(struct.pack("<Q", len(encoded)))
                output.write(encoded)
                for _, item in tensors:
                    lo, hi = item["data_offsets"]
                    original.seek(data_start + lo)
                    remaining = hi - lo
                    while remaining:
                        free = available_ram_gib()
                        if free is None or free < 0.8:
                            raise EngineError("memoria_insuficiente")
                        lowest = min(lowest, free)
                        chunk = original.read(min(16 * 1024**2, remaining))
                        if not chunk:
                            raise ValueError("Archivo truncado.")
                        if item["dtype"] == "F32":
                            values = np.frombuffer(chunk, dtype="<f4")
                            if not np.isfinite(values).all() or np.abs(values).max(initial=0) > 65504:
                                raise ValueError("Pesos fuera del rango FP16.")
                            output.write(values.astype("<f2").tobytes())
                        else:
                            output.write(chunk)
                        remaining -= len(chunk)
        partial.rename(destination)
    finally:
        partial.unlink(missing_ok=True)
    return {"bytes": destination.stat().st_size, "ram_free_min_gib": round(lowest, 2)}
