import type { OpcionResolucion } from '../tipos';

interface SelectorResolucionProps {
  /** Opciones calculadas por el backend: solo las mayores que la resolución actual. */
  opciones: OpcionResolucion[];
  /** Clave de la opción elegida, o null si aún no se elige ninguna. */
  claveSeleccionada: OpcionResolucion['clave'] | null;
  alSeleccionar: (clave: OpcionResolucion['clave']) => void;
}

/**
 * Paso 2 (HU-02): muestra HD, Full HD, 2K y 4K con la resolución final de cada una.
 * No hace cálculos: solo muestra lo que respondió la API.
 */
export default function SelectorResolucion({ opciones, claveSeleccionada, alSeleccionar }: SelectorResolucionProps) {
  if (opciones.length === 0) {
    return (
      <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
        Tu imagen ya supera todas las resoluciones disponibles.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {opciones.map((opcion) => {
        const seleccionada = opcion.clave === claveSeleccionada;
        return (
          <button
            key={opcion.clave}
            type="button"
            onClick={() => alSeleccionar(opcion.clave)}
            aria-pressed={seleccionada}
            className={`rounded-xl border px-4 py-3 text-left transition-colors ${
              seleccionada ? 'border-2 border-indigo-700 bg-indigo-50' : 'border-slate-200 bg-white hover:border-indigo-300'
            }`}
          >
            <span className="block font-bold text-slate-900">{opcion.nombre}</span>
            <span className="block text-xs text-slate-500">
              Resultado: {opcion.ancho} × {opcion.alto} px
            </span>
          </button>
        );
      })}
    </div>
  );
}
