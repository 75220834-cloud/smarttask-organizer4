"""
Punto de entrada principal de SmartTask Organizer.

Este script se encarga de verificar que la estructura del proyecto sea
correcta (carpeta 'src' y archivo 'src/main.py' existan) antes de
importar y ejecutar la aplicación principal.

Uso:
    python run.py

Requisitos:
    - Python 3.8 o superior
    - Dependencias listadas en requirements.txt
    - Carpeta 'src/' con el código fuente del proyecto
"""

import os
import sys

def main():
    """Inicializa y ejecuta la aplicación SmartTask Organizer.

    Realiza las siguientes verificaciones antes de lanzar la app:
        1. Establece el directorio de trabajo al directorio del script.
        2. Verifica que exista la carpeta 'src/' con el código fuente.
        3. Verifica que exista el archivo 'src/main.py' (módulo principal).
        4. Configura el path de Python para encontrar los módulos.
        5. Importa y ejecuta la función main() desde src.main.

    Si alguna verificación falla, muestra un mensaje de error
    descriptivo y espera que el usuario presione Enter antes de salir.
    """
    # Establecer CWD al directorio del proyecto (donde está run.py)
    # Esto garantiza que funcione desde VSCode, terminal o doble clic
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("🚀 Iniciando SmartTask Organizer...")
    
    # 1. Verificar carpeta de código fuente (SRC)
    if not os.path.exists("src"):
        print("❌ Error: No se encuentra la carpeta 'src'")
        print("   Asegúrate de estar en la carpeta correcta.")
        input("Presiona Enter para salir...")
        return
    
    # 2. Verificar archivo principal
    if not os.path.exists("src/main.py"):
        print("❌ Error: No se encuentra src/main.py")
        input("Presiona Enter para salir...")
        return
    
    # 3. Configurar Path
    sys.path.insert(0, os.getcwd())
    
    try:
        # IMPORTANTE: Importar desde SRC, no desde APP
        from src.main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que src/__init__.py existe")
        print("2. Ejecuta en la terminal: pip install -r requirements.txt")
        input("\nPresiona Enter para salir...")
        
if __name__ == "__main__":
    main()
