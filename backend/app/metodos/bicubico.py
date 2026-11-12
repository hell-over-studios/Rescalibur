"""Interpolacion bicubica implementada con NumPy (HU-08, seccion 16.4).

La idea en cuatro pasos, para cada pixel nuevo:
    1. Ubicar el punto que le corresponde en la imagen original (x, y).
    2. Tomar sus 4 x 4 = 16 vecinos originales.
    3. Darle un peso a cada vecino con el nucleo cubico k(s): pesa mas el mas cercano.
    4. Sumar vecino x peso y recortar el resultado a [0, 255].

Como el peso de cada vecino es (peso en x) * (peso en y), la suma se hace en dos
pasadas: primero se mezclan las columnas y luego las filas.
"""

import numpy as np

from app.metodos.base import MetodoInterpolacion

# Medio pixel: hace coincidir los centros de los pixeles (convencion de OpenCV).
MEDIO_PIXEL = 0.5

# Parametro del nucleo cubico de Keys. -0.75 es el valor de OpenCV (INTER_CUBIC).
PARAMETRO_A = -0.75

# Los 4 vecinos de cada eje respecto a x0 = piso(x): x0 - 1, x0, x0 + 1 y x0 + 2.
DESPLAZAMIENTOS = np.array([-1, 0, 1, 2])

# Rango valido de un canal de 8 bits.
NIVEL_MINIMO = 0
NIVEL_MAXIMO = 255


class Bicubico(MetodoInterpolacion):
    """Reescala una imagen mezclando los 16 pixeles originales mas cercanos (4 x 4).

    Cada pixel nuevo es una suma ponderada de sus 16 vecinos. Los pesos salen
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

        # Una imagen en gris (h, w) se trata como si tuviera un canal (h, w, 1).
        es_gris = matriz.ndim == 2
        imagen = matriz[:, :, np.newaxis] if es_gris else matriz
        alto, ancho = imagen.shape[:2]

        # Pasos 1 a 3: los 4 vecinos y los 4 pesos de cada columna y de cada fila nueva.
        columnas, pesos_x = self._vecinos_y_pesos(nuevo_ancho, ancho)
        filas, pesos_y = self._vecinos_y_pesos(nuevo_alto, alto)

        # Paso 4: sumar vecino x peso. Se usa float64 porque los pesos negativos
        # pueden dar valores menores que 0 o mayores que 255.
        imagen_decimal = imagen.astype(np.float64)
        mezcla_columnas = self._mezclar_columnas(imagen_decimal, columnas, pesos_x)
        mezcla = self._mezclar_filas(mezcla_columnas, filas, pesos_y)

        # Redondear y recortar a [0, 255] ANTES de volver a 8 bits.
        # Sin el recorte, -24 en uint8 se convertiria en 232 (da la "vuelta").
        resultado = np.clip(np.rint(mezcla), NIVEL_MINIMO, NIVEL_MAXIMO).astype(matriz.dtype)
        return resultado[:, :, 0] if es_gris else resultado

    @staticmethod
    def nucleo(s: np.ndarray) -> np.ndarray:
        """Nucleo cubico de Keys con a = -0.75 (seccion 16.4).

            k(s) = (a + 2)|s|^3 - (a + 3)|s|^2 + 1      si |s| <= 1
            k(s) = a|s|^3 - 5a|s|^2 + 8a|s| - 4a        si 1 < |s| < 2
            k(s) = 0                                    si |s| >= 2

        Recibe las distancias a los vecinos y devuelve el peso de cada uno.
        Ejemplo (CP-18): para t = 0.5 las distancias a los 4 vecinos son
        [1.5, 0.5, -0.5, -1.5] y los pesos [-0.09375, 0.59375, 0.59375, -0.09375].
        """
        a = PARAMETRO_A
        s = np.abs(s)
        cerca = (a + 2) * s**3 - (a + 3) * s**2 + 1
        lejos = a * s**3 - 5 * a * s**2 + 8 * a * s - 4 * a
        return np.where(s <= 1, cerca, np.where(s < 2, lejos, 0.0))

    @staticmethod
    def _vecinos_y_pesos(tamano_nuevo: int, tamano_original: int) -> tuple[np.ndarray, np.ndarray]:
        """Calcula, para cada posicion nueva de un eje, sus 4 vecinos y sus 4 pesos.

        Sirve igual para las columnas (con anchos) y para las filas (con altos).
        Devuelve dos tablas con una fila por posicion nueva y 4 columnas:
            vecinos: [x0 - 1, x0, x0 + 1, x0 + 2], ya dentro de la imagen
            pesos:   el peso de cada uno de esos vecinos (siempre suman 1)
        """
        escala = tamano_original / tamano_nuevo
        posiciones_nuevas = np.arange(tamano_nuevo)

        # Paso 1: posicion en la imagen original, x = (j + 0.5) * w / W - 0.5 (seccion 5.4).
        x = (posiciones_nuevas + MEDIO_PIXEL) * escala - MEDIO_PIXEL

        # El vecino base x0 = piso(x) y la parte fraccionaria t = x - x0 (entre 0 y 1).
        x0 = np.floor(x).astype(np.intp)
        t = x - x0

        # Paso 2: los 4 vecinos. reshape(-1, 1) vuelve cada valor una fila para sumarle
        # los 4 desplazamientos. Los que se salen de la imagen se pegan al borde.
        vecinos = np.clip(x0.reshape(-1, 1) + DESPLAZAMIENTOS, 0, tamano_original - 1)

        # Paso 3: el peso de cada vecino depende de su distancia al punto, t - m.
        pesos = Bicubico.nucleo(t.reshape(-1, 1) - DESPLAZAMIENTOS)
        return vecinos, pesos

    @staticmethod
    def _mezclar_columnas(imagen: np.ndarray, columnas: np.ndarray, pesos_x: np.ndarray) -> np.ndarray:
        """Primera pasada: cambia el ancho. De (h, w, c) pasa a (h, W, c).

        Cada columna nueva = suma de sus 4 columnas vecinas por su peso.
        Son 4 vueltas (una por vecino), no una vuelta por pixel.
        """
        resultado = np.zeros((imagen.shape[0], len(columnas), imagen.shape[2]))
        for m in range(4):
            peso = pesos_x[:, m].reshape(1, -1, 1)  # un peso por columna nueva
            resultado += peso * imagen[:, columnas[:, m]]
        return resultado

    @staticmethod
    def _mezclar_filas(imagen: np.ndarray, filas: np.ndarray, pesos_y: np.ndarray) -> np.ndarray:
        """Segunda pasada: cambia el alto. De (h, W, c) pasa a (H, W, c).

        Cada fila nueva = suma de sus 4 filas vecinas por su peso.
        """
        resultado = np.zeros((len(filas), imagen.shape[1], imagen.shape[2]))
        for n in range(4):
            peso = pesos_y[:, n].reshape(-1, 1, 1)  # un peso por fila nueva
            resultado += peso * imagen[filas[:, n]]
        return resultado
