"""Proceso aislado para diagnosticar la conversion con los mismos pesos en PyTorch.

No publica resultados: el controlador exige filtros separados antes y despues.
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    for name in ("model", "config", "image", "output"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    import torch
    from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
    from accelerate import disk_offload
    from PIL import Image
    torch.set_num_threads(2)
    pipe = StableDiffusionImg2ImgPipeline.from_single_file(
        args.model, config=args.config, torch_dtype=torch.float16,
        local_files_only=True, safety_checker=None, feature_extractor=None,
        requires_safety_checker=False,
    )
    # Carga compacta; los bloques UNet se materializan en F32 al usarse.
    # Evita operaciones FP16 de CPU y no mantiene el UNet F32 entero en RAM.
    disk_offload(pipe.unet, offload_dir=str(Path(args.output).parent / "offload"),
                 execution_device=torch.device("cpu"))
    pipe.unet.to(dtype=torch.float32)
    pipe.vae.to(dtype=torch.float32)
    pipe.text_encoder.to(dtype=torch.float32)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
    pipe.enable_attention_slicing("max")
    pipe.enable_vae_slicing()
    pipe.set_progress_bar_config(disable=False)
    image = Image.open(args.image).convert("RGB")
    with torch.inference_mode():
        result = pipe(
            prompt="photorealistic photograph of an adult man, natural human facial proportions, realistic brown eyes, short wavy brown hair, teal jacket, beige shirt, soft studio lighting, real skin pores",
            negative_prompt="cartoon, anime, drawing, illustration, 3d render, giant eyes, doll, distorted face, deformed",
            image=image, strength=.78, num_inference_steps=16, guidance_scale=7,
            generator=torch.Generator(device="cpu").manual_seed(1234),
        ).images[0]
    result.save(args.output)
    print(json.dumps({"status": "generated", "size": result.size}), flush=True)


if __name__ == "__main__":
    main()
