"""Pruebas de HU-11: calidad con PSNR y archivos del estudio comparativo.

CP-28: el estudio genera resultados.csv con 3 métodos × 4 resoluciones por imagen.
CP-29: una imagen con un error de 5 niveles en todos los píxeles da un PSNR de 34,15 dB.

Las pruebas de tiempos (mediana de 5, imágenes del estudio) están en test_estudio_tiempos.py.
Aquí las pruebas usan imágenes pequeñas y 1 repetición para que el estudio completo corra rápido.
"""

import csv
import math

import cv2
import numpy as np
import pytest

from app.config import METODOS_DISPONIBLES
from app.metodos.vecino import VecinoMasCercano
from app.metricas import psnr
from app.reporte import GeneradorReportePDF
from estudio import comparativo
from estudio.comparativo import (
    FACTORES_REDUCCION,
    MedicionCalidad,
    ejecutar_estudio,
    imprimir_calidad,
    medir_calidad,
    reducir,
)

METODOS = list(METODOS_DISPONIBLES)
IMAGENES = ["a_horizontal.png", "b_vertical.png", "c_cuadrada.png"]
RESOLUCIONES = ["hd", "fullhd", "2k", "4k"]


def guardar_imagen(ruta, matriz: np.ndarray) -> None:
    cv2.imwrite(str(ruta), matriz)


def imagen_suave(alto: int, ancho: int) -> np.ndarray:
    """Degradado suave en 3 canales: la interpolación lo recupera bien al ampliar."""
    y, x = np.mgrid[0:alto, 0:ancho]
    base = 127 + 100 * np.sin(x / 9.0) * np.cos(y / 11.0)
    return np.stack([base, base * 0.8, base * 0.6], axis=-1).astype(np.uint8)


def crear_carpeta(ruta):
    """Carpeta con 3 imágenes pequeñas (horizontal, vertical y cuadrada) y un archivo que no es imagen."""
    ruta.mkdir(parents=True, exist_ok=True)
    guardar_imagen(ruta / IMAGENES[0], imagen_suave(48, 64))
    guardar_imagen(ruta / IMAGENES[1], imagen_suave(64, 48))
    guardar_imagen(ruta / IMAGENES[2], imagen_suave(48, 48))
    (ruta / "LEEME.md").write_text("no es una imagen")
    return ruta


@pytest.fixture
def carpeta(tmp_path):
    return crear_carpeta(tmp_path)


# --- PSNR ---


def test_cp29_error_de_5_niveles_da_34_15_db():
    original = np.full((10, 10), 100, dtype=np.uint8)
    estimada = np.full((10, 10), 105, dtype=np.uint8)

    assert round(psnr(original, estimada), 2) == 34.15


def test_psnr_de_imagenes_identicas_es_infinito():
    imagen = imagen_suave(20, 30)

    assert psnr(imagen, imagen.copy()) == math.inf


def test_psnr_de_negro_contra_blanco_es_cero():
    negro = np.zeros((8, 8, 3), dtype=np.uint8)
    blanco = np.full((8, 8, 3), 255, dtype=np.uint8)

    assert psnr(negro, blanco) == pytest.approx(0.0)


def test_psnr_no_se_desborda_con_uint8():
    """10 - 20 en uint8 daría 246; el PSNR debe tratar la diferencia como -10, igual que 20 - 10."""
    a = np.full((5, 5), 10, dtype=np.uint8)
    b = np.full((5, 5), 20, dtype=np.uint8)

    assert psnr(a, b) == pytest.approx(psnr(b, a))
    assert psnr(a, b) == pytest.approx(10 * math.log10(255**2 / 100))


def test_psnr_usa_el_promedio_de_todos_los_pixeles():
    """Un solo píxel con error 10 en 100 píxeles: MSE = 100/100 = 1."""
    original = np.zeros((10, 10), dtype=np.uint8)
    estimada = original.copy()
    estimada[0, 0] = 10

    assert psnr(original, estimada) == pytest.approx(10 * math.log10(255**2 / 1))


def test_psnr_con_formas_distintas_lanza_error():
    with pytest.raises(ValueError, match="misma forma"):
        psnr(np.zeros((4, 4), dtype=np.uint8), np.zeros((4, 5), dtype=np.uint8))


# --- Reducción con INTER_AREA ---


@pytest.mark.parametrize("factor", FACTORES_REDUCCION)
def test_reducir_divide_las_dimensiones_entre_el_factor(factor):
    reducida = reducir(imagen_suave(60, 84), factor)

    assert reducida.shape == (60 // factor, 84 // factor, 3)


def test_reducir_promedia_los_pixeles_cubiertos():
    """INTER_AREA con factor 2: cada píxel nuevo es el promedio de un bloque de 2 × 2."""
    matriz = np.array([[0, 100], [100, 200]], dtype=np.uint8)

    assert reducir(matriz, 2).tolist() == [[100]]


def test_reducir_una_imagen_muy_pequena_lanza_error():
    with pytest.raises(ValueError, match="muy pequeña"):
        reducir(np.zeros((3, 3), dtype=np.uint8), 4)


# --- medir_calidad ---


def test_mide_cada_imagen_con_cada_factor_y_cada_metodo_en_orden(carpeta):
    mediciones = medir_calidad(carpeta)

    assert len(mediciones) == 3 * len(FACTORES_REDUCCION) * 3
    primera_imagen = [m for m in mediciones if m.imagen == IMAGENES[0]]
    assert [(m.factor, m.metodo) for m in primera_imagen] == [
        (factor, metodo) for factor in FACTORES_REDUCCION for metodo in METODOS
    ]
    assert [m.imagen for m in mediciones[:: len(mediciones) // 3]] == IMAGENES


def test_el_psnr_baja_cuando_se_reduce_mas(carpeta):
    """Con más reducción se pierde más información, así que lo que se recupera se parece menos."""
    mediciones = medir_calidad(carpeta, metodos={"bilineal": METODOS_DISPONIBLES["bilineal"]})

    por_factor = {m.factor: m.psnr_db for m in mediciones if m.imagen == IMAGENES[0]}
    assert por_factor[2] > por_factor[3] > por_factor[4]


def test_en_una_imagen_suave_el_bicubico_supera_al_bilineal_y_este_al_vecino(carpeta):
    mediciones = medir_calidad(carpeta, factores=(2,))

    for imagen in IMAGENES:
        psnr_por_metodo = {m.metodo: m.psnr_db for m in mediciones if m.imagen == imagen}
        assert psnr_por_metodo["bicubico"] > psnr_por_metodo["bilineal"] > psnr_por_metodo["vecino"]


def test_la_ampliacion_vuelve_al_tamano_original(carpeta, monkeypatch):
    formas = []
    original = comparativo.psnr

    def psnr_que_anota(a, b):
        formas.append((a.shape, b.shape))
        return original(a, b)

    monkeypatch.setattr(comparativo, "psnr", psnr_que_anota)

    medir_calidad(carpeta, metodos={"vecino": VecinoMasCercano}, factores=(3,))

    assert formas and all(forma_original == forma_ampliada for forma_original, forma_ampliada in formas)


def test_una_imagen_muy_pequena_detiene_la_calidad_y_dice_cual(carpeta):
    guardar_imagen(carpeta / "a_diminuta.png", np.zeros((3, 3), dtype=np.uint8))

    with pytest.raises(ValueError, match="a_diminuta.png"):
        medir_calidad(carpeta, metodos={"vecino": VecinoMasCercano})


# --- Salida en la terminal ---


def test_imprimir_calidad_muestra_un_encabezado_y_una_fila_por_medicion(capsys):
    imprimir_calidad(
        [
            MedicionCalidad("paisaje.png", 2, "bicubico", 31.456),
            MedicionCalidad("paisaje.png", 4, "vecino", math.inf),
        ]
    )

    lineas = capsys.readouterr().out.splitlines()
    assert len(lineas) == 3
    assert "PSNR (dB)" in lineas[0]
    assert "x2" in lineas[1] and lineas[1].rstrip().endswith("31.46")
    assert "x4" in lineas[2] and lineas[2].rstrip().endswith("inf")


# --- Estudio completo: CSV y PDF (CP-28) ---


def leer_csv(ruta) -> list[dict]:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


@pytest.fixture(scope="module")
def estudio(tmp_path_factory):
    """Corre el estudio completo una sola vez (es lo más lento) y devuelve la carpeta de resultados."""
    base = tmp_path_factory.mktemp("estudio")
    carpeta = crear_carpeta(base / "imagenes")
    resultados = base / "salida" / "resultados"  # No existe: el estudio la crea
    ejecutar_estudio(carpeta, resultados, repeticiones=1)
    return resultados


def test_cp28_resultados_csv_tiene_3_metodos_por_4_resoluciones_por_imagen(estudio):
    filas = leer_csv(estudio / "resultados.csv")

    assert len(filas) == 3 * 4 * 3
    combinaciones = {(f["imagen"], f["resolucion"], f["metodo"]) for f in filas}
    esperadas = {(i, r, m) for i in IMAGENES for r in RESOLUCIONES for m in METODOS}
    assert combinaciones == esperadas


def test_resultados_csv_tiene_tiempo_y_tamano_de_cada_combinacion(estudio):
    filas = leer_csv(estudio / "resultados.csv")

    assert list(filas[0]) == [
        "imagen",
        "ancho_original",
        "alto_original",
        "resolucion",
        "ancho_final",
        "alto_final",
        "metodo",
        "tiempo_ms",
        "tamano_kb",
    ]
    assert all(float(f["tiempo_ms"]) > 0 and float(f["tamano_kb"]) > 0 for f in filas)
    vertical = next(f for f in filas if f["imagen"] == IMAGENES[1] and f["resolucion"] == "hd")
    assert (vertical["ancho_original"], vertical["alto_original"]) == ("48", "64")


def test_calidad_csv_tiene_un_renglon_por_imagen_factor_y_metodo(estudio):
    filas = leer_csv(estudio / "calidad.csv")

    assert len(filas) == 3 * len(FACTORES_REDUCCION) * 3
    assert list(filas[0]) == ["imagen", "factor", "metodo", "psnr_db"]
    assert {int(f["factor"]) for f in filas} == set(FACTORES_REDUCCION)
    assert all(float(f["psnr_db"]) > 0 for f in filas)


def test_el_estudio_genera_el_pdf(estudio):
    pdf = (estudio / "estudio_comparativo.pdf").read_bytes()

    assert pdf.startswith(b"%PDF")
    assert b"%%EOF" in pdf[-1024:]


def test_el_estudio_crea_la_carpeta_de_resultados_y_solo_deja_los_tres_archivos(estudio):
    assert sorted(ruta.name for ruta in estudio.iterdir()) == [
        "calidad.csv",
        "estudio_comparativo.pdf",
        "resultados.csv",
    ]


def test_ejecutar_estudio_devuelve_las_mediciones(carpeta, tmp_path):
    metodos = {"vecino": VecinoMasCercano}

    tiempos, calidad = ejecutar_estudio(carpeta, tmp_path / "r", metodos, repeticiones=1)

    assert len(tiempos) == 3 * 4
    assert len(calidad) == 3 * len(FACTORES_REDUCCION)


def test_un_psnr_infinito_se_escribe_como_inf_en_el_csv(tmp_path):
    ruta = tmp_path / "calidad.csv"

    comparativo.escribir_csv_calidad([MedicionCalidad("foto.png", 2, "vecino", math.inf)], ruta)

    assert leer_csv(ruta)[0]["psnr_db"] == "inf"


def test_el_pdf_del_estudio_usa_el_titulo_y_la_calidad(carpeta, tmp_path, monkeypatch):
    """escribir_pdf le pasa al generador los tiempos como registros, el título del estudio y la calidad."""
    recibido = {}

    class GeneradorFalso:
        def generar(self, registros, titulo, calidad=None):
            recibido.update(registros=registros, titulo=titulo, calidad=calidad)
            return bytearray(b"%PDF-1.4\n%%EOF\n")

    monkeypatch.setattr(comparativo, "GeneradorReportePDF", GeneradorFalso)

    metodos = {"vecino": VecinoMasCercano}
    tiempos, calidad = ejecutar_estudio(carpeta, tmp_path / "r", metodos, repeticiones=1)

    assert recibido["titulo"] == comparativo.TITULO_PDF
    assert recibido["calidad"] == calidad
    assert [(r.archivo, r.metodo, r.resolucion, r.tiempo_ms) for r in recibido["registros"]] == [
        (m.imagen, m.metodo, m.resolucion, m.tiempo_ms) for m in tiempos
    ]
    assert (tmp_path / "r" / "estudio_comparativo.pdf").read_bytes() == b"%PDF-1.4\n%%EOF\n"


# --- GeneradorReportePDF con calidad (extensión de HU-10) ---


def test_el_generador_agrega_la_tabla_de_calidad_solo_cuando_se_la_piden():
    calidad = [MedicionCalidad("foto.png", f, m, 30.0 + f) for f in FACTORES_REDUCCION for m in METODOS]

    sin_calidad = GeneradorReportePDF().generar([])
    con_calidad = GeneradorReportePDF().generar([], calidad=calidad)

    assert bytes(con_calidad).startswith(b"%PDF")
    assert len(con_calidad) > len(sin_calidad)
