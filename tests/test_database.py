"""
Pruebas unitarias para src/database.py — Operaciones CRUD.

Cobertura: crear_tarea, obtener_todas_tareas, obtener_tarea,
actualizar_tarea, eliminar_tarea, marcar_como_completada,
obtener_categorias, obtener_estadisticas, init_db.
"""
import pytest


# ============================================================
# TESTS: Inicialización de la BD (init_db)
# ============================================================

class TestInitDB:
    """Tests para la inicialización de la base de datos."""

    def test_categorias_por_defecto(self, db_limpia):
        """Verifica que se crean 6 categorías por defecto (HU08)."""
        categorias = db_limpia.obtener_categorias()
        assert len(categorias) == 6

    def test_nombres_categorias(self, db_limpia):
        """Verifica los nombres de las 6 categorías por defecto."""
        categorias = db_limpia.obtener_categorias()
        nombres = [cat['nombre'] for cat in categorias]
        esperadas = ['Estudio', 'Finanzas', 'Hogar', 'Personal', 'Salud', 'Trabajo']
        assert sorted(nombres) == sorted(esperadas)

    def test_tareas_ejemplo(self, db_limpia):
        """Verifica que se insertan 5 tareas de ejemplo al inicializar."""
        tareas = db_limpia.obtener_todas_tareas()
        assert len(tareas) == 5

    def test_conexion_row_factory(self, db_limpia):
        """Verifica que las filas se acceden por nombre de columna."""
        tareas = db_limpia.obtener_todas_tareas()
        primera = tareas[0]
        # Debe poder accederse por nombre
        assert 'titulo' in primera.keys()
        assert 'estado' in primera.keys()


# ============================================================
# TESTS: Crear tarea (HU01)
# ============================================================

class TestCrearTarea:
    """Tests para la operación CREATE."""

    def test_crear_con_todos_los_campos(self, db_vacia, categorias_ids):
        """Crea una tarea con todos los campos y verifica que se guarda."""
        _, cats = categorias_ids
        tarea_id = db_vacia.crear_tarea(
            titulo="Tarea completa",
            descripcion="Descripción completa",
            fecha_limite="2026-12-31",
            prioridad="alta",
            categoria_id=cats['Trabajo']
        )
        assert tarea_id is not None
        assert isinstance(tarea_id, int)
        assert tarea_id > 0

    def test_crear_solo_titulo(self, db_vacia):
        """Crea una tarea con solo el título (mínimo obligatorio)."""
        tarea_id = db_vacia.crear_tarea(titulo="Solo título")
        tarea = db_vacia.obtener_tarea(tarea_id)
        assert tarea['titulo'] == "Solo título"
        assert tarea['descripcion'] == ""
        assert tarea['fecha_limite'] is None
        assert tarea['prioridad'] == "media"
        assert tarea['categoria_id'] is None

    def test_estado_inicial_pendiente(self, db_vacia):
        """Verifica que el estado inicial de una tarea es 'pendiente'."""
        tarea_id = db_vacia.crear_tarea(titulo="Nueva tarea")
        tarea = db_vacia.obtener_tarea(tarea_id)
        assert tarea['estado'] == "pendiente"

    def test_crear_con_categoria(self, db_vacia):
        """Verifica que se asigna la categoría correctamente (HU09)."""
        categorias = db_vacia.obtener_categorias()
        cat_estudio = next(c for c in categorias if c['nombre'] == 'Estudio')

        tarea_id = db_vacia.crear_tarea(
            titulo="Estudiar para examen",
            categoria_id=cat_estudio['id']
        )
        tarea = db_vacia.obtener_tarea(tarea_id)
        assert tarea['categoria_id'] == cat_estudio['id']
        assert tarea['categoria_nombre'] == 'Estudio'

    def test_crear_con_fecha_limite(self, db_vacia):
        """Verifica que la fecha límite se guarda correctamente (HU06)."""
        tarea_id = db_vacia.crear_tarea(
            titulo="Con fecha",
            fecha_limite="2026-06-15"
        )
        tarea = db_vacia.obtener_tarea(tarea_id)
        assert tarea['fecha_limite'] == "2026-06-15"

    def test_crear_multiples_tareas(self, db_vacia):
        """Verifica que se pueden crear varias tareas con IDs únicos."""
        id1 = db_vacia.crear_tarea(titulo="Tarea 1")
        id2 = db_vacia.crear_tarea(titulo="Tarea 2")
        id3 = db_vacia.crear_tarea(titulo="Tarea 3")
        assert id1 != id2 != id3
        assert len(db_vacia.obtener_todas_tareas()) == 3

    def test_crear_prioridades_validas(self, db_vacia):
        """Verifica que se aceptan las 3 prioridades válidas."""
        for prioridad in ['baja', 'media', 'alta']:
            tid = db_vacia.crear_tarea(titulo=f"Tarea {prioridad}", prioridad=prioridad)
            tarea = db_vacia.obtener_tarea(tid)
            assert tarea['prioridad'] == prioridad


# ============================================================
# TESTS: Obtener tareas (HU02)
# ============================================================

class TestObtenerTareas:
    """Tests para la operación READ."""

    def test_obtener_todas_con_datos(self, db_limpia):
        """Verifica que obtener_todas_tareas retorna las tareas existentes."""
        tareas = db_limpia.obtener_todas_tareas()
        assert len(tareas) > 0

    def test_obtener_todas_vacia(self, db_vacia):
        """Verifica que retorna lista vacía cuando no hay tareas."""
        tareas = db_vacia.obtener_todas_tareas()
        assert len(tareas) == 0

    def test_obtener_tarea_por_id(self, tarea_ejemplo):
        """Verifica que se puede obtener una tarea por su ID."""
        db, tarea_id = tarea_ejemplo
        tarea = db.obtener_tarea(tarea_id)
        assert tarea is not None
        assert tarea['titulo'] == "Tarea de prueba"
        assert tarea['descripcion'] == "Descripción de prueba"

    def test_obtener_tarea_inexistente(self, db_vacia):
        """Verifica que retorna None para un ID que no existe."""
        tarea = db_vacia.obtener_tarea(9999)
        assert tarea is None

    def test_obtener_incluye_categoria_nombre(self, tarea_ejemplo):
        """Verifica que la consulta incluye el nombre de la categoría."""
        db, tarea_id = tarea_ejemplo
        tarea = db.obtener_tarea(tarea_id)
        assert 'categoria_nombre' in tarea.keys()

    def test_filtrar_por_categoria(self, db_limpia):
        """Verifica el filtro por categoría (HU10)."""
        # Crear tarea con categoría específica
        categorias = db_limpia.obtener_categorias()
        cat_salud = next(c for c in categorias if c['nombre'] == 'Salud')

        db_limpia.crear_tarea(titulo="Tarea salud", categoria_id=cat_salud['id'])

        tareas_salud = db_limpia.obtener_todas_tareas(categoria_filtro="Salud")
        for tarea in tareas_salud:
            assert tarea['categoria_nombre'] == 'Salud'

    def test_filtrar_todas(self, db_limpia):
        """Verifica que filtro 'TODAS' retorna todas las tareas."""
        todas = db_limpia.obtener_todas_tareas(categoria_filtro="TODAS")
        sin_filtro = db_limpia.obtener_todas_tareas()
        assert len(todas) == len(sin_filtro)

    def test_filtrar_categoria_inexistente(self, db_limpia):
        """Verifica que filtrar por categoría inexistente retorna vacío."""
        tareas = db_limpia.obtener_todas_tareas(categoria_filtro="NoExiste")
        assert len(tareas) == 0


# ============================================================
# TESTS: Actualizar tarea (HU03)
# ============================================================

class TestActualizarTarea:
    """Tests para la operación UPDATE."""

    def test_actualizar_titulo(self, tarea_ejemplo):
        """Verifica que se puede actualizar el título."""
        db, tarea_id = tarea_ejemplo
        resultado = db.actualizar_tarea(tarea_id, titulo="Nuevo título")
        assert resultado is True

        tarea = db.obtener_tarea(tarea_id)
        assert tarea['titulo'] == "Nuevo título"

    def test_actualizar_multiples_campos(self, tarea_ejemplo):
        """Verifica que se pueden actualizar varios campos a la vez."""
        db, tarea_id = tarea_ejemplo
        db.actualizar_tarea(
            tarea_id,
            titulo="Actualizado",
            descripcion="Nueva descripción",
            prioridad="baja"
        )
        tarea = db.obtener_tarea(tarea_id)
        assert tarea['titulo'] == "Actualizado"
        assert tarea['descripcion'] == "Nueva descripción"
        assert tarea['prioridad'] == "baja"

    def test_actualizar_tarea_inexistente(self, db_vacia):
        """Verifica que actualizar un ID inexistente retorna False."""
        resultado = db_vacia.actualizar_tarea(9999, titulo="Nada")
        assert resultado is False

    def test_actualizar_sin_campos(self, tarea_ejemplo):
        """Verifica que actualizar sin campos retorna False."""
        db, tarea_id = tarea_ejemplo
        resultado = db.actualizar_tarea(tarea_id)
        assert resultado is False

    def test_actualizar_estado(self, tarea_ejemplo):
        """Verifica que se puede cambiar el estado directamente."""
        db, tarea_id = tarea_ejemplo
        db.actualizar_tarea(tarea_id, estado="completada")
        tarea = db.obtener_tarea(tarea_id)
        assert tarea['estado'] == "completada"


# ============================================================
# TESTS: Eliminar tarea (HU04)
# ============================================================

class TestEliminarTarea:
    """Tests para la operación DELETE."""

    def test_eliminar_existente(self, tarea_ejemplo):
        """Verifica que se puede eliminar una tarea existente."""
        db, tarea_id = tarea_ejemplo
        resultado = db.eliminar_tarea(tarea_id)
        assert resultado is True

        # Verificar que ya no existe
        tarea = db.obtener_tarea(tarea_id)
        assert tarea is None

    def test_eliminar_inexistente(self, db_vacia):
        """Verifica que eliminar un ID inexistente retorna False."""
        resultado = db_vacia.eliminar_tarea(9999)
        assert resultado is False

    def test_eliminar_no_afecta_otras(self, db_vacia):
        """Verifica que eliminar una tarea no borra las demás."""
        id1 = db_vacia.crear_tarea(titulo="Tarea 1")
        id2 = db_vacia.crear_tarea(titulo="Tarea 2")

        db_vacia.eliminar_tarea(id1)

        assert db_vacia.obtener_tarea(id2) is not None
        assert len(db_vacia.obtener_todas_tareas()) == 1


# ============================================================
# TESTS: Marcar como completada (HU05)
# ============================================================

class TestMarcarCompletada:
    """Tests para marcar tareas como completadas."""

    def test_completar_tarea(self, tarea_ejemplo):
        """Verifica que marcar como completada cambia el estado (HU05)."""
        db, tarea_id = tarea_ejemplo
        resultado = db.marcar_como_completada(tarea_id)
        assert resultado is True

        tarea = db.obtener_tarea(tarea_id)
        assert tarea['estado'] == "completada"

    def test_completar_inexistente(self, db_vacia):
        """Verifica que completar un ID inexistente retorna False."""
        resultado = db_vacia.marcar_como_completada(9999)
        assert resultado is False


# ============================================================
# TESTS: Categorías (HU08)
# ============================================================

class TestCategorias:
    """Tests para las operaciones con categorías."""

    def test_obtener_categorias(self, db_limpia):
        """Verifica que se obtienen las 6 categorías."""
        categorias = db_limpia.obtener_categorias()
        assert len(categorias) == 6

    def test_categorias_tienen_id_y_nombre(self, db_limpia):
        """Verifica que cada categoría tiene id y nombre."""
        categorias = db_limpia.obtener_categorias()
        for cat in categorias:
            assert cat['id'] is not None
            assert cat['nombre'] is not None
            assert len(cat['nombre']) > 0

    def test_categorias_orden_alfabetico(self, db_limpia):
        """Verifica que las categorías están ordenadas alfabéticamente."""
        categorias = db_limpia.obtener_categorias()
        nombres = [cat['nombre'] for cat in categorias]
        assert nombres == sorted(nombres)


# ============================================================
# TESTS: Estadísticas
# ============================================================

class TestEstadisticas:
    """Tests para las estadísticas de tareas."""

    def test_estadisticas_vacia(self, db_vacia):
        """Verifica estadísticas con 0 tareas."""
        stats = db_vacia.obtener_estadisticas()
        assert stats['total'] == 0
        assert stats['completadas'] == 0
        assert stats['pendientes'] == 0
        assert stats['vencidas'] == 0

    def test_estadisticas_con_tareas(self, db_vacia):
        """Verifica conteos correctos por estado."""
        db_vacia.crear_tarea(titulo="Pendiente 1")
        db_vacia.crear_tarea(titulo="Pendiente 2")
        id3 = db_vacia.crear_tarea(titulo="Completada")
        db_vacia.marcar_como_completada(id3)

        stats = db_vacia.obtener_estadisticas()
        assert stats['total'] == 3
        assert stats['completadas'] == 1
        assert stats['pendientes'] == 2

    def test_estadisticas_retorna_dict(self, db_vacia):
        """Verifica que estadísticas retorna un diccionario."""
        stats = db_vacia.obtener_estadisticas()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'completadas' in stats
        assert 'pendientes' in stats
        assert 'vencidas' in stats

    def test_estadisticas_tarea_vencida(self, db_vacia):
        """Verifica que tareas con fecha pasada se cuentan como vencidas (HU07)."""
        db_vacia.crear_tarea(
            titulo="Vencida",
            fecha_limite="2020-01-01"  # Fecha en el pasado
        )
        stats = db_vacia.obtener_estadisticas()
        assert stats['vencidas'] >= 1
