"""HU-03 · Interpolación por vecino más cercano (grado 0).

Fórmula de la sección 5.4, con centros de píxel alineados (convención de OpenCV):

    D[i, j] = I[ mín(⌊(i + 0.5) · h / H⌋, h − 1) ,  mín(⌊(j + 0.5) · w / W⌋, w − 1) ]

    w × h : tamaño de la imagen original
    W × H : tamaño de la imagen destino
    i, j  : fila y columna que recorren la imagen destino

Se usa solo NumPy; cv2.resize está prohibido aquí (sección 1.5).
"""

import numpy as np

from app.metodos.base import MetodoInterpolacion


class VecinoMasCercano(MetodoInterpolacion):
    """Cada píxel destino copia el valor del píxel original más cercano a su centro."""

    nombre = "vecino"

    def reescalar(
        self, matriz: np.ndarray, nuevo_ancho: int, nuevo_alto: int
    ) -> np.ndarray:
        """Reescala la imagen a nuevo_ancho × nuevo_alto con el vecino más cercano.

        Funciona igual en gris (h, w), color (h, w, 3) y con alfa (h, w, 4):
        la fórmula solo mueve posiciones y cada píxel se copia con todos sus canales.
        """
        self.validar_entrada(matriz, nuevo_ancho, nuevo_alto)
        alto, ancho = matriz.shape[:2]

        filas_origen = self._indices_origen(nuevo_alto, alto)
        columnas_origen = self._indices_origen(nuevo_ancho, ancho)

        # filas_origen[:, None] es una columna y columnas_origen una fila:
        # NumPy las combina (broadcasting) y arma de una vez la cuadrícula H × W.
        return matriz[filas_origen[:, None], columnas_origen]

    @staticmethod
    def _indices_origen(tamano_destino: int, tamano_origen: int) -> np.ndarray:
        """Calcula mín(⌊(k + 0.5) · n / N⌋, n − 1) para k = 0, 1, ..., N − 1.

        Se multiplica todo por 2 para trabajar solo con enteros:
            (k + 0.5) · n / N  =  (2k + 1) · n / (2N)
        Así // da el piso exacto, sin errores de redondeo de los flotantes.
        """
        k = np.arange(tamano_destino)
        indices = (2 * k + 1) * tamano_origen // (2 * tamano_destino)
        # El mín de la fórmula: protege el borde para no salirse de la imagen (riesgo R2)
        return np.minimum(indices, tamano_origen - 1)