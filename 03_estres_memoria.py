#!/usr/bin/env python3
"""Reserva memoria gradualmente y se detiene antes de poner en riesgo el equipo."""

from __future__ import annotations

import argparse
import os
import time

import psutil


def mib(bytes_: int) -> float:
    return bytes_ / 1024**2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite-mb", type=int, default=512, help="RAM máxima del proceso.")
    parser.add_argument("--reserva-sistema", type=float, default=20.0, help="RAM disponible mínima, en %%.")
    parser.add_argument("--duracion", type=int, default=120, help="Duración máxima en segundos.")
    parser.add_argument("--lote", type=int, default=10_000, help="Strings creados antes de cada revisión.")
    parser.add_argument(
        "--mantener",
        type=int,
        default=0,
        metavar="SEGUNDOS",
        help="Conserva los objetos en RAM antes de salir (máximo 300 segundos).",
    )
    args = parser.parse_args()
    if not 32 <= args.limite_mb <= 4096:
        parser.error("--limite-mb debe estar entre 32 y 4096")
    if not 10 <= args.reserva_sistema <= 90 or args.duracion < 1 or args.lote < 100:
        parser.error("reserva: 10-90; duración >= 1; lote >= 100")
    if not 0 <= args.mantener <= 300:
        parser.error("--mantener debe estar entre 0 y 300 segundos")

    proceso = psutil.Process(os.getpid())
    objetos: list[str] = []
    inicio = time.monotonic()
    motivo = ""
    print("Prueba iniciada. Ctrl+C también la detiene de forma segura.")

    try:
        while True:  # El límite se evalúa tras cada lote, antes de continuar.
            base = len(objetos)
            objetos.extend(f"objeto-{base + i:012d}-" + "X" * 96 for i in range(args.lote))
            rss = proceso.memory_info().rss
            memoria = psutil.virtual_memory()
            swap = psutil.swap_memory()
            transcurrido = time.monotonic() - inicio
            print(
                f"Objetos: {len(objetos):,} | proceso: {mib(rss):,.1f} MiB | "
                f"RAM: {memoria.percent:.1f}% | swap: {mib(swap.used):,.1f} MiB",
                end="\r",
                flush=True,
            )
            if mib(rss) >= args.limite_mb:
                motivo = f"el proceso alcanzó {args.limite_mb} MiB"
                break
            if memoria.available / memoria.total * 100 <= args.reserva_sistema:
                motivo = f"la RAM disponible llegó a la reserva del {args.reserva_sistema:.1f}%"
                break
            if transcurrido >= args.duracion:
                motivo = f"se cumplieron {args.duracion} segundos"
                break
    except KeyboardInterrupt:
        motivo = "el usuario presionó Ctrl+C"
    except MemoryError:
        motivo = "Python detectó falta de memoria"

    print(f"\nPrueba detenida: {motivo}.")
    if args.mantener:
        print(
            f"La memoria se conservará durante {args.mantener} segundos para tomar "
            "la evidencia. Presiona Ctrl+C para liberarla antes."
        )
        try:
            for restantes in range(args.mantener, 0, -1):
                print(f"Liberación automática en {restantes:3d} s", end="\r", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nEspera interrumpida por el usuario.")
    print("\nSe liberarán los objetos al salir.")


if __name__ == "__main__":
    main()
