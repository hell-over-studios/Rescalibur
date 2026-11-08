from collections import defaultdict
from datetime import datetime

from fpdf import FPDF


class GeneradorReportePDF:
    def generar(
        self,
        registros: list,
        titulo: str = "Rescalibur · Métricas de ejecución",
        calidad: list | None = None,
    ) -> bytes:
        """Arma el PDF de métricas en memoria y devuelve sus bytes.

        calidad es opcional (HU-11): una lista de mediciones de calidad con imagen, factor, metodo y
        psnr_db. Si se entrega, se agrega la tabla «Calidad (PSNR)» al final. Sin ella, el PDF es el
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