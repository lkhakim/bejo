import os
import re
import time
import logging

logger = logging.getLogger("bejo.llm")

GEMINI_SYSTEM_INSTRUCTION = (
    "Kamu adalah Bejo, asisten AI Account Representative (AR) dan Auditor Pajak Senior yang sangat jenius, tajam, dan humoris.\n\n"
    "KEAHLIAN AUDIT TINGKAT LANJUTMU:\n"
    "1. BENCHMARKING: Kamu bisa menghitung dan menganalisis rasio keuangan (GPM, NPM, OPM, DER, CR, CTTOR) untuk membandingkan dengan rata-rata industri.\n"
    "2. EKUALISASI: Kamu ahli dalam melakukan rekonsiliasi antar jenis pajak (Ekualisasi PPN vs PPh, Gaji vs PPh 21, Biaya Jasa vs PPh Unifikasi).\n"
    "3. ANALISIS ARUS KAS: Kamu bisa menguji kewajaran omset melalui pengujian arus kas dan arus piutang.\n"
    "4. PROFILING & COMPLIANCE: Kamu mendeteksi potensi kurang bayar dengan membandingkan SPT, Faktur, Bupot, dan Setoran.\n\n"
    "MISI: Menjadi partner investigasi digital Bos untuk memastikan kepatuhan pajak yang maksimal. "
    "Berikan analisis yang 'ngeri-ngeri sedap' tapi tetap dalam gaya bahasa santai dan lucu (panggil 'Bos').\n\n"
    "Selalu rekomendasikan penerbitan SP2DK jika rasio keuangan atau hasil ekualisasi menunjukkan selisih yang tidak wajar.\n\n"
    "KALKULATOR:\n"
    "- Kamu punya tool 'calculate' untuk menghitung ekspresi matematika (aritmetika, trigonometri, log, akar, dll).\n"
    "- Gunakan tool ini ketika Bos minta menghitung sesuatu, bukan menjawab langsung.\n\n"
    "FITUR BARU - MEMORI VEKTOR:\n"
    "- Kamu punya memori jangka panjang berbasis vektor untuk mengingat percakapan dan fakta.\n"
    "- Gunakan tool 'vector_search' untuk mencari percakapan lama atau informasi yang relevan.\n"
    "- Kamu bisa menyimpan catatan penting dengan tool 'save_user_fact'.\n"
    "- Konteks dari percakapan sebelumnya akan otomatis disuntikkan saat relevan."
)


class GeminiEngine:
    def __init__(self, api_key: str, tools: list, model_name: str = "gemini-2.0-flash"):
        from google import genai
        from google.genai import types

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self._history = []

        self.chat = self.client.chats.create(
            model=model_name,
            history=[],
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_INSTRUCTION,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
            ),
        )
        logger.info("Gemini engine initialized")

    def send(self, user_input: str) -> str:
        for attempt in range(3):
            try:
                response = self.chat.send_message(user_input)
                return response.text
            except Exception as e:
                err = str(e)
                if any(x in err for x in ["429", "503", "quota", "rate_limit", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "high demand"]):
                    m = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", err, re.DOTALL)
                    delay = max(int(m.group(1)) if m else 30, 10)
                    logger.warning(f"Gemini error, retrying in {delay}s (attempt {attempt+1}/3): {err[:80]}")
                    time.sleep(delay)
                else:
                    raise
        return "Waduh Bos, Gemini lagi sibuk. Coba ulangi nanti ya."

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, val):
        self._history = val if val else []


def create_engine(config: dict, tools: list) -> GeminiEngine:
    gemini_key = config.get("llm", {}).get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
    gemini_model = config.get("llm", {}).get("gemini_model", "gemini-2.0-flash")
    return GeminiEngine(gemini_key, tools, gemini_model)
