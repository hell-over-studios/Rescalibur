import { useState } from 'react';

interface ImagenConMarcoProps {
  src: string;
  ancho: number;
  alto: number;
  alt: string;
}

/** Imagen que reserva su espacio con la proporción real. Si el navegador no puede mostrarla (p. ej. TIFF), deja un aviso. */
export default function ImagenConMarco({ src, ancho, alto, alt }: ImagenConMarcoProps) {
  const [fallo, setFallo] = useState(false);
  return (
    <div className="relative w-full bg-superficie" style={{ aspectRatio: `${ancho} / ${alto}` }}>
      {fallo ? (
        <p className="absolute inset-0 flex items-center justify-center p-2 text-center text-sm text-tinta-2">
          Sin vista previa
        </p>
      ) : (
        <img src={src} alt={alt} onError={() => setFallo(true)} className="absolute inset-0 size-full object-cover" />
      )}
    </div>
  );
}
