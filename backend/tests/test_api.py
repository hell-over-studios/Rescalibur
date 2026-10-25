"""Pruebas de integración del endpoint /api/imagen/info (HU-01 y HU-02)."""

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def subir(contenido: bytes, nombre: str):
    return cliente.post("/api/imagen/info", files={"archivo": (nombre, contenido)})


def test_info_imagen_valida():
    _, buffer = cv2.imencode(".png", np.zeros((1080, 1920, 3), np.uint8))
    respuesta = subir(buffer.tobytes(), "foto.png")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert (datos["ancho"], datos["alto"]) == (1920, 1080)
    assert [o["clave"] for o in datos["opciones"]] == ["2k", "4k"]


def test_info_archivo_no_imagen_responde_400():
    assert subir(b"hola", "documento.txt").status_code == 400


def test_info_archivo_grande_responde_413():
    assert subir(b"0" * (21 * 1024 * 1024), "grande.png").status_code == 413
