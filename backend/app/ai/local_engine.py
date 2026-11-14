import logging
import os
import time
import diffusers
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image, ImageOps
from .interface import EngineError, HumanizationEngine, save_labeled
from .prompts import DEFAULT_SEED, NEGATIVE, POSITIVE, PRESETS, WORK_SIDE

log = logging.getLogger("lumia.engine")
CPU_WORK_SIDE = 512                                              # sin GPU (laptop con Radeon/16 GB): imagen de trabajo más pequeña


class LocalHumanizationEngine(HumanizationEngine):
    def __init__(self, model_path: str, model_id: str):
        self.model_id = model_id or "stable-diffusion-v1-5"
        self.model_version = f"diffusers-{diffusers.__version__}"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.safety_checker_active = True
        try:
            if os.path.isfile(model_path):                        # un solo archivo .safetensors (p. ej. v1-5-pruned-emaonly)
                single = dict(config=os.path.join(os.path.dirname(model_path), "stable-diffusion-v1-5"),
                              original_config=os.path.join(os.path.dirname(model_path), "v1-inference.yaml"),
                              torch_dtype=dtype, local_files_only=True)
                try:                                              # el filtro de seguridad va activo (informe 4.5)
                    self.pipe = StableDiffusionImg2ImgPipeline.from_single_file(model_path, **single)
                except Exception:                                 # sin pesos del filtro: se carga sin él y queda registrado
                    self.pipe = StableDiffusionImg2ImgPipeline.from_single_file(model_path, safety_checker=None, **single)
                if getattr(self.pipe, "safety_checker", None) is None:
                    self.safety_checker_active = False
            else:
                base = dict(torch_dtype=dtype, use_safetensors=True, local_files_only=True)
                try:                                              # la guía descarga solo los pesos fp16; en CPU se convierten a fp32
                    self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_path, variant="fp16", **base)
                except Exception:
                    self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_path, **base)
        except Exception as e:                                    # pesos ausentes o dañados (CP-09)
            raise EngineError("modelo_no_disponible") from e
        if not self.safety_checker_active:
            log.warning("Filtro de seguridad del modelo NO disponible: se registra en cada trabajo")
        self.pipe = self.pipe.to(self.device)
        if not hasattr(torch.nn.functional, "scaled_dot_product_attention"):
            self.pipe.enable_attention_slicing()
        self.pipe.set_progress_bar_config(disable=True)

    def humanize(self, input_path, output_path, preset, seed=None):
        p = PRESETS.get(preset, PRESETS["natural"])
        seed = DEFAULT_SEED if seed is None else int(seed)
        src = ImageOps.exif_transpose(Image.open(input_path))
        info = dict(src.info)
        src = src.convert("RGB")
        w, h = src.size
        side = WORK_SIDE if self.device == "cuda" else CPU_WORK_SIDE
        k = side / min(w, h)
        work_size = (max(64, int(w * k) // 8 * 8), max(64, int(h * k) // 8 * 8))
        work = src.resize(work_size, Image.LANCZOS)
        generator = torch.Generator(device=self.device).manual_seed(seed)
        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        t0 = time.perf_counter()
        try:
            res = self.pipe(prompt=POSITIVE, negative_prompt=NEGATIVE, image=work,
                            strength=p["strength"], guidance_scale=p["guidance"],
                            num_inference_steps=p["steps"], generator=generator)
        except torch.cuda.OutOfMemoryError as e:
            raise EngineError("gpu_memoria") from e
        if any(getattr(res, "nsfw_content_detected", None) or []):
            raise EngineError("contenido_bloqueado")
        out = res.images[0].resize((w, h), Image.LANCZOS)          # vuelve al tamaño original
        save_labeled(out, output_path, info)
        vram = torch.cuda.max_memory_allocated() / 1e9 if self.device == "cuda" else 0.0
        return {"model_id": self.model_id, "model_version": self.model_version, "preset": preset,
                **p, "seed": seed, "work_size": list(work_size), "device": self.device,
                "seconds": round(time.perf_counter() - t0, 2), "vram_gb": round(vram, 2),
                "filtro_seguridad": self.safety_checker_active}
