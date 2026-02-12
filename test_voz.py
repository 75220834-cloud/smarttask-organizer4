"""
TEST DE VOZ SIMPLIFICADO
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*50)
print("🔊 TEST DE SISTEMA DE VOZ")
print("="*50)

# Probar imports
librerias = ['numpy', 'scipy', 'sounddevice', 'speech_recognition', 'pyttsx3']

for lib in librerias:
    try:
        __import__(lib)
        print(f"✅ {lib}")
    except:
        print(f"❌ {lib}")

print("\n🎤 Probando módulo de voz...")
try:
    from src.voice import voice_assistant
    
    if voice_assistant.voice_available:
        print("✅ Módulo de voz funcionando")
        
        # Probar hablar
        print("\n🔊 Probando síntesis de voz...")
        voice_assistant.hablar("Test de voz funcionando")
        
        print("\n✅ Todo funcionando correctamente")
    else:
        print("❌ Voz no disponible")
        
except Exception as e:
    print(f"❌ Error: {e}")

input("\nPresiona Enter para salir...")