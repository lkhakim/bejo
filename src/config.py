import os
import json
import logging

logger = logging.getLogger("bejo.config")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings.json")

DEFAULT_CONFIG = {
    "llm": {
        "engine": "gemini",
        "gemini_model": "gemini-2.0-flash",
        "gemini_api_key": "",
    },
    "tts": {
        "enabled": True,
        "engine": "edge-tts",
        "lang": "id",
        "voice": "id-ID-ArdiNeural",
        "voice_gender": "male",
        "speed": 1.0,
    },
    "stt": {
        "enabled": True,
        "engine": "windows",
        "lang": "id-ID",
        "auto_listen": True,
        "idle_timeout": 60,
        "timeout": 5,
        "phrase_limit": 10,
    },
    "display": {
        "show_character": True,
    },
    "face": {
        "enabled": True,
        "interval": 2.0,
        "cooldown": 30.0,
        "greeting": "Halo Bos! Ada yang bisa Bejo bantu hari ini?",
    },
}


def load_config() -> dict:
    config = {}
    for section, values in DEFAULT_CONFIG.items():
        config[section] = dict(values)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for section in config:
                if section in saved:
                    config[section].update(
                        {k: v for k, v in saved[section].items() if k in config[section]}
                    )
            logger.info("Settings loaded")
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
    return config


def save_config(config: dict):
    try:
        payload = {}
        for section, values in config.items():
            payload[section] = dict(values)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info("Settings saved")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
