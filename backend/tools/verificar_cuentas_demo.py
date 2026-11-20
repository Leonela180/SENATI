"""Comprueba cuentas y permisos DEMO sin imprimir claves ni modificar imágenes."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import ROOT
from preparar_cuentas_demo import call


def main():
    state = json.loads((ROOT / "private_data/demo_senati/accesos_y_avance.json").read_text(encoding="utf-8"))
    app = create_app(WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
    clients = {}
    counts = {"accounts": 0, "groups": len(state["teams"]), "albums": 0, "images": 0, "completed_jobs": 0, "downloads_checked": 0, "leave_requests": 0}
    for slug, account in state["accounts"].items():
        client = app.test_client()
        call(client, "POST", "/auth/login", json={"email": account["email"], "password": account["password"]})
        clients[slug] = client
        counts["accounts"] += 1
        albums = call(client, "GET", "/albums")
        assert len(albums) >= 3
        counts["albums"] += len(albums)
        images = call(client, "GET", "/images")
        counts["images"] += images["total"]
        for record in account["jobs"].values():
            job = call(client, "GET", f"/jobs/{record['id']}")
            assert job["status"] == "completed" and job["model_id"] != "mock"
            counts["completed_jobs"] += 1
        sample = next(iter(account["jobs"].values()))
        download = client.get(f"/api/v1/jobs/{sample['id']}/download?inline=1")
        assert download.status_code == 200 and download.data.startswith(b"\x89PNG")
        counts["downloads_checked"] += 1
    # El original privado de una persona no es visible para otra cuenta.
    private_id = state["accounts"]["individual1"]["images"]["0"]
    assert clients["individual2"].get(f"/api/v1/images/{private_id}/content").status_code == 404
    for key, team in state["teams"].items():
        owner = clients[f"grupo{key}-lider"]
        assert len(call(owner, "GET", f"/teams/{team['id']}/members")) == 3
        requests = call(owner, "GET", f"/teams/{team['id']}/leave")
        assert len(requests) == 2
        counts["leave_requests"] += len(requests)
        member = clients[f"grupo{key}-editor1"]
        assert len(call(member, "GET", f"/teams/{team['id']}/leave")) == 1
        shared_id = state["accounts"][f"grupo{key}-editor1"]["jobs"]["0-0"]["saved_image"]
        assert owner.get(f"/api/v1/images/{shared_id}/content").status_code == 200
        assert clients["individual2"].get(f"/api/v1/images/{shared_id}/content").status_code == 404
    counts["cross_account_access"] = "verified"
    folder = ROOT / "docs/evidencias/cierre_20261120"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "demo-verificada.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    print(json.dumps(counts), flush=True)


if __name__ == "__main__":
    main()
