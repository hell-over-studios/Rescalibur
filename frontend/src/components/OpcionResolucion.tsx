import type { OpcionResolucion as Opcion } from '../tipos';

interface OpcionResolucionProps {
  opcion: Opcion;
  seleccionada: boolean;
  alElegir: () => void;
}

/** Para qué sirve cada tamaño, en palabras de cualquier usuario. */
const USO: Record<Opcion['clave'], string> = {
  hd: 'Para compartir',
  fullhd: 'Para tu monitor',
  '2k': 'Pantallas grandes',
  '4k': 'TV e impresiones',
};

/** Una opción de resolución. Es un radio nativo: se maneja con las flechas del teclado. */
export default function OpcionResolucion({ opcion, seleccionada, alElegir }: OpcionResolucionProps) {
  return (
    <label
      className={`flex cursor-pointer items-center justify-between gap-3 rounded-2xl border-3 border-tinta px-4 py-3.5 transition-[transform,box-shadow] duration-100 md:px-[18px] ${
        seleccionada
          ? 'translate-x-[3px] translate-y-[3px] bg-acento shadow-none'
          : 'bg-superficie shadow-duro hover:-translate-x-0.5 hover:-translate-y-0.5'
      } has-[:focus-visible]:outline-4 has-[:focus-visible]:outline-offset-4 has-[:focus-visible]:outline-tinta motion-reduce:transform-none`}
    >
      <input
        type="radio"
        name="resolucion"
        value={opcion.clave}
        checked={seleccionada}
        onChange={alElegir}
        className="sr-only"
      />
      <span className="flex flex-col">
        <span className="font-display text-2xl leading-7 font-extrabold tracking-[-0.03em]">{opcion.nombre}</span>
        <span className="text-[15px] leading-5 font-bold">{USO[opcion.clave]}</span>
      </span>
      <span className="font-mono text-sm leading-5">
        {opcion.ancho} × {opcion.alto}
      </span>
    </label>
  );
}
