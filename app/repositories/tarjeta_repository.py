"""Repositorio para operaciones CRUD de tarjetas."""

import sqlite3

from app.models.tarjeta import Tarjeta
from app.repositories.database import obtener_conexion


def _fila_a_tarjeta(fila: sqlite3.Row) -> Tarjeta:
    """Convierte una fila de SQLite en una instancia de Tarjeta."""
    return Tarjeta(
        id=fila["id"],
        titulo=fila["titulo"],
        descripcion=fila["descripcion"],
        columna=fila["columna"],
    )


class TarjetaRepository:
    """Acceso a datos para la entidad Tarjeta."""

    def crear(self, tarjeta: Tarjeta) -> Tarjeta:
        """Inserta una nueva tarjeta y actualiza su id."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                INSERT INTO tarjeta (titulo, descripcion, columna)
                VALUES (?, ?, ?)
                """,
                (tarjeta.titulo, tarjeta.descripcion, tarjeta.columna),
            )
            conn.commit()
            tarjeta.id = cursor.lastrowid
            return tarjeta
        finally:
            conn.close()

    def listar_por_columna(self, columna: str) -> list[Tarjeta]:
        """Devuelve todas las tarjetas de una columna."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                SELECT id, titulo, descripcion, columna
                FROM tarjeta
                WHERE columna = ?
                ORDER BY id ASC
                """,
                (columna,),
            )
            return [_fila_a_tarjeta(fila) for fila in cursor.fetchall()]
        finally:
            conn.close()

    def actualizar(self, tarjeta: Tarjeta) -> Tarjeta:
        """Actualiza una tarjeta existente."""
        if tarjeta.id is None:
            raise ValueError("No se puede actualizar una tarjeta sin id")

        conn = obtener_conexion()
        try:
            conn.execute(
                """
                UPDATE tarjeta
                SET titulo = ?,
                    descripcion = ?,
                    columna = ?
                WHERE id = ?
                """,
                (tarjeta.titulo, tarjeta.descripcion, tarjeta.columna, tarjeta.id),
            )
            conn.commit()
            return tarjeta
        finally:
            conn.close()

    def eliminar(self, tarjeta_id: int) -> None:
        """Elimina una tarjeta por su id."""
        conn = obtener_conexion()
        try:
            conn.execute(
                """
                DELETE FROM tarjeta
                WHERE id = ?
                """,
                (tarjeta_id,),
            )
            conn.commit()
        finally:
            conn.close()

    def obtener(self, tarjeta_id: int) -> Tarjeta | None:
        """Obtiene una tarjeta por su id."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                SELECT id, titulo, descripcion, columna
                FROM tarjeta
                WHERE id = ?
                """,
                (tarjeta_id,),
            )
            fila = cursor.fetchone()
            return _fila_a_tarjeta(fila) if fila else None
        finally:
            conn.close()

    def listar_todas(self) -> list[Tarjeta]:
        """Devuelve todas las tarjetas ordenadas por columna e id."""
        conn = obtener_conexion()
        try:
            cursor = conn.execute(
                """
                SELECT id, titulo, descripcion, columna
                FROM tarjeta
                ORDER BY columna ASC, id ASC
                """
            )
            return [_fila_a_tarjeta(fila) for fila in cursor.fetchall()]
        finally:
            conn.close()
