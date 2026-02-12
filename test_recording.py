
import sys
import os
import time
import speech_recognition as sr
import traceback

# Add project root to path
sys.path.insert(0, os.getcwd())

log_file = "test_recording_log.txt"

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# Clear log
with open(log_file, "w") as f: f.write("Starting test...\n")

try:
    from src.voice import voice_assistant

    log("Testing recording and WAV format...")

    if not voice_assistant.voice_available:
        log("SKIPPING: Voice not available.")
        sys.exit(0)

    log("Recording 2 seconds of audio...")
    # Record short clip
    wav_path = voice_assistant._grabar_audio_sounddevice(duracion_max=2)

    if not wav_path or not os.path.exists(wav_path):
        log("FAILED: No wav file created.")
        sys.exit(1)

    log(f"WAV created at: {wav_path}")

    try:
        log("Attempting to open with SpeechRecognition...")
        with sr.AudioFile(wav_path) as source:
            log("SUCCESS: SpeechRecognition accepted the file format.")

    except Exception as e:
        log(f"FAILED: SpeechRecognition rejected the file: {e}")
        log(traceback.format_exc())
        sys.exit(1)
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
            log("Cleanup done.")
except Exception as e:
    log(f"CRITICAL ERROR: {e}")
    log(traceback.format_exc())
