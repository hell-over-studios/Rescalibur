# Rescalibur

**Reescalador de imágenes web por métodos numéricos**

Rescalibur es una aplicación web que aumenta la resolución de una imagen calculando matemáticamente los píxeles nuevos. El usuario carga una imagen, elige la resolución de salida (HD, Full HD, 2K o 4K) y descarga el resultado en PNG.

Se implementaron y compararon tres métodos clásicos de interpolación, de menor a mayor complejidad: **vecino más cercano → bilineal → bicúbico**. Ninguno usa funciones de reescalado de librerías: cada método se programa a mano con NumPy sobre la matriz de píxeles. El método activo es el **bicúbico**.

---

## Estado del proyecto

Proyecto terminado: 11 historias de usuario completadas en 2 sprints, 257 pruebas automáticas que pasan.

| Método | Idea | Vecinos | Estado |
|---|---|---|---|
| Vecino más cercano | Copia el valor del píxel original más cercano (grado 0). | 1 | Hecho |
| Bilineal | Promedio ponderado por distancia de los 4 vecinos (grado 1 en cada eje). | 4 | Hecho |
| Bicúbico | Suma ponderada de 16 vecinos con el núcleo cúbico de Keys, a = −0,75 (grado 3). | 16 | Hecho · **activo** |

Las tres implementaciones se verificaron contra OpenCV: el vecino es idéntico y el bilineal y el bicúbico difieren como máximo en 1 nivel de intensidad (de 0 a 255).

---

## Cómo funciona

1. **Carga:** el usuario sube una imagen desde su dispositivo.
2. **Conversión:** la imagen se convierte en una matriz numérica de píxeles (alto × ancho × canales).
3. **Elección de resolución:** la aplicación muestra solo las resoluciones mayores que la actual y el tamaño final que tendrá la imagen en cada una.
4. **Interpolación:** se calcula cada píxel nuevo con el método activo.
5. **Descarga:** la imagen reescalada se descarga en formato PNG.

### Resoluciones disponibles

| Opción | Horizontal | Vertical |
|---|---|---|
| HD | 1280 × 720 | 720 × 1280 |
| Full HD | 1920 × 1080 | 1080 × 1920 |
| 2K | 2560 × 1440 | 1440 × 2560 |
| 4K | 3840 × 2160 | 2160 × 3840 |

La proporción original siempre se conserva: la imagen se amplía con un solo factor `s = min(W/w, H/h)` hasta encajar en el marco elegido, y solo se ofrecen las opciones con `s > 1`. Por ejemplo, una imagen de 800 × 600 en Full HD queda en **1440 × 1080**.

### Formatos aceptados

JPG, JPEG, PNG, BMP, WEBP y TIFF, hasta 20 MB. La salida es siempre PNG (sin pérdida), para que la calidad dependa solo del método numérico y no de la compresión.

### Privacidad

Las imágenes se procesan en memoria y se descartan al terminar. No se almacenan en ningún servidor ni base de datos.

---

## Estudio comparativo

Cada imagen de prueba (una foto, una ilustración y un texto, de 400 × 300) se redujo ×2, ×3 y ×4 y se volvió a ampliar con cada método. La calidad se midió con PSNR = 10 · log₁₀(255² / MSE): más dB, más parecida a la original.

| Método | PSNR promedio | Tiempo a 4K (2880 × 2160) | PNG a 4K |
|---|---|---|---|
| Vecino más cercano | 23,53 dB | 74,0 ms | 1 766 KB |
| Bilineal | 24,49 dB | 246,0 ms | 3 966 KB |
| Bicúbico | **25,75 dB** | 586,2 ms | 4 371 KB |

El bicúbico tuvo el PSNR más alto en las 9 combinaciones de imagen y factor. Es unas 8 veces más lento que el vecino, pero lleva una imagen a 4K en menos de 0,6 s; por eso es el método activo.

Para repetir el estudio (no necesita el servidor encendido):

```bash
cd backend
python -m estudio.comparativo
```

Genera `estudio/resultados/resultados.csv` (tiempos), `calidad.csv` (PSNR) y `estudio_comparativo.pdf`.

---

## Tecnologías

| Capa | Tecnologías |
|---|---|
| Frontend | React 19, TypeScript, Tailwind CSS 4, Vite |
| Backend | Python 3, FastAPI |
| Cálculo numérico | NumPy (implementación de los métodos) |
| Lectura y escritura de imágenes | OpenCV, solo para abrir y guardar archivos |
| Reportes | fpdf2 |
| Pruebas y estilo | pytest, Ruff |
| Despliegue local | Docker Compose y nginx |

---

## Estructura del repositorio

```
Rescalibur/
├── docker-compose.yml          # levanta backend y frontend (http://localhost:8080)
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py             # API (FastAPI)
│   │   ├── config.py           # Método de interpolación activo
│   │   ├── servicio.py         # Orquesta el reescalado y registra métricas
│   │   ├── procesador.py       # Lectura y escritura de imágenes (OpenCV)
│   │   ├── resoluciones.py     # Cálculo de resoluciones de salida
│   │   ├── metricas.py         # Registro de ejecuciones y psnr()
│   │   ├── reporte.py          # PDF de métricas (fpdf2)
│   │   ├── graficas.py         # Tablas y gráficas del PDF del estudio
│   │   └── metodos/            # base.py, vecino.py, bilineal.py, bicubico.py
│   ├── estudio/
│   │   ├── comparativo.py      # Estudio de tiempos y PSNR
│   │   ├── imagenes/           # Imágenes de prueba
│   │   └── resultados/         # CSV y PDF generados
│   ├── tests/                  # 257 pruebas (pytest)
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf              # Sirve la página y reenvía /api/ al backend
│   ├── src/
│   │   ├── components/         # Portada, pasos de la app, dudas, pie
│   │   ├── services/api.ts     # Llamadas al backend
│   │   └── App.tsx
│   └── package.json
├── LICENSE
└── README.md
```

---

## Ejecución local

### Con Docker (recomendado)

```bash
docker compose up -d --build
```

La aplicación queda en `http://localhost:8080`.

### Sin Docker

Requisitos: Python 3.10 o superior y Node.js 18 o superior.

**Backend**

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000` y su documentación interactiva en `http://localhost:8000/docs`.

**Frontend**

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

La aplicación queda en `http://localhost:5173`.

### Pruebas

```bash
cd backend
pytest
```

### Cambiar el método de interpolación

El método activo se define con un solo parámetro en `backend/app/config.py`:

```python
METODO_ACTIVO = "bicubico"  # opciones: "vecino", "bilineal", "bicubico"
```

Después de cambiarlo, reinicia el servidor.

---

## API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/salud` | Estado del servicio y método activo. |
| `POST` | `/api/imagen/info` | Recibe una imagen y devuelve su resolución y las opciones de salida disponibles. |
| `POST` | `/api/imagen/reescalar` | Recibe la imagen y la resolución elegida; devuelve el PNG con las cabeceras `X-Metodo`, `X-Tiempo-Ms`, `X-Ancho` y `X-Alto`. |
| `GET` | `/api/metricas` | Lista los reescalados registrados desde que arrancó el servidor. |
| `GET` | `/api/metricas/reporte` | Descarga un PDF con las métricas registradas. |

Una imagen inválida responde 400 y una de más de 20 MB, 413.

---

## Autores

- **Martín Pineda** — Frontend
- **Felipe Beltrán** — Backend

Proyecto académico desarrollado en la Universidad de los Llanos para el curso de Métodos Numéricos.
