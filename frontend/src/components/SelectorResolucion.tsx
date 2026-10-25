// Paso 2 del flujo (HU-02): muestra las resoluciones que la imagen permite.
// El componente NO calcula nada: solo pinta lo que respondió /api/imagen/info.

export interface OpcionResolucion {
  clave: string;
  nombre: string;
  ancho: number;
  alto: number;
}

interface SelectorResolucionProps {
  urlVistaPrevia: string;
  nombreArchivo: string;
  anchoOriginal: number;
  altoOriginal: number;
  opciones: OpcionResolucion[];
  claveSeleccionada: string | null;
  procesando: boolean;
  alSeleccionar: (clave: string) => void;
  alReescalar: () => void;
  alCambiarImagen: () => void;
}

const MENSAJE_SIN_OPCIONES = 'Tu imagen ya supera todas las resoluciones disponibles';

function SelectorResolucion({
  urlVistaPrevia,
  nombreArchivo,
  anchoOriginal,
  altoOriginal,
  opciones,
  claveSeleccionada,
  procesando,
  alSeleccionar,
  alReescalar,
  alCambiarImagen,
}: SelectorResolucionProps) {
  const hayOpciones = opciones.length > 0;

  return (
    <section className="flex flex-col gap-6 md:flex-row">
      {/* Vista previa y datos de la imagen original */}
      <div className="md:w-1/2">
        <img
          src={urlVistaPrevia}
          alt={`Vista previa de ${nombreArchivo}`}
          className="h-auto max-w-full rounded-xl border border-gray-200"
        />
        <p className="mt-3 truncate font-medium text-gray-800">{nombreArchivo}</p>
        <p className="text-sm text-gray-500">
          Resolución actual: {anchoOriginal} × {altoOriginal} px
        </p>
      </div>

      {/* Opciones de resolución */}
      <div className="flex flex-col gap-4 md:w-1/2">
        <h2 className="text-lg font-semibold text-gray-800">Elige la resolución</h2>

        {hayOpciones ? (
          <div className="grid grid-cols-2 gap-3" role="radiogroup" aria-label="Resoluciones disponibles">
            {opciones.map((opcion) => {
              const elegida = opcion.clave === claveSeleccionada;
              return (
                <button
                  key={opcion.clave}
                  type="button"
                  role="radio"
                  aria-checked={elegida}
                  disabled={procesando}
                  onClick={() => alSeleccionar(opcion.clave)}
                  className={`rounded-xl border-2 p-4 text-left transition ${
                    elegida
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-indigo-300'
                  } disabled:opacity-50`}
                >
                  <span className="block font-semibold text-gray-800">{opcion.nombre}</span>
                  <span className="block text-sm text-gray-500">
                    {opcion.ancho} × {opcion.alto} px
                  </span>
                </button>
              );
            })}
          </div>
        ) : (
          <p className="rounded-xl bg-amber-50 p-4 text-amber-800">{MENSAJE_SIN_OPCIONES}</p>
        )}

        <div className="flex flex-col gap-3 sm:flex-row">
          {hayOpciones && (
            <button
              type="button"
              disabled={!claveSeleccionada || procesando}
              onClick={alReescalar}
              className="w-full rounded-xl bg-indigo-600 py-3 font-semibold text-white disabled:opacity-50 sm:w-auto sm:px-6"
            >
              {procesando ? 'Reescalando…' : 'Reescalar'}
            </button>
          )}
          <button
            type="button"
            disabled={procesando}
            onClick={alCambiarImagen}
            className="w-full rounded-xl border border-gray-300 py-3 font-medium text-gray-700 disabled:opacity-50 sm:w-auto sm:px-6"
          >
            Cambiar imagen
          </button>
        </div>
      </div>
    </section>
  );
}

export default SelectorResolucion;