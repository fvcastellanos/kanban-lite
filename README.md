# Kanban Lite

Aplicación de escritorio sencilla para gestionar tareas tipo Kanban, desarrollada en **Python** con **tkinter** y persistencia en **SQLite**.

## Requisitos

- Python `3.13.x` (gestionado con `pyenv`).
- `tkinter` y `sqlite3` disponibles (módulos de la librería estándar).
- Entorno virtual activado (configurado en `.envrc`).

## Ejecución

```bash
python main.py
```

## Estructura del proyecto

```
kanban-lite/
├── .envrc                          # Activa virtualenv
├── .python-version                 # 3.13
├── requirements.txt                # Sin dependencias externas
├── README.md                       # Este archivo
├── main.py                         # Punto de entrada
└── app/
    ├── __init__.py
    ├── models/                     # Entidades de dominio
    ├── repositories/               # Acceso a datos SQLite
    ├── services/                   # Lógica de negocio
    └── views/                      # Interfaz gráfica con tkinter
```

## Estado actual

**Fase 1 — Interfaz de Usuario y Drag & Drop**

Se ha implementado el tablero con 3 columnas fijas (`Por hacer`, `En proceso`, `Hecho`), tarjetas visuales con título y descripción, botones de editar/eliminar, y un diálogo modal para crear y editar tarjetas. El movimiento entre columnas se resuelve arrastrando una tarjeta y soltándola sobre la columna destino. Los datos son aún de prueba (dummy).

**Fase 2 — Modelo de datos y Persistencia**

Se ha implementado la clase `Tarjeta` en `models/`, el `TarjetaRepository` para operaciones CRUD en SQLite, y la inicialización de la base de datos en `main.py`. La persistencia ya está lista para integrarse con la interfaz.

**Fase 3 — Lógica de Negocio y Servicios**

Se ha implementado `TarjetaService` con validaciones (título no vacío, columnas válidas, tarjeta existente al mover/editar) y `BoardView` ahora carga, crea, edita, mueve y elimina tarjetas directamente desde SQLite. Cada cambio se persiste automáticamente.

**Fase 4 — Refinamiento y Detalles**

Se añadió validación visual en el diálogo de tarjetas (mensaje de error si el título está vacío), confirmación antes de eliminar una tarjeta, y resaltado de la columna destino durante el drag & drop para mejorar el feedback visual.
