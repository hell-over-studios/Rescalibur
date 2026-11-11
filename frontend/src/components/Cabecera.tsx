/** Barra superior: logo, enlace a las dudas y botón que baja hasta la app. */
export default function Cabecera() {
  return (
    <header className="mx-auto flex w-full max-w-[1180px] flex-wrap items-center justify-between gap-3.5 px-4 py-5 md:px-6">
      <p className="flex items-center gap-2.5 font-display text-[26px] leading-8 font-extrabold tracking-[-0.03em]">
        <span
          aria-hidden="true"
          className="inline-flex size-9 items-center justify-center rounded-[10px] border-3 border-tinta bg-acento shadow-duro-sm"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 3h6v6" />
            <path d="M9 21H3v-6" />
            <path d="M21 3l-7 7" />
            <path d="M3 21l7-7" />
          </svg>
        </span>
        RESCALIBUR!
      </p>

      <nav aria-label="Principal" className="flex flex-wrap items-center gap-x-6 gap-y-2">
        <a
          href="#dudas"
          className="py-2.5 text-base font-bold underline decoration-3 underline-offset-[5px] focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-tinta"
        >
          ¿Dudas?
        </a>
        <a
          href="https://github.com/hell-over-studios/Rescalibur"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-12 items-center gap-2 rounded-xl border-3 border-tinta bg-tinta px-4 text-base font-bold text-superficie shadow-acento-2 transition-transform duration-100 hover:-translate-x-0.5 hover:-translate-y-0.5 focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-tinta motion-reduce:transform-none"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M16 18l6-6-6-6" />
            <path d="M8 6l-6 6 6 6" />
          </svg>
          GitHub
          <span className="sr-only">(se abre en otra pestaña)</span>
        </a>
        <a
          href="#app"
          className="inline-flex min-h-12 items-center rounded-xl border-3 border-tinta bg-superficie px-5 text-base font-bold shadow-duro transition-transform duration-100 hover:-translate-x-0.5 hover:-translate-y-0.5 focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-tinta motion-reduce:transform-none"
        >
          Agrandar una foto
        </a>
      </nav>
    </header>
  );
}
