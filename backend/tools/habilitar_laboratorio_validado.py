"""Activa solo este servidor tras comprobar el trabajo real DEMO, sin imprimir .env."""
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import set_key
from app.config import ROOT

folder = ROOT / "private_data/demo_senati"
report = json.loads((folder / "conversion-real-hombre.json").read_text(encoding="utf-8"))
assert report["status"] == "completed"
assert report["parameters"]["filtro_seguridad"] is True
assert report["parameters"]["runtime"] == "diffusers_disk_offload"
assert (folder / "conversion-real-hombre.png").is_file()
target = ROOT / ".env"
backup = folder / "env_antes_laboratorio_validado.backup"
if not backup.exists():
    shutil.copyfile(target, backup)
set_key(str(target), "AI_REALISTIC_ENABLED", "1", quote_mode="never")
set_key(str(target), "TRUST_PROXY", "1", quote_mode="never")
report["visual_review_agent"] = "Revisado como ejemplo fotografico experimental; aceptacion de la usuaria pendiente. No se garantiza identidad ni calidad universal."
(folder / "conversion-real-hombre.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("Laboratorio habilitado en la configuracion local tras prueba real. Requiere reiniciar API; no se cambiaron claves ni AI_ENGINE.")
