"""Clase base de los métodos de interpolación (patrón Estrategia, sección 5.2).

Todos los métodos (vecino, bilineal y, en el Sprint 2, bicúbico) heredan de
MetodoInterpolacion y exponen la misma función reescalar(). Así el
ServicioReescalado no necesita saber qué método está usando.
"""

from abc import ABC, abstractmethod

import numpy as np

# Gris con eje de canal (1), color BGR (3) y color con alfa BGRA (4)
CANALES_VALIDOS = (1, 3, 4)


class MetodoInterpolacion(ABC):
    """Contrato común para todos los métodos de reescalado."""

    nombre: str = ""

    @abstractmethod
    def reescalar(
        self, matriz: np.ndarray, nuevo_ancho: int, nuevo_alto: int
    ) -> np.ndarray:
        """Devuelve una matriz nueva de nuevo_alto × nuevo_ancho con los mismos canales.

        Args:
            matriz: imagen como arreglo NumPy de forma (h, w) o (h, w, canales).
            nuevo_ancho: ancho final W calculado en HU-02.
            nuevo_alto: alto final H calculado en HU-02.
        """

    def validar_entrada(
        self, matriz: np.ndarray, nuevo_ancho: int, nuevo_alto: int
    ) -> None:
        """Revisa la matriz y las dimensiones antes de interpolar.

        Lanza ValueError (o TypeError) con un mensaje claro si algo no cumple.
        """
        if not isinstance(matriz, np.ndarray):
            raise TypeError("La imagen debe ser un arreglo de NumPy.")

        if matriz.ndim not in (2, 3):
            raise ValueError(
                f"La imagen debe tener 2 o 3 dimensiones, tiene {matriz.ndim}."
            )

        if matriz.ndim == 3 and matriz.shape[2] not in CANALES_VALIDOS:
            raise ValueError(f"Número de canales no soportado: {matriz.shape[2]}.")

        if matriz.shape[0] == 0 or matriz.shape[1] == 0:
            raise ValueError("La imagen no puede estar vacía.")

        for nombre, valor in (("nuevo_ancho", nuevo_ancho), ("nuevo_alto", nuevo_alto)):
            # bool hereda de int en Python, por eso se excluye a propósito
            if isinstance(valor, bool) or not isinstance(valor, (int, np.integer)):
                raise TypeError(f"{nombre} debe ser un número entero.")
            if valor <= 0:
                raise ValueError(f"{nombre} debe ser mayor que 0.")