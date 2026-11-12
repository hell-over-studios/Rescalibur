import type { Paso } from '../tipos';

const PASOS = ['Sube tu foto', 'Elige el tamaño', 'Descárgala'] as const;

type Estado = 'hecho' | 'actual' | 'pendiente';

function estadoDe(indice: number, paso: Paso): Estado {
  const actual = paso - 1;
  if (indice < actual) return 'hecho';
  return indice === actual ? 'actual' : 'pendiente';
}

// La barra vive sobre el fondo oscuro de la sección de la app.
const CLASES_ESCRITORIO: Record<Estado, string> = {
  hecho: 'border-noche-borde bg-noche-2 text-crema',
  actual: 'border-acento bg-acento text-tinta',
  pendiente: 'border-noche-borde bg-noche text-[#6e7486]',
};

const CLASES_CELULAR: Record<Estado, string> = {
  hecho: 'bg-crema',
  actual: 'bg-acento',
  pendiente: 'bg-noche-borde',
};

/** Barra de 3 pasos. En celular se compacta a tres segmentos y el nombre del paso actual. */
export default function BarraPasos({ paso }: { paso: Paso }) {
  return (
    <nav aria-label="Progreso">
      <ol className="hidden gap-2.5 md:flex">
        {PASOS.map((nombre, i) => {
          const estado = estadoDe(i, paso);
          return (
            <li
              key={nombre}
              aria-current={estado === 'actual' ? 'step' : undefined}
              className={`flex min-h-16 flex-1 items-center gap-3 rounded-2xl border px-4 py-2.5 ${CLASES_ESCRITORIO[estado]}`}
            >
              <span className="inline-flex size-[34px] flex-none items-center justify-center rounded-full border border-current font-mono text-sm font-bold">
                {i + 1}
              </span>
              <span className="truncate text-[17px] font-extrabold">{nombre}</span>
            </li>
          );
        })}
      </ol>

      <div className="md:hidden">
        <ol className="flex gap-1.5">
          {PASOS.map((nombre, i) => {
            const estado = estadoDe(i, paso);
            return (
              <li
                key={nombre}
                aria-current={estado === 'actual' ? 'step' : undefined}
                className={`h-2 flex-1 rounded-full ${CLASES_CELULAR[estado]}`}
              >
                <span className="sr-only">{nombre}</span>
              </li>
            );
          })}
        </ol>
        <p className="mt-2.5 font-display text-base leading-5 font-extrabold">
          {paso}. {PASOS[paso - 1]}
        </p>
      </div>
    </nav>
  );
}
