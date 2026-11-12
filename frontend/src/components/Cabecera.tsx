import Espada from './ui/Espada';

const ENLACE =
  'py-2.5 text-[15px] font-semibold text-niebla transition-colors hover:text-crema focus-visible:rounded focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-acento';

/** Barra superior sobre la portada oscura: logo, enlaces y botón que baja hasta la app. */
export default function Cabecera() {
  return (
    <header className="bg-noche text-crema">
      <div className="mx-auto flex w-full max-w-[1180px] flex-wrap items-center justify-between gap-3.5 px-4 py-5 md:px-6">
        <a href="#" className="flex items-center gap-3 font-display text-[24px] leading-8 font-extrabold tracking-[-0.03em]">
          <Espada className="h-9 w-auto" />
          Rescalibur
        </a>

        <nav aria-label="Principal" className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <a href="#dudas" className={ENLACE}>
            ¿Dudas?
          </a>
          <a
            href="https://github.com/hell-over-studios/Rescalibur"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-11 items-center gap-2 rounded-full border border-noche-borde px-4 font-mono text-sm text-crema transition-colors hover:border-niebla focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-acento"
          >
            GitHub
            <span className="sr-only">(se abre en otra pestaña)</span>
          </a>
          <a
            href="#app"
            className="inline-flex min-h-11 items-center rounded-full bg-acento px-5 text-[15px] font-bold text-tinta transition-colors hover:bg-acento-hover focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-acento"
          >
            Agrandar una foto
          </a>
        </nav>
      </div>
    </header>
  );
}
