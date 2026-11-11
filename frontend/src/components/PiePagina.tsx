/** Pie de página negro con la marca. */
export default function PiePagina() {
  return (
    <footer className="bg-tinta text-superficie">
      <div className="mx-auto flex w-full max-w-[1180px] flex-wrap items-center justify-between gap-x-6 gap-y-3.5 px-4 py-9 md:px-6">
        <p className="font-display text-2xl font-extrabold tracking-[-0.03em]">
          RESCALIBUR<span className="text-acento">!</span>
        </p>
        <p className="text-[15px] text-[#d6d6d6]">Hecho en la Universidad de los Llanos · 2026</p>
      </div>
    </footer>
  );
}
