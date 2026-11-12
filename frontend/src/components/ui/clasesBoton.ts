export type VarianteBoton = 'primario' | 'secundario' | 'deshabilitado';

// Alto mínimo 56 px (≥ 44 px táctiles). En celular ocupa todo el ancho; desde md se ajusta al texto.
// Al pasar el mouse el botón «sube» y al presionarlo «se hunde» sobre su sombra.
const BASE =
  'inline-flex min-h-14 w-full items-center justify-center gap-2.5 rounded-full border border-linea px-7 py-4 text-center text-lg leading-[22px] font-extrabold transition-transform duration-100 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-tinta md:w-auto';

const MOVIMIENTO =
  'cursor-pointer hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-[3px] active:translate-y-[3px] active:shadow-none motion-reduce:transform-none';

const VARIANTES: Record<VarianteBoton, string> = {
  primario: `${MOVIMIENTO} border-acento bg-acento text-tinta shadow-acento-2 hover:bg-acento-hover`,
  secundario: `${MOVIMIENTO} bg-superficie text-tinta shadow-duro`,
  deshabilitado: 'cursor-not-allowed bg-superficie-honda text-tinta-2 opacity-70',
};

export function clasesBoton(variante: VarianteBoton): string {
  return `${BASE} ${VARIANTES[variante]}`;
}
