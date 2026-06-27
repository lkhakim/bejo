import os
import sys
import time
import asyncio
import logging
import threading

logger = logging.getLogger("bejo.voice")

_current_config = None

EDGE_TTS_AVAILABLE = False
try:
    import edge_tts
    import pygame
    EDGE_TTS_AVAILABLE = True
except ImportError:
    logger.warning("edge-tts not available")

GTTS_AVAILABLE = False
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gtts not available")


def set_tts_config(config: dict):
    global _current_config
    _current_config = config


def speak_text(text: str) -> str:
    cfg = _current_config or {}
    if not cfg.get("enabled", True):
        return "TTS disabled"

    engine = cfg.get("engine", "edge-tts")
    lang = cfg.get("lang", "id")

    try:
        if engine == "edge-tts":
            return _speak_edge(text, cfg)
        elif engine == "gtts":
            return _speak_gtts(text, lang)
        else:
            return _speak_edge(text, cfg)
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return f"Gagal memproses suara: {e}"


def _speak_edge(text: str, cfg: dict) -> str:
    if not EDGE_TTS_AVAILABLE:
        return _speak_gtts(text, cfg.get("lang", "id"))

    voice = cfg.get("voice", "id-ID-ArdiNeural")
    short_text = text[:200]
    filename = "temp_voice.mp3"

    try:
        asyncio.run(edge_tts.Communicate(short_text, voice).save(filename))
    except Exception as e:
        logger.error(f"edge-tts synthesis failed: {e}")
        return f"Gagal sintesis suara: {e}"

    _play_mp3(filename)
    return "OK"


def _speak_gtts(text: str, lang: str) -> str:
    if not GTTS_AVAILABLE:
        return "TTS tidak tersedia (gtts belum terinstal)"

    short_text = text[:200]
    filename = "temp_voice.mp3"

    try:
        tts = gTTS(text=short_text, lang=lang)
        tts.save(filename)
    except Exception as e:
        logger.error(f"gTTS synthesis failed: {e}")
        return f"Gagal sintesis suara: {e}"

    _play_mp3(filename)
    return "OK"


def _play_mp3(filename: str):
    import pygame

    actual_stderr = os.dup(sys.stderr.fileno())
    devnull = os.open(os.devnull, os.O_WRONLY)

    was_music_playing = False
    try:
        from tools_media import pause_music_playback, resume_music_playback
        was_music_playing = pause_music_playback()
    except Exception:
        pass

    try:
        os.dup2(devnull, sys.stderr.fileno())
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
    except Exception:
        pass
    finally:
        os.dup2(actual_stderr, sys.stderr.fileno())
        os.close(actual_stderr)
        os.close(devnull)

    if os.path.exists(filename):
        os.remove(filename)

    if was_music_playing:
        try:
            from tools_media import resume_music_playback
            resume_music_playback()
        except Exception:
            pass
