import type { CSSProperties } from 'react';
import type { InfoImagen, OpcionResolucion, ResultadoReescalado } from '../tipos';
import Boton from './ui/Boton';
import ImagenConMarco from './ImagenConMarco';
import TituloPantalla from './ui/TituloPantalla';

interface ResultadoDescargaProps {
  infoImagen: InfoImagen;
  opcion: OpcionResolucion;
  resultado: ResultadoReescalado;
  urlVistaPrevia: string;
  urlResultado: string;
  alOtraImagen: () => void;
}

const TITULO_IMAGEN =
  'font-display text-xl leading-6 font-semibold tracking-[-0.02em] md:text-[22px] md:leading-[26px]';

/** Paso 3 terminado: original y reescalada a escala real, y el botón de descarga. */
export default function ResultadoDescarga({
  infoImagen,
  opcion,
  resultado,
  urlVistaPrevia,
  urlResultado,
  alOtraImagen,
}: ResultadoDescargaProps) {
  const nombreArchivo = `rescalibur_${opcion.clave}.png`;
  // Proporción del tamaño original respecto al nuevo: ambas imágenes se dibujan a la misma escala.
  const escala = infoImagen.ancho / resultado.ancho;
  const estilo = { '--esc': escala } as CSSProperties;

  return (
    <>
      <TituloPantalla
        titulo="Tu imagen está lista"
        subtitulo={`${infoImagen.nombre} · de ${infoImagen.ancho} × ${infoImagen.alto} a ${resultado.ancho} × ${resultado.alto} px`}
      />

      <div className="flex flex-col gap-5 md:flex-row md:items-start md:gap-6" style={estilo}>
        <figure className="flex flex-col gap-2.5 md:w-[calc((100%-1.5rem)/(1+var(--esc)))]">
          <ImagenConMarco
            src={urlResultado}
            ancho={resultado.ancho}
            alto={resultado.alto}
            alt={`Imagen reescalada a ${resultado.ancho} × ${resultado.alto}`}
          />
          <figcaption>
            <p className={TITULO_IMAGEN}>Reescalada</p>
            <p className="text-tinta-2">
              {resultado.ancho} × {resultado.alto} px
            </p>
          </figcaption>
        </figure>

        <figure className="flex w-[calc(100%*var(--esc))] flex-col gap-2.5 md:order-first md:w-[calc((100%-1.5rem)*var(--esc)/(1+var(--esc)))]">
          <ImagenConMarco
            src={urlVistaPrevia}
            ancho={infoImagen.ancho}
            alto={infoImagen.alto}
            alt={`Imagen original de ${infoImagen.ancho} × ${infoImagen.alto}`}
          />
          <figcaption>
            <p className={TITULO_IMAGEN}>Original</p>
            <p className="text-tinta-2">
              {infoImagen.ancho} × {infoImagen.alto} px
            </p>
          </figcaption>
        </figure>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-3 md:flex-row">
          <Boton href={urlResultado} download={nombreArchivo}>
            Descargar PNG
          </Boton>
          <Boton variante="secundario" onClick={alOtraImagen}>
            Reescalar otra imagen
          </Boton>
        </div>
        <p className="text-base leading-[22px] text-tinta-2">Se guardará como {nombreArchivo}</p>
      </div>
    </>
  );
}
