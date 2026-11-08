"""Gráficas de barras y tablas simples para el PDF del estudio comparativo (HU-11).

Se dibujan con las funciones básicas de fpdf2 (rectángulos, líneas y texto), sin librerías de gráficas,
para no sumar dependencias. Todas las medidas están en milímetros, como en fpdf2.
"""

import math
from collections.abc import Callable

from fpdf import FPDF

# Un color por método, de claro a oscuro: de menos a más complejo (vecino, bilineal, bicúbico).
COLORES_METODOS = [(170, 185, 205), (75, 115, 170), (20, 45, 100)]
ALTO_GRAFICA = 42  # mm de alto del área de barras
ANCHO_EJE = 14  # mm que se reservan a la izquierda para los números del eje vertical
ANCHO_MAXIMO_BARRA = 14
LINEAS_GUIA = 4  # El eje vertical se divide en 4 tramos
ALTO_FILA_TABLA = 8
# Alto en mm de una gráfica completa: título 8 + leyenda y margen 11 + barras + categorías 8 + margen 4
ALTO_BLOQUE_GRAFICA = 8 + 11 + ALTO_GRAFICA + 8 + 4


def alto_tabla(filas: int) -> int:
    """Alto en mm de una tabla con encabezado y `filas` renglones."""
    return (filas + 1) * ALTO_FILA_TABLA


def agrupar(
    datos: list[tuple], resumen: Callable[[list[float]], float]
) -> tuple[list[str], dict[str, list[float]]]:
    """Ordena (grupo, serie, valor) para graficar: devuelve los grupos y un valor por grupo de cada serie.

    `resumen` (mediana, promedio...) junta los valores que caen en el mismo grupo y serie.
    Grupos y series quedan en el orden en que aparecen. Si falta una combinación, su valor es 0.
    """
    valores: dict[tuple, list[float]] = {}
    grupos: list[str] = []
    series: list[str] = []
    for grupo, serie, valor in datos:
        if grupo not in grupos:
            grupos.append(grupo)
        if serie not in series:
            series.append(serie)
        valores.setdefault((grupo, serie), []).append(valor)

    return grupos, {
        serie: [resumen(valores[(g, serie)]) if (g, serie) in valores else 0.0 for g in grupos]
        for serie in series
    }


def maximo_agradable(valor: float) -> float:
    """Tope del eje vertical: el menor número «redondo» ≥ valor que se divide bien en 4 tramos.

    Ejemplos: 608.9 -> 800 (tramos de 200); 31.95 -> 40 (tramos de 10); 0.9 -> 1 (tramos de 0.25).
    """
    if valor <= 0:
        return float(LINEAS_GUIA)
    exponente = math.floor(math.log10(valor / LINEAS_GUIA))
    for base in (1, 2, 2.5, 5, 10):
        paso = base * 10**exponente
        if paso * LINEAS_GUIA >= valor:
            return paso * LINEAS_GUIA
    return 10 ** (exponente + 1) * LINEAS_GUIA  # No se llega aquí: con base = 10 siempre alcanza


def dibujar_tabla(pdf: FPDF, encabezados: list[str], filas: list[list[str]], anchos: list[float]) -> None:
    """Dibuja una tabla con encabezado gris y deja el cursor debajo de ella, en el margen izquierdo."""
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", style="B", size=9)
    pdf.set_x(pdf.l_margin)
    for encabezado, ancho in zip(encabezados, anchos):
        pdf.cell(ancho, ALTO_FILA_TABLA, encabezado, border=1, fill=True)
    pdf.ln(ALTO_FILA_TABLA)

    pdf.set_font("helvetica", size=9)
    for fila in filas:
        for valor, ancho in zip(fila, anchos):
            pdf.cell(ancho, ALTO_FILA_TABLA, valor, border=1)
        pdf.ln(ALTO_FILA_TABLA)


def dibujar_barras(
    pdf: FPDF,
    titulo: str,
    grupos: list[str],
    series: dict[str, list[float]],
    decimales: int,
    colorear_grupos: bool = False,
) -> None:
    """Dibuja una gráfica de barras agrupadas: un grupo por categoría y una barra por serie.

    Las barras parten de cero y llevan su valor escrito encima. Con `colorear_grupos` se espera una
    sola serie y cada barra toma el color de su grupo (por ejemplo, un color por método), sin leyenda.
    Si no hay grupos no dibuja nada. Al terminar deja el cursor debajo de la gráfica, en el margen
    izquierdo, y los colores del PDF como los esperan las tablas (texto y líneas negros, relleno gris).
    """
    if not grupos:
        return

    if pdf.get_y() + ALTO_BLOQUE_GRAFICA > pdf.page_break_trigger:
        pdf.add_page()

    x_inicio = pdf.l_margin
    y = pdf.get_y()

    # Título
    pdf.set_font("helvetica", style="B", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(x_inicio, y)
    pdf.cell(0, 6, titulo)
    y += 8

    # Leyenda: un cuadrito de color por serie
    pdf.set_font("helvetica", size=8)
    if not colorear_grupos:
        x = x_inicio + ANCHO_EJE
        for i, nombre in enumerate(series):
            pdf.set_fill_color(*COLORES_METODOS[i % len(COLORES_METODOS)])
            pdf.rect(x, y + 0.5, 3, 3, style="F")
            pdf.text(x + 4.5, y + 3.2, nombre)
            x += 4.5 + pdf.get_string_width(nombre) + 8
    y += 4 if colorear_grupos else 11  # Sin leyenda sobra menos espacio; 4 mm es el margen para el número

    # Eje vertical con líneas guía
    maximo = maximo_agradable(max(max(valores) for valores in series.values()))
    y_base = y + ALTO_GRAFICA
    x_area = x_inicio + ANCHO_EJE
    ancho_area = pdf.w - pdf.l_margin - pdf.r_margin - ANCHO_EJE

    pdf.set_line_width(0.2)
    pdf.set_font("helvetica", size=7)
    for k in range(LINEAS_GUIA + 1):
        y_linea = y_base - ALTO_GRAFICA * k / LINEAS_GUIA
        if k == 0:
            pdf.set_draw_color(120, 120, 120)  # La línea base, más oscura que las guías
        else:
            pdf.set_draw_color(220, 220, 220)
        pdf.line(x_area, y_linea, x_area + ancho_area, y_linea)
        numero = f"{maximo * k / LINEAS_GUIA:g}"
        pdf.set_text_color(90, 90, 90)
        pdf.text(x_area - 1.5 - pdf.get_string_width(numero), y_linea + 1, numero)

    # Barras
    ancho_grupo = ancho_area / len(grupos)
    ancho_barra = min(ancho_grupo * 0.8 / len(series), ANCHO_MAXIMO_BARRA)
    ancho_bloque = ancho_barra * len(series)
    for g, grupo in enumerate(grupos):
        x_bloque = x_area + g * ancho_grupo + (ancho_grupo - ancho_bloque) / 2
        for i, valores in enumerate(series.values()):
            alto = ALTO_GRAFICA * valores[g] / maximo
            x_barra = x_bloque + i * ancho_barra
            color = COLORES_METODOS[(g if colorear_grupos else i) % len(COLORES_METODOS)]
            pdf.set_fill_color(*color)
            pdf.rect(x_barra, y_base - alto, ancho_barra, alto, style="F")

            numero = f"{valores[g]:.{decimales}f}"
            pdf.set_font("helvetica", size=6)
            pdf.set_text_color(0, 0, 0)
            x_numero = x_barra + (ancho_barra - pdf.get_string_width(numero)) / 2
            pdf.text(x_numero, y_base - alto - 1, numero)

        pdf.set_font("helvetica", size=8)
        pdf.text(x_bloque + (ancho_bloque - pdf.get_string_width(grupo)) / 2, y_base + 5, grupo)

    # Se devuelven los colores y el cursor a como los esperan las tablas que siguen
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_xy(x_inicio, y_base + 8 + 4)
