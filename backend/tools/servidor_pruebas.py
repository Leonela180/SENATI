"""Servidor E2E aislado de la base real y sin llamadas externas a Gemini.

Uso: python tools/servidor_pruebas.py inicializar|api|worker
Ejecutar pytest antes de inicializar; ambos usan la base desechable lumia_test.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import ROOT
from app.extensions import db
from tests.conftest import url_bd_pruebas


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    app = create_app(
        TESTING=True, SQLALCHEMY_DATABASE_URI=url_bd_pruebas(),
        PRIVATE_STORAGE_ROOT=ROOT / "private_data" / "e2e",
        AI_ENGINE="mock", GEMINI_API_KEY="", RATELIMIT_ENABLED=False,
        TRUST_PROXY=False, SESSION_COOKIE_SECURE=False,
    )
    if mode == "api":
        from waitress import serve
        serve(app, listen="127.0.0.1:5001")
    elif mode == "inicializar":
        with app.app_context():
            db.create_all()
        print("Base E2E aislada lista.")
    elif mode == "worker":
        from app.ai.interface import MockEngine
        from app.workers.image_worker import heartbeat, process_one
        with app.app_context():
            while True:
                heartbeat(app)
                if not process_one(app, MockEngine()):
                    time.sleep(1)
    else:
        raise SystemExit("Modo esperado: inicializar, api o worker")


if __name__ == "__main__":
    main()
