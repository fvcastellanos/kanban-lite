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
