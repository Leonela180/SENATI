POSITIVE = ("Photorealistic natural human appearance, authentic subtle skin microtexture and pores, realistic fine "
            "hair strands, coherent eyes and catchlights, believable lighting and shadows, natural facial detail, "
            "preserve the original person's apparent identity, pose, expression, skin tone, hairstyle, clothing, "
            "framing and background, avoid beauty retouching, documentary photographic realism.")

NEGATIVE = ("plastic skin, airbrushed skin, waxy face, uncanny eyes, oversmoothing, exaggerated pores, distorted "
            "anatomy, extra fingers, altered identity, different skin tone, excessive sharpening, halos, artifacts, "
            "cartoon, CGI look.")

# Anexo D: fuerza 0,20–0,40 · pasos 25–35 · guía 5–7. Si la evaluación (paso 13) muestra que los tres
# presets no se diferencian, deja solo "natural": la interfaz mostrará un único botón (skill §1.4).
PRESETS = {
    "natural":       {"strength": 0.30, "steps": 30, "guidance": 6.0},
    "fotografico":   {"strength": 0.36, "steps": 32, "guidance": 6.5},
    "detalle_suave": {"strength": 0.22, "steps": 28, "guidance": 5.5},
}
DEFAULT_SEED = 1234          # semilla fija registrada (RNF-10)
WORK_SIDE = 640              # lado menor de trabajo, entre 512 y 768 px
