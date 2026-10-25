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
