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
