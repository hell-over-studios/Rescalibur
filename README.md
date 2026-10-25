# Rescalibur

**Reescalador de imágenes web por métodos numéricos**

Rescalibur es una aplicación web que aumenta la resolución de una imagen calculando matemáticamente los píxeles nuevos. El usuario carga una imagen, elige la resolución de salida (HD, Full HD, 2K o 4K) y descarga el resultado.

El objetivo del proyecto es implementar y comparar, paso a paso, tres métodos clásicos de interpolación, de menor a mayor complejidad: **vecino más cercano → bilineal → bicúbico**. Ninguno usa funciones de reescalado de librerías: cada método se programa a mano sobre la matriz de píxeles.

---

## Estado del proyecto

| Método | Idea | Estado |
|---|---|---|
| Vecino más cercano | Copia el valor del píxel original más cercano (grado 0). | En desarrollo |
| Bilineal | Promedio ponderado de los 4 píxeles vecinos (grado 1 en cada eje). | En desarrollo |
| Bicúbico | Polinomios cúbicos sobre un vecindario de 4 × 4 = 16 píxeles. | Planeado |

---

## Cómo funciona

1. **Carga:** el usuario sube una imagen desde su dispositivo.
2. **Conversión:** la imagen se convierte en una matriz numérica de píxeles (alto × ancho × canales).
3. **Elección de resolución:** la aplicación muestra solo las resoluciones mayores que la actual y el tamaño final que tendrá la imagen en cada una.
4. **Interpolación:** se calcula cada píxel nuevo con el método numérico activo.
5. **Descarga:** la imagen reescalada se descarga en formato PNG.

### Resoluciones disponibles

| Opción | Horizontal | Vertical |
|---|---|---|
| HD | 1280 × 720 | 720 × 1280 |
| Full HD | 1920 × 1080 | 1080 × 1920 |
| 2K | 2560 × 1440 | 1440 × 2560 |
| 4K | 3840 × 2160 | 2160 × 3840 |

La proporción original siempre se conserva: la imagen se amplía hasta encajar en el marco elegido. Por ejemplo, una imagen de 800 × 600 en Full HD queda en **1440 × 1080**.

### Formatos aceptados

JPG, JPEG, PNG, BMP, WEBP y TIFF, hasta 20 MB. La salida es siempre PNG (sin pérdida), para que la calidad dependa solo del método numérico y no de la compresión.

### Privacidad

Las imágenes se procesan en memoria y se descartan al terminar. No se almacenan en ningún servidor ni base de datos.

---

## Tecnologías

| Capa | Tecnologías |
|---|---|
| Frontend | React, Tailwind CSS, Vite |
| Backend | Python 3, FastAPI |
| Cálculo numérico | NumPy (implementación de los métodos) |
| Lectura y escritura de imágenes | OpenCV, solo para abrir y guardar archivos |
| Pruebas | pytest |

---

## Estructura del repositorio

```
rescalibur/
├── backend/
│   ├── app/
│   │   ├── main.py            # API (FastAPI)
│   │   ├── config.py          # Método de interpolación activo
│   │   ├── servicio.py        # Orquesta el proceso de reescalado
│   │   ├── procesador.py      # Lectura y escritura de imágenes
│   │   ├── resoluciones.py    # Cálculo de resoluciones de salida
│   │   └── metodos/           # Vecino, bilineal y bicúbico
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## Ejecución local

### Requisitos

- Python 3.10 o superior
- Node.js 18 o superior

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000` y su documentación interactiva en `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.

### Pruebas

```bash
cd backend
pytest
```

### Cambiar el método de interpolación

El método activo se define con un solo parámetro en `backend/app/config.py`:

```python
METODO_ACTIVO = "bilineal"  # opciones: "vecino", "bilineal", "bicubico"
```

Después de cambiarlo, reinicia el servidor.

---

## API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/salud` | Estado del servicio y método activo. |
| `POST` | `/api/imagen/info` | Recibe una imagen y devuelve su resolución y las opciones de salida disponibles. |
| `POST` | `/api/imagen/reescalar` | Recibe la imagen y la resolución elegida; devuelve la imagen reescalada en PNG. |

---

## Autores

- **Martín Pineda** — Frontend
- **Felipe Beltrán** — Backend

Proyecto académico desarrollado en la Universidad de los Llanos.
