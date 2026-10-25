import { useEffect, useState } from 'react';
import CargadorImagen from './components/CargadorImagen';
import SelectorResolucion from './components/SelectorResolucion';
import { obtenerInfoImagen } from './services/api';
import type { InfoImagen, OpcionResolucion } from './tipos';

/**
 * Componente raíz: guarda el estado general y decide qué paso mostrar.
 * Paso 1: cargar (HU-01) → Paso 2: elegir resolución (HU-02) → Paso 3: descargar (HU-05, pendiente).
 */
export default function App() {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [urlVistaPrevia, setUrlVistaPrevia] = useState<string | null>(null);
  const [infoImagen, setInfoImagen] = useState<InfoImagen | null>(null);
  const [claveResolucion, setClaveResolucion] = useState<OpcionResolucion['clave'] | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [vistaPreviaFallo, setVistaPreviaFallo] = useState(false);

  // Libera la URL temporal de la vista previa cuando cambia la imagen, para no gastar memoria.
  useEffect(() => {
    return () => {
      if (urlVistaPrevia) URL.revokeObjectURL(urlVistaPrevia);
    };
  }, [urlVistaPrevia]);

  const manejarArchivo = async (nuevoArchivo: File) => {
    setArchivo(nuevoArchivo);
    setUrlVistaPrevia(URL.createObjectURL(nuevoArchivo));
    setVistaPreviaFallo(false);
    setInfoImagen(null);
    setClaveResolucion(null);
    setError(null);
    setCargando(true);
    try {
      const info = await obtenerInfoImagen(nuevoArchivo);
      setInfoImagen(info);
      // Se preselecciona la primera opción disponible.
      setClaveResolucion(info.opciones[0]?.clave ?? null);
    } catch (errorApi) {
      setError(errorApi instanceof Error ? errorApi.message : 'Ocurrió un error inesperado.');
    } finally {
      setCargando(false);
    }
  };

  const manejarReinicio = () => {
    setArchivo(null);
    setUrlVistaPrevia(null);
    setInfoImagen(null);
    setClaveResolucion(null);
    setError(null);
  };

  const opcionElegida = infoImagen?.opciones.find((opcion) => opcion.clave === claveResolucion);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-4 py-3 md:px-8">
        <h1 className="text-xl font-bold text-indigo-700">
          Rescalibur
          <span className="ml-2 text-sm font-normal text-slate-700">Reescalador por métodos numéricos</span>
        </h1>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-6">
        {!archivo && <CargadorImagen alSeleccionarArchivo={manejarArchivo} deshabilitado={cargando} />}

        {archivo && (
          <section className="rounded-2xl border border-slate-200 bg-white p-4 md:p-6">
            <h2 className="text-lg font-bold">Elige la resolución de salida</h2>
            <p className="mb-4 text-sm text-slate-500">
              Solo se muestran las resoluciones mayores que la de tu imagen. Se conserva la proporción.
            </p>

            <div className="flex flex-col gap-6 md:flex-row">
              <div className="md:w-64">
                {/* Algunos navegadores no muestran TIFF; en ese caso se oculta la vista previa. */}
                {urlVistaPrevia && !vistaPreviaFallo && (
                  <img
                    src={urlVistaPrevia}
                    alt={`Vista previa de ${archivo.name}`}
                    onError={() => setVistaPreviaFallo(true)}
                    className="h-auto max-w-full rounded-lg border border-slate-200"
                  />
                )}
                <p className="mt-2 text-sm font-bold break-all">{archivo.name}</p>
                {infoImagen && (
                  <p className="text-sm">
                    Resolución actual: <strong>{infoImagen.ancho} × {infoImagen.alto} px</strong>
                  </p>
                )}
              </div>

              <div className="flex-1">
                {cargando && <p className="text-sm text-slate-500">Analizando la imagen…</p>}

                {error && (
                  <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                    {error}
                  </p>
                )}

                {infoImagen && (
                  <SelectorResolucion
                    opciones={infoImagen.opciones}
                    claveSeleccionada={claveResolucion}
                    alSeleccionar={setClaveResolucion}
                  />
                )}

                <div className="mt-6 flex flex-col gap-3 md:flex-row">
                  {/* El reescalado se conecta en HU-05 (T13 y T14). */}
                  <button
                    type="button"
                    disabled={!opcionElegida}
                    className="rounded-lg bg-indigo-700 px-5 py-3 font-bold text-white disabled:opacity-50"
                  >
                    {opcionElegida ? `Reescalar a ${opcionElegida.nombre}` : 'Reescalar'}
                  </button>
                  <button
                    type="button"
                    onClick={manejarReinicio}
                    className="rounded-lg border border-indigo-200 bg-white px-5 py-3 font-bold text-indigo-700"
                  >
                    Cambiar imagen
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
