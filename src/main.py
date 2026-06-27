import os
import sys
import re
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bejo.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("bejo")

from dotenv import load_dotenv
from tools import tools_list
from face_tools import register_face, identify_person, FaceDetector
from osint_tools import osint_tools
from tax_tools import tax_tools
from tax_profiling import profiling_tools
from tax_audit import audit_tools
from tools_media import media_tools
from voice_tools import speak_text, set_tts_config
from conversation import ConversationManager
from display import BejoDisplay, emoji_to_expression
from chat_window import ChatWindow
from settings_window import SettingsWindow
from training_window import TrainingWindow
from stt import recognize_microphone
from config import load_config, save_config
from llm import create_engine
from knowledge import KnowledgeBase
from vector_memory import SemanticMemory
from skill_manager import SkillManager
from inference import InferenceEngine

tools_list.extend([register_face, identify_person])
tools_list.extend(osint_tools)
tools_list.extend(tax_tools)
tools_list.extend(profiling_tools)
tools_list.extend(audit_tools)
tools_list.extend(media_tools)

load_dotenv()

WAKE_WORDS = re.compile(r"^(jo|bejo|jobejo)\b", re.IGNORECASE)


def main():
    config = load_config()
    set_tts_config(config.get("tts", {}))

    cm = ConversationManager()
    bejo = BejoDisplay()

    gemini_engine = create_engine(config, tools_list)
    kb = KnowledgeBase()
    vm = SemanticMemory()
    sm = SkillManager()
    inference = InferenceEngine(knowledge_base=kb, vector_memory=vm, gemini_engine=gemini_engine)

    stt_cfg = config.get("stt", {})

    def start_auto_listen():
        chat_win.start_auto_listen(
            idle_max=stt_cfg.get("idle_timeout", 60),
            listen_timeout=stt_cfg.get("timeout", 5),
        )

    def process_input(user_input):
        if not user_input.strip():
            return

        chat_win.set_expression("processing")
        chat_win.set_status("Memproses...")
        bejo.set_expression("processing")
        bejo.set_status("    Memproses, Bos...")

        cm.on_user_message(user_input)

        try:
            response_text = inference.answer(user_input)

            expr = emoji_to_expression(response_text) or "neutral"
            chat_win.add_message("Bejo", response_text)
            chat_win.set_expression(expr)
            chat_win.set_status("Siap")
            bejo.set_expression(expr)
            bejo.set_status("  Siap Melayani, Bos!")

            cm.on_assistant_response(user_input, response_text)

            if response_text.strip():
                chat_win.pause_mic()
                speak_text(response_text)
                chat_win.resume_mic()
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            bejo.set_expression("error")
            bejo.set_status(f"Error: {str(e)[:40]}")
            chat_win.set_expression("error")
            chat_win.set_status("Error")
            chat_win.add_message("System", f"Waduh, ada error: {e}")

    def on_chat_send(text):
        wake = WAKE_WORDS.match(text.strip())
        if wake:
            reply = "Dalem Bos! Ada yang bisa Bejo bantu? \U0001f604"
            chat_win.add_message("Bejo", reply)
            chat_win.set_expression("happy")
            bejo.set_expression("happy")
            chat_win.pause_mic()
            speak_text(reply)
            chat_win.resume_mic()
            start_auto_listen()
            return

        threading.Thread(target=process_input, args=(text,), daemon=True).start()

    def on_mic_trigger():
        return recognize_microphone(stt_cfg)

    def open_training():
        TrainingWindow(chat_win.root, knowledge_base=kb, gemini_engine=gemini_engine, skill_manager=sm)

    def open_settings():
        def on_settings_closed():
            nonlocal config, gemini_engine, inference
            new_config = load_config()
            config.clear()
            config.update(new_config)
            set_tts_config(config.get("tts", {}))
            gemini_engine = create_engine(config, tools_list)
            inference = InferenceEngine(knowledge_base=kb, vector_memory=vm, gemini_engine=gemini_engine)

            face_cfg = config.get("face", {})
            if face_detector:
                face_detector.stop()
                face_detector = None
            if face_cfg.get("enabled", True):
                try:
                    face_detector = FaceDetector(
                        on_face_detected=on_face,
                        interval=face_cfg.get("interval", 2.0),
                        cooldown=face_cfg.get("cooldown", 30.0),
                    )
                    face_detector.start()
                except Exception as e:
                    logger.warning(f"Face detector restart failed: {e}")

            nonlocal stt_cfg
            stt_cfg = config.get("stt", {})
            start_auto_listen()
            chat_win.set_status("Siap")

        SettingsWindow(chat_win.root, on_close_callback=on_settings_closed)

    face_detector = None

    chat_win = ChatWindow(
        on_send=on_chat_send,
        on_mic=on_mic_trigger,
        on_settings=open_settings,
        on_training=open_training,
    )

    face_cfg = config.get("face", {})

    def on_face():
        fc = config.get("face", {})
        if not fc.get("enabled", True):
            return
        greeting = fc.get("greeting", "Halo Bos! Ada yang bisa Bejo bantu hari ini? \U0001f604")
        chat_win.root.after(0, lambda: chat_win.add_message("Bejo", greeting))
        chat_win.root.after(0, lambda: chat_win.set_expression("happy"))
        bejo.set_expression("happy")
        chat_win.pause_mic()
        speak_text(greeting)
        chat_win.resume_mic()

    if face_cfg.get("enabled", True):
        try:
            face_detector = FaceDetector(
                on_face_detected=on_face,
                interval=face_cfg.get("interval", 2.0),
                cooldown=face_cfg.get("cooldown", 30.0),
            )
            face_detector.start()
        except Exception as e:
            logger.warning(f"Face detector failed to start: {e}")

    logger.info("Bejo AI v3.0 started (local inference + Gemini fallback)")

    chat_win.root.after(2000, start_auto_listen)

    def tick_bejo():
        if not bejo.running:
            chat_win.stop()
            return
        bejo.tick()
        chat_win.root.after(16, tick_bejo)

    chat_win.root.after(500, tick_bejo)
    chat_win.run()

    if face_detector:
        face_detector.stop()
    bejo.stop()
    logger.info("Bejo AI stopped")


if __name__ == "__main__":
    main()
