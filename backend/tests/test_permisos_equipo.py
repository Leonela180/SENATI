from tests.conftest import register
from tests.test_equipos import _team_with_member

PATH = "/api/v1/teams/{}/leave"
DATA = {"starts_at": "2026-12-01T14:00:00+00:00", "ends_at": "2026-12-01T17:00:00+00:00", "reason": "Trámite personal programado"}


def test_integrante_solicita_y_lider_responde(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    endpoint = PATH.format(team_id)
    created = other_client.post(endpoint, json=DATA)
    assert created.status_code == 201
    request_id = created.json["data"]["id"]
    assert client.get(endpoint).json["data"][0]["status"] == "pending"
    decision = client.patch(f"{endpoint}/{request_id}", json={"status": "approved", "review_note": "Coordinado con el equipo"})
    assert decision.status_code == 200 and decision.json["data"]["status"] == "approved"
    assert other_client.get(endpoint).json["data"][0]["review_note"] == "Coordinado con el equipo"
    assert client.patch(f"{endpoint}/{request_id}", json={"status": "rejected"}).status_code == 409


def test_integrante_no_se_autoaprueba_ni_consulta_otro_equipo(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    endpoint = PATH.format(team_id)
    request_id = other_client.post(endpoint, json=DATA).json["data"]["id"]
    assert other_client.patch(f"{endpoint}/{request_id}", json={"status": "approved"}).status_code == 403
    assert other_client.post(endpoint, json=DATA).status_code == 409
    stranger = app.test_client()
    register(stranger, "extra@demo.pe")
    assert stranger.get(endpoint).status_code == 404
    assert stranger.patch(f"{endpoint}/{request_id}", json={"status": "approved"}).status_code == 404


def test_cancelacion_y_datos_invalidos(app, client, other_client):
    team_id, _ = _team_with_member(app, client, other_client)
    endpoint = PATH.format(team_id)
    assert other_client.post(endpoint, json={**DATA, "ends_at": DATA["starts_at"]}).status_code == 400
    assert other_client.post(endpoint, json={**DATA, "starts_at": "2026-12-01T14:00:00"}).status_code == 400
    request_id = other_client.post(endpoint, json=DATA).json["data"]["id"]
    assert client.patch(f"{endpoint}/{request_id}", json={"status": "cancelled"}).status_code == 403
    assert other_client.patch(f"{endpoint}/{request_id}", json={"status": "cancelled"}).json["data"]["status"] == "cancelled"


def test_integrante_no_ve_motivos_de_otros(app, client, other_client):
    from app.extensions import db
    from app.models import TeamMembership, User
    team_id, _ = _team_with_member(app, client, other_client)
    endpoint = PATH.format(team_id)
    other_client.post(endpoint, json=DATA)
    third = app.test_client()
    register(third, "tercero@demo.pe")
    user = db.session.query(User).filter_by(email="tercero@demo.pe").one()
    db.session.add(TeamMembership(team_workspace_id=team_id, user_id=user.id, role="member"))
    db.session.commit()
    assert third.get(endpoint).json["data"] == []
