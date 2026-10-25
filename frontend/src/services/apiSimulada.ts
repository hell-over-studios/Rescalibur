/**
 * API SIMULADA: solo para desarrollar la interfaz mientras el backend no está listo.
 *
 * Se activa con VITE_USAR_SIMULADO=true. NO es el método numérico del proyecto: el cálculo real
 * (vecino más cercano y bilineal con NumPy) vive en el backend. Aquí se reproduce la regla de
 * resoluciones del documento y se escala con un canvas del navegador solo para tener una respuesta.
 */
import { TAMANO_MAXIMO_MB } from '../constantes';
import type { InfoImagen, OpcionResolucion, ResultadoReescalado } from '../tipos';

const MARCOS: { clave: OpcionResolucion['clave']; nombre: string; ancho: number; alto: number }[] = [
  { clave: 'hd', nombre: 'HD', ancho: 1280, alto: 720 },
  { clave: 'fullhd', nombre: 'Full HD', ancho: 1920, alto: 1080 },
  { clave: '2k', nombre: '2K', ancho: 2560, alto: 1440 },
  { clave: '4k', nombre: '4K', ancho: 3840, alto: 2160 },
];

const esperar = (milisegundos: number) => new Promise((resolver) => setTimeout(resolver, milisegundos));

/** Regla del documento: s = mín(W/w, H/h); la opción solo existe si s > 1. */
export function calcularOpciones(ancho: number, alto: number): OpcionResolucion[] {
  const vertical = alto > ancho;
  const opciones: OpcionResolucion[] = [];
  for (const marco of MARCOS) {
    const anchoMarco = vertical ? marco.alto : marco.ancho;
    const altoMarco = vertical ? marco.ancho : marco.alto;
    const escala = Math.min(anchoMarco / ancho, altoMarco / alto);
    if (escala > 1) {
      opciones.push({
        clave: marco.clave,
        nombre: marco.nombre,
        ancho: Math.round(ancho * escala),
        alto: Math.round(alto * escala),
      });
    }
  }
  return opciones;
}

async function decodificar(archivo: File): Promise<HTMLImageElement> {
  const url = URL.createObjectURL(archivo);
  try {
    const imagen = new Image();
    imagen.src = url;
    await imagen.decode();
    return imagen;
  } catch {
    throw new Error('El archivo no es una imagen válida.');
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function obtenerInfoImagen(archivo: File): Promise<InfoImagen> {
  await esperar(400);
  if (archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024) {
    throw new Error(`La imagen supera el tamaño máximo de ${TAMANO_MAXIMO_MB} MB.`);
  }
  const imagen = await decodificar(archivo);
  return {
    nombre: archivo.name,
    ancho: imagen.naturalWidth,
    alto: imagen.naturalHeight,
    opciones: calcularOpciones(imagen.naturalWidth, imagen.naturalHeight),
  };
}

export async function reescalarImagen(archivo: File, opcion: OpcionResolucion): Promise<ResultadoReescalado> {
  const inicio = performance.now();
  await esperar(1500);
  const imagen = await decodificar(archivo);
  const lienzo = document.createElement('canvas');
  lienzo.width = opcion.ancho;
  lienzo.height = opcion.alto;
  const contexto = lienzo.getContext('2d');
  if (!contexto) throw new Error('No se pudo crear el lienzo de la imagen.');
  contexto.imageSmoothingEnabled = false;
  contexto.drawImage(imagen, 0, 0, opcion.ancho, opcion.alto);
  const blob = await new Promise<Blob | null>((resolver) => lienzo.toBlob(resolver, 'image/png'));
  if (!blob) throw new Error('No se pudo generar el PNG.');
  return {
    imagen: blob,
    ancho: opcion.ancho,
    alto: opcion.alto,
    metodo: 'simulado',
    tiempoMs: Math.round(performance.now() - inicio),
  };
}
