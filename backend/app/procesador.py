"""Lectura y escritura de imágenes con OpenCV (HU-01 y HU-05).

OpenCV solo se usa aquí para convertir bytes en matriz y matriz en PNG.
La interpolación nunca usa OpenCV: se programa a mano en app/metodos/.
"""

import cv2
import numpy as np

TAMANO_MAXIMO_MB = 20
BYTES_POR_MB = 1024 * 1024
FORMATOS_ACEPTADOS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")
NIVELES_16_A_8_BITS = 257  # 65535 / 255: lleva el rango 0..65535 a 0..255


class ImagenInvalidaError(ValueError):
    """El archivo no es una imagen que se pueda leer (la API responde 400)."""


class ImagenDemasiadoGrandeError(ValueError):
    """El archivo supera TAMANO_MAXIMO_MB (la API responde 413)."""


class ProcesadorImagen:
    """Convierte bytes en matriz NumPy y matriz en bytes PNG."""

    def leer(self, contenido: bytes) -> np.ndarray:
        """Devuelve la imagen como matriz alto x ancho x canales (uint8).

        Las imágenes en escala de grises quedan como alto x ancho, y las que
        tienen transparencia conservan el canal alfa (4 canales).
        """
        self._validar_tamano(contenido)
        datos = np.frombuffer(contenido, dtype=np.uint8)
        # IMREAD_UNCHANGED conserva el canal alfa y la escala de grises.
        matriz = cv2.imdecode(datos, cv2.IMREAD_UNCHANGED)
        if matriz is None:
            raise ImagenInvalidaError("El archivo no es una imagen válida")
        return self._a_8_bits(matriz)

    def codificar_png(self, matriz: np.ndarray) -> bytes:
        """Codifica la matriz como PNG (sin pérdida) para la descarga."""
        exito, buffer = cv2.imencode(".png", matriz)
        if not exito:
            raise ValueError("No se pudo codificar la imagen en PNG")
        return buffer.tobytes()

    def _validar_tamano(self, contenido: bytes) -> None:
        if len(contenido) > TAMANO_MAXIMO_MB * BYTES_POR_MB:
            raise ImagenDemasiadoGrandeError(f"La imagen supera el máximo de {TAMANO_MAXIMO_MB} MB")
        if len(contenido) == 0:
            raise ImagenInvalidaError("El archivo está vacío")

    @staticmethod
    def _a_8_bits(matriz: np.ndarray) -> np.ndarray:
        """Normaliza imágenes de 16 bits a 8 bits (riesgo R5).

        Los métodos de interpolación trabajan siempre con valores 0..255.
        """
        if matriz.dtype == np.uint16:
            return (matriz // NIVELES_16_A_8_BITS).astype(np.uint8)
        return matriz
