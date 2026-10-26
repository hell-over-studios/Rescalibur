import ast
import inspect
import cv2
import numpy as np
import pytest

from app.metodos import vecino as modulo_vecino
from app.metodos.vecino import VecinoMasCercano

SEMILLA = 2026  
metodo = VecinoMasCercano()


def imagen_aleatoria(alto: int, ancho: int, canales: int | None = None) -> np.ndarray:
    generador = np.random.default_rng(SEMILLA)
    forma = (alto, ancho) if canales is None else (alto, ancho, canales)
    return generador.integers(0, 256, size=forma, dtype=np.uint8)

def test_cp08_matriz_2x2_a_4x4():

    original = np.array([[10, 20], [30, 40]], dtype=np.uint8)

    resultado = metodo.reescalar(original, nuevo_ancho=4, nuevo_alto=4)

    esperado = np.array(
        [
            [10, 10, 20, 20],
            [10, 10, 20, 20],
            [30, 30, 40, 40],
            [30, 30, 40, 40],
        ],
        dtype=np.uint8,
    )
    assert np.array_equal(resultado, esperado)


def test_razon_no_entera_repite_algunos_pixeles_mas_que_otros():
    original = np.array([[10, 20, 30]], dtype=np.uint8)

    resultado = metodo.reescalar(original, nuevo_ancho=5, nuevo_alto=1)

    assert resultado.tolist() == [[10, 10, 20, 30, 30]]


def test_ancho_y_alto_se_calculan_por_separado():
    original = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.uint8)

    resultado = metodo.reescalar(original, nuevo_ancho=4, nuevo_alto=3)

    assert resultado.tolist() == [[1, 1, 2, 2], [3, 3, 4, 4], [5, 5, 6, 6]]


def test_reduccion_toma_el_pixel_del_centro_de_cada_bloque():
    original = np.array([[1, 2, 3, 4]], dtype=np.uint8)

    resultado = metodo.reescalar(original, nuevo_ancho=2, nuevo_alto=1)

    assert resultado.tolist() == [[2, 4]]


def test_un_solo_pixel_se_copia_en_toda_la_imagen():
    original = np.array([[7]], dtype=np.uint8)

    resultado = metodo.reescalar(original, nuevo_ancho=3, nuevo_alto=2)

    assert resultado.tolist() == [[7, 7, 7], [7, 7, 7]]

@pytest.mark.parametrize(
    ("destino", "origen", "esperado"),
    [
        (4, 2, [0, 0, 1, 1]),
        (5, 3, [0, 0, 1, 2, 2]),
        (6, 3, [0, 0, 1, 1, 2, 2]),
        (2, 4, [1, 3]),
        (3, 1, [0, 0, 0]),
    ],
)
def test_indices_origen_a_mano(destino, origen, esperado):
    assert VecinoMasCercano._indices_origen(destino, origen).tolist() == esperado


@pytest.mark.parametrize(
    ("destino", "origen"),
    [(1, 1), (1, 50), (7, 3), (3, 7), (2160, 600), (2880, 800), (800, 2880), (4, 4), (1001, 17)],
)
def test_indices_siempre_dentro_de_la_imagen_y_sin_retroceder(destino, origen):
    indices = VecinoMasCercano._indices_origen(destino, origen)

    assert indices.min() >= 0
    assert indices.max() <= origen - 1
    assert np.all(np.diff(indices) >= 0)


@pytest.mark.parametrize(("destino", "origen"), [(4, 2), (5, 3), (2880, 800), (13, 9), (9, 13)])
def test_indices_enteros_coinciden_con_la_formula_con_decimales(destino, origen):
    k = np.arange(destino)
    con_decimales = np.floor((k + 0.5) * origen / destino).astype(int)

    assert np.array_equal(VecinoMasCercano._indices_origen(destino, origen), con_decimales)


def test_el_minimo_de_proteccion_es_solo_una_red_de_seguridad():
    for destino in range(1, 60):
        for origen in range(1, 60):
            k = np.arange(destino)
            sin_minimo = (2 * k + 1) * origen // (2 * destino)
            assert sin_minimo.max() <= origen - 1, (destino, origen)

@pytest.mark.parametrize(
    ("ancho", "alto", "nuevo_ancho", "nuevo_alto"),
    [
        (800, 600, 2880, 2160),  
        (800, 600, 960, 720),  
        (1080, 1920, 2160, 3840),  
        (1920, 1080, 2560, 1440),  
        (1, 1, 5, 7),
        (3, 2, 3, 2),  
    ],
)
def test_la_imagen_resultante_tiene_exactamente_las_dimensiones_pedidas(ancho, alto, nuevo_ancho, nuevo_alto):
    resultado = metodo.reescalar(imagen_aleatoria(alto, ancho, 3), nuevo_ancho, nuevo_alto)

    assert resultado.shape == (nuevo_alto, nuevo_ancho, 3)

@pytest.mark.parametrize(("factor_x", "factor_y"), [(2, 2), (3, 3), (4, 4), (2, 3), (5, 1)])
def test_ampliacion_entera_convierte_cada_pixel_en_un_bloque(factor_x, factor_y):
    original = imagen_aleatoria(6, 9, 3)
    ancho, alto = 9, 6

    resultado = metodo.reescalar(original, ancho * factor_x, alto * factor_y)

    esperado = np.repeat(np.repeat(original, factor_y, axis=0), factor_x, axis=1)
    assert np.array_equal(resultado, esperado)


def test_no_inventa_valores_nuevos():
    original = np.array([[0, 100, 200], [200, 0, 100]], dtype=np.uint8)

    resultado = metodo.reescalar(original, 17, 11)

    assert set(np.unique(resultado)) <= {0, 100, 200}


def test_las_esquinas_se_conservan():
    original = imagen_aleatoria(600, 800, 3)

    resultado = metodo.reescalar(original, 2880, 2160)

    assert np.array_equal(resultado[0, 0], original[0, 0])
    assert np.array_equal(resultado[0, -1], original[0, -1])
    assert np.array_equal(resultado[-1, 0], original[-1, 0])
    assert np.array_equal(resultado[-1, -1], original[-1, -1])


def test_mismo_tamano_devuelve_la_misma_imagen():
    original = imagen_aleatoria(40, 60, 3)

    resultado = metodo.reescalar(original, 60, 40)

    assert np.array_equal(resultado, original)


def test_conserva_el_tipo_de_dato():
    original = imagen_aleatoria(5, 5, 3)

    assert metodo.reescalar(original, 9, 9).dtype == np.uint8


def test_no_modifica_la_imagen_original_y_devuelve_una_copia():
    original = imagen_aleatoria(8, 8, 3)
    copia_de_seguridad = original.copy()

    resultado = metodo.reescalar(original, 8, 8)
    resultado[:] = 0  

    assert np.array_equal(original, copia_de_seguridad)
    assert not np.shares_memory(resultado, original)


def test_es_determinista():
    original = imagen_aleatoria(30, 40, 3)

    primero = metodo.reescalar(original, 100, 70)
    segundo = metodo.reescalar(original, 100, 70)

    assert np.array_equal(primero, segundo)


def test_ancho_y_alto_no_se_confunden_en_imagen_no_cuadrada():
    original = np.arange(6, dtype=np.uint8).reshape(2, 3)

    resultado = metodo.reescalar(original, nuevo_ancho=6, nuevo_alto=4)

    assert resultado.shape == (4, 6)
    assert resultado[0].tolist() == [0, 0, 1, 1, 2, 2]
    assert resultado[3].tolist() == [3, 3, 4, 4, 5, 5]

def referencia_opencv(imagen: np.ndarray, nuevo_ancho: int, nuevo_alto: int) -> np.ndarray:
    """cv2.resize recibe el tamaño como (ancho, alto), al revés que la forma de NumPy."""
    return cv2.resize(imagen, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_NEAREST_EXACT)


def test_cp09_identica_a_opencv_800x600_a_4k():
    original = imagen_aleatoria(600, 800, 3)

    resultado = metodo.reescalar(original, 2880, 2160)

    assert np.array_equal(resultado, referencia_opencv(original, 2880, 2160))


@pytest.mark.parametrize(
    ("ancho", "alto", "nuevo_ancho", "nuevo_alto"),
    [
        (7, 5, 11, 13), 
        (13, 11, 7, 5), 
        (1920, 1080, 2560, 1440),  
        (1080, 1920, 1440, 2560),  
    ],
)
def test_coincide_con_opencv_en_otras_razones(ancho, alto, nuevo_ancho, nuevo_alto):
    original = imagen_aleatoria(alto, ancho, 3)

    resultado = metodo.reescalar(original, nuevo_ancho, nuevo_alto)

    assert np.array_equal(resultado, referencia_opencv(original, nuevo_ancho, nuevo_alto))

@pytest.mark.parametrize(
    ("canales", "forma_esperada"), [(None, (12, 15)), (1, (12, 15, 1)), (3, (12, 15, 3)), (4, (12, 15, 4))]
)
def test_cp12_conserva_el_numero_de_canales(canales, forma_esperada):
    original = imagen_aleatoria(4, 5, canales)

    resultado = metodo.reescalar(original, nuevo_ancho=15, nuevo_alto=12)

    assert resultado.shape == forma_esperada


def test_cp12_cada_canal_se_trata_igual_que_si_estuviera_solo():
    original = imagen_aleatoria(9, 13, 3)

    junto = metodo.reescalar(original, 31, 22)

    for canal in range(3):
        solo = metodo.reescalar(original[:, :, canal], 31, 22)
        assert np.array_equal(junto[:, :, canal], solo)


def test_cp12_conserva_la_transparencia():
    original = np.zeros((2, 4, 4), dtype=np.uint8)
    original[:, 2:, 3] = 255

    resultado = metodo.reescalar(original, nuevo_ancho=8, nuevo_alto=4)

    alfa = resultado[:, :, 3]
    assert set(np.unique(alfa)) == {0, 255} 
    assert np.all(alfa[:, :4] == 0)
    assert np.all(alfa[:, 4:] == 255)


def test_conserva_los_valores_extremos_0_y_255():
    original = np.array([[0, 255]], dtype=np.uint8)

    resultado = metodo.reescalar(original, 4, 1)

    assert resultado.tolist() == [[0, 0, 255, 255]]

def test_rechaza_algo_que_no_es_un_arreglo_de_numpy():
    with pytest.raises(TypeError, match="NumPy"):
        metodo.reescalar([[1, 2], [3, 4]], 4, 4)

@pytest.mark.parametrize("forma", [(5,), (2, 2, 3, 1)])
def test_rechaza_dimensiones_que_no_son_2_ni_3(forma):
    with pytest.raises(ValueError, match="dimensiones"):
        metodo.reescalar(np.zeros(forma, dtype=np.uint8), 4, 4)


def test_rechaza_un_numero_de_canales_no_soportado():
    with pytest.raises(ValueError, match="canales"):
        metodo.reescalar(np.zeros((2, 2, 2), dtype=np.uint8), 4, 4)


@pytest.mark.parametrize("forma", [(0, 3), (3, 0), (0, 0, 3)])
def test_rechaza_una_imagen_vacia(forma):
    with pytest.raises(ValueError, match="vacía"):
        metodo.reescalar(np.zeros(forma, dtype=np.uint8), 4, 4)


@pytest.mark.parametrize("valor", [0, -1, -100])
def test_rechaza_dimensiones_destino_no_positivas(valor):
    imagen = np.ones((2, 2), dtype=np.uint8)

    with pytest.raises(ValueError, match="nuevo_ancho"):
        metodo.reescalar(imagen, valor, 4)
    with pytest.raises(ValueError, match="nuevo_alto"):
        metodo.reescalar(imagen, 4, valor)


@pytest.mark.parametrize("valor", [4.0, 4.5, "4", None, True])
def test_rechaza_dimensiones_destino_que_no_son_enteros(valor):
    imagen = np.ones((2, 2), dtype=np.uint8)

    with pytest.raises(TypeError, match="nuevo_ancho"):
        metodo.reescalar(imagen, valor, 4)


def test_acepta_enteros_de_numpy_como_dimension_destino():
    imagen = np.ones((2, 2), dtype=np.uint8)

    resultado = metodo.reescalar(imagen, np.int64(4), np.int32(6))

    assert resultado.shape == (6, 4)

def test_el_vecino_no_usa_opencv():
    arbol = ast.parse(inspect.getsource(modulo_vecino))
    modulos_importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos_importados |= {alias.name.split(".")[0] for alias in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos_importados.add(nodo.module.split(".")[0])

    assert "cv2" not in modulos_importados


def test_el_vecino_hereda_del_contrato_comun():
    from app.metodos.base import MetodoInterpolacion

    assert isinstance(metodo, MetodoInterpolacion)
    assert metodo.nombre == "vecino"