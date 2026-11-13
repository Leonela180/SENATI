"""RNF-03: 20 solicitudes por operación sin IA; reporta la media y el máximo en ms."""
import io
import pathlib
import statistics
import sys
import time
import uuid
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from PIL import Image
from app import create_app

app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
c = app.test_client()
c.post("/api/v1/auth/register", json={"email": f"rendimiento+{uuid.uuid4().hex[:6]}@lumia.local",
                                       "display_name": "Medición", "password": "clave-segura-123"})
buf = io.BytesIO(); Image.new("RGB", (512, 512), (180, 140, 120)).save(buf, "PNG"); buf.seek(0)
img_id = c.post("/api/v1/images", data={"file": (buf, "m.png"), "declaracion_ia": "true"},
                content_type="multipart/form-data").json["data"]["id"]

for name, call in [("GET /auth/me", lambda: c.get("/api/v1/auth/me")),
                   ("GET /jobs", lambda: c.get("/api/v1/jobs")),
                   ("GET /images/{id}", lambda: c.get(f"/api/v1/images/{img_id}")),
                   ("GET /workspaces", lambda: c.get("/api/v1/workspaces"))]:
    times = []
    for _ in range(20):
        t0 = time.perf_counter(); call(); times.append((time.perf_counter() - t0) * 1000)
    print(f"{name:20s} media {statistics.mean(times):6.1f} ms   máx {max(times):6.1f} ms")
