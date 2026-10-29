import type { Paso } from '../tipos';

const PASOS = ['Cargar', 'Elegir resolución', 'Descargar'] as const;

type Estado = 'hecho' | 'actual' | 'pendiente';

function estadoDe(indice: number, paso: Paso): Estado {
  const actual = paso - 1;
  if (indice < actual) return 'hecho';
  return indice === actual ? 'actual' : 'pendiente';
}

const CLASES_ESCRITORIO: Record<Estado, string> = {
  hecho: 'bg-superficie-honda text-tinta',
  actual: 'bg-tinta text-suelo',
  pendiente: 'bg-superficie text-tinta-2',
};

const CLASES_CELULAR: Record<Estado, string> = {
  hecho: 'bg-superficie-honda',
  actual: 'bg-tinta',
  pendiente: 'bg-superficie',
};

/** Barra de 3 pasos. En celular se compacta a tres segmentos y el nombre del paso actual. */
export default function BarraPasos({ paso }: { paso: Paso }) {
  return (
    <nav aria-label="Progreso">
      <ol className="hidden gap-1 md:flex">
        {PASOS.map((nombre, i) => {
          const estado = estadoDe(i, paso);
          return (
            <li
              key={nombre}
              aria-current={estado === 'actual' ? 'step' : undefined}
              className={`flex-1 px-5 py-4 text-base leading-[22px] font-medium ${CLASES_ESCRITORIO[estado]}`}
            >
              {nombre}
            </li>
          );
        })}
      </ol>

      <div className="md:hidden">
        <ol className="flex gap-1">
          {PASOS.map((nombre, i) => {
            const estado = estadoDe(i, paso);
            return (
              <li
                key={nombre}
                aria-current={estado === 'actual' ? 'step' : undefined}
                className={`h-1.5 flex-1 ${CLASES_CELULAR[estado]}`}
              >
                <span className="sr-only">{nombre}</span>
              </li>
            );
          })}
        </ol>
        <p className="mt-2.5 font-display text-base leading-5 font-medium">{PASOS[paso - 1]}</p>
      </div>
    </nav>
  );
}
