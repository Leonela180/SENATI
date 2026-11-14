"""Horario y horas: horario semanal, marcación, registros manuales, saldo y vista del equipo."""
from datetime import date, datetime, timedelta, timezone

from app.extensions import db
from app.models import TimeEntry, User
from app.services import hours_service
from tests.conftest import register

LIMA = timezone(timedelta(hours=-5))
LUNES = date(2026, 11, 9)


def _fix_now(monkeypatch, dt):
    monkeypatch.setattr(hours_service, "now_local", lambda: dt)


def _schedule(client):
    days = [{"weekday": d, "start": "08:00", "end": "13:00"} for d in range(5)]        # L–V, 5 h diarias
    return client.put("/api/v1/hours/schedule", json={"days": days})


def test_horario_semanal_y_validaciones(client):
    register(client)
    r = _schedule(client)
    assert r.status_code == 200 and r.json["data"]["weekly_hours"] == 25
    bad = client.put("/api/v1/hours/schedule", json={"days": [{"weekday": 0, "start": "13:00", "end": "08:00"}]})
    assert bad.status_code == 400


def test_marcar_entrada_y_salida(client):
    register(client)
    assert client.post("/api/v1/hours/clock-out").status_code == 409                 # sin entrada
    assert client.post("/api/v1/hours/clock-in").status_code == 201
    assert client.post("/api/v1/hours/clock-in").status_code == 409                  # una sola jornada abierta
    assert client.get("/api/v1/hours/status").json["data"]["open_entry"]["open"] is True
    r = client.post("/api/v1/hours/clock-out")
    assert r.status_code == 200 and r.json["data"]["open"] is False


def test_saldo_y_horas_por_recuperar(app, client, monkeypatch):
    register(client)
    _schedule(client)
    uid = db.session.query(User).one().id
    # Miércoles 11/11 a las 18:00: ya pasaron lunes, martes y miércoles → 15 h esperadas a la fecha
    _fix_now(monkeypatch, datetime(2026, 11, 11, 18, 0, tzinfo=LIMA))
    for d, (h0, h1) in {0: (8, 13), 1: (8, 11)}.items():                            # 5 h + 3 h trabajadas
        day = LUNES + timedelta(days=d)
        db.session.add(TimeEntry(user_id=uid, clock_in=datetime(day.year, day.month, day.day, h0, tzinfo=LIMA),
                                 clock_out=datetime(day.year, day.month, day.day, h1, tzinfo=LIMA), source="web"))
    db.session.commit()
    s = client.get("/api/v1/hours/summary?period=week&date=2026-11-11").json["data"]
    assert s["expected_total"] == 25 and s["expected_to_date"] == 15
    assert s["worked"] == 8 and s["balance"] == -7 and s["to_recover"] == 7
    assert s["days"][2]["expected"] == 5 and s["days"][2]["worked"] == 0


def test_dia_en_curso_cuenta_solo_lo_transcurrido(app, client, monkeypatch):
    register(client)
    _schedule(client)
    _fix_now(monkeypatch, datetime(2026, 11, 9, 10, 30, tzinfo=LIMA))                # lunes 10:30
    s = client.get("/api/v1/hours/summary?date=2026-11-09").json["data"]
    assert s["expected_to_date"] == 2.5                                               # 08:00 → 10:30


def test_registro_manual_con_nota_y_sin_superposicion(app, client, monkeypatch):
    register(client)
    _fix_now(monkeypatch, datetime(2026, 11, 11, 18, 0, tzinfo=LIMA))
    sin_nota = client.post("/api/v1/hours/entries", json={"date": "2026-11-10", "start": "08:00", "end": "12:00"})
    assert sin_nota.status_code == 400 and sin_nota.json["error"]["code"] == "sin_nota"
    ok = client.post("/api/v1/hours/entries", json={"date": "2026-11-10", "start": "08:00", "end": "12:00",
                                                    "note": "Olvidé marcar por corte de luz"})
    assert ok.status_code == 201 and ok.json["data"]["source"] == "manual"
    cruce = client.post("/api/v1/hours/entries", json={"date": "2026-11-10", "start": "11:00", "end": "13:00",
                                                       "note": "Otra vez"})
    assert cruce.status_code == 409
    futuro = client.post("/api/v1/hours/entries", json={"date": "2026-11-20", "start": "08:00", "end": "09:00",
                                                        "note": "No debería poder"})
    assert futuro.status_code == 400
    assert client.delete(f"/api/v1/hours/entries/{ok.json['data']['id']}").status_code == 200


def test_las_marcaciones_web_no_se_borran(client):
    register(client)
    client.post("/api/v1/hours/clock-in")
    entry_id = client.post("/api/v1/hours/clock-out").json["data"]["id"]
    assert client.delete(f"/api/v1/hours/entries/{entry_id}").status_code == 403


def test_propietario_ve_horas_del_equipo_y_exporta(app, client, other_client):
    register(client)
    team_id = client.post("/api/v1/teams", json={"name": "Diseño"}).json["data"]["id"]
    link = client.post(f"/api/v1/teams/{team_id}/invitations").json["data"]["link"]
    register(other_client, "b@demo.pe", "Beto")
    other_client.post("/api/v1/invitations/accept", json={"token": link.split("token=")[1]})
    other_client.post("/api/v1/hours/clock-in")
    rows = client.get(f"/api/v1/teams/{team_id}/hours").json["data"]
    assert {r["display_name"] for r in rows} == {"Demo", "Beto"}
    assert next(r for r in rows if r["display_name"] == "Beto")["working_now"] is True
    csv = client.get(f"/api/v1/teams/{team_id}/hours.csv")
    assert csv.status_code == 200 and "Beto" in csv.get_data(as_text=True)
    # Un integrante (no propietario) no ve las horas de los demás
    assert other_client.get(f"/api/v1/teams/{team_id}/hours").status_code == 404
