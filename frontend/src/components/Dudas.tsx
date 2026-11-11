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
    <section id="dudas" className="mx-auto flex w-full max-w-[860px] scroll-mt-6 flex-col gap-3.5 px-4 py-20 md:px-6 md:pt-24 md:pb-28">
      <h2 className="mb-2.5 font-display text-[40px] leading-[0.95] font-extrabold tracking-[-0.04em] md:text-[64px]">
        ¿Dudas?
      </h2>
      {PREGUNTAS.map(({ pregunta, respuesta }) => (
        <details key={pregunta} className="group rounded-2xl border-3 border-tinta bg-superficie px-5 py-[18px] shadow-duro">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-[19px] font-extrabold focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-tinta [&::-webkit-details-marker]:hidden">
            {pregunta}
            <span aria-hidden="true" className="text-[28px] leading-none transition-transform group-open:rotate-45">
              +
            </span>
          </summary>
          <p className="mt-2.5 text-[17px]">{respuesta}</p>
        </details>
      ))}
    </section>
  );
}
