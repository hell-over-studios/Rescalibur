"""Pruebas unitarias del metodo bilineal (HU-04): CP-10, CP-11, CP-12 y CP-13."""

import inspect
import time

import cv2
import numpy as np
import pytest

from app.metodos import bilineal as modulo_bilineal
from app.metodos.base import MetodoInterpolacion
from app.metodos.bilineal import Bilineal

DIFERENCIA_MAXIMA_PERMITIDA = 2  # niveles por pixel frente a OpenCV (HU-04)
TIEMPO_MAXIMO_SEGUNDOS = 5  # 800 x 600 -> 4K (HU-04)
SEMILLA = 2026  # para que las imagenes aleatorias sean siempre las mismas


@pytest.fixture
def metodo() -> Bilineal:
    return Bilineal()


def imagen_aleatoria(alto: int, ancho: int, canales: int | None = 3) -> np.ndarray:
    """Imagen uint8 con ruido; es el peor caso para comparar contra OpenCV."""
    generador = np.random.default_rng(SEMILLA)
    forma = (alto, ancho) if canales is None else (alto, ancho, canales)
    return generador.integers(0, 256, size=forma, dtype=np.uint8)


def diferencia_maxima(una: np.ndarray, otra: np.ndarray) -> int:
    """Mayor diferencia absoluta entre dos imagenes, sin desbordar uint8."""
    return int(np.abs(una.astype(np.int16) - otra.astype(np.int16)).max())


# ---------------------------------------------------------------- dimensiones


@pytest.mark.parametrize(
    ("ancho", "alto", "nuevo_ancho", "nuevo_alto"),
    [
        (800, 600, 2880, 2160),  # 4K
        (800, 600, 960, 720),  # HD
        (1080, 1920, 2160, 3840),  # vertical
        (7, 5, 13, 11),  # factores no enteros
        (40, 30, 10, 8),  # reduccion
    ],
)
def test_dimensiones_exactas(metodo, ancho, alto, nuevo_ancho, nuevo_alto):
    resultado = metodo.reescalar(imagen_aleatoria(alto, ancho), nuevo_ancho, nuevo_alto)
    assert resultado.shape == (nuevo_alto, nuevo_ancho, 3)


# ---------------------------------------------------------------- matematica a mano


def test_ejemplo_a_mano_2x2_a_4x4(metodo):
    """Las posiciones origen son 0, 0.25, 0.75 y 1 en cada eje (seccion 5.4)."""
    matriz = np.array([[10, 30], [50, 70]], dtype=np.uint8)
    esperado = np.array(
        [
            [10, 15, 25, 30],
            [20, 25, 35, 40],
            [40, 45, 55, 60],
            [50, 55, 65, 70],
        ],
        dtype=np.uint8,
    )
    np.testing.assert_array_equal(metodo.reescalar(matriz, 4, 4), esperado)


def test_vecinos_y_pesos_a_mano():
    """2 pixeles -> 4: posiciones -0.25, 0.25, 0.75, 1.25 que se recortan a [0, 1]."""
    indice0, indice1, peso = Bilineal._vecinos_y_pesos(tamano_destino=4, tamano_origen=2)
    np.testing.assert_array_equal(indice0, [0, 0, 0, 1])
    np.testing.assert_array_equal(indice1, [1, 1, 1, 1])
    np.testing.assert_allclose(peso, [0.0, 0.25, 0.75, 0.0])


def test_pesos_entre_cero_y_uno():
    _, _, peso = Bilineal._vecinos_y_pesos(tamano_destino=2160, tamano_origen=600)
    assert peso.min() >= 0
    assert peso.max() < 1


def test_vecinos_nunca_se_salen_de_la_imagen():
    indice0, indice1, _ = Bilineal._vecinos_y_pesos(tamano_destino=2880, tamano_origen=800)
    assert indice0.min() >= 0
    assert indice1.max() <= 799


# ---------------------------------------------------------------- CP-10 constante


def test_cp10_constante_3x3_a_7x7(metodo):
    matriz = np.full((3, 3), 77, dtype=np.uint8)
    resultado = metodo.reescalar(matriz, 7, 7)
    assert resultado.shape == (7, 7)
    assert np.all(resultado == 77)


def test_constante_a_color_conserva_cada_canal(metodo):
    matriz = np.zeros((5, 4, 3), dtype=np.uint8)
    matriz[:, :] = (12, 130, 250)
    resultado = metodo.reescalar(matriz, 11, 9)
    assert np.all(resultado == (12, 130, 250))


# ---------------------------------------------------------------- propiedades


def test_esquinas_conservan_su_valor_al_ampliar(metodo):
    matriz = imagen_aleatoria(6, 8)
    resultado = metodo.reescalar(matriz, 32, 24)
    np.testing.assert_array_equal(resultado[0, 0], matriz[0, 0])
    np.testing.assert_array_equal(resultado[0, -1], matriz[0, -1])
    np.testing.assert_array_equal(resultado[-1, 0], matriz[-1, 0])
    np.testing.assert_array_equal(resultado[-1, -1], matriz[-1, -1])


def test_no_inventa_valores_fuera_del_rango_original(metodo):
    """Es un promedio con pesos que suman 1: nunca sale del rango de la imagen."""
    matriz = np.random.default_rng(SEMILLA).integers(40, 201, size=(30, 40), dtype=np.uint8)
    resultado = metodo.reescalar(matriz, 120, 90)
    assert resultado.min() >= matriz.min()
    assert resultado.max() <= matriz.max()


def test_mismo_tamano_devuelve_la_misma_imagen(metodo):
    matriz = imagen_aleatoria(20, 30)
    np.testing.assert_array_equal(metodo.reescalar(matriz, 30, 20), matriz)


def test_no_modifica_la_original(metodo):
    matriz = imagen_aleatoria(10, 10)
    copia = matriz.copy()
    metodo.reescalar(matriz, 25, 25)
    np.testing.assert_array_equal(matriz, copia)


# ---------------------------------------------------------------- CP-11 contra OpenCV


@pytest.mark.parametrize("canales", [None, 3])
def test_cp11_800x600_a_4k_contra_opencv(metodo, canales):
    matriz = imagen_aleatoria(600, 800, canales)
    nuestro = metodo.reescalar(matriz, 2880, 2160)
    opencv = cv2.resize(matriz, (2880, 2160), interpolation=cv2.INTER_LINEAR)
    assert diferencia_maxima(nuestro, opencv) <= DIFERENCIA_MAXIMA_PERMITIDA


@pytest.mark.parametrize(
    ("ancho", "alto", "nuevo_ancho", "nuevo_alto"),
    [
        (800, 600, 960, 720),  # factor 1.2
        (1080, 1920, 2160, 3840),  # vertical, factor 2
        (37, 23, 101, 89),  # factores no enteros y distintos en cada eje
        (300, 200, 1920, 1080),  # cambia la proporcion
    ],
)
def test_otras_resoluciones_contra_opencv(metodo, ancho, alto, nuevo_ancho, nuevo_alto):
    matriz = imagen_aleatoria(alto, ancho)
    nuestro = metodo.reescalar(matriz, nuevo_ancho, nuevo_alto)
    opencv = cv2.resize(matriz, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)
    assert diferencia_maxima(nuestro, opencv) <= DIFERENCIA_MAXIMA_PERMITIDA


# ---------------------------------------------------------------- CP-12 canales


@pytest.mark.parametrize("canales", [1, 3, 4])
def test_cp12_conserva_canales_y_tipo(metodo, canales):
    resultado = metodo.reescalar(imagen_aleatoria(12, 16, canales), 40, 30)
    assert resultado.shape == (30, 40, canales)
    assert resultado.dtype == np.uint8


def test_cp12_gris_sin_eje_de_canal_sigue_siendo_2d(metodo):
    resultado = metodo.reescalar(imagen_aleatoria(12, 16, canales=None), 40, 30)
    assert resultado.shape == (30, 40)


def test_cp12_conserva_la_transparencia(metodo):
    """Una zona totalmente transparente sigue siendo transparente."""
    matriz = imagen_aleatoria(10, 10, canales=4)
    matriz[:, :, 3] = 0
    resultado = metodo.reescalar(matriz, 30, 30)
    assert np.all(resultado[:, :, 3] == 0)


# ---------------------------------------------------------------- CP-13 rendimiento


def test_cp13_800x600_a_4k_en_menos_de_5_segundos(metodo):
    matriz = imagen_aleatoria(600, 800, canales=4)  # peor caso: 4 canales
    inicio = time.perf_counter()
    metodo.reescalar(matriz, 2880, 2160)
    duracion = time.perf_counter() - inicio
    assert duracion < TIEMPO_MAXIMO_SEGUNDOS


# ---------------------------------------------------------------- errores de entrada


@pytest.mark.parametrize(
    ("matriz", "nuevo_ancho", "nuevo_alto", "error"),
    [
        ([[1, 2], [3, 4]], 4, 4, TypeError),  # no es ndarray
        (np.zeros((2, 2), dtype=np.uint8), 4.0, 4, TypeError),  # ancho decimal
        (np.zeros((2, 2), dtype=np.uint8), True, 4, TypeError),  # bool
        (np.zeros((2, 2), dtype=np.uint8), 0, 4, ValueError),  # ancho cero
        (np.zeros((2, 2), dtype=np.uint8), 4, -1, ValueError),  # alto negativo
        (np.zeros((2, 2, 2), dtype=np.uint8), 4, 4, ValueError),  # 2 canales
        (np.zeros(5, dtype=np.uint8), 4, 4, ValueError),  # 1 dimension
    ],
)
def test_errores_de_entrada(metodo, matriz, nuevo_ancho, nuevo_alto, error):
    with pytest.raises(error):
        metodo.reescalar(matriz, nuevo_ancho, nuevo_alto)


# ---------------------------------------------------------------- diseno


def test_hereda_de_metodo_interpolacion(metodo):
    assert isinstance(metodo, MetodoInterpolacion)
    assert metodo.nombre == "bilineal"


def test_bilineal_no_usa_opencv():
    codigo = inspect.getsource(modulo_bilineal)
    assert "cv2" not in codigo
