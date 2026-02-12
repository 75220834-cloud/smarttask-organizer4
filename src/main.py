"""
Aplicación principal de SmartTask Organizer.

Contiene la clase SmartTaskApp que implementa la ventana principal de la
aplicación usando Tkinter con el tema visual Nord. Coordina todos los
módulos del sistema: base de datos, diálogos, voz y deshacer.

Historias de usuario implementadas directamente en este módulo:
    - HU01: Crear tarea (abre diálogo de creación)
    - HU02: Listar tareas (carga y muestra en Treeview)
    - HU03: Editar tarea (abre diálogo de edición)
    - HU04: Eliminar tarea (confirmación y eliminación)
    - HU05: Completar tarea (marca como completada)
    - HU06: Fecha límite (validación y visualización)
    - HU07: Detectar vencidas (cambia estado automáticamente)
    - HU10: Filtrar por categoría (RadioButtons de filtro)
    - HU11: Tarea por voz (modo voz interactivo)
    - HU12: Notificaciones (alerta de tareas vencidas al iniciar)

Funcionalidades adicionales:
    - Estadísticas y gráficos con matplotlib
    - Exportación a CSV compatible con Excel
    - Deshacer acciones con Ctrl+Z (UndoManager)
    - Tema visual Nord con colores personalizados
"""
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import threading
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from tkinter import filedialog

# Asegurar que Python encuentra los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar base de datos
try:
    from src.database import db
    print("✅ Base de datos importada")
except ImportError as e:
    print(f"❌ Error importando base de datos: {e}")
    print("Intentando importar directamente...")
    # Intentar importación relativa
    from database import db

# Importar módulo de voz con manejo de errores
try:
    from src.voice import voice_assistant
    print("✅ Módulo de voz importado")
except ImportError as e:
    print(f"⚠️  Error importando voz: {e}")
    print("Usando voz simulada...")
    
    # Dummy para desarrollo
    class DummyVoice:
        """Clase sustituta cuando el módulo de voz no está disponible.

        Proporciona la misma interfaz que VoiceAssistant pero sin
        funcionalidad real. Los métodos imprimen mensajes simulados
        en la consola en lugar de usar el micrófono o altavoces.
        """

        def __init__(self): 
            """Inicializa el DummyVoice con voz simulada disponible."""
            self.voice_available = True
            self.is_listening = False
        def hablar(self, texto): 
            """Simula hablar imprimiendo el texto en consola.

            Args:
                texto (str): Texto que se simula hablar.
            """
            print(f"🤖 [Simulado]: {texto}")
        def escuchar(self, timeout=5): 
            """Simula escuchar. Siempre retorna None.

            Args:
                timeout (int): Tiempo de espera en segundos (ignorado).

            Returns:
                None: Siempre retorna None al ser simulado.
            """
            return None
        def iniciar_modo_voz(self): 
            """Simula activar el modo voz.

            Returns:
                bool: Siempre retorna True.
            """
            print("🎤 Modo voz simulado activado")
            return True
        def detener_modo_voz(self): 
            """Simula desactivar el modo voz."""
            print("🎤 Modo voz desactivado")
    
    voice_assistant = DummyVoice()

# ============================================================================
# ============================================================================
# DIÁLOGOS
# ============================================================================
from src.dialogos import CrearTareaDialog, EditarTareaDialog, EliminarTareaDialog
from src.undo_manager import UndoManager



# ============================================================================
# VENTANA PRINCIPAL
# ============================================================================

class SmartTaskApp:
    """Ventana principal de SmartTask Organizer.

    Implementa la interfaz gráfica completa de la aplicación utilizando
    Tkinter con el tema visual Nord. Gestiona la lista de tareas,
    filtros por categoría, acciones CRUD, estadísticas, exportación
    y el modo de voz.

    Attributes:
        root (tk.Tk): Ventana raíz de Tkinter.
        filtro_categoria (tk.StringVar): Variable para el filtro de
            categoría activo. Valor por defecto: 'TODAS'.
        modo_voz_activo (bool): Indica si el modo voz está activado.
        undo_manager (UndoManager): Gestor de acciones reversibles.
        tree (ttk.Treeview): Widget tabla para mostrar las tareas.
        lbl_stats (ttk.Label): Label para mostrar estadísticas.

    Historias de usuario:
        HU01-HU07, HU10-HU12 (ver docstrings de cada método).
    """
    
    def __init__(self, root):
        """Inicializa la aplicación y construye la interfaz completa.

        Configura la ventana principal, aplica el tema Nord, crea
        todos los widgets, carga las tareas desde la base de datos
        y programa la verificación de notificaciones (HU12).

        Args:
            root (tk.Tk): Ventana raíz de Tkinter proporcionada
                por el punto de entrada.
        """
        self.root = root
        self.root.title("SmartTask Organizer - Gestor de Tareas")
        self.root.geometry("1200x800")
        
        # Variables
        self.filtro_categoria = tk.StringVar(value="TODAS")
        self.modo_voz_activo = False
        
        self.undo_manager = UndoManager()
        
        # Binding Undo
        self.root.bind('<Control-z>', lambda e: self._deshacer_accion())
        
        # Configurar estilos
        self._configurar_estilos()
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Cargar tareas
        self._cargar_tareas()
        
        # Centrar ventana
        self._centrar_ventana()
        
        # Verificar notificaciones al inicio
        self.root.after(1000, self._verificar_notificaciones)
        
        print("✅ Aplicación inicializada correctamente")
    
    def _verificar_notificaciones(self):
        """Verifica tareas vencidas o para hoy y envía notificación de Windows (HU12).

        Se ejecuta automáticamente 1 segundo después de iniciar la
        aplicación. Consulta las estadísticas y la lista de tareas
        para determinar si hay tareas vencidas o con fecha límite hoy.

        Utiliza la librería 'plyer' para enviar notificaciones nativas
        del sistema operativo. Si plyer no está disponible, el error
        se captura silenciosamente.
        """
        try:
            from plyer import notification
            
            stats = db.obtener_estadisticas()
            pendientes = stats['pendientes']
            vencidas = stats['vencidas']
            
            # Buscar tareas para hoy
            tareas = db.obtener_todas_tareas()
            hoy = date.today()
            para_hoy = 0
            
            for t in tareas:
                if t['estado'] == 'pendiente' and t['fecha_limite']:
                    try:
                        fecha_limite = datetime.strptime(t['fecha_limite'], "%Y-%m-%d").date()
                        if fecha_limite == hoy:
                            para_hoy += 1
                    except:
                        pass
            
            mensaje = ""
            if vencidas > 0:
                mensaje += f"⚠️ Tienes {vencidas} tarea(s) vencida(s)!\n"
            if para_hoy > 0:
                mensaje += f"📅 Tienes {para_hoy} tarea(s) para hoy!"
            
            if mensaje:
                notification.notify(
                    title='SmartTask Organizer',
                    message=mensaje,
                    app_name='SmartTask',
                    timeout=10
                )
                print("🔔 Notificación enviada a Windows")
                
        except Exception as e:
            print(f"⚠️ No se pudo enviar notificación: {e}")
    
    def _configurar_estilos(self):
        """Configura el tema visual Nord para toda la aplicación.

        Aplica la paleta de colores Nord (16 colores) a todos los
        widgets de ttk: botones, labels, entries, treeview, scrollbars
        y radiobuttons. Define estilos especiales para botones de
        acción: Accent (azul), Success (verde) y Danger (rojo).
        """
        self.root.configure(background='#2E3440') # Polar Night (Darkest)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta Nord
        nord0 = "#2E3440" # Polar Night 1
        nord1 = "#3B4252" # Polar Night 2
        nord2 = "#434C5E" # Polar Night 3
        nord3 = "#4C566A" # Polar Night 4
        nord4 = "#D8DEE9" # Snow Storm 1
        nord5 = "#E5E9F0" # Snow Storm 2
        nord6 = "#ECEFF4" # Snow Storm 3
        nord7 = "#8FBCBB" # Frost 1 (Green-Blue)
        nord8 = "#88C0D0" # Frost 2 (Cyan)
        nord9 = "#81A1C1" # Frost 3 (Blue)
        nord10 = "#5E81AC" # Frost 4 (Dark Blue)
        nord11 = "#BF616A" # Red
        nord12 = "#D08770" # Orange
        nord13 = "#EBCB8B" # Yellow
        nord14 = "#A3BE8C" # Green
        nord15 = "#B48EAD" # Purple

        # Configuración General
        style.configure('.', 
            background=nord0, 
            foreground=nord4, 
            font=("Segoe UI", 10)
        )
        
        # Frames
        style.configure('TFrame', background=nord0)
        style.configure('TLabelframe', background=nord0, foreground=nord8, bordercolor=nord3)
        style.configure('TLabelframe.Label', background=nord0, foreground=nord8, font=("Segoe UI", 10, "bold"))
        
        # Labels
        style.configure('TLabel', background=nord0, foreground=nord4)
        
        # Inputs (Entry)
        style.configure('TEntry', 
            fieldbackground=nord1,
            foreground=nord6,
            insertcolor=nord6,
            bordercolor=nord3,
            lightcolor=nord3,
            darkcolor=nord3,
            padding=5
        )
        
        # Botones (Generic)
        style.configure('TButton', 
            background=nord3, 
            foreground=nord6, 
            borderwidth=0, 
            focuscolor=nord8,
            padding=(10, 5)
        )
        style.map('TButton', 
            background=[('active', nord2), ('pressed', nord1)],
            foreground=[('active', nord6)]
        )
        
        # Botones Especiales
        style.configure('Accent.TButton', background=nord10, foreground=nord6, font=("Segoe UI", 10, "bold"))
        style.map('Accent.TButton', background=[('active', nord9), ('pressed', nord10)])
        
        style.configure('Success.TButton', background=nord14, foreground=nord1, font=("Segoe UI", 10, "bold"))
        style.map('Success.TButton', background=[('active', '#8FBCBB')]) # Lighter green
        
        style.configure('Danger.TButton', background=nord11, foreground=nord6, font=("Segoe UI", 10, "bold"))
        style.map('Danger.TButton', background=[('active', '#D08770')]) # Orange-Red

        # Treeview (Lista)
        style.configure("Treeview", 
            background=nord1,
            foreground=nord6, 
            fieldbackground=nord1,
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure("Treeview.Heading", 
            background=nord2, 
            foreground=nord4, 
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=5
        )
        style.map("Treeview", background=[('selected', nord3)], foreground=[('selected', nord6)])
        
        # Scrollbars
        style.configure("Vertical.TScrollbar", background=nord3, troughcolor=nord0, borderwidth=0, arrowcolor=nord4)
        style.configure("Horizontal.TScrollbar", background=nord3, troughcolor=nord0, borderwidth=0, arrowcolor=nord4)
        
        # Radiobuttons
        style.configure("TRadiobutton", background=nord0, foreground=nord4, font=("Segoe UI", 10))
        style.map("TRadiobutton", background=[('active', nord1)])
    
    def _centrar_ventana(self):
        """Centra la ventana principal en la pantalla del usuario.

        Calcula la posición (x, y) basándose en el tamaño de la
        pantalla y el tamaño actual de la ventana para posicionarla
        exactamente en el centro.
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _crear_interfaz(self):
        """Construye todos los widgets de la interfaz gráfica principal.

        Crea la siguiente estructura de layout:
            - Cabecera: Título de la app y botones (Gráficos, Voz, Nueva Tarea).
            - Filtros: RadioButtons para filtrar por categoría (HU10).
            - Tabla (Treeview): Muestra las tareas con 7 columnas (HU02).
            - Leyenda: Indicadores de color para estados y prioridades.
            - Botones de acción: Editar, Eliminar, Completar, Exportar, Actualizar.
            - Barra de estado: Estadísticas en tiempo real.
        """
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabecera
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="SMARTTASK ORGANIZER", 
                 font=("Segoe UI", 24, "bold"), foreground="#88C0D0").pack(side=tk.LEFT)
        
        # Botones de acción superior (Gráficos y Voz)
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="📊 GRÁFICOS", 
                  command=self._mostrar_graficos,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🎤 VOZ", 
                  command=self._alternar_modo_voz,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="+ NUEVA TAREA", 
                  command=self._abrir_crear_tarea,
                  style="Success.TButton").pack(side=tk.LEFT, padx=5)
        
        # Filtros (HU10)
        filtro_frame = ttk.LabelFrame(main_frame, text="FILTROS", padding="10")
        filtro_frame.pack(fill=tk.X, pady=(0, 15))
        
        categorias = db.obtener_categorias()
        filtros = ["TODAS"] + [cat['nombre'] for cat in categorias]
        
        for filtro in filtros:
            ttk.Radiobutton(filtro_frame, text=filtro, 
                           variable=self.filtro_categoria,
                           value=filtro, 
                           command=self._cargar_tareas).pack(side=tk.LEFT, padx=5)
        
        # Treeview para tareas
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Título", "Descripción", "Fecha Límite", "Estado", "Prioridad", "Categoría")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configurar columnas
        column_widths = {
            "ID": 50,
            "Título": 200,
            "Descripción": 250,
            "Fecha Límite": 100,
            "Estado": 100,
            "Prioridad": 80,
            "Categoría": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])
        
        # Scrollbars personalizados (Dark)
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", background="#3B4252", troughcolor="#2E3440", borderwidth=0, arrowcolor="#ECEFF4")
        style.configure("Horizontal.TScrollbar", background="#3B4252", troughcolor="#2E3440", borderwidth=0, arrowcolor="#ECEFF4")
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configurar expansión
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Leyenda de Colores (Estilo Nord)
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(legend_frame, text="LEYENDA:", font=("Segoe UI", 9, "bold"), foreground="#88C0D0").pack(side=tk.LEFT, padx=5)
        
        # Texto visible sobre fondo oscuro
        legends = [
            ("COMPLETADA", "#A3BE8C", "#2E3440"), # Verde Nord
            ("VENCIDA", "#BF616A", "#2E3440"),    # Rojo Nord
            ("PRIORIDAD ALTA", "#EBCB8B", "#2E3440"), # Amarillo Nord
            ("PRIORIDAD MEDIA", "#88C0D0", "#2E3440") # Cyan Nord
        ]
        
        for text, fg, bg in legends:
            lbl = tk.Label(legend_frame, text=text, fg=fg, bg=bg, 
                          padx=8, pady=2, font=("Segoe UI", 9, "bold"), relief="flat")
            lbl.pack(side=tk.LEFT, padx=5)

        # Botones de acción inferiores
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="✏️ EDITAR", 
                  command=self._abrir_editar_tarea).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="🗑️ ELIMINAR", 
                  command=self._abrir_eliminar_tarea,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="✅ COMPLETAR", 
                  command=self._completar_tarea,
                  style="Success.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="📄 EXPORTAR", 
                  command=self._exportar_csv).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="🔄 ACTUALIZAR", 
                  command=self._cargar_tareas).pack(side=tk.RIGHT, padx=5)
        
        # Barra de estado
        self.lbl_stats = ttk.Label(main_frame, text="", font=("Segoe UI", 11))
        self.lbl_stats.pack(fill=tk.X, pady=5)
        
        # Configurar expansión
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def _cargar_tareas(self):
        """Carga y muestra todas las tareas en la tabla Treeview (HU02, HU07, HU10).

        Limpia la tabla actual, consulta las tareas desde la base de datos
        (aplicando filtro de categoría si está activo - HU10), formatea
        las fechas a DD/MM/AAAA, detecta tareas vencidas cambiando su
        estado automáticamente (HU07), y aplica colores según estado
        y prioridad usando la paleta Nord.

        Colores aplicados:
            - Verde (#A3BE8C): Tareas completadas.
            - Rojo (#BF616A): Tareas vencidas.
            - Amarillo (#EBCB8B): Prioridad alta.
            - Cyan (#88C0D0): Prioridad media.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtro = self.filtro_categoria.get()
        if filtro == "TODAS":
            filtro = None
        
        tareas = db.obtener_todas_tareas(filtro)
        
        for tarea in tareas:
            fecha = ""
            if tarea['fecha_limite']:
                try:
                    fecha_obj = datetime.strptime(tarea['fecha_limite'], "%Y-%m-%d")
                    fecha = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha = tarea['fecha_limite']
            
            estado = tarea['estado'].upper()
            
            # HU07 - Verificar si está vencida
            if tarea['estado'] == 'pendiente' and tarea['fecha_limite']:
                try:
                    fecha_limite = datetime.strptime(tarea['fecha_limite'], "%Y-%m-%d").date()
                    if fecha_limite < date.today():
                        estado = "VENCIDA"
                        db.actualizar_tarea(tarea['id'], estado='vencida')
                except:
                    pass
            
            item_id = self.tree.insert("", tk.END, values=(
                tarea['id'],
                tarea['titulo'],
                tarea['descripcion'] or "",
                fecha,
                estado,
                tarea['prioridad'].upper(),
                tarea['categoria_nombre'] or "Sin categoría"
            ))
            
        # Colorear (Prioridad: Completada > Vencida > Prioridad)
            if estado == "COMPLETADA":
                self.tree.item(item_id, tags=('completada',))
            elif estado == "VENCIDA":
                self.tree.item(item_id, tags=('vencida',))
            elif tarea['prioridad'] == 'alta':
                self.tree.item(item_id, tags=('alta',))
            elif tarea['prioridad'] == 'media':
                self.tree.item(item_id, tags=('media',))
        
        # Configurar Tags con colores NORD
        # Fondo oscuro, texto color pastel brillante
        self.tree.tag_configure('completada', background='#2E3440', foreground='#A3BE8C') # Verde
        self.tree.tag_configure('vencida', background='#2E3440', foreground='#BF616A')    # Rojo
        self.tree.tag_configure('alta', background='#2E3440', foreground='#EBCB8B')       # Amarillo
        self.tree.tag_configure('media', background='#2E3440', foreground='#88C0D0')      # Cyan
        
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        """Actualiza la barra de estado con estadísticas en tiempo real (funcionalidad adicional).

        Consulta las estadísticas desde la base de datos y actualiza
        el label inferior mostrando el total de tareas, completadas,
        pendientes y vencidas.
        """
        stats = db.obtener_estadisticas()
        texto = f"📊 TOTAL: {stats['total']}  |  ✅ COMPLETADAS: {stats['completadas']}  |  ⏳ PENDIENTES: {stats['pendientes']}  |  ⚠️ VENCIDAS: {stats['vencidas']}"
        self.lbl_stats.config(text=texto, foreground="#88C0D0") # Cyan para destacar

    def _mostrar_graficos(self):
        """Muestra una ventana con gráficos de pastel estadísticos (funcionalidad adicional).

        Crea una ventana secundaria (Toplevel) con:
            - Resumen numérico de tareas por estado.
            - Gráfico de pastel (pie chart) con matplotlib usando la
              paleta de colores Nord.

        Los segmentos del gráfico representan: Completadas (verde),
        Pendientes (cyan) y Vencidas (rojo). Se omiten segmentos
        con valor 0.
        """
        stats = db.obtener_estadisticas()
        
        # Crear ventana con tema Nord
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Estadísticas SmartTask")
        graph_window.geometry("700x600")
        graph_window.configure(background="#2E3440")
        
        # Frame datos
        ttk.Label(graph_window, text="ESTADÍSTICAS", 
                 font=("Segoe UI", 20, "bold"), foreground="#88C0D0", background="#2E3440").pack(pady=20)
        
        info_frame = tk.Frame(graph_window, bg="#3B4252", padx=20, pady=20)
        info_frame.pack(fill=tk.X, padx=40)
        
        texto_resumen = (
            f"Total Tareas: {stats['total']}\n"
            f"✅ Completadas: {stats['completadas']}\n"
            f"⏳ Pendientes: {stats['pendientes']}\n"
            f"⚠️ Vencidas: {stats['vencidas']}"
        )
        tk.Label(info_frame, text=texto_resumen, font=("Segoe UI", 12), 
                 bg="#3B4252", fg="#ECEFF4", justify=tk.LEFT).pack()
        
        # Preparar datos
        labels_base = ['Completadas', 'Pendientes', 'Vencidas']
        
        pendientes_reales = stats['pendientes'] 
        
        sizes_base = [stats['completadas'], pendientes_reales, stats['vencidas']]
        # Colores Nord
        colors_base = ['#A3BE8C', '#88C0D0', '#BF616A'] # Verde, Cyan, Rojo
        explode_base = (0.05, 0, 0.05)
        
        final_labels = []
        final_sizes = []
        final_colors = []
        final_explode = []
        
        for i, size in enumerate(sizes_base):
            if size and size > 0:
                final_labels.append(labels_base[i])
                final_sizes.append(size)
                final_colors.append(colors_base[i])
                final_explode.append(explode_base[i])
        
        if not final_sizes:
            tk.Label(graph_window, text="\nNo hay suficientes datos", 
                     bg="#2E3440", fg="gray").pack(pady=20)
            return

        # Matplotlib Dark Theme (Nord-ish)
        try:
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(6, 5), facecolor='#2E3440')
            
            wedges, texts, autotexts = ax.pie(final_sizes, explode=final_explode, labels=final_labels, 
                   colors=final_colors, autopct='%1.1f%%', shadow=True, startangle=90,
                   textprops={'color':"#ECEFF4", 'weight':'bold'})
            
            # Personalizar textos del pie
            for autotext in autotexts:
                autotext.set_color('#2E3440') # Texto oscuro para contraste sobre pastel
                autotext.set_fontsize(10)

            ax.axis('equal') 
            ax.set_title("Distribución de Tareas", color="#88C0D0", fontsize=14, pad=20)
            
            # Integrar en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            canvas.get_tk_widget().configure(bg='#2E3440') # Fondo del widget
            
        except Exception as e:
            tk.Label(graph_window, text=f"Error creando gráfico: {e}", bg="red").pack()
        
        ttk.Button(graph_window, text="Cerrar", command=graph_window.destroy).pack(pady=15)
   
    def _abrir_crear_tarea(self):
        """Abre el diálogo para crear una nueva tarea (HU01, HU11).

        Intenta importar el asistente de voz real. Si no está disponible,
        utiliza un DummyVoice como sustituto. Abre el diálogo
        CrearTareaDialog que soporta tanto entrada manual como dictado
        por voz (HU11).
        """
        try:
            # Importar voice_assistant global
            from src.voice import voice_assistant
        except ImportError:
            # Si falla, usar dummy
            class DummyVoice:
                """Sustituto local de VoiceAssistant para cuando la voz no está disponible."""

                def __init__(self): 
                    self.voice_available = False
                    self.is_listening = False
                def hablar(self, texto): print(f"🤖: {texto}")
                def escuchar_y_parsear(self, callback=None): return None
        
            voice_assistant = DummyVoice()
    
        # Crear diálogo con el asistente disponible
        dialog = CrearTareaDialog(self.root, self._cargar_tareas, voice_assistant)
        self.root.wait_window(dialog.top)
    
    def _abrir_editar_tarea(self):
        """Abre el diálogo para editar la tarea seleccionada (HU03).

        Verifica que haya una tarea seleccionada en el Treeview.
        Si no hay selección, muestra una advertencia al usuario.
        Obtiene el ID de la tarea seleccionada y abre el diálogo
        EditarTareaDialog.
        """
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una tarea para editar")
            return
    
        item = seleccion[0]
        tarea_id = self.tree.item(item, 'values')[0]
    
        dialog = EditarTareaDialog(self.root, tarea_id, self._cargar_tareas)
        self.root.wait_window(dialog.top)
    
    def _abrir_eliminar_tarea(self):
        """Elimina la tarea seleccionada con confirmación (HU04).

        Verifica que haya una tarea seleccionada, muestra un diálogo
        de confirmación (messagebox.askyesno), y si el usuario confirma:
            1. Guarda los datos de la tarea en el UndoManager para
               poder deshacerla con Ctrl+Z.
            2. Elimina la tarea de la base de datos.
            3. Recarga la lista de tareas.
        """
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una tarea para eliminar")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        tarea_id = valores[0]
        titulo = valores[1]
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar la tarea '{titulo}'?"
        )
        
        if respuesta:
            # UNDO: Guardar datos antes de eliminar
            tarea_obj = db.obtener_tarea(tarea_id)
            if tarea_obj:
                # Convertir Row a dict
                datos = dict(tarea_obj)
                self.undo_manager.registrar_accion("ELIMINAR", datos)
            
            if db.eliminar_tarea(tarea_id):
                self._cargar_tareas()
                messagebox.showinfo("Éxito", "Tarea eliminada correctamente\n(Ctrl+Z para deshacer)")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la tarea")
    
    def _completar_tarea(self):
        """Marca la tarea seleccionada como completada (HU05).

        Verifica que haya una tarea seleccionada, pide confirmación
        al usuario, y si confirma:
            1. Registra la acción en el UndoManager para poder
               deshacerla con Ctrl+Z.
            2. Actualiza el estado a 'completada' en la base de datos.
            3. Recarga la lista de tareas.
        """
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona una tarea para completar")
            return
        
        item = seleccion[0]
        tarea_id = self.tree.item(item, 'values')[0]
        titulo = self.tree.item(item, 'values')[1]
        
        respuesta = messagebox.askyesno(
            "Completar Tarea",
            f"¿Marcar '{titulo}' como completada?"
        )
        
        if respuesta:
            # UNDO: Registrar acción
            self.undo_manager.registrar_accion("COMPLETAR", {'id': tarea_id})
            
            if db.marcar_como_completada(tarea_id):
                self._cargar_tareas()
                messagebox.showinfo("Éxito", "Tarea marcada como completada\n(Ctrl+Z para deshacer)")
            else:
                messagebox.showerror("Error", "No se pudo completar la tarea")
    
    def _exportar_csv(self):
        """Exporta todas las tareas a un archivo CSV compatible con Excel (funcionalidad adicional).

        Genera un archivo CSV con codificación UTF-8 BOM (para que Excel
        reconozca acentos) y separador punto y coma (;) que es el estándar
        en configuraciones regionales en español.

        El archivo incluye las columnas: ID, Título, Descripción,
        Fecha Límite, Estado, Prioridad y Categoría.

        Abre un diálogo para que el usuario elija dónde guardar el archivo.
        El nombre por defecto incluye la fecha y hora actual.
        """
        try:
            tareas = db.obtener_todas_tareas()
            if not tareas:
                messagebox.showinfo("Info", "No hay tareas para exportar")
                return

            # Ordenar por ID para mantener orden
            # Convertir a lista de dicts si no lo es, aunque db devuelve Row objects que actuan como dicts
            tareas_lista = [dict(t) for t in tareas]
            tareas_lista.sort(key=lambda x: x['id'])

            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = filedialog.asksaveasfilename(
                initialfile=f"smarttask_backup_{fecha_str}.csv",
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
            )
            
            if not filename:
                return
            
            # Usar utf-8-sig para que Excel reconozca acentos
            # Usar delimiter=';' porque en español Excel lo espera así
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                # Escribir cabeceras
                writer.writerow(["ID", "Título", "Descripción", "Fecha Límite", "Estado", "Prioridad", "Categoría"])
                
                # Escribir datos
                for t in tareas_lista:
                    writer.writerow([
                        t['id'],
                        t['titulo'],
                        t['descripcion'],
                        t['fecha_limite'],
                        t['estado'],
                        t['prioridad'],
                        t['categoria_nombre']
                    ])
            
            messagebox.showinfo("Éxito", f"Tareas exportadas correctamente a:\n{filename}\n\nNota: Se usó punto y coma (;) como separador.")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def _deshacer_accion(self):
        """Revierte la última acción realizada por el usuario (funcionalidad adicional).

        Se activa con el atajo de teclado Ctrl+Z. Llama al UndoManager
        para revertir la última acción (eliminar o completar).
        Muestra un mensaje tipo 'toast' en la parte inferior de la
        ventana que desaparece automáticamente después de 2 segundos.
        """
        resultado = self.undo_manager.deshacer()
        if resultado:
            self._cargar_tareas()
            
            # Mostrar feedback visual no intrusivo (Toast simulado)
            lbl = tk.Label(self.root, text=f"↩️ {resultado}", bg="#88C0D0", fg="#2E3440", 
                           font=("Segoe UI", 12, "bold"), padx=20, pady=10)
            lbl.place(relx=0.5, rely=0.9, anchor="center")
            
            # Desaparecer en 2 segundos
            self.root.after(2000, lbl.destroy)
        else:
            print("Nada que deshacer")

    def _alternar_modo_voz(self):
        """Activa o desactiva el modo voz interactivo (HU11).

        Cuando se activa:
            - Inicia el asistente de voz.
            - Muestra instrucciones al usuario.
            - Ejecuta un hilo en segundo plano para escuchar comandos.

        Cuando se desactiva:
            - Detiene la escucha activa.
            - Notifica al usuario.

        El modo voz permite comandos básicos por terminal:
        'crear tarea', 'listar tareas', 'ayuda', 'salir'.
        """
        if not self.modo_voz_activo:
            self.modo_voz_activo = True
            
            if voice_assistant.iniciar_modo_voz():
                messagebox.showinfo(
                    "Modo Voz", 
                    "Modo voz activado.\n\n"
                    "Instrucciones:\n"
                    "1. Los comandos se ingresan por TECLADO en la terminal\n"
                    "2. La respuesta se escuchará por ALTAVOCES\n"
                    "3. Escribe 'ayuda' para ver comandos\n"
                    "4. Escribe 'salir' para terminar"
                )
                
                # Ejecutar en segundo plano
                thread = threading.Thread(target=self._ejecutar_modo_voz, daemon=True)
                thread.start()
            else:
                self.modo_voz_activo = False
                messagebox.showerror("Error", "No se pudo iniciar el modo voz")
        else:
            self.modo_voz_activo = False
            voice_assistant.detener_modo_voz()
            messagebox.showinfo("Modo Voz", "Modo voz desactivado")
    
    def _ejecutar_modo_voz(self):
        """Ejecuta el bucle principal del modo voz en un hilo separado (HU11).

        Escucha continuamente comandos de voz mientras modo_voz_activo
        sea True. Los comandos soportados son:
            - 'salir' / 'terminar': Desactiva el modo voz.
            - 'crear tarea': Informa cómo crear tareas desde la interfaz.
            - 'listar tareas': Indica la cantidad de tareas visibles.
            - 'ayuda': Lista los comandos disponibles.

        Este método se ejecuta como daemon thread y no bloquea la
        interfaz gráfica.
        """
        while self.modo_voz_activo:
            try:
                comando = voice_assistant.escuchar(timeout=10)
                
                if comando:
                    if "salir" in comando or "terminar" in comando:
                        self.modo_voz_activo = False
                        voice_assistant.hablar("Saliendo del modo voz")
                        break
                    elif "crear tarea" in comando:
                        voice_assistant.hablar("Para crear una tarea, usa el botón 'NUEVA' en la interfaz")
                    elif "listar tareas" in comando:
                        voice_assistant.hablar(f"Tienes {len(self.tree.get_children())} tareas en la lista")
                    elif "ayuda" in comando:
                        voice_assistant.hablar("Comandos: crear tarea, listar tareas, ayuda, salir")
                    else:
                        voice_assistant.hablar(f"Comando '{comando}' recibido")
            except:
                pass

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal que inicia la aplicación SmartTask Organizer.

    Crea la ventana raíz de Tkinter, instancia SmartTaskApp y
    ejecuta el bucle principal de eventos. Si ocurre un error
    crítico, lo muestra en consola con traceback completo.
    """
    try:
        root = tk.Tk()
        app = SmartTaskApp(root)
        root.mainloop()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    print("="*60)
    print("SMARTTASK ORGANIZER - Iniciando...")
    print("="*60)
    main()