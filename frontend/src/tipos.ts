/**
 * Tipos de datos que intercambian el frontend y la API.
 * Siguen el contrato de API de la sección 5.1 del documento del Sprint 1.
 */

/** Una resolución de salida disponible, con las dimensiones finales ya calculadas por el backend. */
export interface OpcionResolucion {
  clave: 'hd' | 'fullhd' | '2k' | '4k';
  nombre: string;
  ancho: number;
  alto: number;
}

/** Respuesta de POST /api/imagen/info. */
export interface InfoImagen {
  nombre: string;
  ancho: number;
  alto: number;
  opciones: OpcionResolucion[];
}

/** Resultado de POST /api/imagen/reescalar: la imagen en PNG y los datos que envía la API en las cabeceras. */
export interface ResultadoReescalado {
  imagen: Blob;
  ancho: number;
  alto: number;
  /** Cabecera X-Metodo. No se muestra en pantalla; queda disponible para las métricas del Sprint 2. */
  metodo: string | null;
  /** Cabecera X-Tiempo-Ms. No se muestra en pantalla; queda disponible para las métricas del Sprint 2. */
  tiempoMs: number | null;
}

/** Mensaje de error listo para mostrar en el AvisoError. */
export interface MensajeError {
  titulo: string;
  mensaje: string;
}

/** Paso actual del flujo: 1 cargar, 2 elegir resolución, 3 descargar. */
export type Paso = 1 | 2 | 3;
