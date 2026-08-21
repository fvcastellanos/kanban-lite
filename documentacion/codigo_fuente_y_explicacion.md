# Kanban Lite — Código fuente y explicación

Este documento contiene el código fuente completo de la aplicación **Kanban Lite** en la primera sección y, en la segunda sección, una explicación sencilla orientada al usuario final sobre la arquitectura, las librerías utilizadas y las funcionalidades del proyecto.

---

# 1. Código fuente de la aplicación

A continuación se muestra el contenido de cada archivo de la aplicación (archivos `.py`). No se incluyen archivos de documentación ni archivos de control de versiones (git).

## main.py

```python
"""Punto de entrada de Kanban Lite."""

from app.repositories.database import inicializar_base_de_datos
from app.views.main_window import main


if __name__ == "__main__":
    inicializar_base_de_datos()
    main()
```

## app/__init__.py

```python
"""Paquete raíz de la aplicación Kanban Lite."""

__version__ = "0.0.1"
```

## app/models/__init__.py

```python
"""Modelos de dominio de Kanban Lite."""
```

## app/models/tarjeta.py

```python
"""Modelo de dominio: Tarjeta Kanban."""

from dataclasses import dataclass


@dataclass
class Tarjeta:
    """Representa una tarjeta del tablero Kanban."""

    id: int | None = None
    titulo: str = ""
    descripcion: str = ""
    columna: str = "por_hacer"

    def __post_init__(self):
        if self.id is not None and self.id < 0:
            raise ValueError("El id debe ser mayor o igual a cero")
        # id == None indica una tarjeta aún no persistida en la base de datos.
```

## app/repositories/__init__.py

```python
"""Repositorios de acceso a datos de Kanban Lite."""
```

## app/repositories/database.py

```python
"""Conexión SQLite e inicialización de la base de datos."""

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "db/kanban_lite.db"


def obtener_conexion() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_base_de_datos() -> None:
    """Crea las tablas necesarias si no existen."""
    conn = obtener_conexion()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tarjeta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                columna TEXT NOT NULL DEFAULT 'por_hacer'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
```

## app/repositories/tarjeta_repository.py

```python
"""Repositorio para operaciones CRUD de tarjetas."""

import sqlite3

from app.models.tarjeta import Tarjeta
from app.repositories.database import obtener_conexion


def _fila_a_tarjeta(fila: sqlite3.Row) -> Tarjeta:
    """Convierte una fila de SQLite en una instancia de Tarjeta."""
    return Tarjeta(
        id=fila["id"],
        titulo=fila["titulo"],
        descripcion=fila["descripcion"],
        columna=fila["columna"],
    )


class TarjetaRepository:
    """Acceso a datos para la entidad Tarjeta."""

    def crear(self, tarjeta: Tarjeta) -> Tarjeta:
        """Inserta una nueva tarjeta y actualiza su id."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                INSERT INTO tarjeta (titulo, descripcion, columna)
                VALUES (?, ?, ?)
                """,
                (tarjeta.titulo, tarjeta.descripcion, tarjeta.columna),
            )
            conn.commit()
            tarjeta.id = cursor.lastrowid
            return tarjeta
        finally:
            conn.close()

    def listar_por_columna(self, columna: str) -> list[Tarjeta]:
        """Devuelve todas las tarjetas de una columna."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                SELECT id, titulo, descripcion, columna
                FROM tarjeta
                WHERE columna = ?
                ORDER BY id ASC
                """,
                (columna,),
            )
            return [_fila_a_tarjeta(fila) for fila in cursor.fetchall()]
        finally:
            conn.close()

    def actualizar(self, tarjeta: Tarjeta) -> Tarjeta:
        """Actualiza una tarjeta existente."""
        if tarjeta.id is None:
            raise ValueError("No se puede actualizar una tarjeta sin id")

        conn = obtener_conexion()
        try:
            conn.execute(
                """
                UPDATE tarjeta
                SET titulo = ?,
                    descripcion = ?,
                    columna = ?
                WHERE id = ?
                """,
                (tarjeta.titulo, tarjeta.descripcion, tarjeta.columna, tarjeta.id),
            )
            conn.commit()
            return tarjeta
        finally:
            conn.close()

    def eliminar(self, tarjeta_id: int) -> None:
        """Elimina una tarjeta por su id."""
        conn = obtener_conexion()
        try:
            conn.execute(
                """
                DELETE FROM tarjeta
                WHERE id = ?
                """,
                (tarjeta_id,),
            )
            conn.commit()
        finally:
            conn.close()

    def obtener(self, tarjeta_id: int) -> Tarjeta | None:
        """Obtiene una tarjeta por su id."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                SELECT id, titulo, descripcion, columna
                FROM tarjeta
                WHERE id = ?
                """,
                (tarjeta_id,),
            )
            fila = cursor.fetchone()
            return _fila_a_tarjeta(fila) if fila else None
        finally:
            conn.close()

    def listar_todas(self) -> list[Tarjeta]:
        """Devuelve todas las tarjetas ordenadas por columna e id."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                SELECT id, titulo, descripcion, columna
                FROM tarjeta
                ORDER BY columna ASC, id ASC
                """
            )
            return [_fila_a_tarjeta(fila) for fila in cursor.fetchall()]
        finally:
            conn.close()
```

## app/services/__init__.py

```python
"""Servicios de lógica de negocio de Kanban Lite."""
```

## app/services/tarjeta_service.py

```python
"""Lógica de negocio para tarjetas Kanban."""

from app.models.tarjeta import Tarjeta
from app.repositories.tarjeta_repository import TarjetaRepository


class TarjetaService:
    """Orquesta las operaciones sobre tarjetas y valida reglas."""

    COLUMNAS_VALIDAS = {"por_hacer", "en_proceso", "hecho"}

    def __init__(self, repository: TarjetaRepository | None = None):
        self._repo = repository or TarjetaRepository()

    def crear_tarjeta(self, titulo: str, descripcion: str = "", columna: str = "por_hacer") -> Tarjeta:
        """Crea una tarjeta validando los datos de entrada."""
        titulo_limpio = titulo.strip()
        if not titulo_limpio:
            raise ValueError("El título de la tarjeta no puede estar vacío")

        if columna not in self.COLUMNAS_VALIDAS:
            raise ValueError(f"Columna no válida: {columna}")

        tarjeta = Tarjeta(
            titulo=titulo_limpio,
            descripcion=descripcion.strip(),
            columna=columna,
        )
        return self._repo.crear(tarjeta)

    def mover_tarjeta(self, tarjeta_id: int, columna_destino: str) -> Tarjeta:
        """Mueve una tarjeta a otra columna."""
        if columna_destino not in self.COLUMNAS_VALIDAS:
            raise ValueError(f"Columna destino no válida: {columna_destino}")

        tarjeta = self._repo.obtener(tarjeta_id)
        if tarjeta is None:
            raise ValueError(f"No existe la tarjeta con id {tarjeta_id}")

        if tarjeta.columna == columna_destino:
            return tarjeta

        tarjeta.columna = columna_destino
        return self._repo.actualizar(tarjeta)

    def listar_tarjetas(self, columna: str) -> list[Tarjeta]:
        """Devuelve las tarjetas de una columna."""
        if columna not in self.COLUMNAS_VALIDAS:
            raise ValueError(f"Columna no válida: {columna}")
        return self._repo.listar_por_columna(columna)

    def eliminar_tarjeta(self, tarjeta_id: int) -> None:
        """Elimina una tarjeta del tablero."""
        self._repo.eliminar(tarjeta_id)

    def actualizar_tarjeta(
        self,
        tarjeta_id: int,
        titulo: str | None = None,
        descripcion: str | None = None,
        columna: str | None = None,
    ) -> Tarjeta:
        """Actualiza una tarjeta existente validando los datos."""
        tarjeta = self._repo.obtener(tarjeta_id)
        if tarjeta is None:
            raise ValueError(f"No existe la tarjeta con id {tarjeta_id}")

        if titulo is not None:
            titulo_limpio = titulo.strip()
            if not titulo_limpio:
                raise ValueError("El título de la tarjeta no puede estar vacío")
            tarjeta.titulo = titulo_limpio

        if descripcion is not None:
            tarjeta.descripcion = descripcion.strip()

        if columna is not None:
            if columna not in self.COLUMNAS_VALIDAS:
                raise ValueError(f"Columna no válida: {columna}")
            tarjeta.columna = columna

        return self._repo.actualizar(tarjeta)
```

## app/views/__init__.py

```python
"""Vistas de la interfaz gráfica de Kanban Lite."""
```

## app/views/styles.py

```python
"""Estilos ttk personalizados inspirados en Jira, forzando tema claro."""

import tkinter as tk
from tkinter import ttk


# Paleta inspirada en Jira
AZUL_JIRA = "#0052CC"
AZUL_JIRA_OSCURO = "#0747A6"
AZUL_JIRA_CLARO = "#4C9AFF"
ROJO_JIRA = "#DE350B"
ROJO_JIRA_OSCURO = "#BF2600"
GRIS_FONDO = "#F4F5F7"
GRIS_MEDIO = "#EBECF0"
GRIS_BORDE = "#DFE1E6"
GRIS_TEXTO = "#172B4D"
GRIS_TEXTO_SECUNDARIO = "#5E6C84"
BLANCO = "#FFFFFF"


def configurar_estilos(widget_raiz: "tk.Tk | tk.Tcl | None" = None) -> None:
    """Configura los estilos ttk personalizados para toda la aplicación."""
    estilo = ttk.Style(widget_raiz)

    # Fuerza un tema claro y consistente en todas las plataformas.
    for tema in ("clam", "alt", "default"):
        try:
            estilo.theme_use(tema)
            break
        except tk.TclError:
            continue

    # Fuente base
    estilo.configure("Jira.TButton", font=("Segoe UI", 10, "bold"))

    # Botón primario: azul Jira con texto blanco
    estilo.configure(
        "JiraPrimary.TButton",
        font=("Segoe UI", 10, "bold"),
        background=AZUL_JIRA,
        foreground=BLANCO,
        borderwidth=1,
        focusthickness=0,
        focuscolor=BLANCO,
        padding=(12, 6),
    )
    estilo.map(
        "JiraPrimary.TButton",
        background=[("active", AZUL_JIRA_OSCURO), ("pressed", AZUL_JIRA_OSCURO), ("focus", AZUL_JIRA)],
        foreground=[("active", BLANCO), ("pressed", BLANCO), ("focus", BLANCO)],
    )

    # Botón secundario: fondo blanco con borde gris y texto oscuro
    estilo.configure(
        "JiraSecondary.TButton",
        font=("Segoe UI", 10),
        background=BLANCO,
        foreground=GRIS_TEXTO,
        borderwidth=1,
        focusthickness=0,
        focuscolor=BLANCO,
        padding=(12, 6),
    )
    estilo.map(
        "JiraSecondary.TButton",
        background=[("active", GRIS_MEDIO), ("pressed", GRIS_MEDIO), ("focus", BLANCO)],
        foreground=[("active", GRIS_TEXTO), ("pressed", GRIS_TEXTO), ("focus", GRIS_TEXTO)],
    )

    # Botón de peligro: rojo Jira con texto blanco
    estilo.configure(
        "JiraDanger.TButton",
        font=("Segoe UI", 9, "bold"),
        background=ROJO_JIRA,
        foreground=BLANCO,
        borderwidth=1,
        focusthickness=0,
        focuscolor=BLANCO,
        padding=(6, 3),
    )
    estilo.map(
        "JiraDanger.TButton",
        background=[("active", ROJO_JIRA_OSCURO), ("pressed", ROJO_JIRA_OSCURO), ("focus", ROJO_JIRA)],
        foreground=[("active", BLANCO), ("pressed", BLANCO), ("focus", BLANCO)],
    )

    # Botón pequeño primario (para tarjetas)
    estilo.configure(
        "JiraCard.TButton",
        font=("Segoe UI", 9, "bold"),
        background=AZUL_JIRA,
        foreground=BLANCO,
        borderwidth=1,
        focusthickness=0,
        focuscolor=BLANCO,
        padding=(0, 2),
    )
    estilo.map(
        "JiraCard.TButton",
        background=[("active", AZUL_JIRA_OSCURO), ("pressed", AZUL_JIRA_OSCURO), ("focus", AZUL_JIRA)],
        foreground=[("active", BLANCO), ("pressed", BLANCO), ("focus", BLANCO)],
    )

    # Etiquetas
    estilo.configure("JiraTitle.TLabel", font=("Segoe UI", 11, "bold"), background=BLANCO, foreground=GRIS_TEXTO)
    estilo.configure(
        "JiraDesc.TLabel",
        font=("Segoe UI", 10),
        background=BLANCO,
        foreground=GRIS_TEXTO_SECUNDARIO,
    )
    estilo.configure(
        "JiraColumn.TLabel",
        font=("Segoe UI", 13, "bold"),
        background=GRIS_MEDIO,
        foreground=GRIS_TEXTO,
    )

    # Frames
    estilo.configure("JiraCard.TFrame", background=BLANCO)
    estilo.configure("JiraColumn.TFrame", background=GRIS_FONDO)
    estilo.configure("JiraColumnHeader.TFrame", background=GRIS_MEDIO)
    estilo.configure("JiraBoard.TFrame", background=BLANCO)
    estilo.configure("JiraDialog.TFrame", background=BLANCO)
```

## app/views/board_view.py

```python
"""Vista del tablero Kanban."""

import tkinter as tk
from tkinter import messagebox, ttk

from app.models.tarjeta import Tarjeta
from app.services.tarjeta_service import TarjetaService
from app.views.column_view import ColumnView
from app.views.dialogs import mostrar_dialogo_tarjeta


COLUMNAS = [
    ("por_hacer", "Por hacer"),
    ("en_proceso", "En proceso"),
    ("hecho", "Hecho"),
]

# Paleta inspirada en Jira
COLOR_FONDO_BOARD = "#FFFFFF"


class BoardView(tk.Frame):
    """Representación visual del tablero con 3 columnas y persistencia."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._service = TarjetaService()
        self._columnas: dict[str, ColumnView] = {}
        self._construir_ui()
        self._cargar_tarjetas()

    def _construir_ui(self):
        self.configure(bg=COLOR_FONDO_BOARD)
        self.grid_rowconfigure(0, weight=1)

        for indice, (columna_id, titulo) in enumerate(COLUMNAS):
            self.grid_columnconfigure(indice, weight=1, uniform="columna")
            columna = ColumnView(
                self,
                columna_id=columna_id,
                titulo=titulo,
                on_mover_tarjeta=self._mover_tarjeta,
                on_editar_tarjeta=self._editar_tarjeta,
                on_eliminar_tarjeta=self._eliminar_tarjeta,
            )
            columna.grid(row=0, column=indice, sticky="nsew", padx=8, pady=8)
            self._columnas[columna_id] = columna

        # Barra inferior
        barra = tk.Frame(self, bg=COLOR_FONDO_BOARD)
        barra.grid(row=1, column=0, columnspan=len(COLUMNAS), sticky="ew", pady=(0, 12))

        btn_nueva = ttk.Button(
            barra,
            text="+ Crear tarjeta",
            command=self._crear_tarjeta,
            style="JiraPrimary.TButton",
        )
        btn_nueva.pack(side="left", padx=8)

    def _cargar_tarjetas(self):
        """Carga las tarjetas desde el servicio y las muestra en el tablero."""
        self._refrescar_tablero()

    def _refrescar_tablero(self):
        """Vuelve a dibujar todas las tarjetas en sus columnas."""
        for columna in self._columnas.values():
            columna.limpiar()

        for columna_id, _ in COLUMNAS:
            for tarjeta in self._service.listar_tarjetas(columna_id):
                self._columnas[columna_id].agregar_tarjeta(tarjeta)

    def _mover_tarjeta(self, tarjeta: Tarjeta, columna_destino: str):
        """Mueve una tarjeta a otra columna y persiste el cambio."""
        if columna_destino not in self._columnas:
            return
        self._service.mover_tarjeta(tarjeta.id, columna_destino)
        self._refrescar_tablero()

    def _crear_tarjeta(self):
        """Abre el diálogo para crear una nueva tarjeta y la persiste."""
        resultado = mostrar_dialogo_tarjeta(self)
        if resultado:
            self._service.crear_tarjeta(
                titulo=resultado["titulo"],
                descripcion=resultado["descripcion"],
                columna=resultado.get("columna", "por_hacer"),
            )
            self._refrescar_tablero()

    def _editar_tarjeta(self, tarjeta: Tarjeta):
        """Abre el diálogo para editar una tarjeta existente y persiste los cambios."""
        resultado = mostrar_dialogo_tarjeta(self, titulo="Editar tarjeta", tarjeta=tarjeta)
        if resultado:
            self._service.actualizar_tarjeta(
                tarjeta_id=tarjeta.id,
                titulo=resultado["titulo"],
                descripcion=resultado["descripcion"],
                columna=resultado.get("columna", tarjeta.columna),
            )
            self._refrescar_tablero()

    def _eliminar_tarjeta(self, tarjeta: Tarjeta):
        """Elimina una tarjeta del tablero y de la base de datos tras confirmar."""
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar la tarjeta \"{tarjeta.titulo}\"?\nEsta acción no se puede deshacer.",
            icon="warning",
        )
        if respuesta:
            self._service.eliminar_tarjeta(tarjeta.id)
            self._refrescar_tablero()
```

## app/views/column_view.py

```python
"""Vista de una columna del tablero."""

import tkinter as tk
from tkinter import ttk

from app.models.tarjeta import Tarjeta
from app.views.card_view import CardView


# Paleta inspirada en Jira
COLOR_FONDO_COLUMNA = "#F4F5F7"
COLOR_BORDE_COLUMNA = "#DFE1E6"
COLOR_FONDO_ENCABEZADO = "#EBECF0"
COLOR_TEXTO_ENCABEZADO = "#172B4D"
COLOR_SCROLLBAR = "#C1C7D0"
COLOR_RESALTADO_COLUMNA = "#4C9AFF"


class ColumnView(tk.Frame):
    """Representación visual de una columna del tablero, zona de drop."""

    def __init__(
        self,
        parent,
        columna_id: str,
        titulo: str,
        on_mover_tarjeta: "callable | None" = None,
        on_editar_tarjeta: "callable | None" = None,
        on_eliminar_tarjeta: "callable | None" = None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self._columna_id = columna_id
        self._titulo = titulo
        self._on_mover_tarjeta = on_mover_tarjeta
        self._on_editar_tarjeta = on_editar_tarjeta
        self._on_eliminar_tarjeta = on_eliminar_tarjeta
        self._construir_ui()
        self._configurar_drop()

    def _construir_ui(self):
        self.configure(
            relief="flat",
            borderwidth=0,
            bg=COLOR_FONDO_COLUMNA,
            highlightbackground=COLOR_BORDE_COLUMNA,
            highlightthickness=1,
        )
        self._columna = self._columna_id
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Encabezado
        header = tk.Frame(self, bg=COLOR_FONDO_ENCABEZADO, height=40)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        lbl_titulo = tk.Label(
            header,
            text=self._titulo,
            font=("Segoe UI", 13, "bold"),
            bg=COLOR_FONDO_ENCABEZADO,
            fg=COLOR_TEXTO_ENCABEZADO,
            anchor="w",
        )
        lbl_titulo.grid(row=0, column=0, sticky="w", padx=12, pady=8)

        # Área de tarjetas con scrollbar
        canvas_frame = tk.Frame(self, bg=COLOR_FONDO_COLUMNA)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(
            canvas_frame,
            highlightthickness=0,
            bg=COLOR_FONDO_COLUMNA,
        )
        self._canvas.grid(row=0, column=0, sticky="nsew")

        # Panel interno para resaltar el área de tarjetas durante drag & drop
        self._resaltado_frame = tk.Frame(
            self,
            bg=COLOR_FONDO_COLUMNA,
            highlightbackground=COLOR_RESALTADO_COLUMNA,
            highlightthickness=0,
        )
        self._resaltado_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self._resaltado_frame.lower(self._canvas)
        self._resaltado_frame.grid_remove()

        scrollbar = tk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self._canvas.yview,
            bg=COLOR_FONDO_COLUMNA,
            troughcolor=COLOR_FONDO_COLUMNA,
            activebackground=COLOR_SCROLLBAR,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas._columna = self._columna_id

        self._cards_frame = tk.Frame(self._canvas, bg=COLOR_FONDO_COLUMNA)
        self._cards_frame._columna = self._columna_id
        self._canvas.create_window(
            (0, 0),
            window=self._cards_frame,
            anchor="nw",
            tags="cards_frame",
        )

        self._cards_frame.bind("<Configure>", self._ajustar_scroll_region)
        self._cards_frame.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._scroll_rueda))
        self._cards_frame.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

    def _ajustar_scroll_region(self, evento: tk.Event = None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._canvas.itemconfig("cards_frame", width=self._canvas.winfo_width())

    def _scroll_rueda(self, evento: tk.Event):
        self._canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

    def _configurar_drop(self):
        """Configura la columna como zona receptora de tarjetas arrastradas."""
        self.bind("<ButtonRelease-1>", self._on_soltar_en_columna)
        self._canvas.bind("<ButtonRelease-1>", self._on_soltar_en_columna)
        self._cards_frame.bind("<ButtonRelease-1>", self._on_soltar_en_columna)

    def _on_soltar_en_columna(self, evento: tk.Event):
        """Manejador reservado para extensiones futuras de D&D nativo."""
        pass

    @property
    def columna_id(self) -> str:
        return self._columna_id

    def limpiar(self):
        """Elimina todas las tarjetas mostradas."""
        for widget in self._cards_frame.winfo_children():
            widget.destroy()

    def agregar_tarjeta(self, tarjeta: Tarjeta):
        """Añade una tarjeta visual a la columna."""
        card = CardView(
            self._cards_frame,
            tarjeta=tarjeta,
            on_editar=self._on_editar_tarjeta,
            on_eliminar=self._on_eliminar_tarjeta,
        )
        card.pack(fill="x", pady=6, padx=0)
        card.bind("<<CardMoved>>", lambda e, c=card: self._solicitar_movimiento(c))

    def _solicitar_movimiento(self, card: CardView):
        """Notifica al board que la tarjeta debe moverse a esta columna."""
        if self._on_mover_tarjeta:
            self._on_mover_tarjeta(card.tarjeta, self._columna_id)

    def resaltar(self, activo: bool):
        """Activa o desactiva el resaltado de la columna como zona de drop."""
        if activo:
            self.configure(highlightbackground=COLOR_RESALTADO_COLUMNA, highlightthickness=2)
        else:
            self.configure(highlightbackground=COLOR_BORDE_COLUMNA, highlightthickness=1)
```

## app/views/card_view.py

```python
"""Vista de una tarjeta del tablero."""

import tkinter as tk
from tkinter import ttk

from app.models.tarjeta import Tarjeta


# Paleta inspirada en Jira
COLOR_FONDO_TARJETA = "#FFFFFF"
COLOR_BORDE_TARJETA = "#DFE1E6"
COLOR_TEXTO_TITULO = "#172B4D"
COLOR_TEXTO_DESCRIPCION = "#5E6C84"
COLOR_SOMBRA = "#C1C7D0"
COLOR_RESALTADO = "#0052CC"
COLOR_RESALTADO_COLUMNA = "#4C9AFF"


class CardView(tk.Frame):
    """Representación visual de una tarjeta con drag & drop."""

    def __init__(
        self,
        parent,
        tarjeta: Tarjeta,
        on_editar: "callable | None" = None,
        on_eliminar: "callable | None" = None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.tarjeta = tarjeta
        self._on_editar = on_editar
        self._on_eliminar = on_eliminar
        self._dragging = False
        self._ghost: tk.Toplevel | None = None
        self._construir_ui()
        self._configurar_drag_drop()

    def _construir_ui(self):
        self.configure(
            relief="flat",
            borderwidth=0,
            bg=COLOR_FONDO_TARJETA,
            cursor="hand2",
            highlightbackground=COLOR_BORDE_TARJETA,
            highlightthickness=1,
        )

        # Contenedor interno con fondo blanco
        inner = tk.Frame(self, bg=COLOR_FONDO_TARJETA)
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        lbl_titulo = ttk.Label(
            inner,
            text=self.tarjeta.titulo,
            style="JiraTitle.TLabel",
            anchor="w",
        )
        lbl_titulo.pack(anchor="w", fill="x")

        if self.tarjeta.descripcion:
            lbl_desc = ttk.Label(
                inner,
                text=self.tarjeta.descripcion,
                wraplength=220,
                style="JiraDesc.TLabel",
                anchor="w",
            )
            lbl_desc.pack(anchor="w", fill="x", pady=(4, 0))

        # Botones de acción
        frame_botones = tk.Frame(inner, bg=COLOR_FONDO_TARJETA)
        frame_botones.pack(anchor="e", fill="x", pady=(8, 0))

        btn_editar = ttk.Button(
            frame_botones,
            text="Editar",
            command=self._editar,
            style="JiraCard.TButton",
            width=8,
        )
        btn_editar.pack(side="right", padx=(4, 0))

        btn_eliminar = ttk.Button(
            frame_botones,
            text="Eliminar",
            command=self._eliminar,
            style="JiraDanger.TButton",
            width=8,
        )
        btn_eliminar.pack(side="right")

    def _configurar_drag_drop(self):
        """Solo el frame principal inicia el arrastre; los hijos delegan."""
        self.bind("<ButtonPress-1>", self._iniciar_arrastre)
        self.bind("<B1-Motion>", self._arrastrar)
        self.bind("<ButtonRelease-1>", self._soltar)

        def _vincular(widget):
            widget.bind("<ButtonPress-1>", self._delegar_a_frame)
            widget.bind("<B1-Motion>", self._delegar_a_frame)
            widget.bind("<ButtonRelease-1>", self._delegar_a_frame)

        self._recorrer_hijos(self, _vincular)

    def _delegar_a_frame(self, evento: tk.Event):
        """Redirige un evento del widget hijo al propio CardView."""
        if not self._dragging:
            self._iniciar_arrastre(evento)
        elif evento.type == tk.EventType.Motion:
            self._arrastrar(evento)
        elif evento.type == tk.EventType.ButtonRelease:
            self._soltar(evento)
        return "break"

    def _recorrer_hijos(self, widget, accion):
        """Aplica una acción a todos los widgets hijos excepto botones."""
        for hijo in widget.winfo_children():
            if isinstance(hijo, ttk.Button):
                continue
            accion(hijo)
            self._recorrer_hijos(hijo, accion)

    def _iniciar_arrastre(self, evento: tk.Event):
        self._dragging = True
        self.configure(highlightbackground=COLOR_RESALTADO, highlightthickness=2)
        self._crear_fantasma()

    def _crear_fantasma(self):
        self._ghost = tk.Toplevel(self)
        self._ghost.overrideredirect(True)
        self._ghost.attributes("-alpha", 0.85)
        self._ghost.configure(bg=COLOR_SOMBRA)

        ancho = self.winfo_width()
        alto = self.winfo_height()
        if ancho < 20:
            ancho = 240
        if alto < 20:
            alto = 90

        ghost_frame = tk.Frame(
            self._ghost,
            relief="flat",
            borderwidth=0,
            bg=COLOR_FONDO_TARJETA,
            highlightbackground=COLOR_RESALTADO,
            highlightthickness=2,
            width=ancho,
            height=alto,
        )
        ghost_frame.pack(fill="both", expand=True)
        ghost_frame.pack_propagate(False)

        ttk.Label(
            ghost_frame,
            text=self.tarjeta.titulo,
            style="JiraTitle.TLabel",
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(10, 0))

        if self.tarjeta.descripcion:
            ttk.Label(
                ghost_frame,
                text=self.tarjeta.descripcion,
                wraplength=ancho - 24,
                style="JiraDesc.TLabel",
                anchor="w",
            ).pack(anchor="w", padx=10, pady=(0, 10))

        self._ghost.withdraw()

    def _arrastrar(self, evento: tk.Event):
        if not self._dragging:
            return
        if self._ghost is None:
            self._crear_fantasma()
        self._ghost.deiconify()
        x = evento.x_root - (self._ghost.winfo_width() // 2)
        y = evento.y_root - 10
        self._ghost.geometry(f"+{x}+{y}")
        self._resaltar_columna_bajo_cursor(evento.x_root, evento.y_root)

    def _soltar(self, evento: tk.Event):
        if not self._dragging:
            return
        self._dragging = False
        self.configure(highlightbackground=COLOR_BORDE_TARJETA, highlightthickness=1)

        x_root = evento.x_root
        y_root = evento.y_root

        if self._ghost is not None:
            self._ghost.destroy()
            self._ghost = None

        destino = self.winfo_containing(x_root, y_root)
        self._limpiar_resaltado_columnas()
        columna = self._buscar_columna(destino)
        if columna and columna != self.tarjeta.columna:
            self._mover_a_columna(columna)

    def _mover_a_columna(self, columna_destino: str) -> None:
        """Notifica a la columna destino que esta tarjeta debe moverse allí."""
        board = self._buscar_board()
        if board is None:
            return
        columna = board._columnas.get(columna_destino)
        if columna is not None:
            columna._solicitar_movimiento(self)

    def _buscar_board(self):
        """Busca el BoardView ancestro de esta tarjeta."""
        actual = self
        while actual is not None and actual != ".":
            if hasattr(actual, "_columnas"):
                return actual
            try:
                parent_name = actual.winfo_parent()
            except tk.TclError:
                break
            if not parent_name or parent_name == ".":
                break
            actual = actual._nametowidget(parent_name)
        return None

    def _buscar_columna(self, widget) -> str | None:
        """Busca el atributo de columna en el widget o sus ancestros."""
        if widget is None or widget == ".":
            return None

        if isinstance(widget, str):
            try:
                widget = self._nametowidget(widget)
            except tk.TclError:
                return None

        actual = widget
        while actual is not None and actual != ".":
            columna = getattr(actual, "_columna", None)
            if columna is not None:
                return columna

            parent_name = actual.winfo_parent()
            if not parent_name or parent_name == ".":
                break

            actual = actual._nametowidget(parent_name)
        return None

    def _resaltar_columna_bajo_cursor(self, x_root: int, y_root: int):
        """Resalta la columna que está bajo el cursor durante el arrastre."""
        self._limpiar_resaltado_columnas()
        destino = self.winfo_containing(x_root, y_root)
        columna_id = self._buscar_columna(destino)
        if columna_id is None:
            return
        board = self._buscar_board()
        if board is None:
            return
        columna = board._columnas.get(columna_id)
        if columna is not None and columna_id != self.tarjeta.columna:
            columna.resaltar(True)
            self._columna_resaltada = columna

    def _limpiar_resaltado_columnas(self):
        """Quita el resaltado de todas las columnas."""
        board = self._buscar_board()
        if board is None:
            return
        for columna in board._columnas.values():
            columna.resaltar(False)
        self._columna_resaltada = None

    def _editar(self):
        if self._on_editar:
            self._on_editar(self.tarjeta)

    def _eliminar(self):
        if self._on_eliminar:
            self._on_eliminar(self.tarjeta)
```

## app/views/dialogs.py

```python
"""Diálogos para crear y editar tarjetas."""

import tkinter as tk
from tkinter import ttk


from app.models.tarjeta import Tarjeta


COLUMNAS_DISPONIBLES = [
    ("por_hacer", "Por hacer"),
    ("en_proceso", "En proceso"),
    ("hecho", "Hecho"),
]

# Paleta inspirada en Jira
COLOR_FONDO_DIALOG = "#FFFFFF"
COLOR_TEXTO_LABEL = "#172B4D"
COLOR_BORDE_INPUT = "#DFE1E6"
COLOR_FONDO_INPUT = "#FFFFFF"
COLOR_TEXTO_INPUT = "#42526E"
COLOR_ERROR = "#DE350B"


def mostrar_dialogo_tarjeta(
    parent, titulo: str = "Nueva tarjeta", tarjeta: Tarjeta | None = None
) -> dict[str, str] | None:
    """Muestra un diálogo modal para crear o editar una tarjeta.

    Retorna un dict con 'titulo', 'descripcion' y 'columna' si se acepta,
    o None si se cancela.
    """
    dialogo = tk.Toplevel(parent)
    dialogo.title(titulo)
    dialogo.geometry("480x400")
    dialogo.transient(parent)
    dialogo.grab_set()
    dialogo.resizable(False, False)
    dialogo.configure(bg=COLOR_FONDO_DIALOG)

    resultado: dict[str, str] | None = None

    # Valores iniciales
    titulo_inicial = tarjeta.titulo if tarjeta else ""
    descripcion_inicial = tarjeta.descripcion if tarjeta else ""
    columna_inicial = tarjeta.columna if tarjeta else "por_hacer"

    # Formulario
    frame = tk.Frame(dialogo, bg=COLOR_FONDO_DIALOG)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(
        frame,
        text="Título",
        font=("Segoe UI", 10, "bold"),
        bg=COLOR_FONDO_DIALOG,
        fg=COLOR_TEXTO_LABEL,
        anchor="w",
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))
    entrada_titulo = tk.Entry(
        frame,
        width=40,
        font=("Segoe UI", 10),
        relief="solid",
        borderwidth=1,
        bg=COLOR_FONDO_INPUT,
        fg=COLOR_TEXTO_INPUT,
        insertbackground=COLOR_TEXTO_INPUT,
        highlightbackground=COLOR_BORDE_INPUT,
        highlightthickness=1,
    )
    entrada_titulo.grid(row=1, column=0, sticky="ew", pady=(0, 12))
    entrada_titulo.insert(0, titulo_inicial)

    tk.Label(
        frame,
        text="Descripción",
        font=("Segoe UI", 10, "bold"),
        bg=COLOR_FONDO_DIALOG,
        fg=COLOR_TEXTO_LABEL,
        anchor="w",
    ).grid(row=2, column=0, sticky="w", pady=(0, 6))
    entrada_descripcion = tk.Text(
        frame,
        width=30,
        height=5,
        wrap="word",
        font=("Segoe UI", 10),
        relief="solid",
        borderwidth=1,
        bg=COLOR_FONDO_INPUT,
        fg=COLOR_TEXTO_INPUT,
        insertbackground=COLOR_TEXTO_INPUT,
        highlightbackground=COLOR_BORDE_INPUT,
        highlightthickness=1,
    )
    entrada_descripcion.grid(row=3, column=0, sticky="ew", pady=(0, 12))
    entrada_descripcion.insert("1.0", descripcion_inicial)

    tk.Label(
        frame,
        text="Columna",
        font=("Segoe UI", 10, "bold"),
        bg=COLOR_FONDO_DIALOG,
        fg=COLOR_TEXTO_LABEL,
        anchor="w",
    ).grid(row=4, column=0, sticky="w", pady=(0, 6))

    # Mapeo de texto visible a id interno
    texto_a_id = {texto: id_col for id_col, texto in COLUMNAS_DISPONIBLES}
    id_a_texto = {id_col: texto for id_col, texto in COLUMNAS_DISPONIBLES}

    columna_seleccionada = tk.StringVar(value=id_a_texto.get(columna_inicial, "Por hacer"))
    combo_columna = tk.OptionMenu(
        frame,
        columna_seleccionada,
        *[texto for _, texto in COLUMNAS_DISPONIBLES],
    )
    combo_columna.configure(
        font=("Segoe UI", 10),
        bg=COLOR_FONDO_INPUT,
        fg=COLOR_TEXTO_INPUT,
        activebackground="#F4F5F7",
        activeforeground=COLOR_TEXTO_INPUT,
        relief="solid",
        borderwidth=1,
        highlightbackground=COLOR_BORDE_INPUT,
        highlightthickness=1,
    )
    combo_columna["menu"].configure(
        bg=COLOR_FONDO_INPUT,
        fg=COLOR_TEXTO_INPUT,
        activebackground="#0052CC",
        activeforeground="white",
        font=("Segoe UI", 10),
    )
    combo_columna.grid(row=5, column=0, sticky="ew", pady=(0, 12))

    frame.grid_columnconfigure(0, weight=1)

    # Mensaje de error para validaciones
    lbl_error = tk.Label(
        frame,
        text="El título es obligatorio.",
        font=("Segoe UI", 9, "italic"),
        bg=COLOR_FONDO_DIALOG,
        fg=COLOR_ERROR,
        anchor="w",
    )
    lbl_error.grid(row=6, column=0, sticky="w", pady=(0, 12))
    lbl_error.grid_remove()

    def mostrar_error(mensaje: str):
        lbl_error.configure(text=mensaje)
        lbl_error.grid()
        entrada_titulo.configure(highlightbackground=COLOR_ERROR, highlightthickness=2)

    def ocultar_error():
        lbl_error.grid_remove()
        entrada_titulo.configure(highlightbackground=COLOR_BORDE_INPUT, highlightthickness=1)

    def aceptar():
        nonlocal resultado
        titulo_texto = entrada_titulo.get().strip()
        if not titulo_texto:
            mostrar_error("El título es obligatorio.")
            return
        ocultar_error()
        texto_columna = columna_seleccionada.get()
        columna_id = texto_a_id.get(texto_columna, "por_hacer")
        resultado = {
            "titulo": titulo_texto,
            "descripcion": entrada_descripcion.get("1.0", "end-1c").strip(),
            "columna": columna_id,
        }
        dialogo.destroy()

    def cancelar():
        dialogo.destroy()

    entrada_titulo.bind("<KeyRelease>", lambda e: ocultar_error() if entrada_titulo.get().strip() else None)

    # Botones
    frame_botones = tk.Frame(dialogo, bg=COLOR_FONDO_DIALOG)
    frame_botones.pack(fill="x", padx=20, pady=(0, 20))

    btn_guardar = ttk.Button(
        frame_botones,
        text="Guardar",
        command=aceptar,
        style="JiraPrimary.TButton",
    )
    btn_guardar.pack(side="right", padx=(8, 0))

    btn_cancelar = ttk.Button(
        frame_botones,
        text="Cancelar",
        command=cancelar,
        style="JiraSecondary.TButton",
    )
    btn_cancelar.pack(side="right")

    entrada_titulo.focus_set()
    dialogo.bind("<Return>", lambda e: aceptar())
    dialogo.bind("<Escape>", lambda e: cancelar())
    dialogo.protocol("WM_DELETE_WINDOW", cancelar)

    parent.wait_window(dialogo)
    return resultado
```

## app/views/main_window.py

```python
"""Ventana principal de la aplicación."""

import tkinter as tk

from app.views.board_view import BoardView
from app.views.styles import configurar_estilos


# Paleta inspirada en Jira
COLOR_FONDO_VENTANA = "#FFFFFF"
COLOR_BARRA_SUPERIOR = "#0747A6"
COLOR_TEXTO_BARRA = "#FFFFFF"


class MainWindow(tk.Tk):
    """Ventana principal de Kanban Lite."""

    def __init__(self):
        super().__init__()
        self.title("Kanban Lite")
        self.geometry("1100x700")
        self.configure(bg=COLOR_FONDO_VENTANA)
        configurar_estilos(self)
        self._construir_ui()

    def _construir_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Barra superior estilo Jira
        barra_superior = tk.Frame(self, bg=COLOR_BARRA_SUPERIOR, height=48)
        barra_superior.grid(row=0, column=0, sticky="ew")
        barra_superior.grid_propagate(False)

        titulo = tk.Label(
            barra_superior,
            text="Kanban Lite",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_BARRA_SUPERIOR,
            fg=COLOR_TEXTO_BARRA,
            anchor="w",
        )
        titulo.pack(side="left", padx=16, pady=8)

        board = BoardView(self)
        board.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)


def main():
    """Punto de entrada de la aplicación."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
```

---

# 2. Explicación para el usuario final

## ¿Qué es Kanban Lite?

**Kanban Lite** es una aplicación de escritorio sencilla que permite organizar tareas en un tablero estilo Kanban. Es ideal para gestionar el trabajo de forma visual, dividiendo las tareas en tres columnas según su estado.

Las tres columnas del tablero son:

- **Por hacer**: tareas que aún no se han iniciado.
- **En proceso**: tareas en las que se está trabajando actualmente.
- **Hecho**: tareas finalizadas.

## ¿Qué puedo hacer con la aplicación?

- **Crear tarjetas**: añade nuevas tareas con un título y una descripción opcional.
- **Editar tarjetas**: modifica el título, la descripción o cambia la tarjeta de columna.
- **Mover tarjetas**: arrastra una tarjeta de una columna a otra para reflejar su avance.
- **Eliminar tarjetas**: borra una tarea del tablero después de confirmar la acción.
- **Persistencia automática**: todo lo que hagas se guarda de forma automática en una base de datos local. Al cerrar y volver a abrir la aplicación, las tarjetas siguen ahí.

## ¿Cómo funciona por dentro? (arquitectura)

La aplicación está organizada en capas separadas, lo que facilita su mantenimiento y ampliación:

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| **Modelos** | `app/models` | Define cómo es una tarjeta (sus datos). |
| **Servicios** | `app/services` | Contiene la lógica de negocio y las validaciones. |
| **Repositorios** | `app/repositories` | Se comunica con la base de datos para guardar y recuperar la información. |
| **Vistas** | `app/views` | Muestra la interfaz gráfica y permite al usuario interactuar. |

Esta separación significa que cada parte tiene un trabajo claro:

1. La **vista** recibe las acciones del usuario (crear, mover, editar, eliminar).
2. El **servicio** valida que las acciones sean correctas (por ejemplo, que el título no esté vacío o que la columna sea válida).
3. El **repositorio** se encarga de leer o escribir en la base de datos.
4. El **modelo** define la estructura de datos que viaja entre estas capas.

## ¿Qué tecnologías y librerías utiliza?

La aplicación está desarrollada en **Python** y utiliza únicamente **librerías estándar** incluidas con el propio lenguaje, por lo que no requiere instalar dependencias externas:

- **tkinter**: crea la interfaz gráfica de escritorio (ventanas, botones, listas, etc.).
- **sqlite3**: gestiona la base de datos local donde se guardan las tarjetas.
- **dataclasses**: simplifica la definición del modelo de datos de una tarjeta.
- **pathlib**: ayuda a localizar el archivo de la base de datos de forma segura.

## ¿Dónde se guardan mis datos?

Los datos se guardan en un archivo de base de datos SQLite llamado `kanban_lite.db`, ubicado dentro de la carpeta `db/` del proyecto. La base de datos se crea automáticamente la primera vez que se ejecuta la aplicación.

## ¿Cómo se ejecuta la aplicación?

Desde la carpeta raíz del proyecto:

```bash
python main.py
```

Al iniciarse, la aplicación crea la base de datos si no existe y abre la ventana principal del tablero.