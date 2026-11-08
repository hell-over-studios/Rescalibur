import os
import numpy as np
from backend.app.metricas import psnr

def test_psnr_calculo_cp29():
    original = np.full((10, 10), 100, dtype=np.uint8)
    estimada = np.full((10, 10), 105, dtype=np.uint8)
    
    resultado = psnr(original, estimada)
    
    assert round(resultado, 2) == 34.15

def test_estudio_completo_archivos_cp28():
    ruta_resultados = os.path.join(os.path.dirname(__file__), "..", "estudio", "resultados")
    ruta_csv = os.path.join(ruta_resultados, "resultados.csv")
    
    assert os.path.exists(ruta_resultados), "La carpeta de resultados no existe."
    
