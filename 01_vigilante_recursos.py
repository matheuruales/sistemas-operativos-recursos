#!/usr/bin/env python3
"""Panel sencillo de CPU/RAM con registro de alertas de memoria."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import time

import psutil


def barra(porcentaje: float, ancho: int = 30) -> str:
    llenos = round(ancho * porcentaje / 100)
    return "█" * llenos + "░" * (ancho - llenos)


def guardar_alerta(ruta: Path, ram: float, cpu: float, umbral: float) -> None:
    marca = datetime.now().astimezone().isoformat(timespec="seconds")
    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(
            f"{marca} | ALERTA: RAM={ram:.1f}% (> {umbral:.1f}%) | "
            f"CPU={cpu:.1f}%\n"
        )


def monitorear(intervalo: float, umbral: float, log: Path, muestras: int) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    contador = 0
    print("Vigilante activo. Presiona Ctrl+C para detenerlo.\n")
    try:
        while muestras == 0 or contador < muestras:
            cpu = psutil.cpu_percent(interval=intervalo)
            memoria = psutil.virtual_memory()
            contador += 1

            print("\033[2J\033[H", end="")
            print("╔══════════ VIGILANTE DE RECURSOS ══════════╗")
            print(f" CPU  [{barra(cpu)}] {cpu:5.1f}%")
            print(f" RAM  [{barra(memoria.percent)}] {memoria.percent:5.1f}%")
            print(
                f" RAM usada: {memoria.used / 1024**3:.2f} GiB de "
                f"{memoria.total / 1024**3:.2f} GiB"
            )
            print(f" Umbral de alerta: {umbral:.1f}%")
            print(f" Log: {log.resolve()}")
            print("╚════════════════════════════════════════════╝")

            if memoria.percent > umbral:
                guardar_alerta(log, memoria.percent, cpu, umbral)
                print("⚠ RAM sobre el umbral: alerta guardada.")
    except KeyboardInterrupt:
        print("\nMonitoreo finalizado por el usuario.")


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intervalo", type=float, default=1.0, help="Segundos entre muestras.")
    parser.add_argument("--umbral", type=float, default=80.0, help="Umbral de RAM (0-100).")
    parser.add_argument("--log", type=Path, default=Path("alertas_ram.txt"), help="Archivo de alertas.")
    parser.add_argument("--muestras", type=int, default=0, help="0 = ejecutar hasta Ctrl+C.")
    args = parser.parse_args()
    if args.intervalo <= 0 or not 0 <= args.umbral <= 100 or args.muestras < 0:
        parser.error("intervalo debe ser > 0; umbral entre 0 y 100; muestras >= 0")
    return args


if __name__ == "__main__":
    opciones = argumentos()
    monitorear(opciones.intervalo, opciones.umbral, opciones.log, opciones.muestras)
