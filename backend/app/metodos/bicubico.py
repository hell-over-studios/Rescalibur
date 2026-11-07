"""Interpolacion bicubica implementada con NumPy (HU-08, seccion 16.4)."""

import numpy as np

from app.metodos.base import MetodoInterpolacion

# Medio pixel: hace coincidir los centros de los pixeles (convencion de OpenCV).
MEDIO_PIXEL = 0.5

# Parametro del nucleo cubico de Keys. -0.75 es el valor de OpenCV (INTER_CUBIC).
PARAMETRO_A = -0.75

# Posicion de los 4 vecinos de cada eje respecto a x0 = piso(x):
# columnas x0 - 1, x0, x0 + 1 y x0 + 2 (lo mismo para las filas).
DESPLAZAMIENTOS = np.array([-1, 0, 1, 2])

# Rango valido de un canal de 8 bits.
NIVEL_MINIMO = 0
NIVEL_MAXIMO = 255


class Bicubico(MetodoInterpolacion):
    """Reescala una imagen mezclando los 16 pixeles originales mas cercanos (4 x 4).

    Cada pixel destino es una suma ponderada de sus 16 vecinos. Los pesos salen
    del nucleo cubico k(s), un polinomio de grado 3. A diferencia del bilineal,
    algunos pesos son negativos: eso realza los bordes, pero puede dar valores
    fuera de [0, 255], y por eso al final se recorta.
    """

    nombre = "bicubico"

    def reescalar(self, matriz: np.ndarray, nuevo_ancho: int, nuevo_alto: int) -> np.ndarray:
        """Devuelve una imagen nueva de tamano (nuevo_alto, nuevo_ancho).

        Funciona con imagenes en gris (h, w) y con 1, 3 o 4 canales (h, w, c).
        No modifica la matriz original y conserva su tipo de dato.
        """
        self.validar_entrada(matriz, nuevo_ancho, nuevo_alto)

        # Igual que en el bilineal: una imagen en gris (h, w) se trata como si
        # tuviera un canal (h, w, 1) y al final se le quita.
        es_gris = matriz.ndim == 2
        imagen = matriz[:, :, np.newaxis] if es_gris else matriz
        alto, ancho = imagen.shape[:2]

        # Pasos 1 a 4: los 4 vecinos y los 4 pesos de cada columna y de cada fila destino.
        columnas, pesos_x = self._vecinos_y_pesos(nuevo_ancho, ancho)
        filas, pesos_y = self._vecinos_y_pesos(nuevo_alto, alto)

        # Paso 5: mezclar en dos pasadas. float64 porque los pesos negativos
        # pueden dar valores menores que 0 o mayores que 255 (riesgo R10).
        mezcla = self._mezclar(imagen.astype(np.float64), columnas, pesos_x, filas, pesos_y)

        # Paso 6: redondear y recortar a [0, 255] ANTES de volver a 8 bits.
        # Sin el recorte, -24 en uint8 se convertiria en 232 (una "vuelta").
        resultado = np.clip(np.rint(mezcla), NIVEL_MINIMO, NIVEL_MAXIMO).astype(matriz.dtype)
        return resultado[:, :, 0] if es_gris else resultado

    @staticmethod
    def nucleo(s: np.ndarray) -> np.ndarray:
        """Nucleo cubico de Keys con a = -0.75 (seccion 16.4).

            k(s) = (a + 2)|s|^3 - (a + 3)|s|^2 + 1      si |s| <= 1
            k(s) = a|s|^3 - 5a|s|^2 + 8a|s| - 4a        si 1 < |s| < 2
            k(s) = 0                                    si |s| >= 2

        Recibe un arreglo de distancias y devuelve el peso de cada una.
        Ejemplo (CP-18): para t = 0.5 las distancias a los 4 vecinos son
        [1.5, 0.5, -0.5, -1.5] y los pesos [-0.09375, 0.59375, 0.59375, -0.09375].
        """
        a = PARAMETRO_A
        s = np.abs(s)
        cerca = (a + 2) * s**3 - (a + 3) * s**2 + 1
        lejos = a * s**3 - 5 * a * s**2 + 8 * a * s - 4 * a
        return np.where(s <= 1, cerca, np.where(s < 2, lejos, 0.0))

    @staticmethod
    def _vecinos_y_pesos(tamano_destino: int, tamano_origen: int) -> tuple[np.ndarray, np.ndarray]:
        """Calcula, para cada posicion destino, sus 4 vecinos y sus 4 pesos.

        Se usa igual para columnas (con anchos) y para filas (con altos).
        Devuelve dos matrices de forma (tamano_destino, 4):
            indices: los 4 vecinos x0 - 1, x0, x0 + 1, x0 + 2, ya dentro de la imagen
            pesos:   k(t - m) para m = -1, 0, 1, 2 (siempre suman 1)
        """
        escala = tamano_origen / tamano_destino
        destino = np.arange(tamano_destino)

        # Paso 1: posicion en la imagen original, x = (j + 0.5) * w / W - 0.5 (seccion 5.4).
        posicion = (destino + MEDIO_PIXEL) * escala - MEDIO_PIXEL

        # Paso 2: el vecino base y la parte fraccionaria, x0 = piso(x) y t = x - x0.
        base = np.floor(posicion).astype(np.intp)
        t = posicion - base

        # Paso 3: los 4 vecinos de cada posicion. Cada fila de la matriz es
        # [x0 - 1, x0, x0 + 1, x0 + 2]. Los que se salen de la imagen se
        # recortan al borde mas cercano (borde replicado).
        indices = np.clip(base[:, np.newaxis] + DESPLAZAMIENTOS, 0, tamano_origen - 1)

        # Paso 4: el peso de cada vecino depende de su distancia a la posicion, t - m.
        pesos = Bicubico.nucleo(t[:, np.newaxis] - DESPLAZAMIENTOS)
        return indices, pesos

    @staticmethod
    def _mezclar(
        imagen: np.ndarray,
        columnas: np.ndarray,
        pesos_x: np.ndarray,
        filas: np.ndarray,
        pesos_y: np.ndarray,
    ) -> np.ndarray:
        """Aplica la formula bicubica a todos los pixeles a la vez.

        La doble suma de la seccion 16.4,
            D[i, j] = suma_n suma_m k(u - n) * k(t - m) * I[y0 + n, x0 + m],
        se separa en dos pasadas porque cada peso es (peso en y) * (peso en x):
        primero se mezclan 4 columnas en cada fila original y luego 4 filas.
        El ciclo es de 4 vueltas (una por vecino), no un ciclo por pixel.
        """
        alto, _, canales = imagen.shape
        nuevo_alto, nuevo_ancho = len(filas), len(columnas)

        # Pasada horizontal: (h, w, c) -> (h, W, c).
        # pesos_x[:, m] tiene forma (W,); se le dan ejes para aplicarlo por columna.
        horizontal = np.zeros((alto, nuevo_ancho, canales))
        for m in range(len(DESPLAZAMIENTOS)):
            peso = pesos_x[:, m][np.newaxis, :, np.newaxis]  # forma (1, W, 1)
            horizontal += peso * imagen[:, columnas[:, m]]

        # Pasada vertical: (h, W, c) -> (H, W, c).
        vertical = np.zeros((nuevo_alto, nuevo_ancho, canales))
        for n in range(len(DESPLAZAMIENTOS)):
            peso = pesos_y[:, n][:, np.newaxis, np.newaxis]  # forma (H, 1, 1)
            vertical += peso * horizontal[filas[:, n]]
        return vertical
