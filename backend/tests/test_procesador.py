"""Pruebas de ProcesadorImagen y ServicioReescalado.obtener_info (HU-01, CP-01 a CP-04)."""

import cv2
import numpy as np
import pytest

from app.procesador import (
    TAMANO_MAXIMO_MB,
    ImagenDemasiadoGrande,
    ImagenInvalida,
    ProcesadorImagen,
)
from app.resoluciones import CalculadoraResolucion
from app.servicio import ServicioReescalado

procesador = ProcesadorImagen()
servicio = ServicioReescalado(procesador, CalculadoraResolucion())


def a_bytes(matriz: np.ndarray, extension: str = ".png") -> bytes:
    """Codifica una matriz como si fuera un archivo subido por el usuario."""
    _, buffer = cv2.imencode(extension, matriz)
    return buffer.tobytes()


def test_lee_imagen_a_color():
    matriz = procesador.leer(a_bytes(np.zeros((600, 800, 3), np.uint8), ".jpg"))
    assert matriz.shape == (600, 800, 3)


def test_conserva_canal_alfa():
    matriz = procesador.leer(a_bytes(np.zeros((10, 20, 4), np.uint8)))
    assert matriz.shape == (10, 20, 4)


def test_conserva_escala_de_grises():
    matriz = procesador.leer(a_bytes(np.zeros((10, 20), np.uint8)))
    assert matriz.shape == (10, 20)


def test_normaliza_16_bits_a_8_bits():
    original = np.full((4, 4, 3), 65535, np.uint16)
    matriz = procesador.leer(a_bytes(original))
    assert matriz.dtype == np.uint8
    assert matriz.max() == 255


def test_cp02_archivo_que_no_es_imagen():
    with pytest.raises(ImagenInvalida):
        procesador.leer(b"esto es un texto, no una imagen")


def test_archivo_vacio():
    with pytest.raises(ImagenInvalida):
        procesador.leer(b"")


def test_cp03_archivo_demasiado_grande():
    with pytest.raises(ImagenDemasiadoGrande):
        procesador.leer(b"0" * (TAMANO_MAXIMO_MB * 1024 * 1024 + 1))


def test_codificar_png_ida_y_vuelta():
    original = np.random.randint(0, 256, (5, 7, 3), np.uint8)
    recuperada = procesador.leer(procesador.codificar_png(original))
    assert np.array_equal(original, recuperada)


def test_cp01_y_cp04_obtener_info():
    info = servicio.obtener_info(a_bytes(np.zeros((600, 800, 3), np.uint8)), "paisaje.png")
    assert (info["nombre"], info["ancho"], info["alto"]) == ("paisaje.png", 800, 600)
    assert info["opciones"][1] == {"clave": "fullhd", "nombre": "Full HD", "ancho": 1440, "alto": 1080}


def test_extension_no_aceptada():
    with pytest.raises(ImagenInvalida):
        servicio.obtener_info(a_bytes(np.zeros((10, 10, 3), np.uint8)), "documento.txt")