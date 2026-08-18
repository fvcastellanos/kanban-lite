"""Lógica de negocio para tarjetas Kanban."""

from app.models.tarjeta import Tarjeta
from app.repositories.tarjeta_repository import TarjetaRepository


class TarjetaService:
    """Orquesta las operaciones sobre tarjetas y valida reglas."""

    COLUMNAS_VALIDAS = {"por_hacer", "en_proceso", "hecho"}

    def __init__(self, repository: TarjetaRepository | None = None):
        self._repo = repository or TarjetaRepository()

    def crear_tarjeta(self, titulo: str, descripcion: str = "", columna: str = "por_hacer") -> Tarjeta:
        """Crea una tarjeta validando los datos de entrada."""
        raise NotImplementedError

    def mover_tarjeta(self, tarjeta_id: int, columna_destino: str) -> Tarjeta:
        """Mueve una tarjeta a otra columna."""
        raise NotImplementedError

    def listar_tarjetas(self, columna: str) -> list[Tarjeta]:
        """Devuelve las tarjetas de una columna."""
        raise NotImplementedError

    def eliminar_tarjeta(self, tarjeta_id: int) -> None:
        """Elimina una tarjeta del tablero."""
        raise NotImplementedError
