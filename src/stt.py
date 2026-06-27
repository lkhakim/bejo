import logging
import threading
import time

logger = logging.getLogger("bejo.stt")

WINDOWS_STT_AVAILABLE = False
WINDOWS_INDO_AVAILABLE = False
try:
    import pythoncom
    import winspeech
    WINDOWS_STT_AVAILABLE = True
except ImportError:
    logger.warning("winspeech/pywin32 not available, Windows STT disabled")

GOOGLE_STT_AVAILABLE = False
try:
    import speech_recognition as sr
    GOOGLE_STT_AVAILABLE = True
except ImportError:
    logger.warning("speech_recognition not available, Google STT disabled")


def _find_sapi_token(target_lcid="0421"):
    try:
        import pythoncom
        pythoncom.CoInitialize()
        from win32com.client import Dispatch
        cat = Dispatch("SAPI.SpObjectTokenCategory")
        cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Recognizers\Tokens", False)
        for token in cat.EnumerateTokens():
            attrs = str(token.GetAttributes())
            if target_lcid in attrs:
                return token
    except Exception as e:
        logger.warning(f"SAPI: Error finding token: {e}")
    return None


def _check_indonesian_sapi():
    global WINDOWS_INDO_AVAILABLE
    token = _find_sapi_token("0421")
    if token:
        WINDOWS_INDO_AVAILABLE = True
        logger.info("SAPI: Indonesian speech recognizer found")
        return True
    logger.warning("SAPI: No Indonesian speech recognizer installed (install id-ID SAPI pack)")
    return False


if WINDOWS_STT_AVAILABLE:
    _check_indonesian_sapi()


def _set_sapi_language(lang_code="id-ID"):
    lcid_map = {"id-ID": "0421", "en-US": "0409", "en-GB": "0809"}
    target = lcid_map.get(lang_code, "0421")
    try:
        token = _find_sapi_token(target)
        if token:
            import pythoncom
            pythoncom.CoInitialize()
            winspeech._recognizer.SetRecognizer(token)
            logger.info(f"SAPI: Recognizer language set to {lang_code} ({target})")
            return True
    except Exception as e:
        logger.warning(f"SAPI: Failed to set language {lang_code}: {e}")
    return False


def recognize_microphone(config: dict, timeout: float = None) -> str | None:
    engine = config.get("engine", "windows")
    to = timeout if timeout is not None else config.get("timeout", 5)

    if engine == "windows":
        if WINDOWS_INDO_AVAILABLE:
            return _recognize_windows(to)
        else:
            logger.info("STT: Indonesian SAPI not available, falling back to Google STT id-ID")
            return _recognize_google(config, to, forced_lang="id-ID")
    else:
        return _recognize_google(config, to)


def _recognize_windows(timeout: float) -> str | None:
    if not WINDOWS_STT_AVAILABLE:
        return "ERR: Windows STT (winspeech) tidak tersedia. Install: pip install winspeech pywin32"

    pythoncom.CoInitialize()

    try:
        winspeech.initialize_recognizer(winspeech.INPROC_RECOGNIZER)
    except Exception:
        pass

    _set_sapi_language("id-ID")

    result = [None]
    done = threading.Event()

    def callback(phrase, listener):
        if not done.is_set():
            result[0] = phrase
            listener.stop_listening()
            done.set()

    listener = winspeech.listen_for_anything(callback)
    done.wait(timeout=timeout)

    if not done.is_set():
        listener.stop_listening()
        logger.info("STT (Windows): no speech detected within timeout")
        return None

    text = result[0]
    logger.info(f"STT (Windows SAPI): {text}")
    return text


def _recognize_google(config: dict, timeout: float, forced_lang: str = None) -> str | None:
    if not GOOGLE_STT_AVAILABLE:
        return "ERR: SpeechRecognition tidak terinstal. Install: pip install speechrecognition"

    lang = forced_lang or config.get("lang", "id-ID")
    phrase_limit = config.get("phrase_limit", 10)

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    recognizer.pause_threshold = 0.6

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            logger.info(f"STT (Google): listening (lang={lang}, timeout={timeout}s)...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        logger.info("STT (Google): no speech detected within timeout")
        return None
    except OSError as e:
        msg = str(e).lower()
        if "no device" in msg or "not found" in msg:
            return "ERR: Microphone tidak terdeteksi. Pastikan mic terhubung."
        if "permission" in msg or "access" in msg:
            return "ERR: Izin microphone ditolak. Periksa pengaturan privasi."
        return f"ERR: Microphone error: {e}"
    except Exception as e:
        logger.error(f"STT (Google): audio capture error: {e}")
        return f"ERR: Gagal akses mic: {e}"

    try:
        text = recognizer.recognize_google(audio, language=lang)
        logger.info(f"STT (Google): {text}")
        return text
    except sr.UnknownValueError:
        logger.info("STT (Google): could not understand audio")
        return None
    except sr.RequestError as e:
        logger.error(f"STT (Google): API error: {e}")
        return f"ERR: Gagal mengenali suara: {e}"
