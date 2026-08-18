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
        if self.id is None:
            self.id = 0
