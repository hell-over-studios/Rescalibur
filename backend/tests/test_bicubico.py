import pytest
import numpy as np
import cv2
from app.metodos.bicubico import Bicubico

@pytest.fixture
def bicubico():
    return Bicubico()

# CP-17: Bicúbico constante
def test_bicubico_constante(bicubico):
    matriz_original = np.full((3, 3, 3), 77, dtype=np.uint8)
    resultado = bicubico.reescalar(matriz_original, 7, 7)
    assert np.all(resultado == 77), "Todos los valores deben ser 77"

# CP-18: Pesos del núcleo
def test_pesos_nucleo(bicubico):
    pesos = bicubico.nucleo(np.array([1.5, 0.5, -0.5, -1.5]))
    esperado = np.array([-0.09375, 0.59375, 0.59375, -0.09375])
    np.testing.assert_allclose(pesos, esperado, rtol=1e-5)
    assert np.isclose(np.sum(pesos), 1.0), "Los pesos deben sumar 1"

# CP-20: Recorte a [0, 255]
def test_recorte_pesos_negativos(bicubico):
    escalon = np.array([[[0], [0], [0], [255]]], dtype=np.uint8)
    resultado = bicubico.reescalar(escalon, 8, 1)
    assert np.all(resultado >= 0) and np.all(resultado <= 255), "Los valores deben quedar entre 0 y 255"

# CP-19: Contra referencia OpenCV (diferencia <= 2)
def test_contra_opencv(bicubico):
    np.random.seed(42)
    matriz = np.random.randint(0, 256, (600, 800, 3), dtype=np.uint8)
    resultado_nuestro = bicubico.reescalar(matriz, 2880, 2160)
    resultado_cv2 = cv2.resize(matriz, (2880, 2160), interpolation=cv2.INTER_CUBIC)

    diferencia = np.abs(resultado_nuestro.astype(np.int16) - resultado_cv2.astype(np.int16))
    assert np.max(diferencia) <= 2, "La diferencia máxima con OpenCV debe ser de 2 niveles o menos"

# CP-21: Canales (escala de grises y alfa)
def test_canales_conservados(bicubico):
    grises = np.random.randint(0, 256, (10, 10, 1), dtype=np.uint8)
    alfa = np.random.randint(0, 256, (10, 10, 4), dtype=np.uint8)
    
    assert bicubico.reescalar(grises, 20, 20).shape[-1] == 1
    assert bicubico.reescalar(alfa, 20, 20).shape[-1] == 4