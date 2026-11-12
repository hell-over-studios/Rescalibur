import Espada from './ui/Espada';

/** Pie de página oscuro con la marca y los autores. */
export default function PiePagina() {
  return (
    <footer className="bg-noche text-crema">
      <div className="mx-auto flex w-full max-w-[1180px] flex-wrap items-center justify-between gap-x-6 gap-y-4 px-4 py-10 md:px-6">
        <p className="flex items-center gap-3 font-display text-2xl font-extrabold tracking-[-0.03em]">
          <Espada className="h-10 w-auto" />
          Rescalibur
        </p>
        <p className="text-[15px] text-niebla">
          Martín Pineda <span className="text-acento">·</span> Felipe Beltrán{' '}
          <span className="text-acento">·</span> Universidad de los Llanos · 2026
        </p>
      </div>
    </footer>
  );
}
