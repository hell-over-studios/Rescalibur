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
        <TituloPantalla titulo="¿Qué tan grande la quieres?" subtitulo={`${nombre} · ${ancho} × ${alto} px`} />
        <div className="flex flex-col gap-6 md:grid md:grid-cols-[1.65fr_1fr]">
          <ImagenConMarco src={urlVistaPrevia} ancho={ancho} alto={alto} alt={`Vista previa de ${nombre}`} />
          <div className="flex flex-col justify-center gap-3 rounded-2xl border-3 border-tinta bg-superficie p-6 shadow-duro md:p-7">
            <h3 className="font-display text-2xl leading-7 font-extrabold tracking-[-0.02em] md:text-[28px] md:leading-8">
              ¡Tu foto ya es más grande que 4K!
            </h3>
            <p className="text-base leading-[22px] font-medium">
              HD, Full HD, 2K y 4K son más pequeñas que {ancho} × {alto} px, así que no hace falta agrandarla.
            </p>
          </div>
        </div>
        <div>
          <Boton onClick={alCambiarImagen}>Subir otra foto</Boton>
        </div>
      </>
    );
  }

  const opcionElegida = opciones.find((opcion) => opcion.clave === claveSeleccionada) ?? opciones[0];

  return (
    <>
      <TituloPantalla
        titulo="¿Qué tan grande la quieres?"
        subtitulo={
          <>
            <span className="md:hidden">Cada rectángulo muestra cuánto crece tu foto.</span>
            <span className="hidden md:inline">
              Cada rectángulo muestra, a escala real, cuánto crece tu foto. No se estira ni se deforma.
            </span>
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
            <span className="font-extrabold break-all md:text-lg md:leading-6">{nombre}</span>
            <span className="font-medium">
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
              Agrandar a {opcionElegida.nombre}
              <span className="hidden md:inline">
                {' '}
                · {opcionElegida.ancho} × {opcionElegida.alto}
              </span>
            </span>
          </Boton>
          <Boton variante="secundario" onClick={alCambiarImagen}>
            Cambiar foto
          </Boton>
        </div>
        <p className="text-base leading-[22px] font-medium">
          Recibirás un PNG, sin pérdida de calidad por compresión.
        </p>
      </div>
    </>
  );
}
