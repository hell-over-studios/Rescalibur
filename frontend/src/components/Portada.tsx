// Colores de la foto pixelada de 4 × 3 del dibujo (un atardecer). Solo decoración.
const PIXELES = [
  '#1b1f5e', '#2e2a78', '#2e2a78', '#1b1f5e',
  '#96407a', '#f6c46e', '#e07a5f', '#96407a',
  '#3c1e50', '#7a3a5a', '#5a2e5e', '#3c1e50',
];

// La misma escena, suave, para la foto «agrandada».
const ATARDECER_SUAVE =
  'radial-gradient(circle at 50% 66%, #ffec96 0%, #f6c46e 10%, rgba(224,122,95,0) 28%), linear-gradient(180deg, #1b1f5e 0%, #46287a 30%, #96407a 50%, #e07a5f 64%, #3c1e50 65%, #120c24 100%)';

/** Portada: título grande y un dibujo de una foto chiquita que pasa a ser grande. */
export default function Portada() {
  return (
    <section className="mx-auto flex w-full max-w-[1180px] flex-wrap items-center gap-12 px-4 pt-8 pb-16 md:px-6 md:pt-12 md:pb-22">
      <div className="flex min-w-0 flex-[1_1_520px] flex-col items-start gap-6">
        <h1 className="font-display text-[56px] leading-[0.88] font-extrabold tracking-[-0.04em] md:text-[clamp(56px,9vw,128px)]">
          HAZLA
          <br />
          MÁS
          <br />
          <span className="inline-block -rotate-2 border-4 border-tinta bg-acento px-3">GRANDE.</span>
        </h1>
        <p className="max-w-[480px] text-xl leading-7 font-medium md:text-[21px]">
          Sube tu foto chiquita y sácala en HD, Full HD, 2K o 4K. Así de simple.
        </p>
      </div>

      <div aria-hidden="true" className="flex min-w-0 flex-[1_1_380px] items-center justify-center gap-4">
        <div className="w-[90px] flex-none rounded-xl border-3 border-tinta bg-superficie p-1.5 shadow-duro">
          <div className="grid aspect-[4/3] grid-cols-4">
            {PIXELES.map((color, i) => (
              <div key={i} style={{ backgroundColor: color }} />
            ))}
          </div>
        </div>
        <svg width="56" height="32" viewBox="0 0 56 32" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="flex-none">
          <path d="M3 16h46" />
          <path d="M38 5l12 11-12 11" />
        </svg>
        <div className="max-w-[300px] flex-[1_1_auto] rotate-2 rounded-2xl border-3 border-tinta bg-superficie p-2.5 shadow-duro-lg">
          <div className="aspect-[4/3] rounded-lg" style={{ background: ATARDECER_SUAVE }} />
        </div>
      </div>
    </section>
  );
}
