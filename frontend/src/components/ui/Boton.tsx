import type { ReactNode } from 'react';
import { clasesBoton } from './clasesBoton';
import type { VarianteBoton } from './clasesBoton';

interface BotonProps {
  variante?: VarianteBoton;
  children: ReactNode;
  onClick?: () => void;
  /** Si se indica, se dibuja como enlace (por ejemplo, para descargar un archivo). */
  href?: string;
  download?: string;
}

export default function Boton({ variante = 'primario', children, onClick, href, download }: BotonProps) {
  const clases = clasesBoton(variante);
  if (href && variante !== 'deshabilitado') {
    return (
      <a href={href} download={download} className={clases}>
        {children}
      </a>
    );
  }
  return (
    <button type="button" className={clases} onClick={onClick} disabled={variante === 'deshabilitado'}>
      {children}
    </button>
  );
}
