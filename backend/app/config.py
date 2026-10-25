"""Configuración general del backend.

Todas las constantes que pueden cambiar entre entornos viven aquí.
"""

# Direcciones desde las que el navegador puede llamar a la API.
# 5173 es el puerto por defecto de Vite (npm run dev).
ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Cabeceras propias que el frontend necesita leer en la respuesta de /api/imagen/reescalar.
# Sin declararlas aquí, el navegador las oculta aunque el servidor las envíe.
CABECERAS_EXPUESTAS = ["X-Metodo", "X-Tiempo-Ms", "X-Ancho", "X-Alto"]
