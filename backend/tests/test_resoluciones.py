"""Pruebas unitarias de CalculadoraResolucion (HU-02, casos CP-04 a CP-07)."""

import pytest

from app.resoluciones import CalculadoraResolucion

calculadora = CalculadoraResolucion()


def resumen(ancho: int, alto: int) -> dict[str, tuple[int, int]]:
    """Convierte las opciones en {clave: (ancho, alto)} para comparar fácil."""
    return {o.clave: (o.ancho, o.alto) for o in calculadora.opciones_disponibles(ancho, alto)}


def test_cp04_todas_las_opciones():
    assert resumen(800, 600) == {
        "hd": (960, 720),
        "fullhd": (1440, 1080),
        "2k": (1920, 1440),
        "4k": (2880, 2160),
    }


def test_cp05_opciones_parciales():
    # Full HD exacto: s = 1 en HD y Full HD, por eso no se ofrecen.
    assert resumen(1920, 1080) == {"2k": (2560, 1440), "4k": (3840, 2160)}


def test_cp06_imagen_vertical_gira_el_marco():
    assert resumen(1080, 1920) == {"2k": (1440, 2560), "4k": (2160, 3840)}


def test_cp07_sin_opciones():
    assert resumen(4000, 3000) == {}


def test_imagen_cuadrada_usa_marco_horizontal():
    # 500 x 500 en HD: s = min(1280/500, 720/500) = 1.44 -> 720 x 720
    assert resumen(500, 500)["hd"] == (720, 720)


def test_se_conserva_la_proporcion():
    for opcion in calculadora.opciones_disponibles(1000, 750):
        assert abs(opcion.ancho / opcion.alto - 1000 / 750) < 0.01


def test_calcular_dimensiones_de_una_clave():
    assert calculadora.calcular_dimensiones(800, 600, "fullhd") == (1440, 1080)


def test_clave_desconocida_lanza_error():
    with pytest.raises(ValueError):
        calculadora.calcular_dimensiones(800, 600, "8k")


def test_clave_no_disponible_lanza_error():
    with pytest.raises(ValueError):
        calculadora.calcular_dimensiones(1920, 1080, "hd")