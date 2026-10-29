import type { Paso } from '../tipos';
import BarraPasos from './BarraPasos';

/** Logo + barra de pasos. Aparece igual en todas las pantallas. */
export default function Cabecera({ paso }: { paso: Paso }) {
  return (
    <div className="flex flex-col gap-6 md:gap-10">
      <p className="font-display text-2xl leading-7 font-bold tracking-[-0.03em] md:text-[28px] md:leading-8">
        rescalibur
      </p>
      <BarraPasos paso={paso} />
    </div>
  );
}
