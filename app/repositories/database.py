"""Conexión SQLite e inicialización de la base de datos."""

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "kanban_lite.db"


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
            CREATE TABLE IF NOT EXISTS tarjetas (
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
