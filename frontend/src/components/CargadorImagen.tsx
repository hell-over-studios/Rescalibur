import { useState } from 'react';
import type { ChangeEvent, DragEvent } from 'react';
import { EXTENSIONES_PERMITIDAS, TAMANO_MAXIMO_MB } from '../constantes';
import type { MensajeError } from '../tipos';
import AvisoError from './ui/AvisoError';
import { clasesBoton } from './ui/clasesBoton';
import TituloPantalla from './ui/TituloPantalla';

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
 * Paso 1 (HU-01): zona para cargar la imagen con botón, con toque o arrastrando el archivo.
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
      <TituloPantalla
        titulo="Carga tu imagen"
        subtitulo={
          <>
            <span className="md:hidden">La reescalamos y la descargas en PNG.</span>
            <span className="hidden md:inline">La reescalamos a HD, Full HD, 2K o 4K y la descargas en PNG.</span>
          </>
        }
      />

      {errorVisible && <AvisoError {...errorVisible} />}

      <label
        onDragOver={(evento) => {
          evento.preventDefault();
          setArrastrando(true);
        }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={manejarSoltar}
        className={`flex cursor-pointer flex-col items-center justify-center gap-4 px-5 py-10 text-center transition-colors md:gap-5 md:px-10 md:py-20 ${
          arrastrando ? 'bg-superficie-honda' : 'bg-superficie'
        } has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-tinta`}
      >
        <input
          type="file"
          accept={extensionesAceptadas}
          onChange={manejarCambio}
          disabled={deshabilitado}
          className="sr-only"
        />
        <span className="font-display text-[26px] leading-[30px] font-semibold tracking-[-0.03em] md:text-[40px] md:leading-[44px]">
          <span className="md:hidden">Toca para elegir tu imagen</span>
          <span className="hidden md:inline">Arrastra tu imagen aquí</span>
        </span>
        <span className="hidden text-base text-tinta-2 md:block">o</span>
        <span className={clasesBoton(deshabilitado ? 'deshabilitado' : 'primario')}>
          {deshabilitado ? 'Leyendo imagen…' : 'Elegir imagen'}
        </span>
        <span className="text-base leading-[22px] text-tinta-2">
          JPG, JPEG, PNG, BMP, WEBP o TIFF · máximo {TAMANO_MAXIMO_MB} MB
        </span>
      </label>
    </>
  );
}
