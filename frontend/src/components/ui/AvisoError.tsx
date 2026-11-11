import type { MensajeError } from '../../tipos';

export default function AvisoError({ titulo, mensaje }: MensajeError) {
  return (
    <div
      role="alert"
      className="flex flex-col gap-1 rounded-2xl border-3 border-tinta bg-superficie px-6 py-5 shadow-duro"
    >
      <p className="font-display text-[22px] leading-[26px] font-extrabold tracking-[-0.02em]">{titulo}</p>
      <p className="text-base leading-[22px] font-medium">{mensaje}</p>
    </div>
  );
}
