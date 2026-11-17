"""Inicia API/worker de pruebas, ejecuta Playwright y cierra solo sus procesos."""
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    log_dir = ROOT / "private_data" / "e2e"
    log_dir.mkdir(parents=True, exist_ok=True)
    processes, logs = [], []
    try:
        # pytest elimina sus tablas al terminar; preparar el esquema antes de servir.
        subprocess.run([sys.executable, str(ROOT / "backend/tools/servidor_pruebas.py"), "inicializar"],
                       cwd=ROOT / "backend", check=True)
        for mode in ("api", "worker"):
            log = open(log_dir / f"{mode}.log", "w", encoding="utf-8")
            logs.append(log)
            processes.append(subprocess.Popen(
                [sys.executable, str(ROOT / "backend/tools/servidor_pruebas.py"), mode],
                cwd=ROOT / "backend", stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            ))
        for _ in range(60):
            try:
                urllib.request.urlopen("http://127.0.0.1:5001/api/v1/health", timeout=1).close()
                break
            except OSError:
                if any(p.poll() is not None for p in processes):
                    raise SystemExit("El servidor E2E no pudo iniciar; revisa private_data/e2e.")
                time.sleep(0.25)
        else:
            raise SystemExit("El servidor E2E no responde.")
        return subprocess.call([shutil.which("npm.cmd") or "npm", "run", "e2e"], cwd=ROOT / "frontend")
    finally:
        for process in processes:
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                else:
                    process.terminate()
                process.wait(timeout=10)
        for log in logs:
            log.close()


if __name__ == "__main__":
    raise SystemExit(main())
