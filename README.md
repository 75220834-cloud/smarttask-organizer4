# 🚀 SmartTask Organizer

Sistema de gestión de tareas de escritorio con reconocimiento de voz, categorías, fechas límite, gráficos estadísticos y base de datos SQLite.

Desarrollado como proyecto de fin de curso para la materia de **Construcción de Software**.

---

## 📋 Historias de Usuario Implementadas

| HU   | Nombre                | Descripción                                                    |
|------|-----------------------|----------------------------------------------------------------|
| HU01 | Crear tarea           | Formulario completo con validación de campos                   |
| HU02 | Listar tareas         | Vista en tabla con ordenamiento por estado y prioridad         |
| HU03 | Editar tarea          | Modificación de todos los campos de una tarea existente        |
| HU04 | Eliminar tarea        | Diálogo de confirmación paso a paso (3 pasos)                  |
| HU05 | Completar tarea       | Marcar tareas como completadas con un clic                     |
| HU06 | Fecha límite          | Validación de formato DD/MM/AAAA y restricción de fechas       |
| HU07 | Detectar vencidas     | Detección automática de tareas con fecha límite pasada         |
| HU08 | Crear categoría       | 6 categorías predefinidas al inicializar la BD                 |
| HU09 | Asignar categoría     | Selección de categoría en formularios de creación/edición      |
| HU10 | Filtrar por categoría | RadioButtons para filtrar la tabla por categoría               |
| HU11 | Tarea por voz         | Dictado por micrófono con parseo inteligente de datos          |
| HU12 | Notificaciones        | Alertas de Windows para tareas vencidas y del día              |

**Funcionalidades adicionales:**
- 📊 Gráficos estadísticos con matplotlib (tema Nord)
- 📄 Exportación a CSV compatible con Excel
- ↩️ Deshacer acciones con Ctrl+Z (patrón Pila LIFO)
- 🎨 Tema visual Nord con colores personalizados

---

## 🛠️ Tecnologías Utilizadas

| Tecnología         | Versión    | Uso                                           |
|--------------------|------------|-----------------------------------------------|
| Python             | 3.8+       | Lenguaje principal                             |
| Tkinter + ttk      | (incluido) | Interfaz gráfica de escritorio                 |
| SQLite3            | (incluido) | Base de datos local persistente                |
| SpeechRecognition  | ≥3.10.0    | Reconocimiento de voz (Google Speech API)      |
| pyttsx3            | ≥2.90      | Síntesis de voz offline (texto a voz)          |
| sounddevice        | ≥0.4.6     | Grabación de audio del micrófono               |
| numpy              | ≥1.21.0    | Procesamiento de arrays de audio               |
| scipy              | ≥1.7.0     | Escritura de archivos WAV temporales           |
| matplotlib         | ≥3.3.0     | Gráficos estadísticos                          |
| plyer              | ≥2.1.0     | Notificaciones nativas de Windows              |
| python-dateutil    | ≥2.8.2     | Manejo avanzado de fechas                      |

---

## 📦 Requisitos Previos

- **Sistema Operativo:** Windows 10/11
- **Python:** 3.8 o superior ([Descargar Python](https://www.python.org/downloads/))
  - ⚠️ Marcar la casilla **"Add Python to PATH"** al instalar
- **Micrófono** (opcional, solo para funcionalidad de voz)
- **Conexión a internet** (solo para reconocimiento de voz con Google)

---

## 🚀 Instalación Paso a Paso

### Opción 1: Instalación automática (Recomendado)

```bash
# 1. Clonar o descargar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd smarttask-organizer4

# 2. Ejecutar el instalador automático (doble clic o desde terminal)
setup.bat
```

El script `setup.bat` hace todo automáticamente:
1. ✅ Verifica que Python esté instalado
2. ✅ Crea el entorno virtual (`.venv`)
3. ✅ Instala todas las dependencias
4. ✅ Inicializa la base de datos
5. ✅ Ejecuta la aplicación

### Opción 2: Instalación manual

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python run.py
```

### Instalar módulo de voz (opcional)

Si la voz no funciona con `setup.bat`, ejecutar:

```bash
instalar_voz.bat
```

---

## ▶️ Uso

### Ejecutar la aplicación

```bash
# Activar entorno virtual (si no está activo)
.venv\Scripts\activate

# Ejecutar
python run.py
```

### Interfaz principal

<!-- CAPTURA: Toma una captura de la ventana principal de la app mostrando la tabla con
     varias tareas (pendientes, completadas, vencidas) y los filtros de categoría visibles.
     Guárdala como: DOC/captura_principal.png -->

La ventana principal contiene:
- **Barra superior:** Botones Gráficos, Voz y Nueva Tarea
- **Panel de filtros:** RadioButtons para filtrar por categoría
- **Tabla central:** Lista de tareas con columnas ID, Título, Descripción, Fecha, Estado, Prioridad, Categoría
- **Leyenda de colores:** Verde (completada), Rojo (vencida), Amarillo (alta), Cyan (media)
- **Barra inferior:** Estadísticas en tiempo real

### Crear una tarea

<!-- CAPTURA: Toma una captura del diálogo "NUEVA TAREA" con los campos del formulario
     visibles y el botón de dictado por voz. Guárdala como: DOC/captura_crear_tarea.png -->

1. Clic en **"+ NUEVA TAREA"**
2. Completar: Título (obligatorio), Descripción, Fecha Límite (DD/MM/AAAA), Prioridad y Categoría
3. Clic en **"GUARDAR"**

### Crear tarea por voz (HU11)

<!-- CAPTURA: Toma una captura del diálogo de "Escuchando..." mientras se dicta una tarea.
     Guárdala como: DOC/captura_dictado_voz.png -->

1. Clic en **"🎤 DICTAR TAREA COMPLETA"** dentro del formulario de nueva tarea
2. Hablar claramente la tarea. Ejemplo:
   > "Reunión equipo **detalle** preparar presentación **fecha** quince diciembre **prioridad** alta **categoría** trabajo **terminar**"
3. Los campos se rellenan automáticamente

### Editar / Eliminar / Completar

- **Editar:** Seleccionar tarea → clic en "✏️ EDITAR"
- **Eliminar:** Seleccionar tarea → clic en "🗑️ ELIMINAR" → Confirmación en 3 pasos
- **Completar:** Seleccionar tarea → clic en "✅ COMPLETAR"
- **Deshacer:** Presionar **Ctrl+Z** para revertir la última acción

### Ver estadísticas

<!-- CAPTURA: Toma una captura de la ventana de gráficos mostrando el gráfico de pastel
     con la distribución de tareas. Guárdala como: DOC/captura_graficos.png -->

Clic en **"📊 GRÁFICOS"** para ver el gráfico de pastel con la distribución de tareas.

### Exportar a CSV

Clic en **"📄 EXPORTAR"** → Elegir ubicación → Se genera un archivo `.csv` compatible con Excel.

---

## 📁 Estructura del Proyecto

```
smarttask-organizer4/
├── run.py                  # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── setup.bat               # Instalador automático
├── instalar_voz.bat        # Instalador del módulo de voz
├── pytest.ini              # Configuración de pytest
├── .gitignore              # Archivos excluidos de Git
├── README.md               # Este archivo
│
├── src/                    # Código fuente principal
│   ├── __init__.py
│   ├── main.py             # Ventana principal (SmartTaskApp)
│   ├── database.py         # Capa de datos SQLite (CRUD)
│   ├── dialogos.py         # Diálogos de creación, edición y eliminación
│   ├── voice.py            # Reconocimiento y síntesis de voz
│   └── undo_manager.py     # Gestor de deshacer (Pila LIFO)
│
├── tests/                  # Pruebas unitarias
│   ├── __init__.py
│   ├── conftest.py         # Fixtures reutilizables
│   ├── test_database.py    # Tests CRUD (~25 tests)
│   └── test_undo_manager.py # Tests deshacer (~10 tests)
│
├── DOC/                    # Documentación adicional
│   └── Proyecto de Fin de Curso.docx.pdf
│
└── smarttask.db            # Base de datos SQLite (se genera automáticamente)
```

---

## 🧪 Ejecutar Pruebas Unitarias

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar pytest (si no está instalado)
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con reporte de cobertura
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 👤 Autor

**[Tu Nombre]** — Proyecto de Fin de Curso  
Materia: Construcción de Software  
Año: 2026