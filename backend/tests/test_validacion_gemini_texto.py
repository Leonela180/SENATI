from tools import validar_gemini


def test_diagnostico_por_defecto_solo_texto(monkeypatch, capsys):
    monkeypatch.setattr(validar_gemini.Config, "GEMINI_API_KEY", "clave-solo-prueba")
    monkeypatch.setattr(validar_gemini, "chat", lambda *args: ("respuesta de prueba", "mejorar_calidad"))
    monkeypatch.setattr(validar_gemini, "generate_image", lambda *args: (_ for _ in ()).throw(AssertionError("No llamar imagenes")))
    assert validar_gemini.main([]) == 0
    output = capsys.readouterr().out
    assert "clave-solo-prueba" not in output and "respuesta de prueba" not in output


def test_diagnostico_imagenes_exige_activacion(monkeypatch):
    monkeypatch.setattr(validar_gemini.Config, "GEMINI_IMAGE_ENABLED", False)
    monkeypatch.setattr(validar_gemini, "generate_image", lambda *args: (_ for _ in ()).throw(AssertionError("No llamar imagenes")))
    assert validar_gemini.main(["--imagenes"]) == 2
