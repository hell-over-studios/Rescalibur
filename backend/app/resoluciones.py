"""Resoluciones objetivo y cálculo de opciones disponibles (HU-02).

Regla de cálculo (sección 1.5 del documento del Sprint 1):

    Para una imagen de w x h y un marco W x H (ya orientado como la imagen):

        s = min(W / w, H / h)
        nuevo_ancho = redondear(w * s)
        nuevo_alto  = redondear(h * s)

    La opción solo se ofrece si s > 1 (es decir, si de verdad se amplía).
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ResolucionObjetivo:
    """Una resolución de referencia (HD, Full HD, 2K o 4K) en orientación horizontal."""

    clave: str
    nombre: str
    ancho: int
    alto: int

    def marco_para(self, ancho_imagen: int, alto_imagen: int) -> tuple[int, int]:
        """Devuelve el marco (W, H) girado según la orientación de la imagen.

        Si la imagen es vertical se intercambian ancho y alto del marco
        (Full HD vertical = 1080 x 1920). Sin esto, una foto vertical de
        celular casi nunca tendría opciones.
        """
        if alto_imagen > ancho_imagen:
            return self.alto, self.ancho
        return self.ancho, self.alto


@dataclass(frozen=True)
class OpcionResolucion:
    """Una opción que se le muestra al usuario, con la resolución final ya calculada."""

    clave: str
    nombre: str
    ancho: int
    alto: int

    def a_diccionario(self) -> dict:
        """Formato JSON acordado en el contrato de API (sección 5.1)."""
        return {
            "clave": self.clave,
            "nombre": self.nombre,
            "ancho": self.ancho,
            "alto": self.alto,
        }


RESOLUCIONES = (
    ResolucionObjetivo("hd", "HD", 1280, 720),
    ResolucionObjetivo("fullhd", "Full HD", 1920, 1080),
    ResolucionObjetivo("2k", "2K", 2560, 1440),
    ResolucionObjetivo("4k", "4K", 3840, 2160),
)


def redondear(valor: float) -> int:
    """Redondeo clásico (0.5 sube).

    Se evita round() de Python porque usa redondeo bancario
    (round(2.5) == 2), que no es el que se explica en el informe.
    """
    return math.floor(valor + 0.5)


class CalculadoraResolucion:
    """Decide qué resoluciones se ofrecen y calcula sus dimensiones finales."""

    def __init__(self, resoluciones: tuple[ResolucionObjetivo, ...] = RESOLUCIONES):
        self._resoluciones = {resolucion.clave: resolucion for resolucion in resoluciones}

    def calcular_escala(self, ancho: int, alto: int, resolucion: ResolucionObjetivo) -> float:
        """Factor s = min(W / w, H / h): el mayor que hace caber la imagen en el marco."""
        ancho_marco, alto_marco = resolucion.marco_para(ancho, alto)
        return min(ancho_marco / ancho, alto_marco / alto)

    def calcular_opcion(self, ancho: int, alto: int, resolucion: ResolucionObjetivo) -> OpcionResolucion:
        """Aplica la escala conservando la proporción de la imagen."""
        escala = self.calcular_escala(ancho, alto, resolucion)
        return OpcionResolucion(
            clave=resolucion.clave,
            nombre=resolucion.nombre,
            ancho=redondear(ancho * escala),
            alto=redondear(alto * escala),
        )

    def opciones_disponibles(self, ancho: int, alto: int) -> list[OpcionResolucion]:
        """Lista de opciones con s > 1, en orden de menor a mayor resolución.

        Si la imagen ya es igual o mayor que 4K, la lista queda vacía y el
        frontend muestra el mensaje correspondiente.
        """
        return [
            self.calcular_opcion(ancho, alto, resolucion)
            for resolucion in self._resoluciones.values()
            if self.calcular_escala(ancho, alto, resolucion) > 1
        ]

    def calcular_dimensiones(self, ancho: int, alto: int, clave: str) -> tuple[int, int]:
        """Dimensiones finales para una clave elegida (lo usará /api/imagen/reescalar).

        Lanza ValueError si la clave no existe o no está disponible para
        esta imagen; el endpoint lo convierte en un error 400.
        """
        resolucion = self._resoluciones.get(clave)
        if resolucion is None:
            raise ValueError(f"Resolución desconocida: {clave}")
        if self.calcular_escala(ancho, alto, resolucion) <= 1:
            raise ValueError(f"La resolución {resolucion.nombre} no amplía esta imagen")
        opcion = self.calcular_opcion(ancho, alto, resolucion)
        return opcion.ancho, opcion.alto
