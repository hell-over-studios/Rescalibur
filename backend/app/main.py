"""Punto de entrada de la API de Rescalibur.

Ejecutar desde la carpeta backend/:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import CABECERAS_EXPUESTAS, ORIGENES_PERMITIDOS
from app.metodos.bilineal import Bilineal
from app.procesador import ImagenDemasiadoGrandeError, ImagenInvalidaError, ProcesadorImagen
from app.resoluciones import CalculadoraResolucion
from app.servicio import ServicioReescalado

app = FastAPI(
    title="Rescalibur API",
    description="Reescalado de imágenes por métodos numéricos.",
    version="0.1.0",
)

# CORS: el frontend (otro puerto) puede llamar a la API y leer las cabeceras propias.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=CABECERAS_EXPUESTAS,
)

# Una sola instancia: no guarda estado entre peticiones, solo agrupa las clases.
# El método queda fijo en Bilineal hasta la HU-06, que lo elige con obtener_metodo().
servicio = ServicioReescalado(ProcesadorImagen(), CalculadoraResolucion(), Bilineal())


@app.get("/api/salud")
def verificar_salud() -> dict[str, str]:
    """Indica que el servidor está en ejecución. Sirve para comprobar la conexión."""
    return {"estado": "ok"}


@app.post("/api/imagen/info")
async def obtener_info_imagen(archivo: UploadFile = File(...)) -> dict:
    """Devuelve nombre, ancho, alto y las resoluciones disponibles (HU-01 y HU-02)."""
    contenido = await archivo.read()
    try:
        return servicio.obtener_info(contenido, archivo.filename or "")
    # Primero la excepción más específica: ambas heredan de ValueError.
    except ImagenDemasiadoGrandeError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except ImagenInvalidaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/imagen/reescalar")
async def reescalar_imagen(archivo: UploadFile = File(...), resolucion: str = Form(...)) -> Response:
    """Devuelve la imagen reescalada en PNG con X-Metodo, X-Tiempo-Ms, X-Ancho y X-Alto (HU-05).

    resolucion es la clave elegida en la HU-02: hd, fullhd, 2k o 4k.
    """
    contenido = await archivo.read()
    try:
        resultado = servicio.reescalar(contenido, archivo.filename or "", resolucion)
    # Primero la excepción más específica: ImagenDemasiadoGrandeError también es un ValueError.
    except ImagenDemasiadoGrandeError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    # Imagen inválida o resolución desconocida / que no amplía la imagen.
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return Response(content=resultado.png, media_type="image/png", headers=resultado.cabeceras())
