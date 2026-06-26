import os
import sys
import time
from gtts import gTTS
import pygame

def speak_text(text: str) -> str:
    """Mengubah teks menjadi suara (TTS) dalam bahasa Indonesia dengan peredam error sistem."""
    try:
        short_text = text[:200]
        tts = gTTS(text=short_text, lang='id')
        filename = "temp_voice.mp3"
        tts.save(filename)

        # Simpan file descriptor asli stderr
        actual_stderr = os.dup(sys.stderr.fileno())
        devnull = os.open(os.devnull, os.O_WRONLY)

        try:
            # Alihkan stderr ke devnull (bungkam error ALSA)
            os.dup2(devnull, sys.stderr.fileno())

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()
        except Exception:
            pass
        finally:
            # Kembalikan stderr ke semula
            os.dup2(actual_stderr, sys.stderr.fileno())
            os.close(actual_stderr)
            os.close(devnull)

        if os.path.exists(filename):
            os.remove(filename)
        return "Proses TTS selesai."
    except Exception as e:
        return f"Gagal memproses suara: {e}"

# Tool ini bisa digunakan secara otomatis oleh model jika diperlukan, 
# atau dipanggil secara manual di main loop.
voice_tools = [speak_text]
