"""Conversión de personajes con offload CPU/disco y publicación tras dos filtros."""
from pathlib import Path
import sys
import time
from PIL import Image, ImageOps
from .interface import EngineError, HumanizationEngine, save_labeled
from .lite_engine import exclusive_inference, temporary_workspace, prepare_image
from .processes import run_limited

POSITIVE = (
    "natural documentary photographic portrait of an adult human person inspired by the input character, "
    "preserve the general hairstyle and outfit colors and composition, realistic human facial proportions, "
    "relaxed expression, both eyes naturally open, clear realistic irises, round aligned pupils, "
    "consistent gaze, small natural window catchlights, soft frontal window lighting evenly illuminating "
    "the eyes and face, subtle authentic skin pores, individual hair strands, detailed woven clothing fabric"
)
NEGATIVE = (
    "cartoon, anime, drawing, illustration, 3d render, giant eyes, doll, distorted face, deformed, "
    "crossed eyes, misaligned pupils, asymmetric eyes, double pupils, empty eyes, black eye sockets, "
    "harsh shadows on eyes, glossy plastic skin, beauty retouch, child"
)


class RealisticEngine(HumanizationEngine):
    def __init__(self, safety_engine, model_path):
        self.safety = safety_engine
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            raise EngineError("modelo_no_disponible")

    def humanize(self, input_path, output_path, preset="natural", seed=None, character="adult_person"):
        started = time.monotonic()
        seed = 1234 if seed is None else int(seed)
        subject = {"adult_person": "adult human person", "adult_man": "adult man", "adult_woman": "adult woman"}.get(character)
        if not subject:
            raise EngineError("parametros_invalidos")
        scratch = self.safety.scratch
        with exclusive_inference(scratch / "humanization.lock"), temporary_workspace(scratch, getattr(self.safety, "diagnostics", None)) as temp:
            directory = Path(temp)
            with Image.open(input_path) as source:
                oriented = ImageOps.exif_transpose(source)
                original, info = oriented.convert("RGB"), dict(oriented.info)
            # SD1.5 necesita esta escala para no producir patrones abstractos.
            if min(original.size) < 256:
                raise EngineError("parametros_invalidos")
            work, crop = prepare_image(original, 512)
            src, raw = directory / "input.png", directory / "raw.png"
            work.save(src)
            first = self.safety.check_safety(src, directory, "input")
            (directory / "prompt.txt").write_text(POSITIVE.replace("adult human person", subject), encoding="utf-8")
            (directory / "negative.txt").write_text(NEGATIVE, encoding="utf-8")
            stats = run_limited([sys.executable, "-m", "app.ai.diffusers_probe",
                "--model", self.model_path, "--config", self.safety.models_dir,
                "--image", src, "--output", raw, "--seed", str(seed),
                "--prompt-file", directory / "prompt.txt", "--negative-file", directory / "negative.txt"],
                directory / "inference.log", timeout=900, cwd=Path(__file__).resolve().parents[2])
            if not raw.is_file():
                raise EngineError("resultado_inexistente")
            with Image.open(raw) as generated:
                if generated.size != work.size:
                    raise EngineError("resultado_inexistente")
                result = generated.convert("RGB").crop(crop)
            # No copiar ojos de dibujo ni agrandar artificialmente la salida.
            checked = directory / "checked.png"
            result.save(checked)
            last = self.safety.check_safety(checked, directory, "output")
            save_labeled(result, output_path, info)
        return {"model_id": "stable-diffusion-v1-5", "model_version": "compact-fp16-cpu-offload-v1",
                "seconds": round(time.monotonic()-started, 2), "device": "cpu", "vram_gb": 0,
                "runtime": "diffusers_disk_offload", "seed": seed, "strength": .74, "steps": 28, "guidance": 6.5,
                "work_size": list(work.size), "width": result.width, "height": result.height,
                "blend": 1.0, "filtro_seguridad": True, "conversion_mode": "ilustracion_a_realista",
                "ram_free_min_gib": min(s["ram_free_min_gib"] for s in (first, stats, last))}
