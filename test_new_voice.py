
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

print("Testing voice module import...")
try:
    from src.voice import voice_assistant
    print("SUCCESS: Voice module imported.")
    print(f"Voice available: {voice_assistant.voice_available}")
    
    if voice_assistant.voice_available:
        print("Voice system is ready and using sounddevice (no PyAudio).")
    else:
        print("Voice system disabled (dependencies missing).")

except ImportError as e:
    print(f"FAILED: ImportError: {e}")
except Exception as e:
    print(f"FAILED: Exception: {e}")
