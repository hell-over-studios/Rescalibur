/**
 * Constantes compartidas del frontend.
 * Deben coincidir con las del backend (ProcesadorImagen).
 */

/** Extensiones de imagen aceptadas por la aplicación. */
export const EXTENSIONES_PERMITIDAS = ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'tif', 'tiff'];

/** Tamaño máximo del archivo en megabytes. */
export const TAMANO_MAXIMO_MB = 20;

/** Dirección base de la API. Se puede cambiar con la variable VITE_API_URL. */
export const URL_API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/**
 * Si es "true", la interfaz usa una API simulada en el navegador (services/apiSimulada.ts).
 * Sirve para desarrollar mientras el backend no tenga todos los endpoints.
 */
export const USAR_SIMULADO = import.meta.env.VITE_USAR_SIMULADO === 'true';
