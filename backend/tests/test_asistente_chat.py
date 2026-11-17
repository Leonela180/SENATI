"""Chat del Asistente: consentimiento, límites, herramienta sugerida y errores seguros (sin llamar a Google)."""
import json

from app.api import assistant as chat_api
from app.services import gemini_service
from app.services.gemini_service import GeminiError
from tests.conftest import register

MSG = {"consent": True, "messages": [{"role": "user", "text": "Mi foto antigua tiene rayas"}]}


def test_exige_consentimiento_y_mensajes_validos(client):
    register(client)
    assert client.post("/api/v1/assistant/chat", json={**MSG, "consent": False}).status_code == 400
    assert client.post("/api/v1/assistant/chat", json={"consent": True, "messages": []}).status_code == 400
    bad = {"consent": True, "messages": [{"role": "system", "text": "hola"}]}
    assert client.post("/api/v1/assistant/chat", json=bad).status_code == 400
    last_model = {"consent": True, "messages": [{"role": "user", "text": "a"}, {"role": "model", "text": "b"}]}
    assert client.post("/api/v1/assistant/chat", json=last_model).status_code == 400


def test_requiere_sesion(client):
    assert client.post("/api/v1/assistant/chat", json=MSG).status_code == 401


def test_responde_y_recorta_historial(app, client, monkeypatch):
    register(client)
    app.config["GEMINI_API_KEY"] = "clave-de-prueba"
    seen = {}
    def fake(messages, key, model, timeout):
        seen["messages"] = messages
        return "Usa Restaurar foto y marca las rayas.", "restaurar"
    monkeypatch.setattr(chat_api, "chat", fake)
    long = [{"role": "user" if i % 2 == 0 else "model", "text": "x" * 3000} for i in range(30)] + MSG["messages"]
    r = client.post("/api/v1/assistant/chat", json={"consent": True, "messages": long})
    assert r.status_code == 200 and r.json["data"] == {"reply": "Usa Restaurar foto y marca las rayas.", "tool": "restaurar", "source": "gemini"}
    assert len(seen["messages"]) == chat_api.MAX_TURNS and all(len(m["text"]) <= chat_api.MAX_CHARS for m in seen["messages"])


def test_error_de_gemini_se_informa_sin_romper(app, client, monkeypatch):
    register(client)
    app.config["GEMINI_API_KEY"] = "x"
    def boom(*a, **k):
        raise GeminiError("gemini_limite")
    monkeypatch.setattr(chat_api, "chat", boom)
    r = client.post("/api/v1/assistant/chat", json=MSG)
    assert r.status_code == 503 and r.json["error"]["code"] == "gemini_limite"


def test_cliente_extrae_texto_y_herramienta(monkeypatch):
    payload = {"candidates": [{"content": {"parts": [{"text": "Abre Quitar lunar y marca el centro.\nHERRAMIENTA: quitar_lunar"}]}}]}
    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, n): return json.dumps(payload).encode()
    sent = {}
    def fake_urlopen(req, timeout):
        sent["body"] = json.loads(req.data)
        return Resp()
    monkeypatch.setattr(gemini_service.urllib.request, "urlopen", fake_urlopen)
    text, tool = gemini_service.chat([{"role": "user", "text": "tengo un lunar"}], "k", "gemini-2.5-flash")
    assert text == "Abre Quitar lunar y marca el centro." and tool == "quitar_lunar"
    assert "systemInstruction" in sent["body"] and "inlineData" not in json.dumps(sent["body"])


def test_herramienta_desconocida_se_ignora(monkeypatch):
    payload = {"candidates": [{"content": {"parts": [{"text": "Hola\nHERRAMIENTA: borrar_todo"}]}}]}
    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, n): return json.dumps(payload).encode()
    monkeypatch.setattr(gemini_service.urllib.request, "urlopen", lambda *a, **k: Resp())
    assert gemini_service.chat([{"role": "user", "text": "hola"}], "k", "m") == ("Hola", None)
