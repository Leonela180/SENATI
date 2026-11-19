"""Experimento privado y acotado; no activa el modo en la web."""
from pathlib import Path
import sys
import time
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from app.config import Config, ROOT
from app.ai.lite_engine import LiteHumanizationEngine, exclusive_inference, prepare_image
from app.ai.processes import run_limited
from app.ai.interface import EngineError

folder = ROOT / "private_data" / "prueba_diffusers" / time.strftime("%Y%m%d_%H%M%S")
folder.mkdir(parents=True, exist_ok=True)
engine = LiteHumanizationEngine(Config.AI_CPP_EXECUTABLE, Config.AI_CPP_MODEL_PATH,
                                ROOT / "models/stable-diffusion-v1-5", Config.PRIVATE_STORAGE_ROOT / "lite_jobs", side=256)
try:
    with exclusive_inference(engine.scratch / "humanization.lock"):
        original = Image.open(ROOT / "private_data/experiments/ilustracion.png").convert("RGB")
        prepared, crop = prepare_image(original, 512)
        source, result = folder / "input.png", folder / "resultado.png"
        prepared.save(source)
        engine.check_safety(source, folder, "input")
        stats = run_limited([sys.executable, "-m", "app.ai.diffusers_probe",
            "--model", ROOT / "models/sd15-compact.safetensors",
            "--config", ROOT / "models/stable-diffusion-v1-5",
            "--image", source, "--output", result], folder / "pytorch.log",
            cwd=ROOT / "backend", timeout=900)
        engine.check_safety(result, folder, "output")
        report = {"estado": "prueba_tecnica_completa", "stats": stats, "calidad_visual": "pendiente"}
except EngineError as error:
    report = {"estado": "bloqueado", "error_code": error.code, "phase": getattr(error, "phase", None)}
(folder / "reporte.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report), flush=True)
print("Evidencia:", folder)
