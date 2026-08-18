"""Vista del tablero Kanban."""

import tkinter as tk
from tkinter import ttk

from app.models.tarjeta import Tarjeta
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
    """Representación visual del tablero con 3 columnas y tarjetas dummy."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._tarjetas: list[Tarjeta] = []
        self._columnas: dict[str, ColumnView] = {}
        self._construir_ui()
        self._cargar_tarjetas_dummy()

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

    def _cargar_tarjetas_dummy(self):
        """Carga datos de prueba para visualizar el tablero."""
        self._tarjetas = [
            Tarjeta(id=1, titulo="Tarea 1", descripcion="Descripción inicial", columna="por_hacer"),
            Tarjeta(id=2, titulo="Tarea 2", descripcion="En progreso", columna="en_proceso"),
            Tarjeta(id=3, titulo="Tarea 3", descripcion="Finalizada", columna="hecho"),
        ]
        self._refrescar_tablero()

    def _refrescar_tablero(self):
        """Vuelve a dibujar todas las tarjetas en sus columnas."""
        for columna in self._columnas.values():
            columna.limpiar()

        for tarjeta in self._tarjetas:
            columna = self._columnas.get(tarjeta.columna)
            if columna:
                columna.agregar_tarjeta(tarjeta)

    def _mover_tarjeta(self, tarjeta: Tarjeta, columna_destino: str):
        """Mueve una tarjeta a otra columna."""
        if columna_destino not in self._columnas:
            return
        tarjeta.columna = columna_destino
        self._refrescar_tablero()

    def _crear_tarjeta(self):
        """Abre el diálogo para crear una nueva tarjeta."""
        resultado = mostrar_dialogo_tarjeta(self)
        if resultado:
            nuevo_id = max((t.id for t in self._tarjetas), default=0) + 1
            nueva_tarjeta = Tarjeta(
                id=nuevo_id,
                titulo=resultado["titulo"],
                descripcion=resultado["descripcion"],
                columna=resultado.get("columna", "por_hacer"),
            )
            self._tarjetas.append(nueva_tarjeta)
            self._refrescar_tablero()

    def _editar_tarjeta(self, tarjeta: Tarjeta):
        """Abre el diálogo para editar una tarjeta existente."""
        resultado = mostrar_dialogo_tarjeta(self, titulo="Editar tarjeta", tarjeta=tarjeta)
        if resultado:
            tarjeta.titulo = resultado["titulo"]
            tarjeta.descripcion = resultado["descripcion"]
            tarjeta.columna = resultado.get("columna", tarjeta.columna)
            self._refrescar_tablero()

    def _eliminar_tarjeta(self, tarjeta: Tarjeta):
        """Elimina una tarjeta del tablero."""
        self._tarjetas = [t for t in self._tarjetas if t.id != tarjeta.id]
        self._refrescar_tablero()
