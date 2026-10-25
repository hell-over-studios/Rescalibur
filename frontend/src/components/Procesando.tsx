import { useState } from 'react';
import type { InfoImagen, OpcionResolucion } from '../tipos';
import Boton from './ui/Boton';
import TituloPantalla from './ui/TituloPantalla';

interface ProcesandoProps {
  infoImagen: InfoImagen;
  opcion: OpcionResolucion;
  urlVistaPrevia: string;
}

/** Paso 3 mientras la API trabaja: botón deshabilitado e indicador de carga. */
export default function Procesando({ infoImagen, opcion, urlVistaPrevia }: ProcesandoProps) {
  const [sinVista, setSinVista] = useState(false);

  return (
    <>
      <TituloPantalla
        titulo="Reescalando tu imagen…"
        subtitulo={`${infoImagen.nombre} · de ${infoImagen.ancho} × ${infoImagen.alto} a ${opcion.ancho} × ${opcion.alto} px`}
      />

      <div className="flex flex-col gap-6 md:grid md:grid-cols-[1.65fr_1fr] md:items-start">
        <div
          role="img"
          aria-label={`Tu imagen de ${infoImagen.ancho} × ${infoImagen.alto} dentro del marco ${opcion.nombre}`}
          className="relative w-full bg-acento"
          style={{ aspectRatio: `${opcion.ancho} / ${opcion.alto}` }}
        >
          <div
            className="absolute top-0 left-0 overflow-hidden bg-suelo"
            style={{
              width: `${(infoImagen.ancho / opcion.ancho) * 100}%`,
              height: `${(infoImagen.alto / opcion.alto) * 100}%`,
            }}
          >
            {sinVista ? (
              <span className="flex size-full items-center justify-center text-xs text-tinta-2">Tu imagen</span>
            ) : (
              <img src={urlVistaPrevia} alt="" onError={() => setSinVista(true)} className="size-full object-cover" />
            )}
          </div>
          <span className="absolute right-2 bottom-1.5 text-xs leading-4 font-medium text-tinta md:right-2.5 md:bottom-2 md:text-[13px]">
            {opcion.nombre}
            <span className="hidden md:inline">
              {' '}
              · {opcion.ancho} × {opcion.alto}
            </span>
          </span>
        </div>

        {/* En celular la barra va primero; desde md, el texto va primero. */}
        <div className="flex flex-col-reverse gap-4 md:flex-col">
          <p className="text-base leading-[22px] md:text-lg md:leading-[26px]">
            Esto puede tardar unos segundos con imágenes grandes. No cierres la página.
          </p>
          <div
            role="progressbar"
            aria-label="Reescalando imagen"
            className="h-2 w-full overflow-hidden bg-superficie-honda"
          >
            <div className="h-full w-2/5 animate-pulse bg-tinta motion-reduce:animate-none" />
          </div>
        </div>
      </div>

      <div>
        <Boton variante="deshabilitado">Reescalando…</Boton>
      </div>
    </>
  );
}
