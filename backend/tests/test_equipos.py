from datetime import timedelta
from app.extensions import db, utc_now
from app.models import TeamInvitation, User
from tests.conftest import register, upload


def _team_with_member(app, client, other_client):
    register(client, "owner@demo.pe")
    team_id = client.post("/api/v1/teams", json={"name": "Diseño"}).json["data"]["id"]
    link = client.post(f"/api/v1/teams/{team_id}/invitations").json["data"]["link"]
    token = link.split("token=")[1]
    register(other_client, "member@demo.pe")
    assert other_client.post("/api/v1/invitations/accept", json={"token": token}).status_code == 200
    return team_id, token


def test_rf18_invitacion_un_solo_uso(app, client, other_client):
    _, token = _team_with_member(app, client, other_client)
    third = app.test_client()
    register(third, "c@demo.pe")
    assert third.post("/api/v1/invitations/accept", json={"token": token}).status_code == 400


def test_rf18_invitacion_vencida(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    link = client.post(f"/api/v1/teams/{team_id}/invitations").json["data"]["link"]
    inv = db.session.query(TeamInvitation).order_by(TeamInvitation.id.desc()).first()
    inv.expires_at = utc_now() - timedelta(hours=1)
    db.session.commit()
    third = app.test_client()
    register(third, "c@demo.pe")
    assert third.post("/api/v1/invitations/accept", json={"token": link.split("token=")[1]}).status_code == 400


def test_rf19_compartir_explicito(app, client, other_client):
    _team_with_member(app, client, other_client)
    image_id = upload(client).json["data"]["id"]
    assert other_client.get(f"/api/v1/images/{image_id}").status_code == 404   # privada por defecto
    client.patch(f"/api/v1/images/{image_id}/visibility", json={"visibility": "team"})
    assert other_client.get(f"/api/v1/images/{image_id}").status_code == 200


def test_rf20_estadisticas_agregadas(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    r = other_client.get(f"/api/v1/teams/{team_id}/stats?days=30")
    assert r.status_code == 200 and "storage_key" not in r.get_data(as_text=True)
    outsider = app.test_client()
    register(outsider, "x@demo.pe")
    assert outsider.get(f"/api/v1/teams/{team_id}/stats").status_code == 404   # CU06 flujo 2a


def test_rf21_admin(app, client):
    register(client)
    assert client.get("/api/v1/admin/overview").status_code == 403            # CU07 flujo 1a
    db.session.query(User).filter_by(email="a@demo.pe").update({"global_role": "admin"})
    db.session.commit()
    r = client.get("/api/v1/admin/overview")
    assert r.status_code == 200 and "original_storage_key" not in r.get_data(as_text=True)
