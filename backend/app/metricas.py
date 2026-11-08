"""Registro de métricas de cada reescalado (HU-09).

Cada reescalado exitoso deja un Registro con sus datos. RegistroMetricas los guarda
en una lista en memoria, sin base de datos: se vacía al reiniciar el servidor (riesgo R12).
Con esos datos se arma GET /api/metricas (HU-09) y el PDF de métricas (HU-10).

Aquí también está psnr(), la medida de calidad del estudio comparativo (HU-11).
"""

import math
from dataclasses import dataclass
from datetime import datetime

import numpy as np

BYTES_POR_KB = 1024
DECIMALES_TIEMPO = 2  # Los mismos de la cabecera X-Tiempo-Ms, para que ambos valores coincidan
DECIMALES_TAMANO = 1
NIVEL_MAXIMO = 255  # Valor más alto de un píxel de 8 bits


def psnr(original: np.ndarray, estimada: np.ndarray) -> float:
    """Relación señal-ruido pico entre dos imágenes de 8 bits, en dB (HU-11).

    PSNR = 10·log10(255² / MSE), con MSE el promedio del error al cuadrado de todos los
    píxeles y canales. Más alto es mejor: 0 dB es el peor caso (negro contra blanco) y dos
    imágenes idénticas (MSE = 0) dan infinito.

    Ejemplo: un error de 5 niveles en todos los píxeles da MSE = 25 y PSNR = 34,15 dB.

    Lanza ValueError si las imágenes no tienen la misma forma.
    """
    if original.shape != estimada.shape:
        raise ValueError(
            f"Las imágenes deben tener la misma forma y tienen {original.shape} y {estimada.shape}."
        )
    # Se resta en float64: con uint8 la resta se desborda (10 - 20 daría 246).
    diferencia = original.astype(np.float64) - estimada.astype(np.float64)
    error_cuadratico_medio = float(np.mean(diferencia**2))
    if error_cuadratico_medio == 0:
        return math.inf
    return 10 * math.log10(NIVEL_MAXIMO**2 / error_cuadratico_medio)


@dataclass(frozen=True)
class Registro:
    """Datos de una ejecución: fecha, archivo, método, resoluciones, clave, tiempo y tamaño del PNG."""

    fecha: datetime
    archivo: str
    metodo: str
    ancho_original: int
    alto_original: int
    ancho_final: int
    alto_final: int
    resolucion: str  # Clave elegida en la HU-02: hd, fullhd, 2k o 4k
    tiempo_ms: float  # Solo la interpolación, el mismo valor de ResultadoReescalado
    tamano_kb: float  # Tamaño del PNG que se descargó

    def a_diccionario(self) -> dict:
        """Formato JSON de GET /api/metricas (sección 16.1).

        Se redondea solo aquí, al mostrarlo: el Registro guarda los valores completos.
        """
        return {
            "fecha": self.fecha.isoformat(timespec="seconds"),
            "archivo": self.archivo,
            "metodo": self.metodo,
            "ancho_original": self.ancho_original,
            "alto_original": self.alto_original,
            "ancho_final": self.ancho_final,
            "alto_final": self.alto_final,
            "resolucion": self.resolucion,
            "tiempo_ms": round(self.tiempo_ms, DECIMALES_TIEMPO),
            "tamano_kb": round(self.tamano_kb, DECIMALES_TAMANO),
        }


class RegistroMetricas:
    """Guarda los registros en memoria, los lista y calcula el resumen por método."""

    def __init__(self):
        self._registros: list[Registro] = []

    def agregar(self, registro: Registro) -> None:
        """Agrega un registro al final de la lista (orden de ejecución)."""
        self._registros.append(registro)

    def listar(self) -> list[Registro]:
        """Devuelve los registros en orden de ejecución.

        Es una copia: quien la reciba puede modificarla sin alterar las métricas guardadas.
        """
        return list(self._registros)

    def resumen_por_metodo(self) -> dict[str, dict]:
        """Ejecuciones y tiempo promedio, mínimo y máximo (ms) de cada método.

        Ejemplo: {"bicubico": {"ejecuciones": 2, "promedio_ms": 1009.05,
                               "minimo_ms": 812.4, "maximo_ms": 1205.7}}

        Los métodos aparecen en el orden en que se usaron por primera vez.
        Sin registros devuelve un diccionario vacío.
        """
        tiempos_por_metodo: dict[str, list[float]] = {}
        for registro in self._registros:
            tiempos_por_metodo.setdefault(registro.metodo, []).append(registro.tiempo_ms)

        return {
            metodo: {
                "ejecuciones": len(tiempos),
                "promedio_ms": sum(tiempos) / len(tiempos),
                "minimo_ms": min(tiempos),
                "maximo_ms": max(tiempos),
            }
            for metodo, tiempos in tiempos_por_metodo.items()
        }
