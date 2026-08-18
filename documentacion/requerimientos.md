# Requerimientos — Kanban Lite

## Descripción

Aplicación de escritorio para llevar el control de tareas tipo Kanban, desarrollada en
Python con `tkinter` para la interfaz de usuario.

## Alcance (MVP)

Primera versión funcional con tablero Kanban básico y persistencia en SQLite.

## Requerimientos funcionales

1. Tablero con 3 columnas fijas: **Por hacer**, **En proceso**, **Hecho**.
2. Tarjetas con **título** y **descripción**.
3. **Drag & drop** de tarjetas entre columnas.
4. Crear, editar y eliminar tarjetas.
5. Persistencia en **SQLite** (módulo stdlib de Python, sin dependencias externas).

## Requerimientos técnicos / no funcionales

- Python gestionado con `pyenv`.
- `virtualenv` para aislar las librerías por proyecto.
- Solo `tkinter` + `sqlite3` (módulos de la librería estándar, cero dependencias pip).
- Guardado automático al mover, crear o editar tarjetas.

## Estado del entorno

- `pyenv` instalado.
- Python `3.13.15` (via pyenv) con `tkinter` (Tk `9.0`) y `sqlite3` (`3.51.0`) disponibles.
- `virtualenv` creado con `python -m venv .venv` y activado por `.envrc`.


## Reproducción del ambiente

A continuación se documenta el uso de los archivos de configuración del entorno y los
pasos necesarios para que un tercero pueda reproducir el ambiente desde cero.

### Archivos de configuración del entorno

| Archivo | Propósito | Contenido |
|---------|-----------|-----------|
| `.python-version` | Indica a `pyenv` qué versión de Python usar en el directorio. | `3.13` |
| `.envrc` | Activa automáticamente el `virtualenv` al entrar al directorio (requiere `direnv`). | `source .venv/bin/activate` |
| `requirements.txt` | Declara dependencias pip. En este proyecto no hay dependencias externas. | Comentarios + nota de que solo se usan módulos stdlib. |

### Uso de `.python-version`

Este archivo es leído por `pyenv` para seleccionar automáticamente la versión de Python
cuando se trabaja dentro del directorio del proyecto. Contiene únicamente la versión
principal y menor (p. ej. `3.13`), y `pyenv` resuelve la versión exacta instalada.

**Generación:**

```bash
# 1. Instalar la versión de Python deseada con pyenv (habilitada para tkinter)
pyenv install 3.13.15

# 2. Crear el archivo .python-version en la raíz del proyecto
pyenv local 3.13.15
```

> **Nota:** `pyenv local` crea el archivo `.python-version` con la versión indicada y
> la fija para el directorio actual.

### Uso de `.envrc`

Este archivo es leído por `direnv` para ejecutar comandos automáticamente al entrar al
directorio del proyecto. En este caso, activa el `virtualenv` para que los comandos de
Python usen el intérprete del proyecto.

**Generación:**

```bash
# 1. Instalar direnv (si no está instalado)
brew install direnv

# 2. Añadir el hook de direnv al shell (una sola vez)
#    En zsh (shell por defecto en macOS):
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc

# 3. Crear el archivo .envrc en la raíz del proyecto
echo 'source .venv/bin/activate' > .envrc

# 4. Permitir que direnv ejecute el archivo en este directorio
direnv allow
```

> **Nota:** `direnv allow` es necesario la primera vez para autorizar la ejecución del
> `.envrc`. Sin este paso, `direnv` no activará el ambiente.

### Pasos completos para reproducir el ambiente desde cero

1. **Instalar `tcl-tk`** (necesario para compilar tkinter):

   ```bash
   brew install tcl-tk
   ```

2. **Instalar Python con `pyenv` habilitado para tkinter** (p. ej. `3.13.15`):

   ```bash
   pyenv install 3.13.15
   ```

3. **Fijar la versión de Python para el proyecto** (crea `.python-version`):

   ```bash
   pyenv local 3.13.15
   ```

4. **Crear el `virtualenv`** en el proyecto:

   ```bash
   python -m venv .venv
   ```

5. **Crear el `.envrc`** para activar el ambiente automáticamente:

   ```bash
   echo 'source .venv/bin/activate' > .envrc
   ```

6. **Instalar `direnv` y autorizar el `.envrc`** (si no está instalado):

   ```bash
   brew install direnv
   echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
   direnv allow
   ```

7. **Verificar que el ambiente funciona**:

   ```bash
   python --version          # Debe mostrar 3.13.15
   python -c "import tkinter; print(tkinter.TkVersion)"   # Debe mostrar 9.0
   python -c "import sqlite3; print(sqlite3.sqlite_version)"  # Debe mostrar 3.51.0
   ```

> **Nota:** No hay dependencias pip que instalar (`requirements.txt` está vacío de
> dependencias externas). Solo se usan módulos de la librería estándar.


## Arquitectura

Aplicación organizada en capas, separando la interfaz de usuario (vistas), la lógica de
negocio (servicios) y el acceso a datos (repositorios).

### Estructura de proyecto

```
kanban-lite/
├── .envrc                          # Activa virtualenv
├── .python-version                 # 3.13
├── requirements.txt                # Sin dependencias externas
├── README.md                       # Documentación del proyecto
├── documentacion/
│   └── requerimientos.md           # Requerimientos del MVP
│
├── main.py                         # Punto de entrada de la aplicación
│
└── app/
    ├── __init__.py
    │
    ├── models/                     # Capa de modelos (entidades de dominio)
    │   ├── __init__.py
    │   └── tarjeta.py              # Clase Tarjeta (id, titulo, descripcion, columna)
    │
    ├── repositories/               # Capa de acceso a datos (DAO)
    │   ├── __init__.py
    │   ├── database.py             # Conexión SQLite + creación de tablas
    │   └── tarjeta_repository.py   # CRUD de tarjetas en SQLite
    │
    ├── services/                   # Capa de lógica de negocio
    │   ├── __init__.py
    │   └── tarjeta_service.py      # Reglas de negocio (validaciones, movimientos)
    │
    └── views/                      # Capa de presentación (tkinter)
        ├── __init__.py
        ├── main_window.py          # Ventana principal con el tablero
        ├── board_view.py           # Vista del tablero (3 columnas)
        ├── column_view.py          # Vista de una columna
        ├── card_view.py            # Vista de una tarjeta
        └── dialogs.py              # Diálogos (crear/editar tarjeta)
```

### Flujo de dependencias

```
┌─────────────────────────────┐
│         views (tkinter)     │  ← Solo se encarga de la UI
│  main_window, board, card   │
└──────────────┬──────────────┘
               │  usa
┌──────────────▼──────────────┐
│        services             │  ← Lógica de negocio
│  tarjeta_service            │  (validaciones, reglas)
└──────────────┬──────────────┘
               │  usa
┌──────────────▼──────────────┐
│      repositories           │  ← Acceso a datos (SQLite)
│  tarjeta_repository         │
└──────────────┬──────────────┘
               │  usa
┌──────────────▼──────────────┐
│         models              │  ← Entidades de dominio
│  Tarjeta                    │
└─────────────────────────────┘
```

### Responsabilidades de cada capa

| Capa | Responsabilidad | Ejemplo |
|------|----------------|---------|
| **views/** | Interfaz de usuario (tkinter). No contiene lógica de negocio. | Dibujar columnas, tarjetas, manejar drag & drop, abrir diálogos. |
| **services/** | Lógica de negocio. Orquesta operaciones y valida reglas. | Validar que el título no esté vacío, mover tarjeta entre columnas. |
| **repositories/** | Persistencia. Solo SQL crudo / operaciones SQLite. | `INSERT`, `UPDATE`, `DELETE`, `SELECT` de tarjetas. |
| **models/** | Entidades de dominio (datos puros). | Clase `Tarjeta` con atributos y métodos simples. |

### Beneficios de la arquitectura

1. **Separación de responsabilidades**: cada capa tiene un propósito claro.
2. **Testeabilidad**: se pueden probar `services` y `repositories` sin abrir la UI.
3. **Mantenibilidad**: si cambia la UI, solo se modifica la capa `views/`.
4. **Escalabilidad**: fácil añadir nuevas entidades (p. ej. `Columnas`, `Etiquetas`) siguiendo el mismo patrón.
5. **Cero dependencias**: se mantiene el requisito de solo usar `tkinter` + `sqlite3`.

## Plan de Implementación por Fases

### Fase 0: Estructura y "Hola Mundo"
- Crear la estructura de directorios y archivos solicitada en la sección de arquitectura.
- Implementar una ventana básica de `tkinter` que muestre un mensaje "Hola Mundo" centrado.
- Configurar el punto de entrada en `main.py`.

### Fase 1: Interfaz de Usuario (UI) y Drag & Drop
- Implementar la vista del tablero y columnas con datos dummy.
- Crear los diálogos para creación y edición de tarjetas.
- Implementar la funcionalidad de Drag & Drop.

### Fase 2: Modelo de datos y Persistencia
- Implementar la clase `Tarjeta` en `models/`.
- Implementar el `TarjetaRepository` para operaciones básicas en SQLite.
- Establecer la conexión inicial con la base de datos.

### Fase 3: Lógica de Negocio y Servicios
- Implementar `TarjetaService` con validaciones iniciales.
- Definir las reglas de movimiento entre columnas.

### Fase 4: Refinimiento y Detalles
- Implementar el guardado automático.
- Añadir validaciones visuales y feedback para el usuario.

