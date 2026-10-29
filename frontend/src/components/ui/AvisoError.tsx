import type { MensajeError } from '../../tipos';

export default function AvisoError({ titulo, mensaje }: MensajeError) {
  return (
    <div role="alert" className="flex flex-col gap-1 bg-tinta px-6 py-5">
      <p className="font-display text-[22px] leading-[26px] font-semibold tracking-[-0.02em] text-acento">{titulo}</p>
      <p className="text-base leading-[22px] text-suelo">{mensaje}</p>
    </div>
  );
}
