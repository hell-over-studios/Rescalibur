"""Orquestación del proceso: leer -> calcular -> reescalar -> codificar (sección 5.2).

ServicioReescalado no sabe qué método de interpolación usa: lo recibe en el
constructor (patrón Estrategia). En la HU-06, main.py lo elegirá con
obtener_metodo() a partir de METODO_ACTIVO.
"""

import time
from dataclasses import dataclass

from app.metodos.base import MetodoInterpolacion
from app.procesador import FORMATOS_ACEPTADOS, ImagenInvalidaError, ProcesadorImagen
from app.resoluciones import CalculadoraResolucion

MILISEGUNDOS_POR_SEGUNDO = 1000


@dataclass(frozen=True)
class ResultadoReescalado:
    """Lo que devuelve /api/imagen/reescalar: el PNG y los datos que van en las cabeceras."""

    png: bytes
    ancho: int
    alto: int
    metodo: str
    tiempo_ms: float  # Solo la interpolación, sin lectura ni codificación (HU-06)
    clave: str

    def cabeceras(self) -> dict[str, str]:
        """Cabeceras HTTP del contrato de API (sección 5.1).

        Las X-... deben estar en CABECERAS_EXPUESTAS para que el navegador las lea.
        """
        return {
            "X-Metodo": self.metodo,
            "X-Tiempo-Ms": f"{self.tiempo_ms:.2f}",
            "X-Ancho": str(self.ancho),
            "X-Alto": str(self.alto),
            "Content-Disposition": f'attachment; filename="rescalibur_{self.clave}.png"',
        }


class ServicioReescalado:
    """Coordina ProcesadorImagen, CalculadoraResolucion y el método de interpolación."""

    def __init__(
        self,
        procesador: ProcesadorImagen,
        calculadora: CalculadoraResolucion,
        metodo: MetodoInterpolacion,
    ):
        self.procesador = procesador
        self.calculadora = calculadora
        self.metodo = metodo

    def obtener_info(self, contenido: bytes, nombre: str) -> dict:
        """Lee la imagen y devuelve sus datos con las resoluciones disponibles (HU-01 y HU-02).

        Lanza ImagenInvalidaError o ImagenDemasiadoGrandeError; la API las convierte en 400 / 413.
        """
        self._validar_formato(nombre)
        matriz = self.procesador.leer(contenido)
        alto, ancho = matriz.shape[:2]
        opciones = self.calculadora.opciones_disponibles(ancho, alto)
        return {
            "nombre": nombre,
            "ancho": ancho,
            "alto": alto,
            "opciones": [opcion.a_diccionario() for opcion in opciones],
        }

    def reescalar(self, contenido: bytes, nombre: str, clave: str) -> ResultadoReescalado:
        """Reescala la imagen a la resolución elegida y la devuelve en PNG (HU-05).

        Pasos: leer -> calcular dimensiones -> reescalar (midiendo el tiempo) -> codificar.

        Lanza ImagenDemasiadoGrandeError (413), ImagenInvalidaError (400) o
        ValueError si la clave no existe o no amplía esta imagen (400).
        """
        self._validar_formato(nombre)
        matriz = self.procesador.leer(contenido)
        alto, ancho = matriz.shape[:2]
        nuevo_ancho, nuevo_alto = self.calculadora.calcular_dimensiones(ancho, alto, clave)

        # Se mide solo la interpolación: es el dato que se compara entre métodos en el informe.
        inicio = time.perf_counter()
        reescalada = self.metodo.reescalar(matriz, nuevo_ancho, nuevo_alto)
        tiempo_ms = (time.perf_counter() - inicio) * MILISEGUNDOS_POR_SEGUNDO

        return ResultadoReescalado(
            png=self.procesador.codificar_png(reescalada),
            ancho=nuevo_ancho,
            alto=nuevo_alto,
            metodo=self.metodo.nombre,
            tiempo_ms=tiempo_ms,
            clave=clave,
        )

    @staticmethod
    def _validar_formato(nombre: str) -> None:
        """Revisa la extensión del archivo contra FORMATOS_ACEPTADOS."""
        if not nombre.lower().endswith(FORMATOS_ACEPTADOS):
            raise ImagenInvalidaError("Formato no aceptado. Usa JPG, PNG, BMP, WEBP o TIFF")
