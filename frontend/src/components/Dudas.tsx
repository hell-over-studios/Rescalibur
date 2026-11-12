const PREGUNTAS = [
  {
    pregunta: '¿Guardan mis fotos?',
    respuesta: 'No. Tu foto se usa solo para agrandarla y se borra apenas termina.',
  },
  {
    pregunta: '¿Por qué no quedó exactamente en 3840 × 2160?',
    respuesta: 'Porque respetamos la forma de tu foto. La agrandamos hasta que quepa en ese tamaño sin estirarla.',
  },
  {
    pregunta: '¿Por qué no aparecen todos los tamaños?',
    respuesta: 'Si tu foto ya es igual o más grande que un tamaño, no hace falta agrandarla, así que no lo mostramos.',
  },
  {
    pregunta: '¿Mi foto va a quedar como nueva?',
    respuesta:
      'Va a quedar más grande y suave, sin cuadritos. Pero si la foto original está muy borrosa, no podemos inventar detalles que no tenía.',
  },
];

/** Preguntas frecuentes. Cada una se abre y se cierra (details nativo, funciona con teclado). */
export default function Dudas() {
  return (
    <section id="dudas" className="mx-auto flex w-full max-w-[860px] scroll-mt-6 flex-col gap-3 px-4 py-20 md:px-6 md:pt-24 md:pb-28">
      <p className="font-mono text-[13px] font-semibold tracking-[0.2em] text-acento-oscuro uppercase">Preguntas</p>
      <h2 className="mb-4 font-display text-[44px] leading-[0.95] font-extrabold tracking-[-0.04em] md:text-[64px]">¿Dudas?</h2>
      {PREGUNTAS.map(({ pregunta, respuesta }) => (
        <details key={pregunta} className="group rounded-2xl border border-linea bg-superficie px-6 py-5 open:shadow-duro">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-lg font-semibold focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-tinta [&::-webkit-details-marker]:hidden">
            {pregunta}
            <span aria-hidden="true" className="font-mono text-2xl leading-none text-acento-oscuro transition-transform group-open:rotate-45">
              +
            </span>
          </summary>
          <p className="mt-3 text-[17px] leading-7 text-tinta-2">{respuesta}</p>
        </details>
      ))}
    </section>
  );
}
