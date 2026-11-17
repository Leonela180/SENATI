"""Procesos de inferencia aislados, con memoria y tiempo vigilados."""
import os
import subprocess
import time

from .interface import EngineError
from .resources import available_ram_gib


def run_limited(command, log_path, timeout=900, minimum_free_gib=0.8, start_free_gib=2.0, cwd=None):
    free = available_ram_gib()
    if free is None or free < start_free_gib:
        raise EngineError("memoria_insuficiente")
    lowest = free
    env = os.environ.copy()
    env.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
    started = time.monotonic()
    process = None
    with open(log_path, "w", encoding="utf-8") as log:
        try:
            process = subprocess.Popen([str(part) for part in command], cwd=cwd, env=env,
                                       stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            while process.poll() is None:
                available = available_ram_gib()
                if available is not None:
                    lowest = min(lowest, available)
                    if available < minimum_free_gib:
                        raise EngineError("memoria_insuficiente")
                if time.monotonic() - started > timeout:
                    raise EngineError("tiempo_agotado")
                time.sleep(0.25)
            if process.returncode:
                raise EngineError("motor_error")
        finally:
            if process is not None and process.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                else:
                    process.terminate()
                process.wait(timeout=10)
            log.write(f"\nLUMIA: seconds={time.monotonic() - started:.2f}; min_free_gib={lowest:.2f}; exit_code={process.returncode if process else None}\n")
            log.flush()
    return {"seconds": round(time.monotonic() - started, 2), "ram_free_min_gib": round(lowest, 2)}
