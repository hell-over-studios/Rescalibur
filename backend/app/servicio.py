"""Orquestación del proceso: leer -> calcular -> (reescalar) -> codificar.

Por ahora solo tiene obtener_info (HU-01 y HU-02). El método reescalar()
y el atributo metodo se agregan en la HU-05, junto con la configuración de la HU-06.
"""

from app.procesador import FORMATOS_ACEPTADOS, ImagenInvalidaError, ProcesadorImagen
from app.resoluciones import CalculadoraResolucion


class ServicioReescalado:
    """Coordina ProcesadorImagen y CalculadoraResolucion."""

    def __init__(self, procesador: ProcesadorImagen, calculadora: CalculadoraResolucion):
        self.procesador = procesador
        self.calculadora = calculadora

    def obtener_info(self, contenido: bytes, nombre: str) -> dict:
        """Lee la imagen y devuelve sus datos con las resoluciones disponibles.

           Lanza ImagenInvalidaError
        o ImagenDemasiadoGrandeError; la API las convierte en 400 / 413.
        """
        if not nombre.lower().endswith(FORMATOS_ACEPTADOS):
            raise ImagenInvalidaError
        ("Formato no aceptado. Usa JPG, PNG, BMP, WEBP o TIFF")
        matriz = self.procesador.leer(contenido)
        alto, ancho = matriz.shape[:2]
        opciones = self.calculadora.opciones_disponibles(ancho, alto)
        return {
            "nombre": nombre,
            "ancho": ancho,
            "alto": alto,
            "opciones": [opcion.a_diccionario() for opcion in opciones],
        }
