#!/usr/bin/env python3
"""Ejecuta el mismo cálculo con una prioridad de proceso seleccionable."""

from __future__ import annotations

import argparse
import os
import platform
from time import perf_counter

import psutil


def cambiar_prioridad(nivel: str, permitir_tiempo_real: bool) -> str:
    proceso = psutil.Process()
    if os.name == "nt":
        clases = {
            "baja": psutil.IDLE_PRIORITY_CLASS,
            "normal": psutil.NORMAL_PRIORITY_CLASS,
            "alta": psutil.HIGH_PRIORITY_CLASS,
            "tiempo-real": psutil.REALTIME_PRIORITY_CLASS,
        }
        if nivel == "tiempo-real" and not permitir_tiempo_real:
            raise PermissionError("tiempo-real exige --permitir-tiempo-real")
        proceso.nice(clases[nivel])
        return nivel

    valores_nice = {"baja": 10, "normal": 0, "alta": -10}
    if nivel == "tiempo-real":
        if not permitir_tiempo_real:
            raise PermissionError("tiempo-real exige --permitir-tiempo-real")
        if not hasattr(os, "sched_setscheduler"):
            raise OSError("este sistema no ofrece scheduling de tiempo real desde Python")
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(1))
        return "tiempo-real (SCHED_FIFO, prioridad 1)"
    proceso.nice(valores_nice[nivel])
    return f"{nivel} (nice={proceso.nice()})"


def calculo_pesado(iteraciones: int) -> int:
    # Operaciones enteras deterministas: ambas instancias realizan exactamente lo mismo.
    acumulado = 0
    for numero in range(1, iteraciones + 1):
        acumulado = (acumulado + numero * numero % 1_000_003) % 2_147_483_647
    return acumulado


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prioridad", choices=("baja", "normal", "alta", "tiempo-real"), required=True)
    parser.add_argument("--iteraciones", type=int, default=30_000_000)
    parser.add_argument(
        "--permitir-tiempo-real",
        action="store_true",
        help="Confirma que se entiende el riesgo; puede requerir permisos de administrador.",
    )
    args = parser.parse_args()
    if not 100_000 <= args.iteraciones <= 2_000_000_000:
        parser.error("--iteraciones debe estar entre 100 000 y 2 000 000 000")

    try:
        prioridad = cambiar_prioridad(args.prioridad, args.permitir_tiempo_real)
    except (psutil.Error, PermissionError, OSError) as error:
        parser.error(f"no fue posible aplicar la prioridad: {error}")

    print(f"PID: {os.getpid()} | SO: {platform.system()} | prioridad: {prioridad}")
    print(f"Cálculo de {args.iteraciones:,} iteraciones iniciado...")
    inicio = perf_counter()
    resultado = calculo_pesado(args.iteraciones)
    duracion = perf_counter() - inicio
    print(f"Terminado en {duracion:.3f} s | comprobación: {resultado}")


if __name__ == "__main__":
    main()
