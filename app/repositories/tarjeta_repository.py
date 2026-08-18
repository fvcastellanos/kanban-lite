"""Repositorio para operaciones CRUD de tarjetas."""

import sqlite3
from typing import Iterable

from app.models.tarjeta import Tarjeta
from app.repositories.database import obtener_conexion


class TarjetaRepository:
    """Acceso a datos para la entidad Tarjeta."""

    def crear(self, tarjeta: Tarjeta) -> Tarjeta:
        """Inserta una nueva tarjeta y actualiza su id."""
        raise NotImplementedError

    def listar_por_columna(self, columna: str) -> list[Tarjeta]:
        """Devuelve todas las tarjetas de una columna."""
        raise NotImplementedError

    def actualizar(self, tarjeta: Tarjeta) -> Tarjeta:
        """Actualiza una tarjeta existente."""
        raise NotImplementedError

    def eliminar(self, tarjeta_id: int) -> None:
        """Elimina una tarjeta por su id."""
        raise NotImplementedError

    def obtener(self, tarjeta_id: int) -> Tarjeta | None:
        """Obtiene una tarjeta por su id."""
        raise NotImplementedError
