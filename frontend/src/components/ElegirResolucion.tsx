import type { InfoImagen, MensajeError, OpcionResolucion } from '../tipos';
import AvisoError from './ui/AvisoError';
import Boton from './ui/Boton';
import TituloPantalla from './ui/TituloPantalla';
import DiagramaEscala from './DiagramaEscala';
import ImagenConMarco from './ImagenConMarco';
import SelectorResolucion from './SelectorResolucion';

interface ElegirResolucionProps {
  infoImagen: InfoImagen;
  urlVistaPrevia: string;
  claveSeleccionada: OpcionResolucion['clave'] | null;
  alSeleccionar: (clave: OpcionResolucion['clave']) => void;
  /** Error al reescalar, si el intento anterior falló. */
  error: MensajeError | null;
  alReescalar: (opcion: OpcionResolucion) => void;
  alCambiarImagen: () => void;
}

/**
 * Pantalla del paso 2 (HU-02): diagrama a escala, lista de resoluciones y botones.
 * El frontend solo muestra lo que calculó la API (infoImagen.opciones); no calcula resoluciones.
 */
export default function ElegirResolucion({
  infoImagen,
  urlVistaPrevia,
  claveSeleccionada,
  alSeleccionar,
  error,
  alReescalar,
  alCambiarImagen,
}: ElegirResolucionProps) {
  const { nombre, ancho, alto, opciones } = infoImagen;

  // Imagen que ya supera todas las resoluciones: no hay nada que ampliar.
  if (opciones.length === 0) {
    return (
      <>
        <TituloPantalla titulo="Elige la resolución" subtitulo={`${nombre} · ${ancho} × ${alto} px`} />
        <div className="flex flex-col gap-6 md:grid md:grid-cols-[1.65fr_1fr]">
          <ImagenConMarco src={urlVistaPrevia} ancho={ancho} alto={alto} alt={`Vista previa de ${nombre}`} />
          <div className="flex flex-col justify-center gap-3 bg-superficie p-6 md:p-7">
            <h2 className="font-display text-2xl leading-7 font-semibold tracking-[-0.02em] md:text-[28px] md:leading-8">
              Tu imagen ya supera todas las resoluciones disponibles
            </h2>
            <p className="text-base leading-[22px] text-tinta-2">
              HD, Full HD, 2K y 4K son más pequeñas que {ancho} × {alto} px, así que no hay nada que ampliar.
            </p>
          </div>
        </div>
        <div>
          <Boton onClick={alCambiarImagen}>Cargar otra imagen</Boton>
        </div>
      </>
    );
  }

  const opcionElegida = opciones.find((opcion) => opcion.clave === claveSeleccionada) ?? opciones[0];

  return (
    <>
      <TituloPantalla
        titulo="Elige la resolución"
        subtitulo={
          <>
            <span className="md:hidden">Cada rectángulo muestra cuánto crece tu imagen.</span>
            <span className="hidden md:inline">Cada rectángulo muestra, a escala real, cuánto crece tu imagen.</span>
          </>
        }
      />

      {error && <AvisoError {...error} />}

      <div className="flex flex-col gap-6 md:grid md:grid-cols-[1.65fr_1fr] md:items-start">
        <DiagramaEscala
          infoImagen={infoImagen}
          claveSeleccionada={opcionElegida.clave}
          urlVistaPrevia={urlVistaPrevia}
        />

        <div className="flex flex-col gap-2">
          <p className="flex flex-wrap gap-x-2 md:flex-col md:gap-x-0 md:gap-y-0.5 md:pb-2">
            <span className="font-medium break-all md:text-lg md:leading-6">{nombre}</span>
            <span className="text-tinta-2">
              {ancho} × {alto} px
            </span>
          </p>
          <SelectorResolucion
            opciones={opciones}
            claveSeleccionada={opcionElegida.clave}
            alSeleccionar={alSeleccionar}
          />
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-3 md:flex-row">
          <Boton onClick={() => alReescalar(opcionElegida)}>
            {/* Un solo <span> para que el botón (flex) no recorte el espacio antes del «·». */}
            <span>
              Reescalar a {opcionElegida.nombre}
              <span className="hidden md:inline">
                {' '}
                · {opcionElegida.ancho} × {opcionElegida.alto}
              </span>
            </span>
          </Boton>
          <Boton variante="secundario" onClick={alCambiarImagen}>
            Cambiar imagen
          </Boton>
        </div>
        <p className="text-base leading-[22px] text-tinta-2">
          Recibirás un PNG, sin pérdida de calidad por compresión.
        </p>
      </div>
    </>
  );
}
