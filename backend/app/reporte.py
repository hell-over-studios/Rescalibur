import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from fpdf import FPDF

from app.graficas import ALTO_BLOQUE_GRAFICA, agrupar, alto_tabla, dibujar_barras, dibujar_tabla

NOMBRES_RESOLUCION = {"hd": "HD", "fullhd": "Full HD", "2k": "2K", "4k": "4K"}
ALTO_TITULO_SUBSECCION = 9
ESPACIO_TABLA_GRAFICA = 4
ALTO_CABECERA_SECCION = 35  # Título de la sección y sus párrafos (el más largo ocupa unos 28 mm)


@dataclass(frozen=True)
class SeccionEstudio:
    """Una sección del PDF del estudio (HU-11): qué se mide y cómo se nombra en tablas y gráficas."""

    titulo: str
    descripcion: tuple[str, ...]  # Un párrafo por elemento
    magnitud: str  # Lo que se mide, para los títulos de las gráficas
    unidad: str
    decimales: int
    opcion: str  # Lo que cambia entre grupos de la subsección 2: «factor de reducción» o «resolución»
    mejor: str = ""  # «más es mejor», «menos es mejor» o nada si no hay un mejor


EXPLICACION_PSNR = (
    "PSNR (relación señal-ruido pico): mide en decibelios (dB) qué tan parecida queda la imagen "
    "ampliada a la original, con 10·log10(255² / MSE), donde MSE es el error cuadrático medio entre "
    "sus píxeles. Más dB = más parecida."
)
SECCION_CALIDAD = SeccionEstudio(
    titulo="Calidad (PSNR)",
    descripcion=(
        EXPLICACION_PSNR,
        "Cada imagen se redujo con INTER_AREA y se amplió de vuelta a su tamaño original con cada método.",
    ),
    magnitud="PSNR",
    unidad="dB",
    decimales=2,
    opcion="factor de reducción",
    mejor="más es mejor",
)
SECCION_TIEMPO = SeccionEstudio(
    titulo="Tiempo de reescalado",
    descripcion=(
        "Lo que tarda cada método en reescalar la imagen, sin contar leerla ni guardarla. Cada medición "
        "es la mediana de 5 repeticiones; aquí se promedian las de las imágenes del estudio.",
    ),
    magnitud="Tiempo",
    unidad="ms",
    decimales=1,
    opcion="resolución",
    mejor="menos es mejor",
)
SECCION_TAMANO = SeccionEstudio(
    titulo="Tamaño del PNG",
    descripcion=(
        "Lo que pesa el PNG de la imagen ampliada, que es el archivo que descarga el usuario. "
        "No mide calidad: solo cuánto ocupa.",
    ),
    magnitud="Tamaño del PNG",
    unidad="KB",
    decimales=1,
    opcion="resolución",
)


class GeneradorReportePDF:
    def generar(
        self,
        registros: list,
        titulo: str = "Rescalibur · Métricas de ejecución",
        calidad: list | None = None,
    ) -> bytes:
        """Arma el PDF de métricas en memoria y devuelve sus bytes.

        calidad es opcional (HU-11): una lista de mediciones de calidad con imagen, factor, metodo y
        psnr_db. Si se entrega, el PDF pasa a ser el del estudio comparativo: tres secciones (calidad,
        tiempo y tamaño) con tablas y gráficas por método, por opción y por imagen, y al final los datos
        completos como anexos. Sin ella, el PDF es el mismo de siempre (HU-10).
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

        if calidad:
            self._agregar_estudio(pdf, registros, calidad)
            pdf.add_page()
            self._agregar_registro(pdf, registros, "Anexo A. Registro de ejecuciones")
            self._agregar_calidad(pdf, calidad, "Anexo B. Calidad (PSNR) por medición")
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

        self._agregar_registro(pdf, registros)

        return pdf.output()

    @staticmethod
    def _agregar_registro(pdf: FPDF, registros: list, titulo: str = "Registro de ejecuciones") -> None:
        """Tabla con un renglón por ejecución: fecha, archivo, método, resoluciones, tiempo y tamaño."""
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, titulo, ln=True)
        pdf.set_font("helvetica", size=8)

        encabezados = ["#", "Fecha", "Archivo", "Método", "Original", "Final", "Tiempo (ms)", "PNG (KB)"]
        anchos = [10, 25, 35, 25, 25, 25, 25, 20]

        pdf.set_fill_color(240, 240, 240)
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

    @staticmethod
    def _agregar_calidad(pdf: FPDF, calidad: list, titulo: str = "Calidad (PSNR)") -> None:
        """Tabla de PSNR del estudio comparativo (HU-11): un renglón por medición."""
        pdf.ln(10)
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, titulo, ln=True)
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

    # --- Estudio comparativo (HU-11) ---

    def _agregar_estudio(self, pdf: FPDF, registros: list, calidad: list) -> None:
        """Las tres secciones del estudio: calidad, tiempo y tamaño del PNG.

        Cada medida es (imagen, opción, método, valor). Los PSNR infinitos (imágenes idénticas) no se
        pueden promediar ni dibujar y se dejan fuera.
        """
        secciones = [
            (
                SECCION_CALIDAD,
                [
                    (c.imagen, f"Reducción x{c.factor}", c.metodo, c.psnr_db)
                    for c in calidad
                    if math.isfinite(c.psnr_db)
                ],
            ),
            (
                SECCION_TIEMPO,
                [(r.archivo, self._nombre_resolucion(r), r.metodo, r.tiempo_ms) for r in registros],
            ),
            (
                SECCION_TAMANO,
                [(r.archivo, self._nombre_resolucion(r), r.metodo, r.tamano_kb) for r in registros],
            ),
        ]
        for numero, (seccion, medidas) in enumerate(secciones, 1):
            self._agregar_seccion(pdf, numero, seccion, medidas)

    @staticmethod
    def _nombre_resolucion(registro) -> str:
        return NOMBRES_RESOLUCION.get(registro.resolucion, registro.resolucion)

    def _agregar_seccion(self, pdf: FPDF, numero: int, seccion: SeccionEstudio, medidas: list[tuple]) -> None:
        """Una sección: título, qué se mide y tres subsecciones, cada una con su tabla y su gráfica."""
        if not medidas:
            return
        # La sección arranca en otra página si no caben juntos su título y su primera subsección
        primera = ALTO_TITULO_SUBSECCION + alto_tabla(3) + ESPACIO_TABLA_GRAFICA + ALTO_BLOQUE_GRAFICA
        self._reservar(pdf, ALTO_CABECERA_SECCION + primera)

        pdf.set_font("helvetica", style="B", size=14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"{numero}. {seccion.titulo}")
        pdf.ln(10)
        pdf.set_font("helvetica", size=9)
        for parrafo in seccion.descripcion:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, parrafo)
            pdf.set_x(pdf.l_margin)
        pdf.ln(3)

        por_opcion = [(opcion, metodo, valor) for _, opcion, metodo, valor in medidas]
        por_imagen = [(imagen, metodo, valor) for imagen, _, metodo, valor in medidas]
        self._subseccion_por_metodo(pdf, f"{numero}.1", seccion, medidas)
        self._subseccion_agrupada(
            pdf, f"{numero}.2", f"por {seccion.opcion}", seccion, por_opcion, seccion.opcion.capitalize()
        )
        self._subseccion_agrupada(pdf, f"{numero}.3", "por imagen", seccion, por_imagen, "Imagen")

    @staticmethod
    def _titulo_grafica(seccion: SeccionEstudio, por_que: str) -> str:
        """Ejemplo: «PSNR promedio por método (dB, más es mejor)»."""
        detalle = f"{seccion.unidad}, {seccion.mejor}" if seccion.mejor else seccion.unidad
        return f"{seccion.magnitud} promedio {por_que} ({detalle})"

    @staticmethod
    def _reservar(pdf: FPDF, alto: float) -> None:
        """Pasa a otra página si no caben `alto` mm: un título no se separa de su tabla y su gráfica."""
        if pdf.get_y() + alto > pdf.page_break_trigger:
            pdf.add_page()

    @staticmethod
    def _titulo_subseccion(pdf: FPDF, texto: str) -> None:
        pdf.set_font("helvetica", style="B", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 6, texto)
        pdf.ln(ALTO_TITULO_SUBSECCION)

    def _subseccion_por_metodo(
        self, pdf: FPDF, numero: str, seccion: SeccionEstudio, medidas: list[tuple]
    ) -> None:
        """Tabla (promedio, mínimo, máximo y mediciones) y gráfica con una barra por método."""
        valores_por_metodo: dict[str, list[float]] = {}
        for _, _, metodo, valor in medidas:
            valores_por_metodo.setdefault(metodo, []).append(valor)

        d, u = seccion.decimales, seccion.unidad
        filas = [
            [metodo, f"{statistics.fmean(v):.{d}f}", f"{min(v):.{d}f}", f"{max(v):.{d}f}", str(len(v))]
            for metodo, v in valores_por_metodo.items()
        ]
        self._reservar(
            pdf, ALTO_TITULO_SUBSECCION + alto_tabla(len(filas)) + ESPACIO_TABLA_GRAFICA + ALTO_BLOQUE_GRAFICA
        )
        self._titulo_subseccion(pdf, f"{numero} Comparación por método")
        dibujar_tabla(
            pdf,
            ["Método", f"Promedio ({u})", f"Mínimo ({u})", f"Máximo ({u})", "Mediciones"],
            filas,
            [40, 40, 35, 35, 35],
        )
        pdf.ln(ESPACIO_TABLA_GRAFICA)
        dibujar_barras(
            pdf,
            self._titulo_grafica(seccion, "por método"),
            list(valores_por_metodo),
            {"Promedio": [statistics.fmean(v) for v in valores_por_metodo.values()]},
            d,
            colorear_grupos=True,
        )

    def _subseccion_agrupada(
        self,
        pdf: FPDF,
        numero: str,
        por_que: str,
        seccion: SeccionEstudio,
        datos: list[tuple],
        encabezado_grupo: str,
    ) -> None:
        """Tabla y gráfica con un grupo por categoría (opción o imagen) y una barra por método."""
        grupos, series = agrupar(datos, statistics.fmean)
        d, u = seccion.decimales, seccion.unidad
        filas = [
            [grupo] + [f"{valores[i]:.{d}f}" for valores in series.values()] for i, grupo in enumerate(grupos)
        ]
        ancho_metodo = (190 - 55) / len(series)
        self._reservar(
            pdf, ALTO_TITULO_SUBSECCION + alto_tabla(len(filas)) + ESPACIO_TABLA_GRAFICA + ALTO_BLOQUE_GRAFICA
        )
        self._titulo_subseccion(pdf, f"{numero} Comparación {por_que}")
        dibujar_tabla(
            pdf,
            [encabezado_grupo] + [f"{metodo} ({u})" for metodo in series],
            filas,
            [55] + [ancho_metodo] * len(series),
        )
        pdf.ln(ESPACIO_TABLA_GRAFICA)
        dibujar_barras(pdf, self._titulo_grafica(seccion, por_que), grupos, series, d)
