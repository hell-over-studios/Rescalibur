"""Pruebas de HU-00: el servidor responde y CORS está bien configurado."""

from fastapi.testclient import TestClient

from app.config import METODO_ACTIVO
from app.main import app

cliente = TestClient(app)
ORIGEN_FRONTEND = "http://localhost:5173"


def test_salud_responde_ok():
    respuesta = cliente.get("/api/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "metodo": METODO_ACTIVO}


def test_cors_permite_al_frontend():
    respuesta = cliente.get("/api/salud", headers={"Origin": ORIGEN_FRONTEND})

    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_FRONTEND


def test_cors_expone_cabeceras_personalizadas():
    respuesta = cliente.get("/api/salud", headers={"Origin": ORIGEN_FRONTEND})
    expuestas = respuesta.headers["access-control-expose-headers"].lower()

    for cabecera in ["x-metodo", "x-tiempo-ms", "x-ancho", "x-alto"]:
        assert cabecera in expuestas


def test_cors_rechaza_origen_desconocido():
    respuesta = cliente.get("/api/salud", headers={"Origin": "http://sitio-desconocido.com"})

    assert "access-control-allow-origin" not in respuesta.headers
