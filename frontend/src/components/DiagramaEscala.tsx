import { useState } from 'react';
import type { InfoImagen, OpcionResolucion } from '../tipos';

// Tonos de la opción más grande a la más pequeña. La opción elegida siempre se pinta de acento.
const TONOS = [
  'bg-superficie text-tinta',
  'bg-superficie-honda text-tinta',
  'bg-tinta-2 text-suelo',
  'bg-tinta text-suelo',
];

interface DiagramaEscalaProps {
  infoImagen: InfoImagen;
  claveSeleccionada: OpcionResolucion['clave'];
  urlVistaPrevia: string;
}

/**
 * Rectángulos anidados a escala real: el más grande es la mayor opción disponible y la imagen
 * original se dibuja en la esquina con su tamaño proporcional. Muestra cuánto crece la imagen.
 */
export default function DiagramaEscala({ infoImagen, claveSeleccionada, urlVistaPrevia }: DiagramaEscalaProps) {
  const [sinVista, setSinVista] = useState(false);
  const orden = [...infoImagen.opciones].sort((a, b) => b.ancho - a.ancho);
  const mayor = orden[0];
  const sinElegida = orden.filter((opcion) => opcion.clave !== claveSeleccionada);
  const pct = (valor: number, total: number) => `${(valor / total) * 100}%`;

  return (
    <div
      role="img"
      aria-label={`Tu imagen de ${infoImagen.ancho} × ${infoImagen.alto} dentro de cada resolución, a escala`}
      className="relative w-full"
      style={{ aspectRatio: `${mayor.ancho} / ${mayor.alto}` }}
    >
      {orden.map((opcion) => (
        <div
          key={opcion.clave}
          className={`absolute top-0 left-0 ${
            opcion.clave === claveSeleccionada
              ? 'bg-acento text-tinta'
              : TONOS[Math.min(sinElegida.indexOf(opcion), TONOS.length - 1)]
          }`}
          style={{ width: pct(opcion.ancho, mayor.ancho), height: pct(opcion.alto, mayor.alto) }}
        >
          <span className="absolute right-1.5 bottom-0.5 text-xs leading-3 font-medium md:right-2.5 md:bottom-1 md:text-[13px] md:leading-4">
            {opcion.nombre}
            <span className="hidden md:inline">
              {' '}
              · {opcion.ancho} × {opcion.alto}
            </span>
          </span>
        </div>
      ))}

      <div
        className="absolute top-0 left-0 overflow-hidden bg-suelo"
        style={{ width: pct(infoImagen.ancho, mayor.ancho), height: pct(infoImagen.alto, mayor.alto) }}
      >
        {sinVista ? (
          <span className="flex size-full items-center justify-center text-[10px] leading-3 text-tinta-2 md:text-xs">
            Tu imagen
          </span>
        ) : (
          <img src={urlVistaPrevia} alt="" onError={() => setSinVista(true)} className="size-full object-cover" />
        )}
      </div>
    </div>
  );
}
