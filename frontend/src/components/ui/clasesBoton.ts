export type VarianteBoton = 'primario' | 'secundario' | 'deshabilitado';

// Alto mínimo 56 px (≥ 44 px táctiles). En celular ocupa todo el ancho; desde md se ajusta al texto.
const BASE =
  'inline-flex min-h-14 w-full items-center justify-center px-7 py-[18px] text-center text-lg leading-[22px] font-semibold transition-colors duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-tinta md:w-auto';

const VARIANTES: Record<VarianteBoton, string> = {
  primario: 'cursor-pointer bg-acento text-tinta hover:bg-acento-hover',
  secundario: 'cursor-pointer bg-superficie text-tinta hover:bg-superficie-honda',
  deshabilitado: 'cursor-not-allowed bg-superficie-honda text-tinta-2',
};

export function clasesBoton(variante: VarianteBoton): string {
  return `${BASE} ${VARIANTES[variante]}`;
}
