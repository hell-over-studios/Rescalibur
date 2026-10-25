"""Punto de entrada de la API de Rescalibur.

Ejecutar desde la carpeta backend/:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import CABECERAS_EXPUESTAS, ORIGENES_PERMITIDOS
from app.procesador import ImagenDemasiadoGrande, ImagenInvalida, ProcesadorImagen
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
servicio = ServicioReescalado(ProcesadorImagen(), CalculadoraResolucion())


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
    except ImagenDemasiadoGrande as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except ImagenInvalida as error:
        raise HTTPException(status_code=400, detail=str(error)) from error