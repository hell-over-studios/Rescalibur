import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

interface TituloPantallaProps {
  titulo: string;
  subtitulo?: ReactNode;
}

/**
 * Título de cada paso. Es un h2 porque el h1 de la página está en la portada.
 * Al aparecer recibe el foco para que los lectores de pantalla anuncien el cambio de paso.
 */
export default function TituloPantalla({ titulo, subtitulo }: TituloPantallaProps) {
  const ref = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    ref.current?.focus({ preventScroll: true });
  }, []);

  return (
    <header className="flex flex-col gap-1.5 md:gap-2">
      <h2
        ref={ref}
        tabIndex={-1}
        className="font-display text-[28px] leading-8 font-extrabold tracking-[-0.03em] outline-none md:text-[34px] md:leading-[38px]"
      >
        {titulo}
      </h2>
      {subtitulo && <p className="text-base leading-[22px] font-medium md:text-lg md:leading-[26px]">{subtitulo}</p>}
    </header>
  );
}
