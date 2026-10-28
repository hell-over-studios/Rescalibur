"""Interpolacion bilineal implementada con NumPy (HU-04, seccion 5.4)."""

import numpy as np

from app.metodos.base import MetodoInterpolacion

# Medio pixel: hace coincidir los centros de los pixeles (convencion de OpenCV).
MEDIO_PIXEL = 0.5

# Rango valido de un canal de 8 bits.
NIVEL_MINIMO = 0
NIVEL_MAXIMO = 255


class Bilineal(MetodoInterpolacion):
    """Reescala una imagen mezclando los 4 pixeles originales mas cercanos.

    Cada pixel destino es un promedio ponderado de sus 4 vecinos en la imagen
    original. Los pesos dependen de la distancia: el vecino mas cercano pesa mas.
    Es interpolacion de grado 1 en cada direccion, por eso el resultado es mas
    suave que con el vecino mas cercano.
    """

    nombre = "bilineal"

    def reescalar(self, matriz: np.ndarray, nuevo_ancho: int, nuevo_alto: int) -> np.ndarray:
        """Devuelve una imagen nueva de tamano (nuevo_alto, nuevo_ancho).

        Funciona con imagenes en gris (h, w) y con 1, 3 o 4 canales (h, w, c).
        No modifica la matriz original y conserva su tipo de dato.
        """
        self.validar_entrada(matriz, nuevo_ancho, nuevo_alto)

        # Para no escribir dos versiones del calculo, una imagen en gris (h, w)
        # se trata como si tuviera un canal (h, w, 1) y al final se le quita.
        es_gris = matriz.ndim == 2
        imagen = matriz[:, :, np.newaxis] if es_gris else matriz
        alto, ancho = imagen.shape[:2]

        # Pasos 1 a 4: vecinos y pesos de cada columna y de cada fila destino.
        x0, x1, a = self._vecinos_y_pesos(nuevo_ancho, ancho)
        y0, y1, b = self._vecinos_y_pesos(nuevo_alto, alto)

        # Paso 5: mezclar. float32 evita perder decimales y ahorra memoria.
        mezcla = self._mezclar(imagen.astype(np.float32), x0, x1, a, y0, y1, b)

        # Redondear y limitar a [0, 255], como indica la seccion 5.4.
        resultado = np.clip(np.rint(mezcla), NIVEL_MINIMO, NIVEL_MAXIMO).astype(matriz.dtype)
        return resultado[:, :, 0] if es_gris else resultado

    @staticmethod
    def _vecinos_y_pesos(
        tamano_destino: int, tamano_origen: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcula, para cada posicion destino, sus dos vecinos y su peso.

        Se usa igual para columnas (con anchos) y para filas (con altos).
        Devuelve tres vectores de largo tamano_destino:
            indice0: vecino de la izquierda (o de arriba)
            indice1: vecino de la derecha (o de abajo)
            peso:    distancia al primer vecino, entre 0 y 1 (a o b en la seccion 5.4)
        """
        escala = tamano_origen / tamano_destino
        destino = np.arange(tamano_destino)

        # Paso 1: posicion en la imagen original, x = (j + 0.5) * w / W - 0.5
        posicion = (destino + MEDIO_PIXEL) * escala - MEDIO_PIXEL

        # Paso 2: recortar al rango [0, tamano_origen - 1] para no salirse en los bordes.
        posicion = np.clip(posicion, 0, tamano_origen - 1)

        # Paso 3: los dos vecinos, x0 = piso(x) y x1 = min(x0 + 1, w - 1).
        indice0 = np.floor(posicion).astype(np.intp)
        indice1 = np.minimum(indice0 + 1, tamano_origen - 1)

        # Paso 4: que tan lejos esta la posicion del primer vecino, a = x - x0.
        peso = (posicion - indice0).astype(np.float32)
        return indice0, indice1, peso

    @staticmethod
    def _mezclar(
        imagen: np.ndarray,
        x0: np.ndarray,
        x1: np.ndarray,
        a: np.ndarray,
        y0: np.ndarray,
        y1: np.ndarray,
        b: np.ndarray,
    ) -> np.ndarray:
        """Aplica la formula bilineal a todos los pixeles a la vez.

        Se interpola primero en x y luego en y. Es la misma formula de 4 terminos
        de la seccion 5.4, solo que agrupada:
            (1-b)·[(1-a)·I00 + a·I01] + b·[(1-a)·I10 + a·I11]
        """
        # Se le dan ejes extra a los pesos para que NumPy los aplique por columna
        # (a) o por fila (b) en todos los canales a la vez (broadcasting).
        a = a[np.newaxis, :, np.newaxis]  # forma (1, W, 1)
        b = b[:, np.newaxis, np.newaxis]  # forma (H, 1, 1)

        # Mezcla horizontal: entre la columna x0 y la x1 de cada fila original.
        horizontal = (1 - a) * imagen[:, x0] + a * imagen[:, x1]  # forma (h, W, c)

        # Mezcla vertical: entre la fila y0 ("arriba") y la y1 ("abajo").
        arriba = horizontal[y0]  # forma (H, W, c)
        abajo = horizontal[y1]  # forma (H, W, c)
        return (1 - b) * arriba + b * abajo