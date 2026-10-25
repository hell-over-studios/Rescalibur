/**
 * Único módulo que se comunica con el backend.
 * Los componentes nunca llaman a fetch directamente.
 */
import { URL_API } from '../constantes';
import type { InfoImagen } from '../tipos';

/**
 * Lee el mensaje de error que envía FastAPI ({"detail": "..."}).
 * Si no se puede leer, devuelve un mensaje genérico.
 */
async function leerMensajeError(respuesta: Response): Promise<string> {
  try {
    const cuerpo = await respuesta.json();
    return typeof cuerpo.detail === 'string' ? cuerpo.detail : 'Ocurrió un error en el servidor.';
  } catch {
    return 'Ocurrió un error en el servidor.';
  }
}

/**
 * Envía la imagen al backend y obtiene su resolución y las opciones de salida (HU-02).
 * @param archivo Imagen seleccionada por el usuario.
 */
export async function obtenerInfoImagen(archivo: File): Promise<InfoImagen> {
  const formulario = new FormData();
  formulario.append('archivo', archivo);

  let respuesta: Response;
  try {
    respuesta = await fetch(`${URL_API}/api/imagen/info`, { method: 'POST', body: formulario });
  } catch {
    throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.');
  }

  if (!respuesta.ok) {
    throw new Error(await leerMensajeError(respuesta));
  }
  return respuesta.json();
}
