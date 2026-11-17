import pytest
from app.models import ProcessingJob
from app.extensions import db
from tests.conftest import new_job, register, upload, url_bd_pruebas


@pytest.mark.parametrize("body", [[], "texto", 10, {"email": []}, {"password": {}}, {"display_name": 7}])
def test_json_incorrecto_no_produce_error_interno(client, body):
    assert client.post("/api/v1/auth/register", json=body).status_code == 400


def test_no_permite_base_real_para_pruebas(monkeypatch):
    import os
    monkeypatch.setenv("TEST_DATABASE_URL", os.environ["DATABASE_URL"])
    with pytest.raises(RuntimeError, match="distinta"):
        url_bd_pruebas()


def test_no_cache_y_cabeceras_de_seguridad(client):
    response = client.get("/api/v1/auth/csrf")
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_renombrar_album_duplicado_responde_conflicto(client):
    register(client)
    client.post("/api/v1/albums", json={"name": "Primero"})
    second = client.post("/api/v1/albums", json={"name": "Segundo"}).json["data"]
    assert client.patch(f"/api/v1/albums/{second['id']}", json={"name": "Primero"}).status_code == 409
    assert len(client.get("/api/v1/albums").json["data"]) == 2


def test_borrado_de_imagen_en_proceso_se_rechaza(app, client):
    register(client)
    image_id = upload(client).json["data"]["id"]
    job_id = new_job(client, image_id).json["data"]["id"]
    db.session.get(ProcessingJob, job_id).status = "processing"
    db.session.commit()
    assert client.delete(f"/api/v1/images/{image_id}").status_code == 409
    assert client.get(f"/api/v1/images/{image_id}/content").status_code == 200
