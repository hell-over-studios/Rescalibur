import { useState } from 'react';
import type { ChangeEvent, DragEvent } from 'react';
import { EXTENSIONES_PERMITIDAS, TAMANO_MAXIMO_MB } from '../constantes';
import type { MensajeError } from '../tipos';
import AvisoError from './ui/AvisoError';

interface CargadorImagenProps {
  /** Se llama cuando el usuario elige un archivo que pasa la validación. */
  alSeleccionarArchivo: (archivo: File) => void;
  /** Deshabilita la carga mientras el servidor lee la imagen. */
  deshabilitado?: boolean;
  /** Error que viene del servidor (por ejemplo, un archivo que no se pudo leer). */
  error?: MensajeError | null;
}

/** Muestra el peso con un decimal solo si hace falta: 25 → "25", 20.4 → "20.4". */
function formatearMB(bytes: number): string {
  const megabytes = bytes / (1024 * 1024);
  return Number.isInteger(megabytes) ? String(megabytes) : megabytes.toFixed(1);
}

/**
 * Valida el archivo antes de enviarlo al backend.
 * Se valida por extensión porque algunos navegadores no informan el tipo MIME de BMP o TIFF.
 * @returns El error para mostrar, o null si el archivo es válido.
 */
function validarArchivo(archivo: File): MensajeError | null {
  const extension = archivo.name.split('.').pop()?.toLowerCase() ?? '';
  if (!EXTENSIONES_PERMITIDAS.includes(extension)) {
    return {
      titulo: `No pudimos cargar «${archivo.name}»`,
      mensaje: 'Ese archivo no es una imagen. Elige un JPG, PNG, BMP, WEBP o TIFF.',
    };
  }
  if (archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024) {
    return {
      titulo: `Tu imagen pesa ${formatearMB(archivo.size)} MB`,
      mensaje: `El máximo es ${TAMANO_MAXIMO_MB} MB. Elige una imagen más liviana.`,
    };
  }
  return null;
}

/**
 * Paso 1 (HU-01): zona para cargar la imagen con clic, con toque o arrastrando el archivo.
 * No lleva título propio: el título «Tres toques y listo» y la barra de pasos ya dicen en qué paso va.
 * Toda la zona es un <label> del input de archivo, así que funciona con clic, toque (en celular no se
 * puede arrastrar) y teclado.
 */
export default function CargadorImagen({
  alSeleccionarArchivo,
  deshabilitado = false,
  error = null,
}: CargadorImagenProps) {
  const [errorLocal, setErrorLocal] = useState<MensajeError | null>(null);
  const [arrastrando, setArrastrando] = useState(false);

  const procesarArchivo = (archivo: File) => {
    const errorValidacion = validarArchivo(archivo);
    setErrorLocal(errorValidacion);
    if (!errorValidacion) alSeleccionarArchivo(archivo);
  };

  const manejarSoltar = (evento: DragEvent<HTMLLabelElement>) => {
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
  const errorVisible = errorLocal ?? error;

  return (
    <>
      {errorVisible && <AvisoError {...errorVisible} />}

      <label
        onDragOver={(evento) => {
          evento.preventDefault();
          setArrastrando(true);
        }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={manejarSoltar}
        className={`flex flex-col items-center justify-center gap-3.5 rounded-[18px] border-3 border-dashed border-tinta px-5 py-12 text-center transition-colors md:py-[72px] ${
          deshabilitado ? 'cursor-wait' : 'cursor-pointer'
        } ${
          arrastrando ? 'bg-superficie' : 'bg-transparent hover:bg-superficie/60'
        } has-[:focus-visible]:outline-4 has-[:focus-visible]:outline-offset-4 has-[:focus-visible]:outline-tinta`}
      >
        <input
          type="file"
          accept={extensionesAceptadas}
          onChange={manejarCambio}
          disabled={deshabilitado}
          className="sr-only"
        />
        <span
          aria-hidden="true"
          className="inline-flex size-[72px] items-center justify-center rounded-full bg-tinta text-suelo"
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 16V4" />
            <path d="M7 9l5-5 5 5" />
            <path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
          </svg>
        </span>
        <span className="font-display text-[26px] leading-[30px] font-extrabold tracking-[-0.03em] md:text-[34px] md:leading-9">
          {deshabilitado ? (
            'Leyendo tu foto…'
          ) : arrastrando ? (
            '¡Suéltala!'
          ) : (
            <>
              <span className="md:hidden">Toca para elegir tu foto</span>
              <span className="hidden md:inline">Arrastra tu foto aquí</span>
            </>
          )}
        </span>
        <span className="text-base leading-[22px] font-medium">
          <span className="hidden md:inline">o toca para elegirla · </span>
          JPG, PNG, WEBP, BMP o TIFF · máximo {TAMANO_MAXIMO_MB} MB
        </span>
      </label>
    </>
  );
}
