"""Humanización SD 1.5 con pesos en disco y procesos que liberan la RAM.

El filtro CLIP se ejecuta antes y después, separado de la difusión. Solo se
publica un resultado si ambos controles terminan y lo aprueban.
"""
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import sys
import shutil
import tempfile
import time

from PIL import Image, ImageOps
from .interface import EngineError, HumanizationEngine, save_labeled
from .processes import run_limited
from .prompts import DEFAULT_SEED, NEGATIVE, POSITIVE, PRESETS
from .facial_detail import enhance_facial_detail


@contextmanager
def temporary_workspace(parent, diagnostics=None):
    with tempfile.TemporaryDirectory(dir=parent, prefix="job_") as temporary:
        try:
            yield temporary
        except Exception:
            if diagnostics is not None:
                for log in Path(temporary).glob("*.log"):
                    shutil.copyfile(log, Path(diagnostics) / log.name)
            raise


@contextmanager
def exclusive_inference(path):
    with open(path, "a+b") as lock:
        try:
            if os.fstat(lock.fileno()).st_size == 0:
                lock.write(b"0")
                lock.flush()
            lock.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise EngineError("motor_ocupado") from None
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == "nt":
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def prepare_image(source, side):
    image = source.copy()
    image.thumbnail((side, side), Image.Resampling.LANCZOS)
    width = max(64, math.ceil(image.width / 64) * 64)
    height = max(64, math.ceil(image.height / 64) * 64)
    left, top = (width - image.width) // 2, (height - image.height) // 2
    work = ImageOps.expand(image, (left, top, width - image.width - left, height - image.height - top), fill=image.getpixel((0, 0)))
    return work, (left, top, left + image.width, top + image.height)


class LiteHumanizationEngine(HumanizationEngine):
    model_id = "stable-diffusion-v1-5-q4_0"
    model_version = "stable-diffusion.cpp-local"
    device = "cpu"

    def __init__(self, executable, model_path, models_dir, scratch_dir, side=384, blend=0.35, detail_intensity=.65):
        self.executable, self.model_path = Path(executable), Path(model_path)
        self.model_id = f"stable-diffusion-v1-5:{self.model_path.stem}"
        self.models_dir, self.scratch = Path(models_dir), Path(scratch_dir)
        if side not in (256, 320, 384, 448, 512) or not 0.1 <= blend <= 1 or not 0 <= detail_intensity <= 1:
            raise EngineError("parametros_invalidos")
        self.side, self.blend = side, blend
        self.detail_intensity = detail_intensity
        if not self.executable.is_file() or not self.model_path.is_file():
            raise EngineError("modelo_no_disponible")
        with self.model_path.open("rb") as stream:
            magic = stream.read(4)
            if magic != b"GGUF":
                import struct
                stream.seek(0)
                try:
                    length = struct.unpack("<Q", stream.read(8))[0]
                    if not 2 <= length <= 16 * 1024**2:
                        raise ValueError()
                    header = json.loads(stream.read(length))
                    if not isinstance(header, dict) or not any(name.startswith("model.diffusion_model.") for name in header):
                        raise ValueError()
                except (ValueError, OSError, struct.error):
                    raise EngineError("modelo_no_disponible") from None
        if not (self.models_dir / "safety_checker/model.fp16.safetensors").is_file():
            raise EngineError("filtro_no_disponible")
        self.scratch.mkdir(parents=True, exist_ok=True)

    def check_safety(self, image, directory, stage):
        report_path = directory / f"safety_{stage}.json"
        try:
            stats = run_limited([sys.executable, "-m", "app.ai.safety_worker", "--image", image,
                                 "--models", self.models_dir, "--report", report_path],
                                directory / f"safety_{stage}.log", timeout=180, start_free_gib=1.5)
        except EngineError as error:
            error.phase = f"safety_{stage}"
            raise
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise EngineError("filtro_no_disponible") from None
        if not isinstance(report, dict) or report.get("approved") is not True:
            if not isinstance(report, dict):
                raise EngineError("filtro_no_disponible")
            raise EngineError("contenido_bloqueado" if report.get("code") == "contenido_bloqueado" else "filtro_no_disponible")
        return stats

    def humanize(self, input_path, output_path, preset, seed=None, mode="humanizar"):
        started = time.monotonic()
        parameters = PRESETS.get(preset, PRESETS["natural"])
        positive, negative = POSITIVE, NEGATIVE
        if mode == "realista":
            parameters = {"strength": .78, "steps": 32, "guidance": 7.0}
            positive = ("Photorealistic editorial photograph of an adult human person inspired by the input animated character, "
                        "real human facial proportions, realistic small eyes, natural skin pores, lifelike fabric and hair, "
                        "preserve the general hairstyle, outfit colors, pose and composition, soft cinematic natural lighting, "
                        "high quality photography, realistic anatomy, adult.")
            negative = NEGATIVE + ", illustration, painting, animation, 3D render, giant eyes, doll, child"
        seed = DEFAULT_SEED if seed is None else int(seed)
        with exclusive_inference(self.scratch / "humanization.lock"), temporary_workspace(self.scratch, getattr(self, "diagnostics", None)) as temporary:
            directory = Path(temporary)
            with Image.open(input_path) as source:
                oriented = ImageOps.exif_transpose(source)
                original = oriented.convert("RGB")
                info = dict(oriented.info)
            work, crop = prepare_image(original, self.side)
            source_path, raw_path = directory / "input.png", directory / "raw.png"
            work.save(source_path)
            safety_input = self.check_safety(source_path, directory, "input")
            (directory / "prompt.txt").write_text(positive, encoding="utf-8")
            (directory / "negative.txt").write_text(negative, encoding="utf-8")
            inference = run_limited([
                self.executable, "--model", self.model_path, "--backend", "cpu", "--params-backend", "cpu" if mode == "realista" else "disk",
                *(["--mmap"] if mode == "realista" else []),
                "--disable-prefetch", "--threads", "2",
                *(["--linear-scale", "0.0078125", "--attn-scale", "0.0078125"] if mode == "realista" else []),
                "--flash-attn", "auto", "--init-img", source_path, "--output", raw_path,
                "--width", str(work.width), "--height", str(work.height), "--steps", str(parameters["steps"]),
                "--strength", str(parameters["strength"]), "--cfg-scale", str(parameters["guidance"]),
                "--seed", str(seed), "--prompt-file", directory / "prompt.txt", "--negative-prompt-file", directory / "negative.txt",
            ], directory / "inference.log", timeout=900, cwd=self.executable.parent)
            if not raw_path.is_file():
                raise EngineError("resultado_inexistente")
            with Image.open(raw_path) as generated:
                generated.load()
                if generated.size != work.size:
                    raise EngineError("resultado_inexistente")
                result = generated.convert("RGB").crop(crop).resize(original.size, Image.Resampling.LANCZOS)
            if mode == "realista":
                detail_metadata = {"conversion_mode": "ilustracion_a_realista"}
            else:
                result = Image.blend(original, result, self.blend)
                result, detail_metadata = enhance_facial_detail(original, result, self.detail_intensity, seed)
            result_path = directory / "result.png"
            result.save(result_path)
            safety_output = self.check_safety(result_path, directory, "output")
            save_labeled(result, output_path, info)
        return {"model_id": self.model_id, "model_version": self.model_version,
                **parameters, "seed": seed, "work_size": list(work.size), "device": "cpu", "vram_gb": 0,
                "seconds": round(time.monotonic() - started, 2), "filtro_seguridad": True,
                "runtime": "cpp", "blend": 1.0 if mode == "realista" else self.blend, **detail_metadata,
                "ram_free_min_gib": min(item["ram_free_min_gib"] for item in (safety_input, inference, safety_output))}
