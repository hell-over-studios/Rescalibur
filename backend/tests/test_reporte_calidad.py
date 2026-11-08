"""Pruebas del PDF del estudio (HU-11): secciones de calidad, tiempo y tamaño con tablas y gráficas.

Aquí no se lee el PDF: se cambia FPDF por una copia que anota lo que se le pide dibujar (textos,
párrafos, rectángulos y líneas). Así se comprueba qué contiene cada sección sin depender de cómo
queda en la página. Que se vea bien se revisa a mano abriendo el PDF del estudio (ver la PR).
"""

import math
from datetime import datetime

import pytest

import app.reporte
from app.graficas import ALTO_GRAFICA, agrupar, maximo_agradable
from app.metricas import Registro
from app.reporte import EXPLICACION_PSNR, GeneradorReportePDF
from estudio.comparativo import MedicionCalidad

METODOS = ["vecino", "bilineal", "bicubico"]
ANCHO_LEYENDA = 3  # mm del cuadrito de color de la leyenda
SECCIONES = ["1. Calidad (PSNR)", "2. Tiempo de reescalado", "3. Tamaño del PNG"]
SUBSECCIONES = [
    "1.1 Comparación por método",
    "1.2 Comparación por factor de reducción",
    "1.3 Comparación por imagen",
    "2.1 Comparación por método",
    "2.2 Comparación por resolución",
    "2.3 Comparación por imagen",
    "3.1 Comparación por método",
    "3.2 Comparación por resolución",
    "3.3 Comparación por imagen",
]
TITULOS_GRAFICAS = [
    "PSNR promedio por método (dB, más es mejor)",
    "PSNR promedio por factor de reducción (dB, más es mejor)",
    "PSNR promedio por imagen (dB, más es mejor)",
    "Tiempo promedio por método (ms, menos es mejor)",
    "Tiempo promedio por resolución (ms, menos es mejor)",
    "Tiempo promedio por imagen (ms, menos es mejor)",
    "Tamaño del PNG promedio por método (KB)",
    "Tamaño del PNG promedio por resolución (KB)",
    "Tamaño del PNG promedio por imagen (KB)",
]


def registro(imagen: str, metodo: str, resolucion: str, tiempo_ms: float) -> Registro:
    """El tamaño es el doble del tiempo más 1: así ningún valor de una sección cae en la otra."""
    fecha = datetime(2026, 11, 7)
    return Registro(fecha, imagen, metodo, 400, 300, 960, 720, resolucion, tiempo_ms, tiempo_ms * 2 + 1)


def registros_de_estudio() -> list[Registro]:
    """3 imágenes × 2 resoluciones × 3 métodos. Con 3 imágenes la mediana y el promedio son distintos."""
    return [
        registro(imagen, metodo, resolucion, base * (indice + 1) * multiplo)
        for imagen, multiplo in (("a.png", 1), ("b.png", 3), ("c.png", 8))
        for resolucion, base in (("hd", 10), ("4k", 100))
        for indice, metodo in enumerate(METODOS)
    ]


def calidad_de_estudio() -> list[MedicionCalidad]:
    """3 imágenes × 2 factores × 3 métodos: el PSNR sube 2 dB de un método al siguiente."""
    return [
        MedicionCalidad(imagen, factor, metodo, 20.0 + indice * 2 + extra - factor)
        for imagen, extra in (("a.png", 0), ("b.png", 4), ("c.png", 11))
        for factor in (2, 4)
        for indice, metodo in enumerate(METODOS)
    ]


@pytest.fixture
def dibujado(monkeypatch) -> dict:
    """Cambia FPDF por una copia que anota lo que se dibuja."""
    anotado = {
        "textos": [],  # Todo lo escrito: títulos, encabezados, celdas y números de las gráficas
        "marcas": [],  # Solo lo que escriben las gráficas: números, leyendas y categorías
        "parrafos": [],
        "rectangulos": 0,
        "barras": [],  # (y, ancho, alto, color) de cada barra; las leyendas son cuadritos y no cuentan
        "lineas": [],  # y de cada línea horizontal: la primera de cada gráfica es el eje, el cero
        "mas_bajo": 0.0,  # La y más baja a la que se dibujó algo
        "alto_pagina": 0.0,
        "color": None,  # Último color de relleno pedido
    }

    class FPDFGrabador(app.reporte.FPDF):
        def text(self, *args, **kwargs):
            anotado["textos"].append(args[2])
            anotado["marcas"].append(args[2])
            anotado["mas_bajo"] = max(anotado["mas_bajo"], args[1])
            anotado["alto_pagina"] = self.h
            return super().text(*args, **kwargs)

        def cell(self, *args, **kwargs):
            anotado["textos"].append(args[2] if len(args) > 2 else "")
            return super().cell(*args, **kwargs)

        def multi_cell(self, *args, **kwargs):
            anotado["parrafos"].append(args[2])
            return super().multi_cell(*args, **kwargs)

        def set_fill_color(self, *args, **kwargs):
            anotado["color"] = args
            return super().set_fill_color(*args, **kwargs)

        def line(self, *args, **kwargs):
            anotado["lineas"].append(args[1])
            return super().line(*args, **kwargs)

        def rect(self, *args, **kwargs):
            if kwargs.get("style") == "F":
                anotado["rectangulos"] += 1
                anotado["mas_bajo"] = max(anotado["mas_bajo"], args[1] + args[3])
                if args[2] > ANCHO_LEYENDA:
                    anotado["barras"].append((*args[1:4], anotado["color"]))
            return super().rect(*args, **kwargs)

    monkeypatch.setattr(app.reporte, "FPDF", FPDFGrabador)
    return anotado


def generar_estudio() -> None:
    GeneradorReportePDF().generar(registros_de_estudio(), calidad=calidad_de_estudio())


# --- Estructura: secciones, subsecciones, tablas y gráficas ---


def test_el_pdf_tiene_las_tres_secciones_en_orden(dibujado):
    generar_estudio()

    posiciones = [dibujado["textos"].index(seccion) for seccion in SECCIONES]
    assert posiciones == sorted(posiciones)


def test_cada_seccion_tiene_sus_tres_subsecciones_en_orden(dibujado):
    generar_estudio()

    posiciones = [dibujado["textos"].index(subseccion) for subseccion in SUBSECCIONES]
    assert posiciones == sorted(posiciones)


def test_cada_subseccion_tiene_su_grafica(dibujado):
    generar_estudio()

    posiciones = [dibujado["textos"].index(titulo) for titulo in TITULOS_GRAFICAS]
    assert posiciones == sorted(posiciones)


def test_cada_subseccion_tiene_su_tabla(dibujado):
    generar_estudio()

    for unidad in ("dB", "ms", "KB"):
        assert f"Promedio ({unidad})" in dibujado["textos"]  # Tabla por método
        assert f"bicubico ({unidad})" in dibujado["textos"]  # Tablas por opción y por imagen
    for encabezado in ("Factor de reducción", "Resolución", "Imagen", "Mediciones"):
        assert encabezado in dibujado["textos"]


def test_la_calidad_explica_que_es_el_psnr(dibujado):
    generar_estudio()

    assert EXPLICACION_PSNR in dibujado["parrafos"]
    assert len(dibujado["parrafos"]) == 4  # PSNR y experimento, tiempo y tamaño
    assert "PSNR" in EXPLICACION_PSNR and "dB" in EXPLICACION_PSNR


def test_los_datos_completos_van_como_anexos(dibujado):
    generar_estudio()

    assert "Anexo A. Registro de ejecuciones" in dibujado["textos"]
    assert "Anexo B. Calidad (PSNR) por medición" in dibujado["textos"]
    anexo_a = dibujado["textos"].index("Anexo A. Registro de ejecuciones")
    assert anexo_a > dibujado["textos"].index("3.3 Comparación por imagen")


def test_hay_una_barra_por_metodo_y_resultado_de_cada_grafica(dibujado):
    generar_estudio()

    # Por método: 3 barras. Por opción (2 grupos) y por imagen (3 grupos): una barra por método en cada
    # grupo. Son 3 secciones iguales: (3 + 2×3 + 3×3) = 18 barras cada una.
    assert len(dibujado["barras"]) == 3 * (3 + 6 + 9)
    # Más los cuadritos de leyenda de las 6 gráficas agrupadas (la de «por método» no lleva leyenda)
    assert dibujado["rectangulos"] == 3 * 18 + 6 * 3


def test_nada_se_dibuja_fuera_de_la_pagina(dibujado):
    generar_estudio()

    assert dibujado["mas_bajo"] < dibujado["alto_pagina"] - 10


# --- Valores ---


def test_la_tabla_y_la_grafica_por_metodo_usan_el_promedio(dibujado):
    generar_estudio()

    # vecino: HD 10, 30, 80 y 4K 100, 300, 800 -> promedio 220.0 (la mediana sería 90.0)
    cuerpo = dibujado["textos"][: dibujado["textos"].index("Anexo A. Registro de ejecuciones")]
    assert "220.0" in dibujado["marcas"] and "90.0" not in dibujado["marcas"]
    assert "220.0" in cuerpo and "90.0" not in cuerpo  # Lo mismo en la tabla (el anexo sí tiene un 90.0)
    # El tamaño es el doble más 1: 441.0 KB
    assert "441.0" in dibujado["marcas"] and "441.0" in cuerpo


def test_el_psnr_por_metodo_es_el_promedio_entre_imagenes_y_factores(dibujado):
    generar_estudio()

    # vecino: 18, 16 (imagen a), 22, 20 (b), 29, 27 (c) -> promedio 22.00
    assert "22.00" in dibujado["marcas"]
    assert "24.00" in dibujado["marcas"] and "26.00" in dibujado["marcas"]


def test_las_agrupaciones_por_opcion_y_por_imagen_promedian_cada_grupo(dibujado):
    generar_estudio()

    assert {"HD", "4K"} <= set(dibujado["marcas"])
    assert {"Reducción x2", "Reducción x4"} <= set(dibujado["marcas"])
    assert {"a.png", "b.png", "c.png"} <= set(dibujado["marcas"])
    # Tiempo de vecino en la imagen a.png: HD 10 y 4K 100 -> promedio 55.0
    assert "55.0" in dibujado["marcas"]
    # Tiempo de vecino en HD: 10, 30 y 80 -> 40.0
    assert "40.0" in dibujado["marcas"]
    # PSNR de vecino con reducción x2: 18, 22 y 29 -> promedio 23.00 (la mediana sería 22.00)
    assert "23.00" in dibujado["marcas"]


def test_las_barras_parten_de_cero_y_su_alto_es_proporcional_a_su_valor(dibujado):
    generar_estudio()

    # Las 3 primeras barras son las del PSNR por método: 22, 24 y 26 dB
    barras = dibujado["barras"][:3]
    bases = {round(y + alto, 6) for y, _, alto, _ in barras}
    altos = [alto for _, _, alto, _ in barras]
    assert bases == {round(dibujado["lineas"][0], 6)}  # Apoyadas en el eje, en el cero
    assert altos[2] / altos[0] == pytest.approx(26 / 22)
    assert ALTO_GRAFICA / 2 <= max(altos) <= ALTO_GRAFICA  # La más alta llena al menos la mitad


def test_en_la_grafica_por_metodo_cada_metodo_tiene_su_color_y_el_mismo_en_las_agrupadas(dibujado):
    generar_estudio()

    colores_por_metodo = [color for *_, color in dibujado["barras"][:3]]
    assert len(set(colores_por_metodo)) == 3
    # Siguiente gráfica (PSNR por factor de reducción): grupos x2 y x4, y en cada uno los 3 métodos
    colores_agrupada = [color for *_, color in dibujado["barras"][3:9]]
    assert colores_agrupada == colores_por_metodo * 2


# --- Casos especiales ---


def test_sin_calidad_el_pdf_no_cambia_y_no_trae_secciones(dibujado):
    GeneradorReportePDF().generar(registros_de_estudio())

    assert dibujado["rectangulos"] == 0
    assert dibujado["parrafos"] == []
    assert not set(SECCIONES) & set(dibujado["textos"])
    assert "Registro de ejecuciones" in dibujado["textos"]


def test_los_psnr_infinitos_se_dejan_fuera_del_promedio(dibujado):
    calidad = [
        MedicionCalidad("a.png", 2, "vecino", math.inf),
        MedicionCalidad("b.png", 2, "vecino", 30.0),
    ]

    GeneradorReportePDF().generar(registros_de_estudio(), calidad=calidad)

    assert "30.00" in dibujado["marcas"]
    assert "inf" not in dibujado["marcas"]  # El anexo sí muestra «inf», pero las gráficas no


def test_si_todos_los_psnr_son_infinitos_se_omite_la_seccion_de_calidad(dibujado):
    calidad = [MedicionCalidad("a.png", 2, "vecino", math.inf)]

    GeneradorReportePDF().generar(registros_de_estudio(), calidad=calidad)

    assert SECCIONES[0] not in dibujado["textos"]
    assert SECCIONES[1] in dibujado["textos"] and SECCIONES[2] in dibujado["textos"]


def test_el_pdf_del_estudio_es_un_pdf_completo():
    pdf = bytes(GeneradorReportePDF().generar(registros_de_estudio(), calidad=calidad_de_estudio()))

    assert pdf.startswith(b"%PDF")
    assert b"%%EOF" in pdf[-1024:]


# --- Funciones de apoyo de graficas.py ---


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [(608.9, 800), (31.95, 40), (0.9, 1.0), (400, 400), (80, 80), (0, 4)],
)
def test_el_tope_del_eje_es_un_numero_redondo_que_se_divide_en_4(valor, esperado):
    tope = maximo_agradable(valor)

    assert tope == pytest.approx(esperado)
    assert tope >= valor


def test_agrupar_junta_por_grupo_y_serie_en_orden_de_aparicion():
    datos = [("HD", "vecino", 1), ("HD", "vecino", 3), ("HD", "bilineal", 5), ("4K", "vecino", 7)]

    grupos, series = agrupar(datos, sum)

    assert grupos == ["HD", "4K"]
    assert series == {"vecino": [4, 7], "bilineal": [5, 0.0]}  # Lo que falta vale 0
