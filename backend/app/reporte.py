import math
import statistics
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime

from fpdf import FPDF

# Gráficas del estudio comparativo (HU-11)
NOMBRES_RESOLUCION = {"hd": "HD", "fullhd": "Full HD", "2k": "2K", "4k": "4K"}
# Un color por método, de claro a oscuro: de menos a más complejo (vecino, bilineal, bicúbico).
COLORES_METODOS = [(170, 185, 205), (75, 115, 170), (20, 45, 100)]
EXPLICACION_PSNR = (
    "PSNR (relación señal-ruido pico): mide en decibelios (dB) qué tan parecida queda la imagen "
    "ampliada a la original, con 10·log10(255² / MSE), donde MSE es el error cuadrático medio entre "
    "sus píxeles. Más dB = más parecida."
)
ALTO_GRAFICA = 50  # mm de alto del área de barras
ANCHO_EJE = 14  # mm que se reservan a la izquierda para los números del eje vertical
LINEAS_GUIA = 4  # El eje vertical se divide en 4 tramos
# Alto en mm de una gráfica completa: título 8 + leyenda 11 + barras + categorías 8 + nota 6 + margen 4
ALTO_BLOQUE_GRAFICA = 8 + 11 + ALTO_GRAFICA + 8 + 6 + 4
ALTO_EXPLICACION = 15  # Las dos líneas del PSNR más el espacio de después


class GeneradorReportePDF:
    def generar(
        self,
        registros: list,
        titulo: str = "Rescalibur · Métricas de ejecución",
        calidad: list | None = None,
    ) -> bytes:
        """Arma el PDF de métricas en memoria y devuelve sus bytes.

        calidad es opcional (HU-11): una lista de mediciones de calidad con imagen, factor, metodo y
        psnr_db. Si se entrega, el PDF agrega las gráficas de tiempo y de calidad (con la explicación
        del PSNR) después del resumen, y la tabla «Calidad (PSNR)» al final. Sin ella, el PDF es el
        mismo de siempre (HU-10).
        """
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("helvetica", style="B", size=16)
        pdf.cell(0, 10, titulo, ln=True, align="C")

        pdf.set_font("helvetica", size=10)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 10, f"Generado el: {fecha_actual}", ln=True, align="C")
        pdf.ln(10)

        if not registros:
            pdf.set_font("helvetica", style="I", size=12)
            pdf.cell(0, 10, "Aún no hay ejecuciones registradas", ln=True, align="C")
            if calidad:
                self._agregar_calidad(pdf, calidad)
            return pdf.output()

        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, "Resumen por método", ln=True)
        pdf.set_font("helvetica", size=10)

        # Calcular métricas del resumen
        metricas = defaultdict(lambda: {"tiempos": []})
        for reg in registros:
            metricas[reg.metodo]["tiempos"].append(reg.tiempo_ms)

        pdf.set_fill_color(240, 240, 240)
        pdf.cell(40, 10, "Método", border=1, fill=True)
        pdf.cell(30, 10, "Ejecuciones", border=1, fill=True)
        pdf.cell(40, 10, "Promedio (ms)", border=1, fill=True)
        pdf.cell(40, 10, "Mínimo (ms)", border=1, fill=True)
        pdf.cell(40, 10, "Máximo (ms)", border=1, fill=True, ln=True)

        for metodo, datos in metricas.items():
            tiempos = datos["tiempos"]
            pdf.cell(40, 10, metodo, border=1)
            pdf.cell(30, 10, str(len(tiempos)), border=1)
            pdf.cell(40, 10, f"{sum(tiempos) / len(tiempos):.1f}", border=1)
            pdf.cell(40, 10, f"{min(tiempos):.1f}", border=1)
            pdf.cell(40, 10, f"{max(tiempos):.1f}", border=1, ln=True)

        pdf.ln(10)

        if calidad:
            self._agregar_graficas(pdf, registros, calidad)

        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, "Registro de ejecuciones", ln=True)
        pdf.set_font("helvetica", size=8)

        encabezados = ["#", "Fecha", "Archivo", "Método", "Original", "Final", "Tiempo (ms)", "PNG (KB)"]
        anchos = [10, 25, 35, 25, 25, 25, 25, 20]

        for i, enc in enumerate(encabezados):
            pdf.cell(anchos[i], 10, enc, border=1, fill=True, ln=(i == len(encabezados) - 1))

        for idx, reg in enumerate(registros, 1):
            fecha_str = (
                reg.fecha.strftime("%d/%m %H:%M") if hasattr(reg.fecha, "strftime") else str(reg.fecha)
            )
            pdf.cell(anchos[0], 10, str(idx), border=1)
            pdf.cell(anchos[1], 10, fecha_str, border=1)
            pdf.cell(
                anchos[2], 10, (reg.archivo[:15] + "..") if len(reg.archivo) > 17 else reg.archivo, border=1
            )
            pdf.cell(anchos[3], 10, reg.metodo, border=1)
            pdf.cell(anchos[4], 10, f"{reg.ancho_original}x{reg.alto_original}", border=1)
            pdf.cell(anchos[5], 10, f"{reg.ancho_final}x{reg.alto_final}", border=1)
            pdf.cell(anchos[6], 10, f"{reg.tiempo_ms:.1f}", border=1)
            pdf.cell(anchos[7], 10, f"{reg.tamano_kb:.1f}", border=1, ln=True)

        if calidad:
            self._agregar_calidad(pdf, calidad)

        return pdf.output()

    @staticmethod
    def _agregar_calidad(pdf: FPDF, calidad: list) -> None:
        """Agrega la tabla de PSNR del estudio comparativo (HU-11): un renglón por medición."""
        pdf.ln(10)
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, "Calidad (PSNR)", ln=True)
        pdf.set_font("helvetica", size=8)

        encabezados = ["Imagen", "Reducción", "Método", "PSNR (dB)"]
        anchos = [50, 30, 30, 30]

        pdf.set_fill_color(240, 240, 240)
        for i, enc in enumerate(encabezados):
            pdf.cell(anchos[i], 10, enc, border=1, fill=True, ln=(i == len(encabezados) - 1))

        for medicion in calidad:
            pdf.cell(anchos[0], 10, medicion.imagen, border=1)
            pdf.cell(anchos[1], 10, f"x{medicion.factor}", border=1)
            pdf.cell(anchos[2], 10, medicion.metodo, border=1)
            pdf.cell(anchos[3], 10, f"{medicion.psnr_db:.2f}", border=1, ln=True)

    def _agregar_graficas(self, pdf: FPDF, registros: list, calidad: list) -> None:
        """Gráfica de tiempos, explicación del PSNR y gráfica de calidad (HU-11).

        Tiempos: una barra por método en cada resolución; el valor es la mediana entre las imágenes.
        Calidad: una barra por método en cada reducción; el valor es el PSNR promedio entre las imágenes.
        Los PSNR infinitos (imágenes idénticas) no se pueden dibujar y se dejan fuera del promedio.
        """
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, "Comparación de métodos")
        pdf.ln(10)

        grupos, series = self._agrupar(
            [(NOMBRES_RESOLUCION.get(r.resolucion, r.resolucion), r.metodo, r.tiempo_ms) for r in registros],
            statistics.median,
        )
        self._dibujar_barras(
            pdf,
            "Tiempo de reescalado por resolución (ms, menos es mejor)",
            grupos,
            series,
            decimales=1,
            nota="Mediana entre las imágenes del estudio; cada tiempo es la mediana de 5 mediciones.",
        )

        # La explicación del PSNR va con su gráfica: si no caben juntas en la página, pasan a la siguiente
        if pdf.get_y() + ALTO_EXPLICACION + ALTO_BLOQUE_GRAFICA > pdf.page_break_trigger:
            pdf.add_page()
        pdf.set_font("helvetica", size=9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, EXPLICACION_PSNR)
        pdf.set_x(pdf.l_margin)
        pdf.ln(3)

        grupos, series = self._agrupar(
            [(f"Reducción x{c.factor}", c.metodo, c.psnr_db) for c in calidad if math.isfinite(c.psnr_db)],
            statistics.fmean,
        )
        self._dibujar_barras(
            pdf,
            "Calidad por reducción (PSNR promedio en dB, más es mejor)",
            grupos,
            series,
            decimales=2,
            nota="Cada imagen se redujo con INTER_AREA y se amplió de vuelta a su tamaño con cada método.",
        )

    @staticmethod
    def _agrupar(
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

    @staticmethod
    def _maximo_agradable(valor: float) -> float:
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

    @staticmethod
    def _dibujar_barras(
        pdf: FPDF,
        titulo: str,
        grupos: list[str],
        series: dict[str, list[float]],
        decimales: int,
        nota: str = "",
    ) -> None:
        """Dibuja una gráfica de barras agrupadas: un grupo por categoría y una barra por serie.

        Con barras que parten de cero y el valor escrito sobre cada una. Si no hay grupos no dibuja nada.
        Al terminar deja el cursor debajo de la gráfica y los colores del PDF como estaban.
        """
        if not grupos:
            return

        if pdf.get_y() + ALTO_BLOQUE_GRAFICA > pdf.page_break_trigger:
            pdf.add_page()

        x_inicio = pdf.l_margin
        y = pdf.get_y()

        # Título y leyenda (un cuadrito de color por serie)
        pdf.set_font("helvetica", style="B", size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(x_inicio, y)
        pdf.cell(0, 6, titulo)
        y += 8

        pdf.set_font("helvetica", size=8)
        x = x_inicio + ANCHO_EJE
        for i, nombre in enumerate(series):
            pdf.set_fill_color(*COLORES_METODOS[i % len(COLORES_METODOS)])
            pdf.rect(x, y + 0.5, 3, 3, style="F")
            pdf.text(x + 4.5, y + 3.2, nombre)
            x += 4.5 + pdf.get_string_width(nombre) + 8
        y += 7 + 4  # 4 mm de margen arriba de la barra más alta para su número

        # Eje vertical con líneas guía
        maximo = GeneradorReportePDF._maximo_agradable(max(max(valores) for valores in series.values()))
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
        ancho_barra = min(ancho_grupo * 0.8 / len(series), 14)
        ancho_bloque = ancho_barra * len(series)
        for g, grupo in enumerate(grupos):
            x_bloque = x_area + g * ancho_grupo + (ancho_grupo - ancho_bloque) / 2
            for i, valores in enumerate(series.values()):
                alto = ALTO_GRAFICA * valores[g] / maximo
                x_barra = x_bloque + i * ancho_barra
                pdf.set_fill_color(*COLORES_METODOS[i % len(COLORES_METODOS)])
                pdf.rect(x_barra, y_base - alto, ancho_barra, alto, style="F")

                numero = f"{valores[g]:.{decimales}f}"
                pdf.set_font("helvetica", size=6)
                pdf.set_text_color(0, 0, 0)
                x_numero = x_barra + (ancho_barra - pdf.get_string_width(numero)) / 2
                pdf.text(x_numero, y_base - alto - 1, numero)

            pdf.set_font("helvetica", size=8)
            pdf.text(x_bloque + (ancho_bloque - pdf.get_string_width(grupo)) / 2, y_base + 5, grupo)

        y = y_base + 8
        if nota:
            pdf.set_font("helvetica", style="I", size=8)
            pdf.set_text_color(90, 90, 90)
            pdf.set_xy(x_inicio, y)
            pdf.cell(0, 5, nota)
            y += 6

        # Se devuelven los colores y el cursor a como los esperan las tablas que siguen
        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_xy(x_inicio, y + 4)
