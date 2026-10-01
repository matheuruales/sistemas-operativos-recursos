# Laboratorio: memoria y procesos del sistema operativo

Cuatro prácticas en Python sobre monitoreo de recursos, caché, memoria virtual y
planificación de procesos. Los programas funcionan en Windows, macOS y Linux,
salvo las diferencias de prioridad explicadas en la práctica 4.

## Preparación

Se necesita Python 3.9 o posterior. Desde esta carpeta:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 1. Vigilante de recursos

```bash
python 01_vigilante_recursos.py
```

Muestra CPU y RAM cada segundo. Cada muestra que supere el 80 % de RAM agrega
una línea con fecha, CPU y RAM a `alertas_ram.txt`. Para una demostración corta:

```bash
python 01_vigilante_recursos.py --muestras 10 --umbral 80
```

## 2. Simulador de caché

El siguiente comando crea un archivo de prueba de 100 MB, lo lee una vez desde
el disco y dos veces desde el diccionario que actúa como caché RAM:

```bash
python 02_simulador_cache.py archivo_grande.txt --crear-muestra-mb 100 --lecturas 3
```

También se puede indicar cualquier archivo existente y omitir
`--crear-muestra-mb`. El programa presenta el tiempo de cada lectura y la mejora
aproximada. La primera lectura puede beneficiarse de la caché real del SO, pero
el origen utilizado por el programa sigue siendo disco frente al diccionario.

## 3. Estrés de memoria con límite de seguridad

Antes de ejecutar, abre el Administrador de tareas de Windows, Monitor de
Actividad de macOS o `htop`/`free` en Linux. Luego ejecuta:

```bash
python 03_estres_memoria.py --limite-mb 512 --duracion 120 --mantener 30
```

El ciclo crea strings por lotes y se detiene al alcanzar cualquiera de estos
límites: 512 MiB del proceso, 20 % de RAM disponible o 120 segundos. Se pueden
ajustar con `--limite-mb`, `--reserva-sistema` y `--duracion`. La opción
`--mantener 30` conserva los objetos durante 30 segundos para poder tomar una
captura antes de liberar la memoria. Que aumente la
swap no está garantizado: depende de la configuración y de las decisiones del
kernel. No se recomienda elevar el límite por encima de la RAM disponible.

## 4. Prioridad y planificación

Abre dos terminales y lanza ambos comandos casi simultáneamente con el mismo
número de iteraciones:

```bash
python 04_prioridad_procesos.py --prioridad baja --iteraciones 30000000
python 04_prioridad_procesos.py --prioridad alta --iteraciones 30000000
```

Compara el tiempo informado al final. La diferencia será más visible si ambos
procesos compiten por un mismo núcleo o si el equipo está ocupado. En Unix, una
prioridad alta suele exigir permisos elevados. En Windows también existe:

```bash
python 04_prioridad_procesos.py --prioridad tiempo-real --permitir-tiempo-real
```

**Precaución:** “tiempo real” puede volver el equipo poco responsivo y requiere
permisos de administrador. Úsalo solo durante una prueba breve, sin aplicaciones
importantes abiertas. En macOS no está disponible mediante esta interfaz; usa
`alta` como comparación. En Linux se intenta `SCHED_FIFO` con la prioridad más
baja del rango de tiempo real y también requiere permisos especiales.

## Qué documentar en el informe

- Captura del panel de CPU/RAM y una línea de `alertas_ram.txt`.
- Tabla con tiempo de lectura desde disco y desde la caché.
- Captura de RAM/swap durante la práctica 3 y los límites utilizados.
- Tiempos finales de las dos instancias de la práctica 4, prioridad y SO.
- Una conclusión breve relacionando cada resultado con el concepto estudiado.
