import time
import statistics
import cv2
from pathlib import Path

from app.metodos.vecino import VecinoMasCercano
from app.metodos.bilineal import Bilineal
from app.metodos.bicubico import Bicubico

def medir_tiempos():
    print("Iniciando estudio comparativo de tiempos...")
    
    rutas_imagenes = [
        "estudio/imagenes/fotografia.png",
        "estudio/imagenes/texto.jpg",
        "estudio/imagenes/ilustracion.jpg"
    ]
    
    resoluciones = {
        "hd": (960, 720),
        "fullhd": (1440, 1080),
        "2k": (1920, 1440),
        "4k": (2880, 2160)
    }
    
    metodos = {
        "vecino": VecinoMasCercano(),
        "bilineal": Bilineal(),
        "bicubico": Bicubico()
    }
    
    resultados_tiempo = []

    for ruta in rutas_imagenes:
        archivo = Path(ruta)
        if not archivo.exists():
            print(f"⚠️ Falta la imagen: {ruta}")
            continue
            
        # Leer con OpenCV (BGR) y pasar a RGB para el procesamiento
        matriz_bgr = cv2.imread(str(archivo))
        if matriz_bgr is None:
            continue
        matriz_rgb = cv2.cvtColor(matriz_bgr, cv2.COLOR_BGR2RGB)
        
        print(f"\nProcesando {archivo.name} ({matriz_rgb.shape[1]}x{matriz_rgb.shape[0]} px)")
        
        for nombre_res, (ancho_fin, alto_fin) in resoluciones.items():
            for nombre_metodo, metodo in metodos.items():
                tiempos_ms = []
                
                # Medir 5 veces para calcular la mediana
                for _ in range(5):
                    inicio = time.time()
                    _ = metodo.reescalar(matriz_rgb, ancho_fin, alto_fin)
                    fin = time.time()
                    tiempos_ms.append((fin - inicio) * 1000)
                    
                mediana_ms = statistics.median(tiempos_ms)
                print(f"  • {nombre_metodo} a {nombre_res.upper()}: {mediana_ms:.1f} ms")
                
                resultados_tiempo.append({
                    "archivo": archivo.name,
                    "metodo": nombre_metodo,
                    "resolucion": nombre_res,
                    "tiempo_ms": mediana_ms
                })
                
    return resultados_tiempo

if __name__ == "__main__":
    medir_tiempos()