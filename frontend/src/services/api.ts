/**
 * Único módulo que se comunica con el backend.
 * Los componentes nunca llaman a fetch directamente.
 */
import { URL_API } from '../constantes';
import type { InfoImagen, OpcionResolucion, ResultadoReescalado } from '../tipos';

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

/** Envía un formulario por POST y lanza un Error con un mensaje claro si algo falla. */
async function enviarFormulario(ruta: string, formulario: FormData): Promise<Response> {
  let respuesta: Response;
  try {
    respuesta = await fetch(`${URL_API}${ruta}`, { method: 'POST', body: formulario });
  } catch {
    throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.');
  }

  if (!respuesta.ok) {
    throw new Error(await leerMensajeError(respuesta));
  }
  return respuesta;
}

/** Lee una cabecera numérica de la respuesta (por ejemplo X-Ancho). Devuelve null si falta o no es válida. */
function leerNumero(respuesta: Response, cabecera: string): number | null {
  const valor = Number(respuesta.headers.get(cabecera));
  return Number.isFinite(valor) && valor > 0 ? valor : null;
}

/**
 * Envía la imagen al backend y obtiene su resolución y las opciones de salida (HU-02).
 * @param archivo Imagen seleccionada por el usuario.
 */
export async function obtenerInfoImagen(archivo: File): Promise<InfoImagen> {
  const formulario = new FormData();
  formulario.append('archivo', archivo);
  const respuesta = await enviarFormulario('/api/imagen/info', formulario);
  return respuesta.json();
}

/**
 * Pide al backend la imagen reescalada a la resolución elegida (HU-05).
 * @param archivo Imagen original.
 * @param opcion Resolución de salida elegida por el usuario.
 */
export async function reescalarImagen(archivo: File, opcion: OpcionResolucion): Promise<ResultadoReescalado> {
  const formulario = new FormData();
  formulario.append('archivo', archivo);
  formulario.append('resolucion', opcion.clave);
  const respuesta = await enviarFormulario('/api/imagen/reescalar', formulario);
  return {
    imagen: await respuesta.blob(),
    ancho: leerNumero(respuesta, 'X-Ancho') ?? opcion.ancho,
    alto: leerNumero(respuesta, 'X-Alto') ?? opcion.alto,
    metodo: respuesta.headers.get('X-Metodo'),
    tiempoMs: leerNumero(respuesta, 'X-Tiempo-Ms'),
  };
}
