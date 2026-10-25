"""Punto de entrada de la API de Rescalibur.

Ejecutar desde la carpeta backend/:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CABECERAS_EXPUESTAS, ORIGENES_PERMITIDOS

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


@app.get("/api/salud")
def verificar_salud() -> dict[str, str]:
    """Indica que el servidor está en ejecución. Sirve para comprobar la conexión."""
    return {"estado": "ok"}
