"""Filtro local ejecutado por separado para liberar su memoria al terminar."""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--models", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    try:
        import numpy as np
        import torch
        from PIL import Image, ImageOps
        from transformers import CLIPImageProcessor
        from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker

        torch.set_num_threads(2)
        processor = CLIPImageProcessor.from_pretrained(args.models / "feature_extractor", local_files_only=True)
        checker = StableDiffusionSafetyChecker.from_pretrained(
            args.models / "safety_checker", variant="fp16", use_safetensors=True,
            torch_dtype=torch.float16, low_cpu_mem_usage=True, local_files_only=True,
            device_map="auto", max_memory={"cpu": "256MiB"},
            offload_folder=str(args.report.parent / "safety_offload"), offload_state_dict=True,
        ).eval()
        with Image.open(args.image) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((512, 512))
            pixels = processor(images=image, return_tensors="pt").pixel_values.to(dtype=torch.float16)
            with torch.inference_mode():
                _, blocked = checker(clip_input=pixels, images=np.array(image)[None].copy())
        report = {"approved": not any(blocked), "code": "contenido_bloqueado" if any(blocked) else None}
    except Exception as error:
        print(type(error).__name__, str(error)[:500], file=sys.stderr)
        report = {"approved": False, "code": "filtro_no_disponible"}
    args.report.write_text(json.dumps(report), encoding="utf-8")


if __name__ == "__main__":
    main()
