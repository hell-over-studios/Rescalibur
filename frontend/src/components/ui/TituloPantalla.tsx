import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

interface TituloPantallaProps {
  titulo: string;
  subtitulo?: ReactNode;
}

/** Título de cada pantalla. Al aparecer recibe el foco para que los lectores de pantalla anuncien el cambio de paso. */
export default function TituloPantalla({ titulo, subtitulo }: TituloPantallaProps) {
  const ref = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    ref.current?.focus({ preventScroll: true });
  }, []);

  return (
    <header className="flex flex-col gap-2 md:gap-3">
      <h1
        ref={ref}
        tabIndex={-1}
        className="font-display text-[32px] leading-9 font-semibold tracking-[-0.03em] outline-none md:text-[44px] md:leading-12"
      >
        {titulo}
      </h1>
      {subtitulo && <p className="text-base leading-[22px] text-tinta-2 md:text-lg md:leading-[26px]">{subtitulo}</p>}
    </header>
  );
}
