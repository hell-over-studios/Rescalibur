"""Pruebas de T31 (HU-11): imágenes del estudio y medición de tiempos con la mediana de 5.

Es la parte de tiempos de CP-28: 3 métodos × 4 resoluciones por imagen. El CSV es de T32 y las
pruebas completas de CP-28 y CP-29 (tests/test_estudio.py), de T33. Por eso este archivo tiene otro
nombre: así no se pisa con el de T33.

Las pruebas de medición usan imágenes pequeñas y, cuando no importa el método, solo el vecino,
para que corran rápido. Las imágenes reales del estudio solo se leen, no se miden aquí.
"""

from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from app.config import METODOS_DISPONIBLES
from app.metodos.vecino import VecinoMasCercano
from app.procesador import ProcesadorImagen
from app.resoluciones import RESOLUCIONES, CalculadoraResolucion
from estudio import comparativo
from estudio.comparativo import (
    MINIMO_IMAGENES,
    REPETICIONES,
    MedicionTiempo,
    imprimir_tabla,
    listar_imagenes,
    medir_mediana_ms,
    medir_tiempos,
)

CLAVES = [resolucion.clave for resolucion in RESOLUCIONES]


def guardar_imagen(ruta, alto: int, ancho: int, canales: int = 3) -> None:
    """Guarda una imagen de prueba con valores aleatorios (fijos por la semilla)."""
    forma = (alto, ancho, canales) if canales > 1 else (alto, ancho)
    matriz = np.random.default_rng(31).integers(0, 256, forma, dtype=np.uint8)
    cv2.imwrite(str(ruta), matriz)


@pytest.fixture
def carpeta(tmp_path):
    """Carpeta con 3 imágenes pequeñas (horizontal, vertical y cuadrada) y un archivo que no es imagen."""
    guardar_imagen(tmp_path / "a_horizontal.png", 30, 40)
    guardar_imagen(tmp_path / "b_vertical.png", 40, 30)
    guardar_imagen(tmp_path / "c_cuadrada.png", 36, 36)
    (tmp_path / "LEEME.md").write_text("no es una imagen")
    return tmp_path


class MetodoContador:
    """Método falso: no calcula nada, solo cuenta cuántas veces se le pide reescalar."""

    def __init__(self):
        self.llamadas = 0

    def reescalar(self, matriz, nuevo_ancho, nuevo_alto):
        self.llamadas += 1
        return matriz


# --- Imágenes del estudio ---


def test_las_imagenes_del_repositorio_cumplen_lo_que_pide_el_estudio():
    procesador = ProcesadorImagen()
    calculadora = CalculadoraResolucion()

    imagenes = listar_imagenes()

    assert len(imagenes) >= MINIMO_IMAGENES
    for ruta in imagenes:
        alto, ancho = procesador.leer(ruta.read_bytes()).shape[:2]
        for clave in CLAVES:  # Lanza ValueError si la imagen no se puede ampliar a esa resolución
            calculadora.calcular_dimensiones(ancho, alto, clave)


def test_listar_imagenes_ordena_por_nombre_e_ignora_lo_que_no_es_imagen(carpeta):
    assert [ruta.name for ruta in listar_imagenes(carpeta)] == [
        "a_horizontal.png",
        "b_vertical.png",
        "c_cuadrada.png",
    ]


def test_listar_imagenes_con_menos_del_minimo_lanza_error(carpeta):
    (carpeta / "c_cuadrada.png").unlink()

    with pytest.raises(ValueError, match="al menos 3 imágenes"):
        listar_imagenes(carpeta)


# --- Mediana de 5 ---


def test_mide_cinco_veces_por_defecto():
    metodo = MetodoContador()

    medir_mediana_ms(metodo, np.zeros((4, 4), dtype=np.uint8), 8, 8)

    assert REPETICIONES == 5
    assert metodo.llamadas == 5


def test_las_repeticiones_se_pueden_cambiar():
    metodo = MetodoContador()

    medir_mediana_ms(metodo, np.zeros((4, 4), dtype=np.uint8), 8, 8, repeticiones=3)

    assert metodo.llamadas == 3


def test_devuelve_la_mediana_y_no_el_promedio(monkeypatch):
    # Cada medición lee el reloj dos veces (inicio y fin). Duraciones: 0,1 s; 5 s; 0,1 s; 0,1 s; 0,1 s.
    # El promedio sería 1 080 ms; la mediana es 100 ms: el tiempo atípico no la afecta.
    lecturas = iter([0.0, 0.1, 10.0, 15.0, 20.0, 20.1, 30.0, 30.1, 40.0, 40.1])
    reloj = SimpleNamespace(perf_counter=lambda: next(lecturas))
    monkeypatch.setattr(comparativo, "time", reloj)

    tiempo_ms = medir_mediana_ms(MetodoContador(), np.zeros((4, 4), dtype=np.uint8), 8, 8)

    assert tiempo_ms == pytest.approx(100.0)


# --- medir_tiempos ---


def test_cada_imagen_se_lleva_a_las_cuatro_resoluciones_en_orden(carpeta):
    mediciones = medir_tiempos(carpeta, metodos={"vecino": VecinoMasCercano}, repeticiones=1)

    assert len(mediciones) == 3 * 4
    for imagen in ["a_horizontal.png", "b_vertical.png", "c_cuadrada.png"]:
        assert [m.resolucion for m in mediciones if m.imagen == imagen] == CLAVES


def test_las_dimensiones_finales_son_las_de_la_calculadora(carpeta):
    calculadora = CalculadoraResolucion()

    mediciones = medir_tiempos(carpeta, metodos={"vecino": VecinoMasCercano}, repeticiones=1)

    for m in mediciones:
        esperado = calculadora.calcular_dimensiones(m.ancho_original, m.alto_original, m.resolucion)
        assert (m.ancho_final, m.alto_final) == esperado
    vertical = next(m for m in mediciones if m.imagen == "b_vertical.png" and m.resolucion == "hd")
    assert (vertical.ancho_original, vertical.alto_original) == (30, 40)
    assert vertical.alto_final > vertical.ancho_final  # El marco gira con las imágenes verticales


def test_por_defecto_mide_los_tres_metodos_del_proyecto(carpeta):
    mediciones = medir_tiempos(carpeta, repeticiones=1)

    assert len(mediciones) == 3 * 4 * 3  # CP-28: 3 métodos × 4 resoluciones por imagen
    primera_combinacion = [m.metodo for m in mediciones[:3]]
    assert primera_combinacion == list(METODOS_DISPONIBLES)
    assert set(primera_combinacion) == {"vecino", "bilineal", "bicubico"}


def test_los_tiempos_son_positivos(carpeta):
    mediciones = medir_tiempos(carpeta, metodos={"vecino": VecinoMasCercano}, repeticiones=1)

    assert all(m.tiempo_ms > 0 for m in mediciones)


def test_una_imagen_que_no_se_puede_ampliar_detiene_el_estudio_y_dice_cual(carpeta):
    guardar_imagen(carpeta / "a_grande.png", 3000, 4000, canales=1)  # 4000 x 3000 no se amplía a HD

    with pytest.raises(ValueError, match="a_grande.png"):
        medir_tiempos(carpeta, metodos={"vecino": VecinoMasCercano}, repeticiones=1)


# --- Salida en la terminal ---


def test_imprimir_tabla_muestra_un_encabezado_y_una_fila_por_medicion(capsys):
    mediciones = [
        MedicionTiempo("paisaje.png", 800, 600, "4k", 2880, 2160, "bicubico", 712.34),
        MedicionTiempo("paisaje.png", 800, 600, "4k", 2880, 2160, "vecino", 76.5),
    ]

    imprimir_tabla(mediciones)

    lineas = capsys.readouterr().out.splitlines()
    assert len(lineas) == 3
    assert "Mediana (ms)" in lineas[0]
    assert "paisaje.png" in lineas[1] and "800x600" in lineas[1] and "2880x2160" in lineas[1]
    assert lineas[1].rstrip().endswith("712.3")
    assert lineas[2].rstrip().endswith("76.5")
