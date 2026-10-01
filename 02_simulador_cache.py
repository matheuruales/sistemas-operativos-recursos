#!/usr/bin/env python3
"""Compara una lectura desde disco con lecturas posteriores desde una caché RAM."""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter


class CacheArchivos:
    def __init__(self) -> None:
        self._datos: dict[Path, bytes] = {}

    def leer(self, ruta: Path) -> tuple[bytes, str, float]:
        ruta = ruta.resolve()
        inicio = perf_counter()
        if ruta in self._datos:
            datos = self._datos[ruta]
            origen = "RAM (caché)"
        else:
            datos = ruta.read_bytes()
            self._datos[ruta] = datos
            origen = "disco"
        return datos, origen, perf_counter() - inicio


def crear_muestra(ruta: Path, megabytes: int) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    bloque = ("Sistemas operativos: ejemplo de jerarquía de memoria.\n" * 2048).encode()
    faltan = megabytes * 1024 * 1024
    with ruta.open("wb") as archivo:
        while faltan:
            parte = bloque[: min(faltan, len(bloque))]
            archivo.write(parte)
            faltan -= len(parte)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archivo", nargs="?", type=Path, default=Path("archivo_grande.txt"))
    parser.add_argument("--lecturas", type=int, default=3, help="Número total de lecturas.")
    parser.add_argument(
        "--crear-muestra-mb",
        type=int,
        metavar="MB",
        help="Crea/reemplaza el archivo de prueba con este tamaño (máximo 512 MB).",
    )
    args = parser.parse_args()
    if args.lecturas < 2:
        parser.error("usa al menos 2 lecturas para comparar disco y caché")
    if args.crear_muestra_mb is not None:
        if not 1 <= args.crear_muestra_mb <= 512:
            parser.error("el archivo de muestra debe tener entre 1 y 512 MB")
        crear_muestra(args.archivo, args.crear_muestra_mb)
        print(f"Muestra creada: {args.archivo.resolve()} ({args.crear_muestra_mb} MB)")
    if not args.archivo.is_file():
        parser.error("el archivo no existe; usa --crear-muestra-mb MB para crearlo")

    cache = CacheArchivos()
    tiempos: list[float] = []
    for numero in range(1, args.lecturas + 1):
        datos, origen, segundos = cache.leer(args.archivo)
        tiempos.append(segundos)
        print(
            f"Lectura {numero}: {origen:<12} | {len(datos) / 1024**2:8.2f} MiB | "
            f"{segundos * 1000:10.3f} ms"
        )

    promedio_cache = sum(tiempos[1:]) / len(tiempos[1:])
    if promedio_cache > 0:
        print(f"\nLa caché fue aproximadamente {tiempos[0] / promedio_cache:.1f}× más rápida.")


if __name__ == "__main__":
    main()
