from app.workers.image_worker import process_one
from tests.test_equipos import _team_with_member
from tests.conftest import register, upload


def test_avance_solo_compartidos_y_solo_lider(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    image_id = upload(other_client).json["data"]["id"]
    other_client.post("/api/v1/jobs", json={"image_id": image_id, "tool": "ajustes"}, headers={"Idempotency-Key": "avance-equipo-001"})
    process_one(app, None)
    path = f"/api/v1/teams/{team_id}/progress"
    before = client.get(path).json["data"]
    assert sum(row["completed"] for row in before) == 0
    assert sum(row["shared_images"] for row in before) == 0
    other_client.patch(f"/api/v1/images/{image_id}/visibility", json={"visibility": "team"})
    after = client.get(path).json["data"]
    assert sum(row["completed"] for row in after) == 1
    assert sum(row["shared_images"] for row in after) == 1
    assert other_client.get(path).status_code == 403
    outsider = app.test_client()
    register(outsider, "externo@demo.pe")
    assert outsider.get(path).status_code == 404
