"""
Módulo de base de datos para SmartTask Organizer.

Gestiona la persistencia de datos mediante SQLite. Define la clase Database
que encapsula todas las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
sobre las tablas 'tareas' y 'categorias'.

Tablas:
    - categorias: Almacena las categorías disponibles (HU08).
      Campos: id, nombre, descripcion.
    - tareas: Almacena las tareas del usuario (HU01-HU06).
      Campos: id, titulo, descripcion, fecha_limite, estado, prioridad,
      categoria_id, fecha_creacion.

Uso:
    from src.database import db
    db.crear_tarea(titulo="Mi tarea", prioridad="alta")
"""
import sqlite3
import os
from datetime import datetime

class Database:
    """Clase que gestiona la conexión y operaciones con la base de datos SQLite.

    Encapsula todas las operaciones CRUD necesarias para el manejo de tareas
    y categorías. Al instanciarse, crea automáticamente las tablas si no
    existen e inserta categorías y tareas de ejemplo por defecto.

    Attributes:
        db_name (str): Nombre del archivo de base de datos SQLite.

    Historias de usuario relacionadas:
        - HU01: Crear tarea
        - HU02: Listar tareas
        - HU03: Editar tarea
        - HU04: Eliminar tarea
        - HU05: Completar tarea
        - HU06: Fecha límite
        - HU07: Detectar vencidas (consulta de estadísticas)
        - HU08: Crear categoría (categorías por defecto)
        - HU09: Asignar categoría (campo categoria_id en tareas)
        - HU10: Filtrar por categoría (consulta con filtro)
    """

    def __init__(self, db_name="smarttask.db"):
        """Inicializa la instancia de Database y crea las tablas si no existen.

        Args:
            db_name (str): Nombre del archivo de base de datos. Por defecto
                es 'smarttask.db' en el directorio actual.
        """
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos SQLite.

        Configura row_factory como sqlite3.Row para que los resultados
        de las consultas se puedan acceder tanto por índice como por
        nombre de columna (diccionario).

        Returns:
            sqlite3.Connection: Objeto de conexión activa a la base de datos.
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa la base de datos creando las tablas y datos por defecto.

        Crea las tablas 'categorias' y 'tareas' si no existen (HU08).
        Inserta 6 categorías por defecto: Trabajo, Personal, Hogar,
        Estudio, Salud y Finanzas. Si la tabla de tareas está vacía,
        inserta 5 tareas de ejemplo para demostración.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de categorías
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT
        )
        ''')
        
        # Tabla de tareas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            fecha_limite TEXT,
            estado TEXT CHECK(estado IN ('pendiente', 'completada', 'vencida')) DEFAULT 'pendiente',
            prioridad TEXT CHECK(prioridad IN ('baja', 'media', 'alta')) DEFAULT 'media',
            categoria_id INTEGER,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        ''')
        
        # Insertar categorías por defecto
        categorias_default = [
            ('Trabajo', 'Tareas relacionadas con el trabajo'),
            ('Personal', 'Tareas personales'),
            ('Hogar', 'Tareas del hogar'),
            ('Estudio', 'Tareas académicas'),
            ('Salud', 'Tareas de salud'),
            ('Finanzas', 'Tareas financieras')
        ]
        
        for nombre, descripcion in categorias_default:
            cursor.execute('INSERT OR IGNORE INTO categorias (nombre, descripcion) VALUES (?, ?)', 
                          (nombre, descripcion))
        
        # Verificar si hay tareas de ejemplo
        cursor.execute("SELECT COUNT(*) FROM tareas")
        if cursor.fetchone()[0] == 0:
            # Obtener IDs de categorías
            cursor.execute("SELECT id, nombre FROM categorias")
            categorias = {row['nombre']: row['id'] for row in cursor.fetchall()}
            
            tareas_ejemplo = [
                ('Revisar informe trimestral', 'Revisar datos y preparar presentación', 
                 '2024-12-15', 'pendiente', 'alta', categorias.get('Trabajo')),
                ('Comprar víveres', 'Ir al supermercado', 
                 '2024-11-30', 'pendiente', 'media', categorias.get('Hogar')),
                ('Estudiar para examen', 'Repasar capítulos 5-8', 
                 '2024-12-10', 'pendiente', 'alta', categorias.get('Estudio')),
                ('Llamar al médico', 'Pedir cita para revisión', 
                 None, 'completada', 'baja', categorias.get('Salud')),
                ('Enviar reporte semanal', 'Enviar por correo al equipo', 
                 '2024-11-25', 'completada', 'media', categorias.get('Trabajo')),
            ]
            
            for tarea in tareas_ejemplo:
                cursor.execute('''
                INSERT INTO tareas (titulo, descripcion, fecha_limite, estado, prioridad, categoria_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', tarea)
        
        conn.commit()
        conn.close()
        print(f"✅ Base de datos '{self.db_name}' inicializada")
    
    # ===== OPERACIONES CRUD =====
    
    def crear_tarea(self, titulo, descripcion="", fecha_limite=None, 
                   prioridad="media", categoria_id=None):
        """Crea una nueva tarea en la base de datos (HU01).

        Inserta un registro en la tabla 'tareas' con los datos
        proporcionados. El estado inicial siempre es 'pendiente'.
        La categoría se asigna opcionalmente (HU09).

        Args:
            titulo (str): Título de la tarea. Campo obligatorio.
            descripcion (str): Descripción detallada. Por defecto vacía.
            fecha_limite (str): Fecha límite en formato 'YYYY-MM-DD' (HU06).
                None si no tiene fecha límite.
            prioridad (str): Nivel de prioridad. Valores permitidos:
                'baja', 'media' (por defecto), 'alta'.
            categoria_id (int): ID de la categoría a asignar (HU09).
                None si no se asigna categoría.

        Returns:
            int: ID autogenerado de la tarea recién creada.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO tareas (titulo, descripcion, fecha_limite, prioridad, categoria_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (titulo, descripcion, fecha_limite, prioridad, categoria_id))
        
        conn.commit()
        tarea_id = cursor.lastrowid
        conn.close()
        return tarea_id
    
    def obtener_todas_tareas(self, categoria_filtro=None):
        """Obtiene todas las tareas, opcionalmente filtradas por categoría (HU02, HU10).

        Realiza un LEFT JOIN con la tabla de categorías para incluir el
        nombre de la categoría. Los resultados se ordenan por:
            1. Estado (pendiente > vencida > completada)
            2. Prioridad (alta > media > baja)
            3. Fecha límite ascendente

        Args:
            categoria_filtro (str): Nombre de la categoría para filtrar (HU10).
                Si es None o 'TODAS', retorna todas las tareas sin filtro.

        Returns:
            list[sqlite3.Row]: Lista de tareas. Cada elemento es un Row
                con campos: id, titulo, descripcion, fecha_limite, estado,
                prioridad, categoria_id, fecha_creacion, categoria_nombre.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if categoria_filtro and categoria_filtro != "TODAS":
            cursor.execute('''
            SELECT t.*, c.nombre as categoria_nombre 
            FROM tareas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE c.nombre = ?
            ORDER BY 
                CASE t.estado 
                    WHEN 'pendiente' THEN 1
                    WHEN 'vencida' THEN 2
                    WHEN 'completada' THEN 3
                END,
                CASE t.prioridad
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baja' THEN 3
                END,
                t.fecha_limite ASC
            ''', (categoria_filtro,))
        else:
            cursor.execute('''
            SELECT t.*, c.nombre as categoria_nombre 
            FROM tareas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            ORDER BY 
                CASE t.estado 
                    WHEN 'pendiente' THEN 1
                    WHEN 'vencida' THEN 2
                    WHEN 'completada' THEN 3
                END,
                CASE t.prioridad
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baja' THEN 3
                END,
                t.fecha_limite ASC
            ''')
        
        tareas = cursor.fetchall()
        conn.close()
        return tareas
    
    def obtener_tarea(self, tarea_id):
        """Obtiene una tarea específica por su ID.

        Realiza un LEFT JOIN con categorías para incluir el nombre
        de la categoría asignada.

        Args:
            tarea_id (int): ID único de la tarea a buscar.

        Returns:
            sqlite3.Row: Datos de la tarea con campos: id, titulo,
                descripcion, fecha_limite, estado, prioridad,
                categoria_id, fecha_creacion, categoria_nombre.
                Retorna None si la tarea no existe.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT t.*, c.nombre as categoria_nombre 
        FROM tareas t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        WHERE t.id = ?
        ''', (tarea_id,))
        
        tarea = cursor.fetchone()
        conn.close()
        return tarea
    
    def actualizar_tarea(self, tarea_id, **kwargs):
        """Actualiza los campos de una tarea existente (HU03).

        Permite actualizar cualquier combinación de campos de la tarea
        usando argumentos con nombre. Solo se actualizan los campos
        que se pasan como argumento y cuyo valor no sea None.

        Args:
            tarea_id (int): ID de la tarea a actualizar.
            **kwargs: Campos a actualizar. Claves válidas:
                - titulo (str): Nuevo título.
                - descripcion (str): Nueva descripción.
                - fecha_limite (str): Nueva fecha en formato 'YYYY-MM-DD' (HU06).
                - estado (str): Nuevo estado ('pendiente', 'completada', 'vencida').
                - prioridad (str): Nueva prioridad ('baja', 'media', 'alta').
                - categoria_id (int): Nueva categoría (HU09).

        Returns:
            bool: True si se actualizó al menos una fila, False en caso
                contrario (tarea no encontrada o sin campos para actualizar).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        campos = []
        valores = []
        
        for key, value in kwargs.items():
            if value is not None:
                campos.append(f"{key} = ?")
                valores.append(value)
        
        if not campos:
            conn.close()
            return False
        
        valores.append(tarea_id)
        query = f"UPDATE tareas SET {', '.join(campos)} WHERE id = ?"
        
        cursor.execute(query, valores)
        conn.commit()
        afectadas = cursor.rowcount
        conn.close()
        
        return afectadas > 0
    
    def eliminar_tarea(self, tarea_id):
        """Elimina una tarea de la base de datos por su ID (HU04).

        Ejecuta un DELETE permanente del registro. Esta acción es
        irreversible a nivel de base de datos, aunque el UndoManager
        puede restaurar la tarea si fue registrada previamente.

        Args:
            tarea_id (int): ID de la tarea a eliminar.

        Returns:
            bool: True si se eliminó la tarea (existía), False si no
                se encontró ninguna tarea con ese ID.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tareas WHERE id = ?', (tarea_id,))
        conn.commit()
        afectadas = cursor.rowcount
        conn.close()
        
        return afectadas > 0
    
    def marcar_como_completada(self, tarea_id):
        """Marca una tarea como completada cambiando su estado (HU05).

        Internamente llama a actualizar_tarea() con estado='completada'.

        Args:
            tarea_id (int): ID de la tarea a completar.

        Returns:
            bool: True si se actualizó correctamente, False si la tarea
                no existe.
        """
        return self.actualizar_tarea(tarea_id, estado='completada')
    
    def obtener_categorias(self):
        """Obtiene todas las categorías disponibles (HU08).

        Retorna las categorías ordenadas alfabéticamente por nombre.

        Returns:
            list[sqlite3.Row]: Lista de categorías. Cada elemento
                tiene campos: id, nombre, descripcion.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM categorias ORDER BY nombre')
        categorias = cursor.fetchall()
        conn.close()
        return categorias
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas generales de las tareas (funcionalidad adicional).

        Calcula conteos agregados de tareas por estado. Las tareas
        pendientes con fecha límite pasada se cuentan como vencidas (HU07).

        Returns:
            dict: Diccionario con las claves:
                - 'total' (int): Número total de tareas.
                - 'completadas' (int): Tareas con estado 'completada'.
                - 'pendientes' (int): Tareas pendientes no vencidas.
                - 'vencidas' (int): Tareas vencidas o pendientes con
                  fecha límite pasada.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SQLite date('now') es UTC. Usamos date('now', 'localtime') para mejor precisión local
        cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as completadas,
            SUM(CASE WHEN estado = 'pendiente' AND fecha_limite >= date('now', 'localtime') THEN 1 
                     WHEN estado = 'pendiente' AND fecha_limite IS NULL THEN 1
                     ELSE 0 END) as pendientes,
            SUM(CASE WHEN estado = 'vencida' THEN 1
                     WHEN estado = 'pendiente' AND fecha_limite < date('now', 'localtime') THEN 1 
                     ELSE 0 END) as vencidas
        FROM tareas
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        return dict(stats)

# Instancia global de la base de datos
db = Database()