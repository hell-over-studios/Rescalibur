"""Configuración general del backend.

Todas las constantes que pueden cambiar entre entornos viven aquí, junto con
obtener_metodo(), que convierte METODO_ACTIVO en el método de interpolación (HU-06).
"""

from app.metodos.base import MetodoInterpolacion
from app.metodos.bilineal import Bilineal
from app.metodos.vecino import VecinoMasCercano

# Direcciones desde las que el navegador puede llamar a la API.
# 5173 es el puerto por defecto de Vite (npm run dev).
ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Cabeceras propias que el frontend necesita leer en la respuesta de /api/imagen/reescalar.
# Sin declararlas aquí, el navegador las oculta aunque el servidor las envíe.
CABECERAS_EXPUESTAS = ["X-Metodo", "X-Tiempo-Ms", "X-Ancho", "X-Alto"]

# Método de interpolación que usa la API (HU-06): "vecino" o "bilineal".
# Para cambiarlo: editar este valor y reiniciar el servidor.
# En el Sprint 2 se agrega "bicubico".
METODO_ACTIVO = "bilineal"

# Nombre -> clase. La clave sale del atributo nombre de cada clase, así el texto
# de METODO_ACTIVO y el de la cabecera X-Metodo son siempre el mismo.
METODOS_DISPONIBLES: dict[str, type[MetodoInterpolacion]] = {
    VecinoMasCercano.nombre: VecinoMasCercano,
    Bilineal.nombre: Bilineal,
}


def obtener_metodo() -> MetodoInterpolacion:
    """Devuelve una instancia del método indicado en METODO_ACTIVO.

    main.py la llama al arrancar. Si el nombre no existe lanza ValueError, y
    así el servidor no arranca con un método que no está programado (HU-06).
    """
    if METODO_ACTIVO not in METODOS_DISPONIBLES:
        validos = ", ".join(f'"{nombre}"' for nombre in METODOS_DISPONIBLES)
        raise ValueError(
            f'METODO_ACTIVO = "{METODO_ACTIVO}" no es un método válido. '
            f"Usa uno de: {validos} (app/config.py)."
        )
    return METODOS_DISPONIBLES[METODO_ACTIVO]()
