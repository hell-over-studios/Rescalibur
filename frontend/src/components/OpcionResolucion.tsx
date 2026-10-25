import type { OpcionResolucion as Opcion } from '../tipos';

interface OpcionResolucionProps {
  opcion: Opcion;
  seleccionada: boolean;
  alElegir: () => void;
}

/** Una opción de resolución. Es un radio nativo: se maneja con las flechas del teclado. */
export default function OpcionResolucion({ opcion, seleccionada, alElegir }: OpcionResolucionProps) {
  return (
    <label
      className={`flex cursor-pointer items-center justify-between gap-3 px-4 py-[18px] transition-colors md:flex-col md:items-start md:justify-start md:gap-0.5 md:px-[18px] md:py-3.5 ${
        seleccionada ? 'bg-tinta' : 'bg-superficie hover:bg-superficie-honda'
      } has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-tinta`}
    >
      <input
        type="radio"
        name="resolucion"
        value={opcion.clave}
        checked={seleccionada}
        onChange={alElegir}
        className="sr-only"
      />
      <span
        className={`font-display text-xl leading-6 font-semibold tracking-[-0.02em] md:text-[22px] md:leading-[26px] ${
          seleccionada ? 'text-suelo' : 'text-tinta'
        }`}
      >
        {opcion.nombre}
      </span>
      <span
        className={`text-base leading-[22px] font-medium md:font-normal ${seleccionada ? 'text-acento' : 'text-tinta'}`}
      >
        {opcion.ancho} × {opcion.alto}
      </span>
    </label>
  );
}
