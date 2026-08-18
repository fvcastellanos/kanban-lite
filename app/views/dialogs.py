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


def mostrar_dialogo_tarjeta(
    parent, titulo: str = "Nueva tarjeta", tarjeta: Tarjeta | None = None
) -> dict[str, str] | None:
    """Muestra un diálogo modal para crear o editar una tarjeta.

    Retorna un dict con 'titulo', 'descripcion' y 'columna' si se acepta,
    o None si se cancela.
    """
    dialogo = tk.Toplevel(parent)
    dialogo.title(titulo)
    dialogo.geometry("480x360")
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

    def aceptar():
        nonlocal resultado
        titulo_texto = entrada_titulo.get().strip()
        if not titulo_texto:
            return
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
