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
