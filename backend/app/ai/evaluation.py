"""Evaluación del motor (Anexo A).
  1) python -m app.ai.evaluation procesar  C:\\lumia_muestras  C:\\lumia_eval
  2) python -m app.ai.evaluation preparar  C:\\lumia_eval  --preset natural
  3) (los revisores llenan las fichas)
  4) python -m app.ai.evaluation resumir   C:\\lumia_eval
"""
import argparse
import csv
import random
import shutil
import statistics
from pathlib import Path
from app.ai.prompts import PRESETS

EXT = {".png", ".jpg", ".jpeg", ".webp"}
FICHA = ["muestra", "revisor", "defecto_principal", "regeneraciones_previas", "minutos_retoque",
         "naturalidad_A", "naturalidad_B", "misma_persona", "conserva_pose_ropa_fondo", "artefactos", "observaciones"]


def procesar(muestras: Path, salida: Path):
    from app import create_app
    from app.ai.local_engine import LocalHumanizationEngine
    app = create_app()
    eng = LocalHumanizationEngine(str(app.config["AI_MODEL_PATH"]), app.config["AI_MODEL_ID"])
    lp = None
    try:
        import lpips, torch                                       # opcional (R. Zhang et al., 2018)
        from PIL import Image
        import torchvision.transforms.functional as TF
        lp = lpips.LPIPS(net="alex")
    except Exception:
        print("LPIPS no disponible: se omite.")
    (salida / "resultados").mkdir(parents=True, exist_ok=True)
    rows = []
    for src in sorted(p for p in muestras.iterdir() if p.suffix.lower() in EXT):
        for preset in PRESETS:
            dst = salida / "resultados" / f"{src.stem}_{preset}.png"
            meta = eng.humanize(str(src), str(dst), preset)
            row = {"muestra": src.stem, **{k: meta.get(k) for k in ("preset", "strength", "steps", "guidance", "seed",
                                                                    "seconds", "vram_gb", "model_id", "model_version")}}
            if lp:
                a = TF.to_tensor(Image.open(src).convert("RGB").resize((256, 256))) * 2 - 1
                b = TF.to_tensor(Image.open(dst).convert("RGB").resize((256, 256))) * 2 - 1
                row["lpips"] = round(float(lp(a[None], b[None])), 4)
            rows.append(row)
            print(row)
    with (salida / "resultados.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"Listo: {salida / 'resultados.csv'}")


def preparar(salida: Path, muestras: Path, preset: str, revisores: int):
    """Pares a ciegas: A/B en orden aleatorio; la clave queda aparte para la autora."""
    ciego = salida / "revision_a_ciegas"
    ciego.mkdir(parents=True, exist_ok=True)
    clave = []
    for res in sorted((salida / "resultados").glob(f"*_{preset}.png")):
        stem = res.stem.rsplit(f"_{preset}", 1)[0]
        orig = next(p for p in muestras.iterdir() if p.stem == stem and p.suffix.lower() in EXT)
        a_es_original = random.random() < 0.5
        shutil.copy(orig if a_es_original else res, ciego / f"{stem}_A{(orig if a_es_original else res).suffix}")
        shutil.copy(res if a_es_original else orig, ciego / f"{stem}_B{(res if a_es_original else orig).suffix}")
        clave.append({"muestra": stem, "A": "original" if a_es_original else "resultado"})
    with (salida / "clave_NO_ENTREGAR_A_REVISORES.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["muestra", "A"]); w.writeheader(); w.writerows(clave)
    for r in range(1, revisores + 1):
        with (salida / f"ficha_revisor_{r}.csv").open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=FICHA); w.writeheader()
            for c in clave:
                w.writerow({"muestra": c["muestra"], "revisor": f"R{r}"})
    print(f"Entrega a cada revisor la carpeta {ciego} y su ficha_revisor_N.csv (escala 1 a 5).")


def resumir(salida: Path):
    clave = {r["muestra"]: r["A"] for r in csv.DictReader((salida / "clave_NO_ENTREGAR_A_REVISORES.csv").open(encoding="utf-8-sig"))}
    nat_o, nat_r, ident, conserva, artef = [], [], [], [], []
    for ficha in salida.glob("ficha_revisor_*.csv"):
        for r in csv.DictReader(ficha.open(encoding="utf-8-sig")):
            if not r["naturalidad_A"]:
                continue
            a, b = float(r["naturalidad_A"]), float(r["naturalidad_B"])
            o, res = (a, b) if clave[r["muestra"]] == "original" else (b, a)
            nat_o.append(o); nat_r.append(res); ident.append(float(r["misma_persona"]))
            conserva.append(r["conserva_pose_ropa_fondo"].strip().lower() in ("si", "sí"))
            artef.append(r["artefactos"].strip().lower() == "graves")
    n = len(nat_o)
    print(f"Respuestas: {n}")
    print(f"Naturalidad media original : {statistics.mean(nat_o):.2f} / 5")
    print(f"Naturalidad media resultado: {statistics.mean(nat_r):.2f} / 5")
    print(f"Pares en que el resultado se ve más natural: {sum(r > o for o, r in zip(nat_o, nat_r)) / n:.0%}")
    print(f"Identidad media (misma persona): {statistics.mean(ident):.2f} / 5")
    print(f"Conserva pose, ropa, encuadre y fondo: {sum(conserva) / n:.0%}")
    print(f"Artefactos graves: {sum(artef) / n:.0%}")
    times = [float(r["seconds"]) for r in csv.DictReader((salida / "resultados.csv").open(encoding="utf-8-sig"))]
    print(f"Tiempo de inferencia medio: {statistics.mean(times):.1f} s (mín {min(times):.1f} · máx {max(times):.1f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("procesar"); p1.add_argument("muestras", type=Path); p1.add_argument("salida", type=Path)
    p2 = sub.add_parser("preparar"); p2.add_argument("salida", type=Path); p2.add_argument("--muestras", type=Path, default=Path(r"C:\lumia_muestras"))
    p2.add_argument("--preset", default="natural"); p2.add_argument("--revisores", type=int, default=3)
    p3 = sub.add_parser("resumir"); p3.add_argument("salida", type=Path)
    a = ap.parse_args()
    if a.cmd == "procesar": procesar(a.muestras, a.salida)
    elif a.cmd == "preparar": preparar(a.salida, a.muestras, a.preset, a.revisores)
    else: resumir(a.salida)
