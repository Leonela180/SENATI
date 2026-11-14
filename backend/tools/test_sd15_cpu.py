import ctypes
import os
import time
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "v1-5-pruned-emaonly.safetensors"
ORIGINAL_CONFIG = ROOT / "models" / "v1-inference.yaml"
DIFFUSERS_CONFIG = ROOT / "models" / "stable-diffusion-v1-5"
OUTPUT_DIR = ROOT / "private_data" / "results"
MIN_FREE_RAM_GIB = 10


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def available_ram_gib():
    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
    kernel32.GlobalMemoryStatusEx.restype = ctypes.c_int
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError(ctypes.get_last_error())
    return status.ullAvailPhys / (1024**3)


def main():
    required_files = (
        MODEL_PATH,
        ORIGINAL_CONFIG,
        DIFFUSERS_CONFIG / "model_index.json",
        DIFFUSERS_CONFIG / "tokenizer" / "vocab.json",
        DIFFUSERS_CONFIG / "tokenizer" / "merges.txt",
        DIFFUSERS_CONFIG / "tokenizer" / "tokenizer_config.json",
        DIFFUSERS_CONFIG / "tokenizer" / "special_tokens_map.json",
        DIFFUSERS_CONFIG / "text_encoder" / "config.json",
        DIFFUSERS_CONFIG / "scheduler" / "scheduler_config.json",
        DIFFUSERS_CONFIG / "unet" / "config.json",
    )
    missing = [str(path) for path in required_files if not path.is_file()]
    if missing:
        raise FileNotFoundError("Faltan archivos locales del modelo: " + ", ".join(missing))

    free_gib = available_ram_gib()
    print(f"FREE_RAM_GIB={free_gib:.2f}")
    if free_gib < MIN_FREE_RAM_GIB:
        raise SystemExit(
            f"Memoria insuficiente: se requieren al menos {MIN_FREE_RAM_GIB} GiB libres "
            "para intentar la carga segura; no se cargó el modelo."
        )

    import torch
    from diffusers import StableDiffusionImg2ImgPipeline
    from PIL import Image, ImageChops

    from app.ai.prompts import NEGATIVE, POSITIVE

    if torch.cuda.is_available():
        raise RuntimeError("CUDA quedó visible a pesar de la configuración CPU-only.")

    image = Image.new("RGB", (256, 256), color=(245, 235, 225))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "cpu_sd15_test.png"
    source_path = OUTPUT_DIR / "cpu_sd15_source.png"
    image.save(source_path)

    load_start = time.perf_counter()
    pipe = StableDiffusionImg2ImgPipeline.from_single_file(
        str(MODEL_PATH),
        config=str(DIFFUSERS_CONFIG),
        original_config=str(ORIGINAL_CONFIG),
        torch_dtype=torch.float32,
        safety_checker=None,
        local_files_only=True,
    ).to("cpu")
    if not hasattr(torch.nn.functional, "scaled_dot_product_attention"):
        pipe.enable_attention_slicing()
    pipe.set_progress_bar_config(disable=True)
    load_seconds = time.perf_counter() - load_start

    inference_start = time.perf_counter()
    with torch.inference_mode():
        result = pipe(
            prompt=POSITIVE,
            negative_prompt=NEGATIVE,
            image=image,
            strength=0.45,
            guidance_scale=7.5,
            num_inference_steps=4,
            output_type="pil",
        )
    image_out = result.images[0]
    inference_seconds = time.perf_counter() - inference_start
    image_out.save(output_path)

    changed = ImageChops.difference(image, image_out).getbbox() is not None
    if not output_path.is_file() or output_path.stat().st_size == 0 or not changed:
        raise RuntimeError("La inferencia no produjo una imagen nueva válida.")

    print(f"MODEL={MODEL_PATH}")
    print(f"PIPELINE={type(pipe).__name__}")
    print(f"LOAD_SECONDS={load_seconds:.2f}")
    print(f"INFERENCE_SECONDS={inference_seconds:.2f}")
    print(f"OUTPUT={output_path}")
    print(f"SIZE={image_out.size}")
    print(f"FILE_SIZE={output_path.stat().st_size}")
    print(f"IMAGE_CHANGED={changed}")


if __name__ == "__main__":
    main()
