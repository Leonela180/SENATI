"""Demostración explícita con API y algoritmos reales; no fabrica trabajos.

Sin --apply solo describe el alcance. Credenciales y registro quedan privados.
No borra usuarios ni modifica sus imágenes existentes.
"""
import argparse
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image as PILImage
from sqlalchemy.engine import make_url
from app import create_app
from app.config import ROOT, Config
from app.extensions import db
from app.models import User, ProcessingJob
from app.workers.image_worker import process_one

PRIVATE = ROOT / "private_data/demo_senati"
MANIFEST = PRIVATE / "accesos_y_avance.json"
NAMES = ["Valeria", "Mateo", "Camila", "Diego", "Luciana"]
TEAMS = ["Aurora Retratos", "Andes Creativo", "Prisma Digital", "Raices Visuales", "Luz de Estudio"]


def backup():
    url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    exe = Path("C:/Program Files/PostgreSQL/17/bin/pg_dump.exe")
    command = str(exe) if exe.exists() else "pg_dump"
    target = PRIVATE / ("antes_demo_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".dump")
    env = dict(os.environ, PGPASSWORD=url.password or "")
    result = subprocess.run([command, "-h", url.host or "localhost", "-p", str(url.port or 5432),
                             "-U", url.username, "-d", url.database, "-Fc", "-f", str(target)],
                            env=env, capture_output=True)
    if result.returncode or not target.exists() or target.stat().st_size < 1000:
        raise RuntimeError("No se pudo verificar el respaldo; no se crearon datos DEMO.")
    return target.name


def call(client, method, path, **kwargs):
    response = client.open("/api/v1" + path, method=method, **kwargs)
    if response.status_code >= 400:
        error = (response.get_json(silent=True) or {}).get("error") or {}
        raise RuntimeError(f"{method} {path}: {response.status_code} {error.get('code', 'error')}")
    return response.get_json()["data"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("Plan: 5 individuales + 5 grupos (lider y 2 integrantes): 20 cuentas DEMO; 60 albumes; ediciones reales. Sin cambios.")
        return
    sources = [ROOT / "frontend/public/demo/ej_piel_antes.webp", PRIVATE / "retrato-artesana.png", PRIVATE / "retrato-disenador.png"]
    if not all(path.is_file() for path in sources):
        raise RuntimeError("Falta una fotografia propia; no se modificaron datos.")
    PRIVATE.mkdir(parents=True, exist_ok=True)
    state = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"demo": True, "accounts": {}, "teams": {}}

    def persist():
        temp = MANIFEST.with_suffix(".tmp")
        temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(MANIFEST)

    # Estos overrides son exclusivos del cliente local de carga, no del servidor web.
    app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
    with app.app_context():
        if db.session.query(ProcessingJob).filter(ProcessingJob.status.in_(["queued", "processing"])).count():
            raise RuntimeError("Hay trabajos activos; esperar antes de preparar la demostracion.")
        state.setdefault("backups", []).append(backup())
        persist()
        clients = {}
        roles = [(f"individual{i+1}", f"DEMO {name} · Individual", None) for i, name in enumerate(NAMES)]
        for i, team in enumerate(TEAMS, 1):
            roles += [(f"grupo{i}-lider", f"DEMO {NAMES[i-1]} · Lider {i}", i),
                      (f"grupo{i}-editor1", f"DEMO Editor A · Grupo {i}", i),
                      (f"grupo{i}-editor2", f"DEMO Editor B · Grupo {i}", i)]
        for slug, name, team_index in roles:
            entry = state["accounts"].get(slug)
            if not entry:
                email = f"{slug}@demo.lumia.test"
                if db.session.query(User).filter_by(email=email).first():
                    raise RuntimeError("Cuenta DEMO existente sin manifiesto; no se cambia su clave.")
                entry = {"name": name, "email": email, "password": secrets.token_urlsafe(18), "group": team_index,
                         "images": {}, "jobs": {}, "albums": {}}
                state["accounts"][slug] = entry
                persist()
            client = app.test_client()
            if not db.session.query(User).filter_by(email=entry["email"]).first():
                call(client, "POST", "/auth/register", json={"email": entry["email"], "password": entry["password"], "display_name": name})
            else:
                call(client, "POST", "/auth/login", json={"email": entry["email"], "password": entry["password"]})
            clients[slug] = client
            persist()
        for i, team_name in enumerate(TEAMS, 1):
            owner = clients[f"grupo{i}-lider"]
            key = str(i)
            team = state["teams"].get(key)
            if not team:
                team = call(owner, "POST", "/teams", json={"name": f"DEMO · {team_name}"})
                team["joined"] = []
                state["teams"][key] = team
                persist()
            for n in (1, 2):
                slug = f"grupo{i}-editor{n}"
                if slug not in team["joined"]:
                    inv = call(owner, "POST", f"/teams/{team['id']}/invitations", json={"email": state["accounts"][slug]["email"]})
                    token = parse_qs(urlparse(inv["link"]).query)["token"][0]
                    call(clients[slug], "POST", "/invitations/accept", json={"token": token})
                    team["joined"].append(slug)
                    persist()
        colors = ["#d8e7e8", "#e4d8c9", "#dcd7ed", "#c8d9cc", "#f1d7ce"]
        for index, (slug, name, team_index) in enumerate(roles):
            client, entry = clients[slug], state["accounts"][slug]
            for album in ("01 · Originales DEMO", "02 · Retoque y versiones DEMO", "03 · Entregables DEMO"):
                if album not in entry["albums"]:
                    existing = call(client, "GET", "/albums")
                    entry["albums"][album] = next((a["id"] for a in existing if a["name"] == album), None) or call(client, "POST", "/albums", json={"name": album})["id"]
                    persist()
            for source_index, path in enumerate(sources):
                source_key = str(source_index)
                if source_key not in entry["images"]:
                    with PILImage.open(path) as photo:
                        photo = photo.convert("RGB")
                        photo.thumbnail((640, 640))
                        buffer = io.BytesIO()
                        photo.save(buffer, "PNG")
                    buffer.seek(0)
                    uploaded = call(client, "POST", "/images", data={"file": (buffer, f"DEMO_retrato_{source_index+1}.png"),
                        "permiso_edicion": "true", "album_id": str(entry["albums"]["01 · Originales DEMO"])}, content_type="multipart/form-data")
                    entry["images"][source_key] = uploaded["id"]
                    persist()
                image_id = entry["images"][source_key]
                operations = [("cambiar_fondo", {"mode": "color", "color": colors[index % 5]}),
                              ("ajustes", {"brightness": 1.03, "contrast": 1.08, "saturation": 1.05, "warmth": .06}),
                              ("mejorar_calidad", {"scale": 2, "sharpen": .5, "denoise": True})]
                if source_index == 0:
                    operations[1] = ("textura_piel", {"intensity": .45 + (index % 4)*.1, "pecas": False})
                elif source_index == 2:
                    operations = [("restaurar", {"intensity": .4, "points": []}),
                                  ("quitar_lunar", {"points": [{"x": 310, "y": 500, "r": 5}]}),
                                  ("desenfoque", {"scope": "fondo", "radius": 5 + index % 4}),
                                  operations[2]]
                for step, (tool, params) in enumerate(operations):
                    record_key = f"{source_index}-{step}"
                    record = entry["jobs"].get(record_key)
                    if record and record.get("saved_image"):
                        image_id = record["saved_image"]
                        continue
                    job = call(client, "POST", "/jobs", json={"image_id": image_id, "tool": tool, "params": params},
                               headers={"Idempotency-Key": f"demo-senati-{slug}-{record_key}-v1"})
                    entry["jobs"][record_key] = record = {"id": job["id"], "tool": tool}
                    persist()
                    for _ in range(4):
                        job = call(client, "GET", f"/jobs/{job['id']}")
                        if job["status"] in ("completed", "failed"):
                            break
                        process_one(app, None)  # Solo se encolan algoritmos del Estudio.
                    if job["status"] != "completed":
                        raise RuntimeError(f"Trabajo DEMO {job['id']} no completado: {job['status']}; no se inventa resultado.")
                    saved = call(client, "POST", f"/jobs/{job['id']}/save")
                    record["saved_image"] = image_id = saved["id"]
                    target_album = "03 · Entregables DEMO" if step == len(operations)-1 else "02 · Retoque y versiones DEMO"
                    call(client, "PATCH", f"/images/{image_id}/album", json={"album_id": entry["albums"][target_album]})
                    if team_index:
                        call(client, "PATCH", f"/images/{image_id}/visibility", json={"visibility": "team"})
                    persist()
            if not entry.get("hours_done"):
                day = (datetime.now(timezone(timedelta(hours=-5))) - timedelta(days=1)).date().isoformat()
                call(client, "POST", "/hours/entries", json={"date": day, "start": "09:00", "end": f"{11 + index % 3}:00",
                     "note": "DEMO: jornada manual de ejemplo para la exposicion; no es asistencia laboral real."})
                entry["hours_done"] = True
                persist()
            if not entry.get("schedule_done"):
                call(client, "PUT", "/hours/schedule", json={"days": [
                    {"weekday": day, "start": "09:00", "end": "13:00"} for day in range(5)]})
                entry["schedule_done"] = True
                persist()
            print(f"DEMO: perfil {index+1}/20 preparado, {len(entry['jobs'])} ediciones reales.", flush=True)
        for i in range(1, 6):
            team = state["teams"][str(i)]
            if team.get("leave_done"):
                continue
            for n in (1, 2):
                start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(days=i+n)
                leave = call(clients[f"grupo{i}-editor{n}"], "POST", f"/teams/{team['id']}/leave", json={
                    "starts_at": start.isoformat(), "ends_at": (start+timedelta(hours=2)).isoformat(),
                    "reason": "DEMO: solicitud de permiso para mostrar el proceso de revision del lider."})
                if n == 1:
                    call(clients[f"grupo{i}-lider"], "PATCH", f"/teams/{team['id']}/leave/{leave['id']}", json={
                        "status": "approved" if i % 2 else "rejected", "review_note": "DEMO: decision de ejemplo para la exposicion."})
            team["leave_done"] = True
            persist()
        state["completed"] = True
        state["completed_at"] = datetime.now(timezone.utc).isoformat()
        persist()
        lines = ["# Accesos privados DEMO LUMIA", "", "Datos sinteticos de demostracion. No compartir este archivo en GitHub.", ""]
        for slug, entry in state["accounts"].items():
            lines += [f"## {entry['name']}", f"Correo: {entry['email']}", f"Clave: {entry['password']}", ""]
        (PRIVATE / "ACCESOS-PRIVADOS.md").write_text("\n".join(lines), encoding="utf-8")
        total_jobs = sum(len(account["jobs"]) for account in state["accounts"].values())
        print(f"DEMO completa: 20 cuentas, 5 equipos, 60 albumes y {total_jobs} trabajos reales. Accesos guardados en private_data/demo_senati.")


if __name__ == "__main__":
    main()
