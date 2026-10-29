"""Pruebas de HU-06: METODO_ACTIVO, obtener_metodo() y CP-14.

CP-14 pide cambiar METODO_ACTIVO y reiniciar el servidor. Aquí se simula así:
se cambia el valor con monkeypatch y se vuelve a cargar app.main con
importlib.reload, que ejecuta el módulo desde cero igual que uvicorn al arrancar.
"""

import importlib

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.main
from app import config
from app.config import METODOS_DISPONIBLES, obtener_metodo
from app.metodos.base import MetodoInterpolacion
from app.metodos.bilineal import Bilineal
from app.metodos.vecino import VecinoMasCercano

METODOS_DEL_SPRINT = [("vecino", VecinoMasCercano), ("bilineal", Bilineal)]


def a_png(matriz: np.ndarray) -> bytes:
    _, buffer = cv2.imencode(".png", matriz)
    return buffer.tobytes()


def reescalar(cliente: TestClient, contenido: bytes, resolucion: str = "hd"):
    return cliente.post(
        "/api/imagen/reescalar",
        files={"archivo": ("paisaje.png", contenido)},
        data={"resolucion": resolucion},
    )


@pytest.fixture
def arrancar_con(monkeypatch):
    """Devuelve una función que «reinicia» la API con otro METODO_ACTIVO."""

    def arrancar(nombre: str) -> TestClient:
        monkeypatch.setattr(config, "METODO_ACTIVO", nombre)
        modulo = importlib.reload(app.main)
        return TestClient(modulo.app)

    yield arrancar

    # Deja la API con el METODO_ACTIVO real para las demás pruebas.
    monkeypatch.undo()
    importlib.reload(app.main)


# --- obtener_metodo() ---


def test_metodo_activo_del_repositorio_es_valido():
    assert config.METODO_ACTIVO in METODOS_DISPONIBLES


@pytest.mark.parametrize(("nombre", "clase"), METODOS_DEL_SPRINT)
def test_obtener_metodo_devuelve_la_clase_indicada(monkeypatch, nombre, clase):
    monkeypatch.setattr(config, "METODO_ACTIVO", nombre)

    metodo = obtener_metodo()

    assert isinstance(metodo, clase)
    assert isinstance(metodo, MetodoInterpolacion)
    assert metodo.nombre == nombre


def test_claves_coinciden_con_el_nombre_de_cada_clase():
    """La clave del diccionario es el mismo texto que viaja en X-Metodo."""
    for clave, clase in METODOS_DISPONIBLES.items():
        assert clase.nombre == clave


@pytest.mark.parametrize("nombre", ["bicubico", "Bilineal", "vecino ", ""])
def test_nombre_invalido_lanza_error_con_mensaje_claro(monkeypatch, nombre):
    monkeypatch.setattr(config, "METODO_ACTIVO", nombre)

    with pytest.raises(ValueError) as error:
        obtener_metodo()

    mensaje = str(error.value)
    assert f'"{nombre}"' in mensaje
    assert '"vecino"' in mensaje and '"bilineal"' in mensaje


# --- Arranque de la API ---


def test_metodo_invalido_detiene_el_arranque(arrancar_con):
    with pytest.raises(ValueError, match="no es un método válido"):
        arrancar_con("bicubico")


@pytest.mark.parametrize(("nombre", "_clase"), METODOS_DEL_SPRINT)
def test_salud_informa_el_metodo_activo(arrancar_con, nombre, _clase):
    cliente = arrancar_con(nombre)

    assert cliente.get("/api/salud").json() == {"estado": "ok", "metodo": nombre}


# --- Cambio de método (CP-14) ---


def test_cp14_x_metodo_cambia_segun_metodo_activo(arrancar_con):
    imagen = a_png(np.zeros((600, 800, 3), np.uint8))

    for nombre in ["vecino", "bilineal"]:
        respuesta = reescalar(arrancar_con(nombre), imagen)

        assert respuesta.status_code == 200
        assert respuesta.headers["x-metodo"] == nombre
        assert float(respuesta.headers["x-tiempo-ms"]) >= 0


@pytest.mark.parametrize(("nombre", "clase"), METODOS_DEL_SPRINT)
def test_cp14_la_imagen_sale_del_metodo_activo(arrancar_con, nombre, clase):
    """No basta con la cabecera: los píxeles deben ser los de ese método."""
    generador = np.random.default_rng(14)
    original = generador.integers(0, 256, (60, 80, 3), dtype=np.uint8)

    respuesta = reescalar(arrancar_con(nombre), a_png(original))
    recibida = cv2.imdecode(np.frombuffer(respuesta.content, np.uint8), cv2.IMREAD_UNCHANGED)

    assert np.array_equal(recibida, clase().reescalar(original, 960, 720))
