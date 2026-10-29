import { useEffect, useRef, useState } from 'react';
import Cabecera from './components/Cabecera';
import CargadorImagen from './components/CargadorImagen';
import ElegirResolucion from './components/ElegirResolucion';
import Procesando from './components/Procesando';
import ResultadoDescarga from './components/ResultadoDescarga';
import { obtenerInfoImagen, reescalarImagen } from './services/api';
import type { InfoImagen, MensajeError, OpcionResolucion, Paso, ResultadoReescalado } from './tipos';

/** Etapas de la aplicación. Varias etapas comparten el mismo paso de la barra. */
type Etapa = 'cargar' | 'leyendo' | 'elegir' | 'procesando' | 'listo';

const PASO_DE_ETAPA: Record<Etapa, Paso> = {
  cargar: 1,
  leyendo: 1,
  elegir: 2,
  procesando: 3,
  listo: 3,
};

/** Convierte cualquier error en un texto para el usuario. */
function textoDeError(error: unknown): string {
  return error instanceof Error ? error.message : 'Ocurrió un error inesperado.';
}

/**
 * Componente raíz: guarda el estado general y decide qué paso mostrar.
 * Paso 1: cargar (HU-01) → Paso 2: elegir resolución (HU-02) → Paso 3: reescalar y descargar (HU-05).
 * No hace cálculos: todo lo que se muestra viene de la API.
 */
export default function App() {
  const [etapa, setEtapa] = useState<Etapa>('cargar');
  const [archivo, setArchivo] = useState<File | null>(null);
  const [urlVistaPrevia, setUrlVistaPrevia] = useState<string | null>(null);
  const [infoImagen, setInfoImagen] = useState<InfoImagen | null>(null);
  const [claveResolucion, setClaveResolucion] = useState<OpcionResolucion['clave'] | null>(null);
  const [resultado, setResultado] = useState<ResultadoReescalado | null>(null);
  const [urlResultado, setUrlResultado] = useState<string | null>(null);
  const [error, setError] = useState<MensajeError | null>(null);

  // Cada petición recibe un número. Si el usuario reinicia mientras el servidor responde, la respuesta vieja se ignora.
  const numeroPeticion = useRef(0);

  // Libera las URL temporales cuando cambian o al cerrar la página, para no gastar memoria.
  useEffect(() => {
    return () => {
      if (urlVistaPrevia) URL.revokeObjectURL(urlVistaPrevia);
    };
  }, [urlVistaPrevia]);

  useEffect(() => {
    return () => {
      if (urlResultado) URL.revokeObjectURL(urlResultado);
    };
  }, [urlResultado]);

  const manejarArchivo = async (nuevoArchivo: File) => {
    const peticion = ++numeroPeticion.current;
    setError(null);
    setEtapa('leyendo');
    try {
      const info = await obtenerInfoImagen(nuevoArchivo);
      if (peticion !== numeroPeticion.current) return;
      setArchivo(nuevoArchivo);
      setInfoImagen(info);
      setUrlVistaPrevia(URL.createObjectURL(nuevoArchivo));
      // Se preselecciona la primera opción disponible.
      setClaveResolucion(info.opciones[0]?.clave ?? null);
      setEtapa('elegir');
    } catch (errorApi) {
      if (peticion !== numeroPeticion.current) return;
      setError({ titulo: `No pudimos cargar «${nuevoArchivo.name}»`, mensaje: textoDeError(errorApi) });
      setEtapa('cargar');
    }
  };

  const manejarReescalar = async (opcion: OpcionResolucion) => {
    if (!archivo) return;
    const peticion = ++numeroPeticion.current;
    setError(null);
    setClaveResolucion(opcion.clave);
    setEtapa('procesando');
    try {
      const respuesta = await reescalarImagen(archivo, opcion);
      if (peticion !== numeroPeticion.current) return;
      setResultado(respuesta);
      setUrlResultado(URL.createObjectURL(respuesta.imagen));
      setEtapa('listo');
    } catch (errorApi) {
      if (peticion !== numeroPeticion.current) return;
      setError({ titulo: 'No pudimos reescalar tu imagen', mensaje: textoDeError(errorApi) });
      setEtapa('elegir');
    }
  };

  const manejarReinicio = () => {
    numeroPeticion.current += 1;
    setEtapa('cargar');
    setArchivo(null);
    setUrlVistaPrevia(null);
    setInfoImagen(null);
    setClaveResolucion(null);
    setResultado(null);
    setUrlResultado(null);
    setError(null);
  };

  const opcionElegida = infoImagen?.opciones.find((opcion) => opcion.clave === claveResolucion);

  return (
    <div className="mx-auto flex w-full max-w-[860px] flex-col gap-6 px-4 pt-6 pb-10 md:gap-10 md:px-6 md:pt-10 md:pb-24">
      <Cabecera paso={PASO_DE_ETAPA[etapa]} />

      {(etapa === 'cargar' || etapa === 'leyendo') && (
        <CargadorImagen alSeleccionarArchivo={manejarArchivo} deshabilitado={etapa === 'leyendo'} error={error} />
      )}

      {etapa === 'elegir' && infoImagen && urlVistaPrevia && (
        <ElegirResolucion
          infoImagen={infoImagen}
          urlVistaPrevia={urlVistaPrevia}
          claveSeleccionada={claveResolucion}
          alSeleccionar={setClaveResolucion}
          error={error}
          alReescalar={manejarReescalar}
          alCambiarImagen={manejarReinicio}
        />
      )}

      {etapa === 'procesando' && infoImagen && opcionElegida && urlVistaPrevia && (
        <Procesando infoImagen={infoImagen} opcion={opcionElegida} urlVistaPrevia={urlVistaPrevia} />
      )}

      {etapa === 'listo' && infoImagen && opcionElegida && resultado && urlVistaPrevia && urlResultado && (
        <ResultadoDescarga
          infoImagen={infoImagen}
          opcion={opcionElegida}
          resultado={resultado}
          urlVistaPrevia={urlVistaPrevia}
          urlResultado={urlResultado}
          alOtraImagen={manejarReinicio}
        />
      )}
    </div>
  );
}
