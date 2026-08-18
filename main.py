"""Punto de entrada de Kanban Lite."""

from app.repositories.database import inicializar_base_de_datos
from app.views.main_window import main


if __name__ == "__main__":
    inicializar_base_de_datos()
    main()
