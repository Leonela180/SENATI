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
    class CPUOffloadedImg2ImgPipeline(StableDiffusionImg2ImgPipeline):
        @property
        def _execution_device(self):
            # Un UNet offloaded tiene parametros meta: no inferir el dispositivo
            # a partir del orden de los componentes del pipeline.
            return torch.device("cpu")

    pipe = CPUOffloadedImg2ImgPipeline.from_single_file(
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
            prompt="natural candid photographic portrait of an adult man, relaxed friendly expression, both eyes fully open, clear realistic brown irises, round aligned pupils, consistent gaze looking directly at camera, small natural window catchlights in both eyes, soft frontal window lighting evenly illuminating the eyes and face, natural human facial proportions, short wavy brown hair, teal jacket, beige shirt, authentic subtle skin pores, documentary photography",
            negative_prompt="cartoon, anime, drawing, illustration, 3d render, giant eyes, doll, distorted face, deformed, squinting, sleepy eyes, crossed eyes, misaligned pupils, asymmetric eyes, double pupils, empty eyes, black eye sockets, harsh shadows on eyes, glossy plastic skin, beauty retouch",
            image=image, strength=.74, num_inference_steps=28, guidance_scale=6.5,
            generator=torch.Generator(device="cpu").manual_seed(1234),
        ).images[0]
    result.save(args.output)
    print(json.dumps({"status": "generated", "size": result.size}), flush=True)


if __name__ == "__main__":
    main()
