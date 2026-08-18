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
        titulo_limpio = titulo.strip()
        if not titulo_limpio:
            raise ValueError("El título de la tarjeta no puede estar vacío")

        if columna not in self.COLUMNAS_VALIDAS:
            raise ValueError(f"Columna no válida: {columna}")

        tarjeta = Tarjeta(
            titulo=titulo_limpio,
            descripcion=descripcion.strip(),
            columna=columna,
        )
        return self._repo.crear(tarjeta)

    def mover_tarjeta(self, tarjeta_id: int, columna_destino: str) -> Tarjeta:
        """Mueve una tarjeta a otra columna."""
        if columna_destino not in self.COLUMNAS_VALIDAS:
            raise ValueError(f"Columna destino no válida: {columna_destino}")

        tarjeta = self._repo.obtener(tarjeta_id)
        if tarjeta is None:
            raise ValueError(f"No existe la tarjeta con id {tarjeta_id}")

        if tarjeta.columna == columna_destino:
            return tarjeta

        tarjeta.columna = columna_destino
        return self._repo.actualizar(tarjeta)

    def listar_tarjetas(self, columna: str) -> list[Tarjeta]:
        """Devuelve las tarjetas de una columna."""
        if columna not in self.COLUMNAS_VALIDAS:
            raise ValueError(f"Columna no válida: {columna}")
        return self._repo.listar_por_columna(columna)

    def eliminar_tarjeta(self, tarjeta_id: int) -> None:
        """Elimina una tarjeta del tablero."""
        self._repo.eliminar(tarjeta_id)

    def actualizar_tarjeta(
        self,
        tarjeta_id: int,
        titulo: str | None = None,
        descripcion: str | None = None,
        columna: str | None = None,
    ) -> Tarjeta:
        """Actualiza una tarjeta existente validando los datos."""
        tarjeta = self._repo.obtener(tarjeta_id)
        if tarjeta is None:
            raise ValueError(f"No existe la tarjeta con id {tarjeta_id}")

        if titulo is not None:
            titulo_limpio = titulo.strip()
            if not titulo_limpio:
                raise ValueError("El título de la tarjeta no puede estar vacío")
            tarjeta.titulo = titulo_limpio

        if descripcion is not None:
            tarjeta.descripcion = descripcion.strip()

        if columna is not None:
            if columna not in self.COLUMNAS_VALIDAS:
                raise ValueError(f"Columna no válida: {columna}")
            tarjeta.columna = columna

        return self._repo.actualizar(tarjeta)
