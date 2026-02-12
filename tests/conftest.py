"""
Fixtures reutilizables para las pruebas unitarias de SmartTask Organizer.

Proporciona instancias de Database con base de datos SQLite en memoria
(:memory:) para que cada test sea independiente y no afecte la BD real.
"""
import pytest
import sys
import os

# Agregar el directorio raíz al path para importar src.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import Database


@pytest.fixture
def db_limpia():
    """Crea una instancia de Database con BD en memoria, limpia y con categorías.

    Yields:
        Database: Instancia de Database con tablas creadas, 6 categorías
            por defecto y 5 tareas de ejemplo.
    """
    db = Database(db_name=":memory:")
    yield db


@pytest.fixture
def db_vacia():
    """Crea una instancia de Database en memoria y elimina las tareas de ejemplo.

    Yields:
        Database: Instancia con categorías pero sin tareas.
    """
    db = Database(db_name=":memory:")
    # Eliminar las tareas de ejemplo para empezar limpio
    conn = db.get_connection()
    conn.execute("DELETE FROM tareas")
    conn.commit()
    conn.close()
    yield db


@pytest.fixture
def tarea_ejemplo(db_vacia):
    """Crea una tarea de prueba en la BD vacía y retorna su ID.

    Returns:
        tuple: (Database, int) - Instancia de BD y el ID de la tarea creada.
    """
    tarea_id = db_vacia.crear_tarea(
        titulo="Tarea de prueba",
        descripcion="Descripción de prueba",
        fecha_limite="2026-12-31",
        prioridad="alta",
        categoria_id=1
    )
    return db_vacia, tarea_id


@pytest.fixture
def categorias_ids(db_vacia):
    """Retorna un diccionario {nombre: id} de las categorías por defecto.

    Returns:
        tuple: (Database, dict) - Instancia de BD y diccionario de categorías.
    """
    categorias = db_vacia.obtener_categorias()
    cat_dict = {cat['nombre']: cat['id'] for cat in categorias}
    return db_vacia, cat_dict
