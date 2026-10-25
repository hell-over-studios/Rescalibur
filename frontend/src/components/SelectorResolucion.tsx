import type { OpcionResolucion as Opcion } from '../tipos';
import OpcionResolucion from './OpcionResolucion';

interface SelectorResolucionProps {
  /** Opciones calculadas por el backend: solo las mayores que la resolución actual. */
  opciones: Opcion[];
  /** Clave de la opción elegida, o null si aún no se elige ninguna. */
  claveSeleccionada: Opcion['clave'] | null;
  alSeleccionar: (clave: Opcion['clave']) => void;
}

/**
 * Paso 2 (HU-02): lista de resoluciones (HD, Full HD, 2K y 4K) con el tamaño final de cada una.
 * No hace cálculos: solo muestra lo que respondió la API.
 */
export default function SelectorResolucion({ opciones, claveSeleccionada, alSeleccionar }: SelectorResolucionProps) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="sr-only">Resolución final</legend>
      {opciones.map((opcion) => (
        <OpcionResolucion
          key={opcion.clave}
          opcion={opcion}
          seleccionada={opcion.clave === claveSeleccionada}
          alElegir={() => alSeleccionar(opcion.clave)}
        />
      ))}
    </fieldset>
  );
}
