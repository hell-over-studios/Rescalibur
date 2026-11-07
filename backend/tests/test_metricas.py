"""Pruebas de HU-09: Registro, RegistroMetricas, el registro en el servicio y GET /api/metricas.

CP-24: dos reescalados seguidos quedan en GET /api/metricas con todos los campos y
       con tiempo_ms igual a X-Tiempo-Ms.
CP-25: una petición con error (400 o 413) no agrega registros.

La API usa una sola instancia de ServicioReescalado para todas las pruebas. Para que
los registros de otros archivos no se mezclen, cada prueba de la API le pone un
RegistroMetricas vacío con monkeypatch (se restaura solo al terminar).
"""

from datetime import datetime

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.main
from app.metodos.bilineal import Bilineal
from app.metricas import BYTES_POR_KB, Registro, RegistroMetricas
from app.procesador import ProcesadorImagen
from app.resoluciones import CalculadoraResolucion
from app.servicio import ServicioReescalado

# Claves y orden del JSON de la sección 16.1.
CLAVES_DEL_CONTRATO = [
    "fecha",
    "archivo",
    "metodo",
    "ancho_original",
    "alto_original",
    "ancho_final",
    "alto_final",
    "resolucion",
    "tiempo_ms",
    "tamano_kb",
]
FORMATO_FECHA = "%Y-%m-%dT%H:%M:%S"


def a_png(matriz: np.ndarray) -> bytes:
    _, buffer = cv2.imencode(".png", matriz)
    return buffer.tobytes()


def imagen(alto: int = 600, ancho: int = 800) -> bytes:
    """PNG de prueba con valores aleatorios (fijos por la semilla), para que el PNG no sea trivial."""
    generador = np.random.default_rng(9)
    return a_png(generador.integers(0, 256, (alto, ancho, 3), dtype=np.uint8))


def crear_registro(metodo: str = "bicubico", tiempo_ms: float = 812.4, archivo: str = "paisaje.jpg"):
    """Registro con los datos del ejemplo de la sección 16.1."""
    return Registro(
        fecha=datetime(2026, 11, 5, 10, 42, 10, 654321),
        archivo=archivo,
        metodo=metodo,
        ancho_original=800,
        alto_original=600,
        ancho_final=2880,
        alto_final=2160,
        resolucion="4k",
        tiempo_ms=tiempo_ms,
        tamano_kb=11510272 / BYTES_POR_KB,  # 11 240,5 KB
    )


# --- Registro ---


def test_a_diccionario_tiene_las_claves_del_contrato():
    assert list(crear_registro().a_diccionario()) == CLAVES_DEL_CONTRATO


def test_a_diccionario_sigue_el_ejemplo_de_la_seccion_16_1():
    assert crear_registro().a_diccionario() == {
        "fecha": "2026-11-05T10:42:10",
        "archivo": "paisaje.jpg",
        "metodo": "bicubico",
        "ancho_original": 800,
        "alto_original": 600,
        "ancho_final": 2880,
        "alto_final": 2160,
        "resolucion": "4k",
        "tiempo_ms": 812.4,
        "tamano_kb": 11240.5,
    }


def test_a_diccionario_redondea_como_la_cabecera_x_tiempo_ms():
    tiempo_ms = 812.40567

    assert crear_registro(tiempo_ms=tiempo_ms).a_diccionario()["tiempo_ms"] == float(f"{tiempo_ms:.2f}")


def test_registro_no_se_puede_modificar():
    with pytest.raises(AttributeError):
        crear_registro().tiempo_ms = 0


# --- RegistroMetricas ---


def test_registro_metricas_empieza_vacio():
    metricas = RegistroMetricas()

    assert metricas.listar() == []
    assert metricas.resumen_por_metodo() == {}


def test_listar_respeta_el_orden_de_ejecucion():
    metricas = RegistroMetricas()
    for archivo in ["a.png", "b.png", "c.png"]:
        metricas.agregar(crear_registro(archivo=archivo))

    assert [registro.archivo for registro in metricas.listar()] == ["a.png", "b.png", "c.png"]


def test_listar_devuelve_una_copia():
    metricas = RegistroMetricas()
    metricas.agregar(crear_registro())

    metricas.listar().clear()

    assert len(metricas.listar()) == 1


def test_resumen_por_metodo_del_ejemplo_de_la_seccion_15_1():
    metricas = RegistroMetricas()
    metricas.agregar(crear_registro("bicubico", 812.4))
    metricas.agregar(crear_registro("bilineal", 256.0))
    metricas.agregar(crear_registro("bicubico", 1205.7))

    resumen = metricas.resumen_por_metodo()

    assert list(resumen) == ["bicubico", "bilineal"]  # orden del primer uso
    assert resumen["bicubico"]["ejecuciones"] == 2
    assert resumen["bicubico"]["promedio_ms"] == pytest.approx(1009.05)
    assert resumen["bicubico"]["minimo_ms"] == 812.4
    assert resumen["bicubico"]["maximo_ms"] == 1205.7
    assert resumen["bilineal"] == {
        "ejecuciones": 1,
        "promedio_ms": 256.0,
        "minimo_ms": 256.0,
        "maximo_ms": 256.0,
    }


# --- Registro dentro de ServicioReescalado ---


@pytest.fixture
def servicio():
    return ServicioReescalado(ProcesadorImagen(), CalculadoraResolucion(), Bilineal(), RegistroMetricas())


def test_servicio_registra_un_reescalado_exitoso(servicio):
    resultado = servicio.reescalar(imagen(), "paisaje.png", "hd")

    [registro] = servicio.registro_metricas.listar()
    assert registro.archivo == "paisaje.png"
    assert registro.metodo == "bilineal"
    assert (registro.ancho_original, registro.alto_original) == (800, 600)
    assert (registro.ancho_final, registro.alto_final) == (960, 720)
    assert registro.resolucion == "hd"
    assert registro.tiempo_ms == resultado.tiempo_ms
    assert registro.tamano_kb == len(resultado.png) / BYTES_POR_KB


def test_servicio_sin_registro_crea_uno_vacio():
    servicio = ServicioReescalado(ProcesadorImagen(), CalculadoraResolucion(), Bilineal())

    assert servicio.registro_metricas.listar() == []


@pytest.mark.parametrize(
    ("contenido", "nombre", "clave"),
    [
        (b"esto no es una imagen", "documento.txt", "hd"),  # formato no aceptado
        (b"contenido roto", "roto.png", "hd"),  # extension valida, imagen ilegible
        (b"0" * (21 * 1024 * 1024), "grande.png", "hd"),  # mas de 20 MB
        (imagen(), "paisaje.png", "8k"),  # clave desconocida
        (imagen(1080, 1920), "grande.png", "hd"),  # la resolucion no amplia
    ],
)
def test_servicio_no_registra_si_falla(servicio, contenido, nombre, clave):
    with pytest.raises(ValueError):
        servicio.reescalar(contenido, nombre, clave)

    assert servicio.registro_metricas.listar() == []


# --- GET /api/metricas (CP-24 y CP-25) ---


@pytest.fixture
def cliente(monkeypatch):
    """Cliente de la API con un RegistroMetricas vacío."""
    monkeypatch.setattr(app.main.servicio, "registro_metricas", RegistroMetricas())
    return TestClient(app.main.app)


def reescalar(cliente: TestClient, contenido: bytes, nombre: str, resolucion: str):
    return cliente.post(
        "/api/imagen/reescalar",
        files={"archivo": (nombre, contenido)},
        data={"resolucion": resolucion},
    )


def obtener_metricas(cliente: TestClient) -> list[dict]:
    respuesta = cliente.get("/api/metricas")
    assert respuesta.status_code == 200
    return respuesta.json()


def test_metricas_vacias_al_arrancar(cliente):
    assert obtener_metricas(cliente) == []


def test_cp24_dos_reescalados_quedan_registrados(cliente):
    respuestas = [
        reescalar(cliente, imagen(), "paisaje.png", "hd"),
        reescalar(cliente, imagen(1920, 1080), "retrato.png", "2k"),
    ]

    registros = obtener_metricas(cliente)

    assert len(registros) == 2
    for registro, respuesta in zip(registros, respuestas, strict=True):
        assert respuesta.status_code == 200
        assert list(registro) == CLAVES_DEL_CONTRATO
        assert registro["tiempo_ms"] == float(respuesta.headers["x-tiempo-ms"])
        assert registro["metodo"] == respuesta.headers["x-metodo"]
        assert registro["ancho_final"] == int(respuesta.headers["x-ancho"])
        assert registro["alto_final"] == int(respuesta.headers["x-alto"])
        assert registro["tamano_kb"] == round(len(respuesta.content) / BYTES_POR_KB, 1)
        datetime.strptime(registro["fecha"], FORMATO_FECHA)  # falla si el formato no es el del contrato

    # En orden de ejecución y con los datos de cada petición.
    assert [r["archivo"] for r in registros] == ["paisaje.png", "retrato.png"]
    assert [r["resolucion"] for r in registros] == ["hd", "2k"]
    assert [(r["ancho_original"], r["alto_original"]) for r in registros] == [(800, 600), (1080, 1920)]
    assert [(r["ancho_final"], r["alto_final"]) for r in registros] == [(960, 720), (1440, 2560)]


@pytest.mark.parametrize(
    ("contenido", "nombre", "clave", "codigo"),
    [
        (b"esto no es una imagen", "documento.txt", "hd", 400),  # el caso de CP-25
        (b"contenido roto", "roto.png", "hd", 400),
        (imagen(), "paisaje.png", "8k", 400),
        (imagen(1080, 1920), "grande.png", "hd", 400),
        (b"0" * (21 * 1024 * 1024), "grande.png", "hd", 413),
    ],
)
def test_cp25_peticion_con_error_no_se_registra(cliente, contenido, nombre, clave, codigo):
    reescalar(cliente, imagen(), "paisaje.png", "hd")
    antes = obtener_metricas(cliente)

    respuesta = reescalar(cliente, contenido, nombre, clave)

    assert respuesta.status_code == codigo
    assert obtener_metricas(cliente) == antes
    assert len(antes) == 1