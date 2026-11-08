"""Punto de entrada de la API de Rescalibur.

Ejecutar desde la carpeta backend/:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import CABECERAS_EXPUESTAS, ORIGENES_PERMITIDOS, obtener_metodo
from app.metricas import RegistroMetricas
from app.procesador import ImagenDemasiadoGrandeError, ImagenInvalidaError, ProcesadorImagen
from app.reporte import GeneradorReportePDF
from app.resoluciones import CalculadoraResolucion
from app.servicio import ServicioReescalado

# Nombre con el que el navegador guarda el PDF de métricas (HU-10).
NOMBRE_REPORTE = "rescalibur_metricas.pdf"

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

# Una sola instancia para toda la API.
# El método sale de METODO_ACTIVO en config.py (HU-06). Se lee una vez, al arrancar:
# por eso hay que reiniciar el servidor tras cambiarlo. Un nombre inválido detiene el arranque.
# Su RegistroMetricas guarda las métricas mientras el servidor esté encendido (HU-09).
servicio = ServicioReescalado(
    ProcesadorImagen(), CalculadoraResolucion(), obtener_metodo(), RegistroMetricas()
)


@app.get("/api/salud")
def verificar_salud() -> dict[str, str]:
    """Indica que el servidor está en ejecución y con qué método reescala (HU-00 y HU-06)."""
    return {"estado": "ok", "metodo": servicio.metodo.nombre}


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


@app.get("/api/metricas")
def listar_metricas() -> list[dict]:
    """Devuelve los reescalados exitosos en orden de ejecución (HU-09).

    Es para el equipo: el frontend no la llama. Los datos viven en memoria y se
    pierden al reiniciar el servidor (riesgo R12).
    """
    return [registro.a_diccionario() for registro in servicio.registro_metricas.listar()]


@app.get("/api/metricas/reporte")
def descargar_reporte() -> Response:
    """Devuelve el PDF de métricas con los reescalados registrados hasta ahora (HU-10).

    Es para el equipo: el frontend no la llama (se abre en el navegador o desde /docs).
    El PDF se arma en memoria en cada petición y no se guarda en el servidor. Sin
    registros también se genera: GeneradorReportePDF pone el mensaje de que aún no hay ejecuciones.
    """
    registros = servicio.registro_metricas.listar()
    pdf = GeneradorReportePDF().generar(registros)
    return Response(
        content=bytes(pdf),  # fpdf2 entrega un bytearray y Response necesita bytes
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{NOMBRE_REPORTE}"'},
    )