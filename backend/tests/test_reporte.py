"""Pruebas de HU-10: GET /api/metricas/reporte.

CP-26: con 3 ejecuciones registradas, el endpoint devuelve un PDF (empieza con %PDF).
CP-27: con el servidor recién iniciado (sin registros), el endpoint devuelve igual un PDF.

Qué dibuja el PDF (título, tabla, resumen y el mensaje «Aún no hay ejecuciones registradas»)
lo arma GeneradorReportePDF (T29). Aquí se prueba el endpoint: que entregue el archivo con las
cabeceras correctas, que le pase los registros del servicio y que no guarde nada en el servidor.
Que el PDF muestre los 3 renglones y el resumen se revisa a mano abriendo el archivo (ver la PR).

La API usa una sola instancia de ServicioReescalado para todas las pruebas. Para que los
registros de otros archivos no se mezclen, cada prueba le pone un RegistroMetricas vacío con
monkeypatch (se restaura solo al terminar), igual que test_metricas.py.
"""

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.main
from app.metricas import Registro, RegistroMetricas

RUTA_REPORTE = "/api/metricas/reporte"
NOMBRE_DESCARGA = "rescalibur_metricas.pdf"
PDF_MINIMO = b"%PDF-1.4\n%%EOF\n"  # Lo que devuelve el generador falso de las pruebas de abajo
ARCHIVOS = ["paisaje.png", "retrato.png", "foto.png"]


def imagen_pequena() -> bytes:
    """PNG de 40 x 30 con valores aleatorios (fijos por la semilla): se reescala en pocos ms."""
    generador = np.random.default_rng(10)
    matriz = generador.integers(0, 256, (30, 40, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".png", matriz)
    return buffer.tobytes()


def ejecutar_reescalados(cantidad: int) -> None:
    """Hace reescalados reales (a HD) con el servicio de la API: cada uno queda en el registro."""
    contenido = imagen_pequena()
    for nombre in ARCHIVOS[:cantidad]:
        app.main.servicio.reescalar(contenido, nombre, "hd")


@pytest.fixture
def cliente(monkeypatch):
    """Cliente de la API con un RegistroMetricas vacío."""
    monkeypatch.setattr(app.main.servicio, "registro_metricas", RegistroMetricas())
    return TestClient(app.main.app)


@pytest.fixture
def registros_recibidos(monkeypatch) -> list[list[Registro]]:
    """Cambia GeneradorReportePDF por uno falso que anota los registros que recibe.

    Así se prueba solo el endpoint, sin depender de cómo dibuja el PDF el generador real.
    """
    recibidos: list[list[Registro]] = []

    class GeneradorFalso:
        def generar(self, registros: list[Registro]) -> bytes:
            recibidos.append(registros)
            return PDF_MINIMO

    monkeypatch.setattr(app.main, "GeneradorReportePDF", GeneradorFalso)
    return recibidos


# --- CP-26 y CP-27 (con el generador real) ---


def test_cp26_con_tres_ejecuciones_devuelve_un_pdf(cliente):
    ejecutar_reescalados(3)

    respuesta = cliente.get(RUTA_REPORTE)

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"
    assert respuesta.content.startswith(b"%PDF")
    assert b"%%EOF" in respuesta.content[-1024:]  # El archivo está completo, no cortado


def test_cp27_sin_ejecuciones_devuelve_un_pdf(cliente):
    respuesta = cliente.get(RUTA_REPORTE)

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"
    assert respuesta.content.startswith(b"%PDF")
    assert b"%%EOF" in respuesta.content[-1024:]


def test_se_descarga_como_rescalibur_metricas_pdf(cliente):
    respuesta = cliente.get(RUTA_REPORTE)

    assert respuesta.headers["content-disposition"] == f'attachment; filename="{NOMBRE_DESCARGA}"'


def test_el_pdf_no_se_guarda_en_el_servidor(cliente, tmp_path, monkeypatch):
    ejecutar_reescalados(2)
    monkeypatch.chdir(tmp_path)  # Si el endpoint escribiera un archivo, quedaría aquí

    cliente.get(RUTA_REPORTE)

    assert list(tmp_path.iterdir()) == []


# --- Lo que el endpoint le pasa al generador (generador falso) ---


def test_le_pasa_al_generador_los_registros_en_orden_de_ejecucion(cliente, registros_recibidos):
    ejecutar_reescalados(3)

    cliente.get(RUTA_REPORTE)

    [recibidos] = registros_recibidos
    assert [registro.archivo for registro in recibidos] == ARCHIVOS
    assert recibidos == app.main.servicio.registro_metricas.listar()


def test_sin_ejecuciones_le_pasa_una_lista_vacia(cliente, registros_recibidos):
    cliente.get(RUTA_REPORTE)

    assert registros_recibidos == [[]]


def test_el_reporte_incluye_las_ejecuciones_nuevas(cliente, registros_recibidos):
    cliente.get(RUTA_REPORTE)
    ejecutar_reescalados(1)
    cliente.get(RUTA_REPORTE)

    assert [len(registros) for registros in registros_recibidos] == [0, 1]


def test_pedir_el_reporte_no_cambia_las_metricas(cliente, registros_recibidos):
    ejecutar_reescalados(2)
    antes = app.main.servicio.registro_metricas.listar()

    cliente.get(RUTA_REPORTE)

    assert app.main.servicio.registro_metricas.listar() == antes


def test_responde_con_los_bytes_que_entrega_el_generador(cliente, registros_recibidos):
    assert cliente.get(RUTA_REPORTE).content == PDF_MINIMO


def test_acepta_un_generador_que_devuelve_bytearray(cliente, monkeypatch):
    """fpdf2 entrega un bytearray: el endpoint lo convierte a bytes antes de responder."""

    class GeneradorConBytearray:
        def generar(self, registros: list[Registro]) -> bytearray:
            return bytearray(PDF_MINIMO)

    monkeypatch.setattr(app.main, "GeneradorReportePDF", GeneradorConBytearray)

    respuesta = cliente.get(RUTA_REPORTE)

    assert respuesta.status_code == 200
    assert respuesta.content == PDF_MINIMO


# --- Convivencia con las otras rutas ---


def test_la_ruta_de_metricas_sigue_devolviendo_json(cliente):
    ejecutar_reescalados(1)

    respuesta = cliente.get("/api/metricas")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/json"
    assert [registro["archivo"] for registro in respuesta.json()] == ARCHIVOS[:1]


def test_el_reporte_solo_acepta_get(cliente):
    assert cliente.post(RUTA_REPORTE).status_code == 405
