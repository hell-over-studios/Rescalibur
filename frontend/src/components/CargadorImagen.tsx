import { useRef, useState } from 'react';
import type { ChangeEvent, DragEvent } from 'react';
import { EXTENSIONES_PERMITIDAS, TAMANO_MAXIMO_MB } from '../constantes';

interface CargadorImagenProps {
  /** Se llama cuando el usuario elige un archivo que pasa la validación. */
  alSeleccionarArchivo: (archivo: File) => void;
  /** Deshabilita la carga mientras se procesa una imagen. */
  deshabilitado?: boolean;
}

/**
 * Valida el archivo antes de enviarlo al backend.
 * Se valida por extensión porque algunos navegadores no informan el tipo MIME de BMP o TIFF.
 * @returns Mensaje de error, o null si el archivo es válido.
 */
function validarArchivo(archivo: File): string | null {
  const extension = archivo.name.split('.').pop()?.toLowerCase() ?? '';
  if (!EXTENSIONES_PERMITIDAS.includes(extension)) {
    return `El archivo ${archivo.name} no es una imagen compatible.`;
  }
  if (archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024) {
    return `La imagen supera el tamaño máximo de ${TAMANO_MAXIMO_MB} MB.`;
  }
  return null;
}

/**
 * Paso 1 (HU-01): zona para cargar la imagen con botón o arrastrando el archivo.
 */
export default function CargadorImagen({ alSeleccionarArchivo, deshabilitado = false }: CargadorImagenProps) {
  const [error, setError] = useState<string | null>(null);
  const [arrastrando, setArrastrando] = useState(false);
  const entradaArchivo = useRef<HTMLInputElement>(null);

  const procesarArchivo = (archivo: File) => {
    const mensajeError = validarArchivo(archivo);
    setError(mensajeError);
    if (!mensajeError) alSeleccionarArchivo(archivo);
  };

  const manejarSoltar = (evento: DragEvent<HTMLDivElement>) => {
    evento.preventDefault();
    setArrastrando(false);
    const archivo = evento.dataTransfer.files?.[0];
    if (archivo && !deshabilitado) procesarArchivo(archivo);
  };

  const manejarCambio = (evento: ChangeEvent<HTMLInputElement>) => {
    const archivo = evento.target.files?.[0];
    if (archivo) procesarArchivo(archivo);
    // Se limpia para poder volver a elegir el mismo archivo.
    evento.target.value = '';
  };

  const extensionesAceptadas = EXTENSIONES_PERMITIDAS.map((extension) => `.${extension}`).join(',');

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 md:p-6">
      <h2 className="mb-4 text-lg font-bold text-slate-900">Carga tu imagen</h2>

      {/* En celular no se puede arrastrar, por eso toda la zona también funciona como botón. */}
      <div
        role="button"
        tabIndex={0}
        onClick={() => !deshabilitado && entradaArchivo.current?.click()}
        onKeyDown={(evento) => evento.key === 'Enter' && entradaArchivo.current?.click()}
        onDragOver={(evento) => {
          evento.preventDefault();
          setArrastrando(true);
        }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={manejarSoltar}
        className={`cursor-pointer rounded-xl border-2 border-dashed px-4 py-10 text-center transition-colors ${
          arrastrando ? 'border-indigo-600 bg-indigo-100' : 'border-indigo-300 bg-indigo-50'
        } ${deshabilitado ? 'pointer-events-none opacity-60' : ''}`}
      >
        <p className="mb-1 font-bold text-slate-900">Arrastra tu imagen aquí</p>
        <p className="mb-4 text-sm text-slate-500">o</p>
        <span className="inline-block rounded-lg bg-indigo-700 px-5 py-3 text-sm font-bold text-white">
          Seleccionar archivo
        </span>
        <p className="mt-4 text-xs text-slate-500">
          Formatos: JPG, PNG, BMP, WEBP, TIFF · Máximo {TAMANO_MAXIMO_MB} MB
        </p>
        <input
          ref={entradaArchivo}
          type="file"
          accept={extensionesAceptadas}
          onChange={manejarCambio}
          className="hidden"
        />
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
    </section>
  );
}
