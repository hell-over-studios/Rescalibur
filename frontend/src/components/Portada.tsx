import { useEffect, useRef } from 'react';

/**
 * La escena del dibujo: una espada clavada en una piedra al atardecer. Es un SVG para poder
 * mostrarla nítida (foto «grande») y también reducida a 16 × 12 píxeles (foto «chiquita»).
 */
const ESCENA = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
<defs>
<linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#11131A"/><stop offset="0.35" stop-color="#2B3A67"/>
<stop offset="0.6" stop-color="#96407A"/><stop offset="0.72" stop-color="#E07A3F"/>
</linearGradient>
<radialGradient id="sol" cx="0.5" cy="0.5" r="0.5">
<stop offset="0" stop-color="#FFE7A8"/><stop offset="0.3" stop-color="#F0B54A"/>
<stop offset="1" stop-color="#F0B54A" stop-opacity="0"/>
</radialGradient>
<linearGradient id="suelo" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#2A2E3B"/><stop offset="1" stop-color="#11131A"/>
</linearGradient>
</defs>
<rect width="400" height="300" fill="url(#cielo)"/>
<circle cx="200" cy="200" r="120" fill="url(#sol)"/>
<rect y="210" width="400" height="90" fill="url(#suelo)"/>
<path d="M120 236 Q200 180 280 236 Z" fill="#3A3F4C"/>
<rect x="194" y="128" width="12" height="88" fill="#C9D0DC"/>
<rect x="200" y="128" width="6" height="88" fill="#8E97AA"/>
<rect x="172" y="118" width="56" height="10" fill="#F0B54A"/>
<rect x="194" y="118" width="12" height="10" fill="#7FB2E5"/>
<rect x="195" y="84" width="10" height="34" fill="#5A3E26"/>
<rect x="190" y="76" width="20" height="10" fill="#F0B54A"/>
</svg>`;

const URL_ESCENA = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(ESCENA)}`;

/** Dibuja la escena en un lienzo de 16 × 12: al agrandarlo con «pixelated» se ven los cuadritos. */
function FotoChiquita() {
  const lienzo = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const imagen = new Image();
    imagen.onload = () => {
      const contexto = lienzo.current?.getContext('2d');
      if (!contexto) return;
      contexto.imageSmoothingQuality = 'high';
      contexto.drawImage(imagen, 0, 0, 16, 12);
    };
    imagen.src = URL_ESCENA;
  }, []);
  return <canvas ref={lienzo} width={16} height={12} className="block aspect-[4/3] w-full [image-rendering:pixelated]" />;
}

const ETIQUETA = 'font-mono text-xs text-niebla md:text-[13px]';

/** Portada oscura: frase, botón y el dibujo de una foto chiquita y pixelada que pasa a ser grande y nítida. */
export default function Portada() {
  return (
    <section className="relative overflow-hidden bg-noche text-crema">
      {/* Cuadrícula de píxeles que se desvanece y brillo dorado detrás del dibujo. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-y-0 right-0 w-full md:w-3/5"
        style={{
          backgroundImage:
            'linear-gradient(#2a2e3b 1px, transparent 1px), linear-gradient(90deg, #2a2e3b 1px, transparent 1px)',
          backgroundSize: '40px 40px',
          maskImage: 'radial-gradient(circle at 55% 50%, black 0%, transparent 65%)',
          WebkitMaskImage: 'radial-gradient(circle at 55% 50%, black 0%, transparent 65%)',
        }}
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-y-0 right-0 w-full md:w-3/5"
        style={{ background: 'radial-gradient(circle at 60% 50%, rgb(240 181 74 / 0.16), transparent 55%)' }}
      />

      <div className="relative mx-auto flex w-full max-w-[1180px] flex-wrap items-center gap-12 px-4 pt-10 pb-20 md:px-6 md:pt-14 md:pb-28">
        <div className="flex min-w-0 flex-[1_1_480px] flex-col items-start gap-7">
          <p className="font-mono text-[13px] font-semibold tracking-[0.2em] text-acento uppercase">
            Métodos numéricos · Unillanos
          </p>
          <h1 className="font-display text-[60px] leading-[0.9] font-extrabold tracking-[-0.045em] md:text-[clamp(64px,8.5vw,120px)]">
            Hazla más <span className="text-acento">grande.</span>
          </h1>
          <p className="max-w-[480px] text-xl leading-8 text-niebla md:text-[22px]">
            Sube tu foto chiquita y sácala en HD, Full HD, 2K o 4K. <span className="text-crema">Así de simple.</span>
          </p>
          <a
            href="#app"
            className="inline-flex min-h-14 items-center rounded-full bg-acento px-7 text-lg font-bold text-tinta shadow-acento-2 transition-colors hover:bg-acento-hover focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-acento"
          >
            Agrandar una foto
          </a>
        </div>

        {/* Antes → después. Solo decoración: el texto de al lado ya dice lo mismo. */}
        <div aria-hidden="true" className="flex min-w-0 flex-[1_1_420px] items-center justify-center gap-4 md:gap-6">
          <figure className="flex w-[96px] flex-none flex-col items-center gap-2.5 md:w-[124px]">
            <div className="w-full overflow-hidden rounded-lg border border-noche-borde bg-noche-2 p-1.5">
              <div className="overflow-hidden rounded">
                <FotoChiquita />
              </div>
            </div>
            <figcaption className={ETIQUETA}>400×300</figcaption>
          </figure>

          <svg width="64" height="24" viewBox="0 0 64 24" fill="none" className="flex-none text-acento">
            <path d="M2 12h52" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeDasharray="2 7" />
            <path d="M46 3l11 9-11 9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>

          <figure className="flex max-w-[340px] min-w-0 flex-[1_1_auto] flex-col items-center gap-2.5">
            <div className="w-full rotate-2 overflow-hidden rounded-2xl border border-noche-borde bg-noche-2 p-2 shadow-[0_30px_80px_rgb(240_181_74/0.18)]">
              <img src={URL_ESCENA} alt="" className="block aspect-[4/3] w-full rounded-xl" />
            </div>
            <figcaption className={ETIQUETA}>
              <span className="text-acento">4K</span> · 2880×2160
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}
