import argparse
import ctypes
import json
import math
import os
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = ROOT / "models" / "v1-5-pruned-emaonly.safetensors"
DEFAULT_SD_CLI = ROOT / "private_data" / "tools" / "stable-diffusion.cpp" / "sd-cli.exe"
MIN_START_FREE_GIB = 4.5
MIN_FREE_GIB = 1.5
MAX_INPUT_PIXELS = 24_000_000
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

POSITIVE_PROMPT = (
    "Subtle photorealistic skin-detail refinement of the same adult person. Preserve the person's "
    "identity, facial geometry, expression, eyes, nose, mouth, age, skin tone, hairstyle, pose, "
    "framing, clothing, background, and lighting. Refine only natural visible pores, fine skin "
    "microtexture, and very subtle natural tonal variation. Realistic soft illumination, natural "
    "skin, no beauty retouching, no changes to facial features or composition."
)
NEGATIVE_PROMPT = (
    "different person, identity change, changed face shape, changed expression, altered eyes, "
    "altered nose, altered mouth, different age, different skin tone, different hairstyle, "
    "changed pose, changed framing, changed clothing, changed background, plastic skin, waxy skin, "
    "airbrushed skin, excessive pores, beauty filter, makeup, distortion, artifacts, blur, text"
)


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
    if os.name != "nt":
        raise OSError("This monitored test currently requires Windows.")
    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
    kernel32.GlobalMemoryStatusEx.restype = ctypes.c_int
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError(ctypes.get_last_error())
    return status.ullAvailPhys / (1024**3)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare a CPU-only SD 1.5 img2img skin-quality comparison."
    )
    parser.add_argument("--input", required=True, type=Path, help="Local PNG, JPEG, or WebP image")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--sd-cli", type=Path, default=DEFAULT_SD_CLI)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "private_data" / "results" / "skin_quality",
    )
    parser.add_argument("--strength", type=float, default=0.25)
    parser.add_argument("--steps", type=int, default=16)
    parser.add_argument("--cfg", type=float, default=5.5)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--max-side", type=int, default=512)
    return parser.parse_args()


def load_input(path):
    path = path.expanduser().resolve(strict=True)
    with Image.open(path) as probe:
        image_format = probe.format
        frame_count = getattr(probe, "n_frames", 1)
        size = probe.size
        probe.verify()

    if image_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported input format {image_format!r}; use PNG, JPEG, or WebP."
        )
    if frame_count != 1:
        raise ValueError("Animated images are not supported; provide a single-frame image.")
    if size[0] <= 0 or size[1] <= 0 or size[0] * size[1] > MAX_INPUT_PIXELS:
        raise ValueError(f"Image dimensions {size} are invalid or exceed the pixel limit.")

    with Image.open(path) as source:
        oriented = ImageOps.exif_transpose(source)
        rgba = oriented.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, rgba).convert("RGB")
    return path, image, image_format


def prepare_work_image(image, max_side, path):
    scale = min(1.0, max_side / max(image.size))
    content_size = (
        max(1, int(round(image.width * scale))),
        max(1, int(round(image.height * scale))),
    )
    if min(content_size) < 64:
        raise ValueError("The shorter image side must be at least 64 pixels after resizing.")

    content = image.resize(content_size, Image.Resampling.LANCZOS)
    work_size = (
        int(math.ceil(content.width / 8) * 8),
        int(math.ceil(content.height / 8) * 8),
    )
    left = (work_size[0] - content.width) // 2
    top = (work_size[1] - content.height) // 2
    corners = [
        content.getpixel((0, 0)),
        content.getpixel((content.width - 1, 0)),
        content.getpixel((0, content.height - 1)),
        content.getpixel((content.width - 1, content.height - 1)),
    ]
    fill = tuple(sum(pixel[channel] for pixel in corners) // len(corners) for channel in range(3))
    work = Image.new("RGB", work_size, fill)
    work.paste(content, (left, top))
    work.save(path, format="PNG")
    return content_size, work_size, (left, top)


def stop_exact_pid(pid, process):
    command = f"Stop-Process -Id {int(pid)} -Force"
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and process.poll() is None:
        raise RuntimeError(
            f"Could not stop test PID {pid}: {result.stderr.strip() or result.stdout.strip()}"
        )


def make_comparison(original, result, path):
    preview_width = min(512, original.width)
    scale = preview_width / original.width
    preview_size = (preview_width, max(1, int(round(original.height * scale))))
    original_preview = original.resize(preview_size, Image.Resampling.LANCZOS)
    result_preview = result.resize(preview_size, Image.Resampling.LANCZOS)
    label_height = 30
    comparison = Image.new(
        "RGB",
        (preview_width * 2, preview_size[1] + label_height),
        (28, 28, 28),
    )
    comparison.paste(original_preview, (0, label_height))
    comparison.paste(result_preview, (preview_width, label_height))
    draw = ImageDraw.Draw(comparison)
    draw.text((8, 8), "Original", fill=(255, 255, 255))
    draw.text((preview_width + 8, 8), "SD 1.5 result", fill=(255, 255, 255))
    comparison.save(path, format="PNG")


def elapsed_from_log(text, pattern):
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def main():
    args = parse_args()
    if not 0.0 < args.strength <= 1.0:
        raise ValueError("--strength must be greater than 0 and at most 1.")
    if not 12 <= args.steps <= 20:
        raise ValueError("--steps must be between 12 and 20 for this quality test.")
    if not 1.0 <= args.cfg <= 12.0:
        raise ValueError("--cfg must be between 1 and 12.")
    if args.seed < 0:
        raise ValueError("--seed must be non-negative.")
    if not 64 <= args.max_side <= 768:
        raise ValueError("--max-side must be between 64 and 768.")

    input_path, original, input_format = load_input(args.input)
    model_path = args.model.expanduser().resolve(strict=True)
    cli_path = args.sd_cli.expanduser().resolve(strict=True)
    if not model_path.is_file() or model_path.suffix.lower() != ".safetensors":
        raise ValueError(f"The model must be a local Safetensors file: {model_path}")
    if not cli_path.is_file():
        raise FileNotFoundError(f"stable-diffusion.cpp executable not found: {cli_path}")

    args.output_root.mkdir(parents=True, exist_ok=True)
    run_name = f"{input_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = args.output_root / run_name
    suffix = 1
    while run_dir.exists():
        run_dir = args.output_root / f"{run_name}_{suffix}"
        suffix += 1
    run_dir.mkdir()

    original_copy = run_dir / f"original{input_path.suffix.lower()}"
    shutil.copy2(input_path, original_copy)
    work_path = run_dir / "work_input.png"
    content_size, work_size, pad_offset = prepare_work_image(
        original, args.max_side, work_path
    )
    prompt_path = run_dir / "prompt.txt"
    negative_prompt_path = run_dir / "negative_prompt.txt"
    prompt_path.write_text(POSITIVE_PROMPT, encoding="utf-8")
    negative_prompt_path.write_text(NEGATIVE_PROMPT, encoding="utf-8")

    initial_free = available_ram_gib()
    print(f"RAM_FREE_BEFORE_GIB={initial_free:.2f}", flush=True)
    if initial_free < MIN_START_FREE_GIB:
        raise SystemExit(
            f"Not started: need at least {MIN_START_FREE_GIB:.1f} GiB free before loading."
        )

    raw_output = run_dir / "raw_model_output.png"
    log_path = run_dir / "inference.log"
    command = [
        str(cli_path),
        "--model",
        str(model_path),
        "--backend",
        "cpu",
        "--flash-attn",
        "auto",
        "--params-backend",
        "disk",
        "--init-img",
        str(work_path),
        "--output",
        str(raw_output),
        "--width",
        str(work_size[0]),
        "--height",
        str(work_size[1]),
        "--strength",
        str(args.strength),
        "--steps",
        str(args.steps),
        "--cfg-scale",
        str(args.cfg),
        "--seed",
        str(args.seed),
        "--prompt-file",
        str(prompt_path),
        "--negative-prompt-file",
        str(negative_prompt_path),
    ]

    start = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=cli_path.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    events = []
    events_lock = threading.Lock()

    def collect_output():
        with log_path.open("w", encoding="utf-8") as log:
            for line in process.stdout:
                log.write(line)
                log.flush()
                with events_lock:
                    events.append((time.perf_counter() - start, line))

    reader = threading.Thread(target=collect_output, daemon=True)
    reader.start()

    minimum_free = initial_free
    first_preprocess_seconds = None
    aborted = False
    while process.poll() is None:
        with events_lock:
            new_events = events[:]
            events.clear()
        if first_preprocess_seconds is None:
            for elapsed, line in new_events:
                if "preprocess init:" in line:
                    first_preprocess_seconds = elapsed
                    break

        free = available_ram_gib()
        minimum_free = min(minimum_free, free)
        if free <= MIN_FREE_GIB:
            print(
                f"RAM_LIMIT_REACHED_GIB={free:.2f}; stopping only test PID {process.pid}",
                flush=True,
            )
            if process.poll() is None:
                stop_exact_pid(process.pid, process)
            aborted = True
            break
        time.sleep(0.5)

    exit_code = process.wait()
    reader.join()
    total_seconds = time.perf_counter() - start
    minimum_free = min(minimum_free, available_ram_gib())
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    effective_steps = re.search(r"target t_enc is (\d+) steps", log_text)

    summary = {
        "model": model_path.name,
        "backend": "cpu",
        "params_backend": "disk",
        "input_format": input_format,
        "original_size": list(original.size),
        "work_size": list(work_size),
        "content_size": list(content_size),
        "padding_offset": list(pad_offset),
        "strength": args.strength,
        "requested_steps": args.steps,
        "effective_img2img_steps": int(effective_steps.group(1)) if effective_steps else None,
        "cfg": args.cfg,
        "seed": args.seed,
        "ram_free_before_gib": round(initial_free, 2),
        "ram_free_minimum_gib": round(minimum_free, 2),
        "ram_observed_delta_gib": round(initial_free - minimum_free, 2),
        "process_wall_seconds": round(total_seconds, 2),
        "startup_to_preprocess_seconds": (
            round(first_preprocess_seconds, 2) if first_preprocess_seconds is not None else None
        ),
        "sampling_seconds": elapsed_from_log(
            log_text, r"sampling completed, taking ([0-9.]+)s"
        ),
        "vae_decode_seconds": elapsed_from_log(
            log_text, r"latent \d+ decoded, taking ([0-9.]+)s"
        ),
        "engine_generation_seconds": elapsed_from_log(
            log_text, r"generate_image completed in ([0-9.]+)s"
        ),
        "aborted_for_low_ram": aborted,
        "exit_code": exit_code,
        "raw_output": raw_output.name if raw_output.is_file() else None,
    }

    result_path = run_dir / "result.png"
    comparison_path = run_dir / "comparison.png"
    if not aborted and exit_code == 0 and raw_output.is_file():
        with Image.open(raw_output) as generated:
            generated.verify()
        with Image.open(raw_output) as generated:
            if generated.size != work_size:
                raise RuntimeError(
                    f"Model output size {generated.size} does not match work size {work_size}."
                )
            cropped = generated.convert("RGB").crop(
                (
                    pad_offset[0],
                    pad_offset[1],
                    pad_offset[0] + content_size[0],
                    pad_offset[1] + content_size[1],
                )
            )
        result = cropped.resize(original.size, Image.Resampling.LANCZOS)
        result.save(result_path, format="PNG")
        make_comparison(original, result, comparison_path)
        summary["result"] = result_path.name
        summary["comparison"] = comparison_path.name
        summary["result_size"] = list(result.size)
    else:
        summary["result"] = None
        summary["comparison"] = None

    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"RUN_DIR={run_dir}")
    print(f"LOG={log_path}")
    print(f"SUMMARY={summary_path}")
    print(f"RAM_FREE_MINIMUM_GIB={minimum_free:.2f}")
    print(f"PROCESS_WALL_SECONDS={total_seconds:.2f}")
    print(f"EFFECTIVE_IMG2IMG_STEPS={summary['effective_img2img_steps']}")
    print(f"RESULT={summary['result']}")
    print(f"COMPARISON={summary['comparison']}")

    if aborted:
        raise SystemExit("Stopped at the RAM safety limit. No automatic retry was made.")
    if exit_code != 0:
        raise SystemExit(f"sd-cli failed with exit code {exit_code}; inspect {log_path}.")
    if not result_path.is_file():
        raise RuntimeError("sd-cli exited successfully but no valid result image was prepared.")


if __name__ == "__main__":
    main()
