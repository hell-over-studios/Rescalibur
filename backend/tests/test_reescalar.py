"""Pruebas de integración de POST /api/imagen/reescalar (HU-05, CP-13 y CP-15).

Revisan el contrato de la sección 5.1: PNG en el cuerpo, cabeceras X-...
visibles para el frontend y errores 400 / 413 con mensaje en "detail".
"""

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.config import METODO_ACTIVO
from app.main import app

cliente = TestClient(app)
ORIGEN_FRONTEND = "http://localhost:5173"
LIMITE_SEGUNDOS = 5
FIRMA_PNG = b"\x89PNG"


def a_png(matriz: np.ndarray) -> bytes:
    _, buffer = cv2.imencode(".png", matriz)
    return buffer.tobytes()


def reescalar(contenido: bytes, nombre: str, resolucion: str, cabeceras: dict | None = None):
    return cliente.post(
        "/api/imagen/reescalar",
        files={"archivo": (nombre, contenido)},
        data={"resolucion": resolucion},
        headers=cabeceras,
    )


def leer_respuesta(respuesta) -> np.ndarray:
    """Decodifica el PNG recibido igual que lo abriría el usuario."""
    return cv2.imdecode(np.frombuffer(respuesta.content, np.uint8), cv2.IMREAD_UNCHANGED)


# --- Respuesta exitosa (CP-15) ---


def test_cp15_devuelve_png_con_la_resolucion_elegida():
    respuesta = reescalar(a_png(np.zeros((600, 800, 3), np.uint8)), "paisaje.png", "fullhd")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/png"
    assert respuesta.content.startswith(FIRMA_PNG)
    assert leer_respuesta(respuesta).shape == (1080, 1440, 3)


def test_cabeceras_del_contrato():
    respuesta = reescalar(a_png(np.zeros((600, 800, 3), np.uint8)), "paisaje.png", "hd")

    assert respuesta.headers["x-ancho"] == "960"
    assert respuesta.headers["x-alto"] == "720"
    assert respuesta.headers["x-metodo"] == METODO_ACTIVO
    assert float(respuesta.headers["x-tiempo-ms"]) >= 0


def test_nombre_de_descarga_sigue_el_formato_del_criterio():
    respuesta = reescalar(a_png(np.zeros((600, 800, 3), np.uint8)), "paisaje.png", "2k")

    assert 'filename="rescalibur_2k.png"' in respuesta.headers["content-disposition"]


def test_cabeceras_visibles_para_el_frontend():
    """Riesgo R6: sin expose_headers el navegador oculta las X-..."""
    respuesta = reescalar(
        a_png(np.zeros((600, 800, 3), np.uint8)),
        "paisaje.png",
        "hd",
        cabeceras={"Origin": ORIGEN_FRONTEND},
    )
    expuestas = respuesta.headers["access-control-expose-headers"].lower()

    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_FRONTEND
    for cabecera in ["x-metodo", "x-tiempo-ms", "x-ancho", "x-alto"]:
        assert cabecera in expuestas


def test_imagen_vertical_respeta_la_orientacion():
    respuesta = reescalar(a_png(np.zeros((1920, 1080, 3), np.uint8)), "celular.png", "4k")

    assert respuesta.status_code == 200
    assert leer_respuesta(respuesta).shape == (3840, 2160, 3)


def test_conserva_transparencia_y_escala_de_grises():
    con_alfa = np.zeros((60, 80, 4), np.uint8)
    con_alfa[:, :, 3] = 128
    respuesta_alfa = reescalar(a_png(con_alfa), "logo.png", "hd")
    respuesta_gris = reescalar(a_png(np.full((60, 80), 77, np.uint8)), "gris.png", "hd")

    alfa = leer_respuesta(respuesta_alfa)
    assert alfa.shape == (720, 960, 4)
    assert np.all(alfa[:, :, 3] == 128)
    assert leer_respuesta(respuesta_gris).ndim == 2


def test_acepta_jpg():
    _, buffer = cv2.imencode(".jpg", np.full((600, 800, 3), 200, np.uint8))
    respuesta = reescalar(buffer.tobytes(), "foto.JPG", "hd")

    assert respuesta.status_code == 200


# --- Rendimiento (CP-13) ---


def test_cp13_800x600_a_4k_en_menos_de_5_segundos():
    generador = np.random.default_rng(13)
    imagen = generador.integers(0, 256, (600, 800, 3), dtype=np.uint8)

    respuesta = reescalar(a_png(imagen), "paisaje.png", "4k")

    assert respuesta.status_code == 200
    assert (respuesta.headers["x-ancho"], respuesta.headers["x-alto"]) == ("2880", "2160")
    assert float(respuesta.headers["x-tiempo-ms"]) < LIMITE_SEGUNDOS * 1000


# --- Errores ---


def test_resolucion_que_no_amplia_responde_400():
    respuesta = reescalar(a_png(np.zeros((1080, 1920, 3), np.uint8)), "fullhd.png", "hd")

    assert respuesta.status_code == 400
    assert "no amplía" in respuesta.json()["detail"]


def test_resolucion_desconocida_responde_400():
    respuesta = reescalar(a_png(np.zeros((600, 800, 3), np.uint8)), "paisaje.png", "8k")

    assert respuesta.status_code == 400
    assert "desconocida" in respuesta.json()["detail"]


def test_archivo_no_imagen_responde_400():
    respuesta = reescalar(b"hola", "documento.txt", "hd")

    assert respuesta.status_code == 400
    assert "Formato no aceptado" in respuesta.json()["detail"]


def test_extension_valida_pero_contenido_roto_responde_400():
    respuesta = reescalar(b"esto no es un png", "roto.png", "hd")

    assert respuesta.status_code == 400


def test_archivo_grande_responde_413():
    respuesta = reescalar(b"0" * (21 * 1024 * 1024), "grande.png", "hd")

    assert respuesta.status_code == 413
