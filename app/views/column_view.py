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
