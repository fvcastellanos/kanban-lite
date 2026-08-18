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
