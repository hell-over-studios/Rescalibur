"""Estudio comparativo de los tres métodos de interpolación (HU-11).

Se ejecuta desde backend/ y no necesita el servidor encendido:
    python -m estudio.comparativo

Tiempos (T31): cada imagen de estudio/imagenes/ se lleva a HD, Full HD, 2K y 4K con cada método.
Cada combinación se mide 5 veces y se reporta la mediana. Como en la API (X-Tiempo-Ms), se mide
solo la interpolación: sin leer la imagen ni codificar el PNG.

Calidad (T32): cada imagen se reduce ×2, ×3 y ×4 con INTER_AREA y se amplía de vuelta a su tamaño
original con cada método. Como la imagen original se conoce, se puede medir qué tan parecida
quedó con el PSNR (psnr() en app/metricas.py).

Salidas en estudio/resultados/: resultados.csv (tiempos), calidad.csv (PSNR) y estudio_comparativo.pdf.
"""

import csv
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from app.config import METODOS_DISPONIBLES
from app.metodos.base import MetodoInterpolacion
from app.metricas import BYTES_POR_KB, DECIMALES_TAMANO, DECIMALES_TIEMPO, Registro, psnr
from app.procesador import FORMATOS_ACEPTADOS, ProcesadorImagen
from app.reporte import GeneradorReportePDF
from app.resoluciones import RESOLUCIONES, CalculadoraResolucion

CARPETA_IMAGENES = Path(__file__).parent / "imagenes"
CARPETA_RESULTADOS = Path(__file__).parent / "resultados"
NOMBRE_CSV_TIEMPOS = "resultados.csv"
NOMBRE_CSV_CALIDAD = "calidad.csv"
NOMBRE_PDF = "estudio_comparativo.pdf"
TITULO_PDF = "Rescalibur · Estudio comparativo"

MINIMO_IMAGENES = 3  # Fotografía, texto/bordes e ilustración
REPETICIONES = 5  # La mediana de 5 mediciones descarta un tiempo atípico (por ejemplo, el primero)
FACTORES_REDUCCION = (2, 3, 4)
MILISEGUNDOS_POR_SEGUNDO = 1000
DECIMALES_PSNR = 2


@dataclass(frozen=True)
class MedicionTiempo:
    """Tiempo de un método al llevar una imagen a una resolución (mediana de las repeticiones)."""

    imagen: str
    ancho_original: int
    alto_original: int
    resolucion: str  # Clave de la HU-02: hd, fullhd, 2k o 4k
    ancho_final: int
    alto_final: int
    metodo: str
    tiempo_ms: float  # Mediana de REPETICIONES mediciones
    tamano_kb: float  # Tamaño que tendría el PNG de la imagen ampliada


@dataclass(frozen=True)
class MedicionCalidad:
    """PSNR de un método al ampliar de vuelta una imagen que se redujo `factor` veces."""

    imagen: str
    factor: int  # 2, 3 o 4
    metodo: str
    psnr_db: float  # Infinito si la imagen ampliada es idéntica a la original


# --- Imágenes ---


def listar_imagenes(carpeta: Path = CARPETA_IMAGENES) -> list[Path]:
    """Imágenes de la carpeta (por extensión), en orden alfabético.

    Lanza ValueError si hay menos de MINIMO_IMAGENES. Los demás archivos (LEEME.md) se ignoran.
    """
    imagenes = sorted(
        ruta for ruta in carpeta.glob("*") if ruta.is_file() and ruta.suffix.lower() in FORMATOS_ACEPTADOS
    )
    if len(imagenes) < MINIMO_IMAGENES:
        raise ValueError(
            f"El estudio necesita al menos {MINIMO_IMAGENES} imágenes en {carpeta} y hay {len(imagenes)}."
        )
    return imagenes


# --- Tiempos (T31) ---


def medir_mediana_ms(
    metodo: MetodoInterpolacion,
    matriz: np.ndarray,
    nuevo_ancho: int,
    nuevo_alto: int,
    repeticiones: int = REPETICIONES,
) -> float:
    """Reescala la imagen `repeticiones` veces y devuelve la mediana del tiempo en milisegundos."""
    tiempos_ms = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        metodo.reescalar(matriz, nuevo_ancho, nuevo_alto)
        tiempos_ms.append((time.perf_counter() - inicio) * MILISEGUNDOS_POR_SEGUNDO)
    return statistics.median(tiempos_ms)


def medir_tiempos(
    carpeta: Path = CARPETA_IMAGENES,
    metodos: dict[str, type[MetodoInterpolacion]] = METODOS_DISPONIBLES,
    repeticiones: int = REPETICIONES,
) -> list[MedicionTiempo]:
    """Mide cada método en cada resolución para cada imagen de la carpeta.

    El orden es: imagen (alfabético) -> resolución (HD a 4K) -> método (el de METODOS_DISPONIBLES).
    Las dimensiones finales salen de CalculadoraResolucion, las mismas que usa la API (HU-02).
    Lanza ValueError si una imagen no se puede ampliar a alguna de las cuatro resoluciones.
    """
    procesador = ProcesadorImagen()
    calculadora = CalculadoraResolucion()
    mediciones = []

    for ruta in listar_imagenes(carpeta):
        matriz = procesador.leer(ruta.read_bytes())
        alto, ancho = matriz.shape[:2]

        for resolucion in RESOLUCIONES:
            try:
                nuevo_ancho, nuevo_alto = calculadora.calcular_dimensiones(ancho, alto, resolucion.clave)
            except ValueError as error:
                raise ValueError(f"{ruta.name} ({ancho} x {alto}): {error}") from error

            for nombre, clase in metodos.items():
                metodo = clase()
                mediana_ms = medir_mediana_ms(metodo, matriz, nuevo_ancho, nuevo_alto, repeticiones)
                # Un reescalado más, fuera de la medición, solo para saber cuánto pesaría el PNG.
                png = procesador.codificar_png(metodo.reescalar(matriz, nuevo_ancho, nuevo_alto))
                mediciones.append(
                    MedicionTiempo(
                        imagen=ruta.name,
                        ancho_original=ancho,
                        alto_original=alto,
                        resolucion=resolucion.clave,
                        ancho_final=nuevo_ancho,
                        alto_final=nuevo_alto,
                        metodo=nombre,
                        tiempo_ms=mediana_ms,
                        tamano_kb=len(png) / BYTES_POR_KB,
                    )
                )
    return mediciones


# --- Calidad (T32) ---


def reducir(matriz: np.ndarray, factor: int) -> np.ndarray:
    """Reduce la imagen `factor` veces por lado con INTER_AREA (promedio de los píxeles cubiertos).

    Lanza ValueError si la imagen es tan pequeña que quedaría sin píxeles.
    """
    alto, ancho = matriz.shape[:2]
    nuevo_ancho, nuevo_alto = ancho // factor, alto // factor
    if nuevo_ancho < 1 or nuevo_alto < 1:
        raise ValueError(f"La imagen de {ancho} x {alto} es muy pequeña para reducirla x{factor}.")
    return cv2.resize(matriz, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)


def medir_calidad(
    carpeta: Path = CARPETA_IMAGENES,
    metodos: dict[str, type[MetodoInterpolacion]] = METODOS_DISPONIBLES,
    factores: tuple[int, ...] = FACTORES_REDUCCION,
) -> list[MedicionCalidad]:
    """PSNR de cada método al ampliar de vuelta cada imagen reducida.

    Para cada imagen y cada factor: se reduce con INTER_AREA, se amplía al tamaño original con el
    método y se compara con la imagen original. El orden es imagen -> factor -> método.
    Lanza ValueError si una imagen es muy pequeña para reducirla.
    """
    procesador = ProcesadorImagen()
    mediciones = []

    for ruta in listar_imagenes(carpeta):
        original = procesador.leer(ruta.read_bytes())
        alto, ancho = original.shape[:2]

        for factor in factores:
            try:
                reducida = reducir(original, factor)
            except ValueError as error:
                raise ValueError(f"{ruta.name}: {error}") from error

            for nombre, clase in metodos.items():
                ampliada = clase().reescalar(reducida, ancho, alto)
                mediciones.append(
                    MedicionCalidad(
                        imagen=ruta.name, factor=factor, metodo=nombre, psnr_db=psnr(original, ampliada)
                    )
                )
    return mediciones


# --- Salidas ---


def escribir_csv_tiempos(mediciones: list[MedicionTiempo], ruta: Path) -> None:
    """Escribe resultados.csv: una fila por imagen, resolución y método (CP-28)."""
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            [
                "imagen",
                "ancho_original",
                "alto_original",
                "resolucion",
                "ancho_final",
                "alto_final",
                "metodo",
                "tiempo_ms",
                "tamano_kb",
            ]
        )
        for m in mediciones:
            escritor.writerow(
                [
                    m.imagen,
                    m.ancho_original,
                    m.alto_original,
                    m.resolucion,
                    m.ancho_final,
                    m.alto_final,
                    m.metodo,
                    round(m.tiempo_ms, DECIMALES_TIEMPO),
                    round(m.tamano_kb, DECIMALES_TAMANO),
                ]
            )


def escribir_csv_calidad(mediciones: list[MedicionCalidad], ruta: Path) -> None:
    """Escribe calidad.csv: una fila por imagen, factor de reducción y método."""
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["imagen", "factor", "metodo", "psnr_db"])
        for m in mediciones:
            escritor.writerow([m.imagen, m.factor, m.metodo, round(m.psnr_db, DECIMALES_PSNR)])


def escribir_pdf(tiempos: list[MedicionTiempo], calidad: list[MedicionCalidad], ruta: Path) -> None:
    """Escribe estudio_comparativo.pdf con GeneradorReportePDF (HU-10): tiempos y calidad."""
    fecha = datetime.now()
    registros = [
        Registro(
            fecha=fecha,
            archivo=m.imagen,
            metodo=m.metodo,
            ancho_original=m.ancho_original,
            alto_original=m.alto_original,
            ancho_final=m.ancho_final,
            alto_final=m.alto_final,
            resolucion=m.resolucion,
            tiempo_ms=m.tiempo_ms,
            tamano_kb=m.tamano_kb,
        )
        for m in tiempos
    ]
    pdf = GeneradorReportePDF().generar(registros, titulo=TITULO_PDF, calidad=calidad)
    ruta.write_bytes(bytes(pdf))  # fpdf2 entrega un bytearray


def ejecutar_estudio(
    carpeta_imagenes: Path = CARPETA_IMAGENES,
    carpeta_resultados: Path = CARPETA_RESULTADOS,
    metodos: dict[str, type[MetodoInterpolacion]] = METODOS_DISPONIBLES,
    repeticiones: int = REPETICIONES,
) -> tuple[list[MedicionTiempo], list[MedicionCalidad]]:
    """Mide tiempos y calidad y escribe resultados.csv, calidad.csv y estudio_comparativo.pdf.

    Crea la carpeta de resultados si no existe. Devuelve las mediciones por si se quieren usar.
    """
    tiempos = medir_tiempos(carpeta_imagenes, metodos, repeticiones)
    calidad = medir_calidad(carpeta_imagenes, metodos)

    carpeta_resultados.mkdir(parents=True, exist_ok=True)
    escribir_csv_tiempos(tiempos, carpeta_resultados / NOMBRE_CSV_TIEMPOS)
    escribir_csv_calidad(calidad, carpeta_resultados / NOMBRE_CSV_CALIDAD)
    escribir_pdf(tiempos, calidad, carpeta_resultados / NOMBRE_PDF)
    return tiempos, calidad


# --- Salida en la terminal ---


def imprimir_tabla(mediciones: list[MedicionTiempo]) -> None:
    """Muestra los tiempos en la terminal, una fila por imagen, resolución y método."""
    print(f"{'Imagen':<18}{'Original':<11}{'Res.':<8}{'Final':<12}{'Método':<10}{'Mediana (ms)':>13}")
    for medicion in mediciones:
        original = f"{medicion.ancho_original}x{medicion.alto_original}"
        final = f"{medicion.ancho_final}x{medicion.alto_final}"
        print(
            f"{medicion.imagen:<18}{original:<11}{medicion.resolucion:<8}{final:<12}"
            f"{medicion.metodo:<10}{medicion.tiempo_ms:>13.1f}"
        )


def imprimir_calidad(mediciones: list[MedicionCalidad]) -> None:
    """Muestra el PSNR en la terminal, una fila por imagen, factor de reducción y método."""
    print(f"{'Imagen':<18}{'Reducción':<11}{'Método':<10}{'PSNR (dB)':>10}")
    for medicion in mediciones:
        print(
            f"{medicion.imagen:<18}{'x' + str(medicion.factor):<11}{medicion.metodo:<10}"
            f"{medicion.psnr_db:>10.2f}"
        )


def main() -> None:
    print(f"Midiendo tiempos (mediana de {REPETICIONES}) y calidad de las imágenes de estudio/imagenes/ ...")
    tiempos, calidad = ejecutar_estudio()
    imprimir_tabla(tiempos)
    print()
    imprimir_calidad(calidad)
    print(f"\nResultados guardados en {CARPETA_RESULTADOS}")


if __name__ == "__main__":
    main()
