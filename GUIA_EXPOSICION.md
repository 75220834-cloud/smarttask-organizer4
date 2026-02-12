# 📋 GUÍA COMPLETA DE EXPOSICIÓN — SmartTask Organizer

---

## 1. 🗄️ BASE DE DATOS (SQLite)

### Qué decir al profesor:

> "Utilicé SQLite con `sqlite3` de Python. La base de datos tiene 2 tablas
> con relaciones PK/FK, constraints CHECK para validaciones y ejecución
> automática al iniciar la app."

### Mostrar en el código (`database.py` líneas 82-102):

```sql
-- TABLA categorias
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- PK autoincremental
    nombre TEXT NOT NULL UNIQUE,             -- Validación: no nulo, único
    descripcion TEXT
);

-- TABLA tareas
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                                    -- PK
    titulo TEXT NOT NULL,                                                     -- Validación
    descripcion TEXT,
    fecha_limite TEXT,
    estado TEXT CHECK(estado IN ('pendiente','completada','vencida')),        -- CHECK constraint
    prioridad TEXT CHECK(prioridad IN ('baja','media','alta')),              -- CHECK constraint
    categoria_id INTEGER,                                                    -- FK
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)                     -- Relación FK→PK
);
```

### Qué señalar con el dedo:

1. **PK**: `id INTEGER PRIMARY KEY AUTOINCREMENT` en ambas tablas
2. **FK**: `FOREIGN KEY (categoria_id) REFERENCES categorias(id)` — tareas apunta a categorías
3. **Validaciones CHECK**: Estado solo puede ser 3 valores, prioridad solo 3 valores
4. **NOT NULL / UNIQUE**: `nombre TEXT NOT NULL UNIQUE` en categorías
5. **DEFAULT**: `DEFAULT CURRENT_TIMESTAMP` para fecha de creación
6. **Ejecución automática**: Mostrar que `init_db()` se llama en el `__init__` (línea 54) — la BD se crea sola al ejecutar

### Mostrar en DB Browser for SQLite:

- Abrir `smarttask.db`
- Pestaña **"Database Structure"** → Mostrar las 2 tablas y sus columnas
- Pestaña **"Browse Data"** → Mostrar datos reales

### Diagrama de relación (dibujar en pizarra o slide):

```
┌──────────────┐         ┌──────────────────────┐
│  categorias  │         │       tareas         │
├──────────────┤         ├──────────────────────┤
│ PK id        │◄────────│ FK categoria_id      │
│    nombre    │   1:N   │ PK id                │
│    descripcion│        │    titulo             │
└──────────────┘         │    descripcion        │
                         │    fecha_limite       │
                         │    estado (CHECK)     │
                         │    prioridad (CHECK)  │
                         │    fecha_creacion     │
                         └──────────────────────┘
```

**Relación: 1 categoría → N tareas (uno a muchos)**

---

## 2. 📝 CRUD (Create, Read, Update, Delete)

### Qué decir:

> "Implementé las 4 operaciones CRUD completas con manejo de errores
> try/except en cada operación, validaciones de datos y la funcionalidad
> de deshacer acciones con Ctrl+Z."

### Mostrar en el código (`database.py`):

| Operación | Método | Línea | HU |
|-----------|--------|-------|-----|
| **CREATE** | `crear_tarea()` | 151 | HU01 |
| **READ** | `obtener_todas_tareas()` | 185 | HU02 |
| **READ** | `obtener_tarea()` | 248 | HU02 |
| **UPDATE** | `actualizar_tarea()` | 277 | HU03 |
| **DELETE** | `eliminar_tarea()` | 323 | HU04 |
| **UPDATE** | `marcar_como_completada()` | 347 | HU05 |

### Demostración en vivo:

1. **CREATE**: Abrir app → "+ NUEVA TAREA" → Llenar campos → Guardar → Ver en tabla
2. **READ**: Las tareas aparecen en la tabla principal automáticamente
3. **UPDATE**: Seleccionar tarea → "EDITAR" → Cambiar título → Actualizar
4. **DELETE**: Seleccionar tarea → "ELIMINAR" → Confirmar 3 pasos → Verificar que desapareció

### Validaciones adicionales que mencionar:

- Título obligatorio (no se puede guardar vacío)
- Fecha no puede ser en el pasado
- Formato de fecha DD/MM/AAAA validado
- Prioridad limitada a baja/media/alta por CHECK constraint
- Deshacer con **Ctrl+Z** (patrón Pila LIFO en `undo_manager.py`)

### Manejo de errores que mostrar:

- Intentar guardar sin título → muestra error
- Poner fecha inválida → muestra error
- Cada operación envuelta en `try/except`

---

## 3. 🧪 PRUEBAS UNITARIAS (pytest)

### Qué decir:

> "Implementé 42 pruebas unitarias con pytest usando fixtures reutilizables
> y una base de datos en memoria (:memory:) para que cada test sea
> independiente. Cubro CRUD completo, edge cases y estadísticas."

### Mostrar los archivos:

| Archivo | Tests | Qué prueba |
|---------|-------|------------|
| `tests/conftest.py` | 4 fixtures | BD en memoria, tarea ejemplo, categorías |
| `tests/test_database.py` | 30 tests | Todo el CRUD + estadísticas + edge cases |
| `tests/test_undo_manager.py` | 12 tests | Pila LIFO, deshacer eliminar/completar |

### Ejecutar en vivo:

```cmd
run_tests.bat
```

O manualmente:
```cmd
.venv\Scripts\activate
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Fixtures que explicar (`conftest.py`):

> "Uso fixtures de pytest para crear bases de datos temporales en memoria.
> Así cada test es independiente y no afecta la BD real."

```python
@pytest.fixture
def db_vacia():
    """BD en memoria sin tareas — cada test empieza limpio."""
    db = Database(db_name=":memory:")
    conn = db.get_connection()
    conn.execute("DELETE FROM tareas")
    conn.commit()
    conn.close()
    yield db
```

### Edge cases que mencionar:

- Obtener tarea con ID inexistente (9999) → retorna None
- Eliminar tarea inexistente → retorna False
- Actualizar sin campos → retorna False
- Deshacer con pila vacía → retorna None
- Estadísticas con 0 tareas → todos los conteos en 0
- Tarea con fecha pasada → se cuenta como vencida

---

## 4. 🏗️ ESTRUCTURA DE CÓDIGO

### Qué decir:

> "El proyecto sigue una arquitectura modular donde cada archivo tiene
> una responsabilidad específica. Sigue PEP8 y tiene documentación
> Google-style completa."

### Mostrar la estructura:

```
smarttask-organizer4/
├── run.py              ← Punto de entrada (verifica estructura)
├── src/
│   ├── database.py     ← MODELO (datos + CRUD)
│   ├── main.py         ← VISTA + CONTROLADOR (GUI principal)
│   ├── dialogos.py     ← VISTA (ventanas emergentes)
│   ├── voice.py        ← SERVICIO (reconocimiento de voz)
│   └── undo_manager.py ← SERVICIO (deshacer acciones)
├── tests/              ← Pruebas unitarias
└── DOC/                ← Documentación
```

### Patrón de arquitectura:

> "Aunque no es MVC estricto, el proyecto separa responsabilidades:
> - `database.py` = Modelo (datos)
> - `main.py` + `dialogos.py` = Vista (GUI)
> - La lógica de negocio se distribuye entre los módulos"

### PEP8:

- Imports organizados al inicio de cada archivo
- Nombres en español (consistente con el dominio del proyecto)
- Clases en CamelCase: `SmartTaskApp`, `CrearTareaDialog`
- Métodos en snake_case: `crear_tarea`, `obtener_categorias`
- Constantes implícitas en MAYÚSCULAS: `COLORES` en main.py

---

## 5. 📂 GIT

### Qué mostrar:

- **`.gitignore`** en la raíz → Excluye `.venv/`, `__pycache__/`, `smarttask.db`, IDE
- **`README.md`** completo → Tiene setup, uso, estructura, HUs, cómo ejecutar tests

### Qué decir del README:

> "El README incluye: descripción del proyecto, tabla de 12 historias de
> usuario, tecnologías, requisitos previos, instalación paso a paso,
> guía de uso, estructura del proyecto y cómo ejecutar los tests."

---

## 6. 📖 DOCUMENTACIÓN

### Qué decir:

> "Todos los módulos, clases y métodos tienen docstrings estilo Google.
> Incluyen Args, Returns y Raises donde aplica. Cada docstring
> referencia la Historia de Usuario que implementa."

### Mostrar un ejemplo en vivo (`database.py`):

```python
def crear_tarea(self, titulo, descripcion="", fecha_limite=None,
               prioridad="media", categoria_id=None):
    """Crea una nueva tarea en la base de datos (HU01).

    Args:
        titulo (str): Título de la tarea. Campo obligatorio.
        descripcion (str): Descripción detallada. Por defecto vacía.
        fecha_limite (str): Fecha en formato 'YYYY-MM-DD' (HU06).
        prioridad (str): 'baja', 'media' (defecto), 'alta'.
        categoria_id (int): ID de la categoría (HU09).

    Returns:
        int: ID autogenerado de la tarea creada.
    """
```

### Generar documentación automática (si lo piden):

```cmd
.venv\Scripts\activate
python -m pydoc src.database
```

---

## 7. 🎯 HISTORIAS DE USUARIO (HU01-HU12)

### Tabla completa para la exposición:

| HU   | Nombre            | Archivo principal    | Método/función clave          |
|------|-------------------|----------------------|-------------------------------|
| HU01 | Crear tarea       | `database.py`        | `crear_tarea()`               |
| HU02 | Listar tareas     | `database.py`        | `obtener_todas_tareas()`      |
| HU03 | Editar tarea      | `dialogos.py`        | `EditarTareaDialog`           |
| HU04 | Eliminar tarea    | `dialogos.py`        | `EliminarTareaDialog` (3 pasos)|
| HU05 | Completar tarea   | `database.py`        | `marcar_como_completada()`    |
| HU06 | Fecha límite      | `dialogos.py`        | Validación en `_guardar()`    |
| HU07 | Detectar vencidas | `database.py`        | `obtener_estadisticas()`      |
| HU08 | Crear categorías  | `database.py`        | `init_db()` (6 categorías)    |
| HU09 | Asignar categoría | `dialogos.py`        | Combobox en formulario        |
| HU10 | Filtrar categoría | `main.py`            | RadioButtons + filtro         |
| HU11 | Tarea por voz     | `voice.py`           | `escuchar_y_parsear()`        |
| HU12 | Notificaciones    | `main.py`            | `_verificar_notificaciones()` |

---

## 8. 🖥️ DEMOSTRACIÓN EN VIVO (orden sugerido)

### Paso a paso para la demo:

1. **Ejecutar la app**: `python run.py` → Mostrar que inicia correctamente
2. **Mostrar tabla**: Señalar columnas, colores por estado, leyenda
3. **Crear tarea manual**: "+ NUEVA TAREA" → Llenar todos los campos → Guardar
4. **Crear tarea por VOZ**: 🎤 "DICTAR TAREA COMPLETA" → Hablar → Ver campos rellenados
5. **Editar tarea**: Seleccionar → "EDITAR" → Cambiar datos → Actualizar
6. **Completar tarea**: Seleccionar → "COMPLETAR" → Ver cambio de color a verde
7. **Deshacer (Ctrl+Z)**: Presionar Ctrl+Z → Ver que vuelve a pendiente
8. **Eliminar tarea**: Seleccionar → "ELIMINAR" → Pasar los 3 pasos
9. **Filtrar**: Clic en RadioButtons de categoría → Ver filtrado
10. **Estadísticas**: "GRÁFICOS" → Mostrar gráfico de pastel
11. **Exportar CSV**: "EXPORTAR" → Guardar archivo
12. **Ejecutar tests**: Abrir terminal → `run_tests.bat` → Mostrar todos PASSED
13. **Mostrar BD**: Abrir `smarttask.db` en DB Browser → Mostrar estructura

---

## 9. 🔧 TECNOLOGÍAS (para mencionarlas rápido)

- **Python 3.8+** — Lenguaje principal
- **Tkinter** — GUI de escritorio
- **SQLite3** — Base de datos embebida
- **SpeechRecognition** — Reconocimiento de voz (Google API)
- **pyttsx3** — Texto a voz offline
- **sounddevice** — Grabación de audio (reemplaza PyAudio)
- **matplotlib** — Gráficos estadísticos
- **plyer** — Notificaciones de Windows
- **pytest** — Pruebas unitarias

---

## 10. 💡 PREGUNTAS FRECUENTES DEL PROFESOR

### "¿Por qué no usaste SQLAlchemy?"

> "Opté por sqlite3 directo porque me permitió tener control total sobre
> las consultas SQL y definir relaciones PK/FK, constraints CHECK y
> validaciones directamente en el esquema. El resultado funcional es
> equivalente: tengo modelos con relaciones, validaciones y ejecución
> automática."

### "¿Cómo funciona el deshacer?"

> "Uso el patrón de diseño Pila LIFO (Last In, First Out) en
> `undo_manager.py`. Cada vez que el usuario elimina o completa una tarea,
> se registra la acción con sus datos. Al presionar Ctrl+Z, se saca
> la última acción y se revierte."

### "¿Cómo funciona la voz?"

> "Uso sounddevice para grabar audio del micrófono, lo guardo como WAV
> temporal, y lo envío a Google Speech API con SpeechRecognition para
> convertirlo a texto. Luego un parser inteligente extrae título,
> descripción, fecha, prioridad y categoría del texto hablado."

### "¿Qué pasa si no hay micrófono?"

> "La app detecta automáticamente si las librerías de voz están
> instaladas. Si no están, crea una instancia DummyVoice que desactiva
> los botones de voz sin afectar el resto de la app."

### "¿Cómo garantizas que los tests son independientes?"

> "Cada test usa una base de datos en memoria (:memory:) creada con un
> fixture de pytest. Así cada test empieza con una BD limpia y no
> afecta a los demás."
