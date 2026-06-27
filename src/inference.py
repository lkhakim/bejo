import os
import re
import math
import json
import logging
from datetime import datetime

logger = logging.getLogger("bejo.inference")

ACTIVITY_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "activity_log.json")

SKILL_PARAMS = {
    "web-search": {"tool": "web_search", "vars": {"query": "Apa yang mau dicari, Bos?"}},
    "book-search": {"tool": "web_search", "vars": {"query": "Judul atau topik buku apa yang dicari, Bos?"}},
    "tax-audit": {"tool": "analyze_financial_statement", "vars": {"file_path": "File laporan keuangannya mana, Bos? (PDF/Excel/CSV)"}},
    "osint-forensic": {"tool": "get_whois_info", "vars": {"domain": "Domain apa yang mau dicek, Bos?"}},
    "math-calc": {"tool": "calculate", "vars": {"expression": "Ekspresi matematikanya apa, Bos? Misal: 2+2 atau sqrt(16)"}},
    "memory": {"tool": "save_user_fact", "vars": {"fact_key": "Apa topik faktanya, Bos?", "fact_value": "Apa isi faktanya, Bos?"}},
    "tax_profiling": {"tool": "save_taxpayer_data", "vars": {"npwp": "NPWP-nya berapa, Bos?", "data_type": "Jenis datanya apa? (SPT/Faktur/Bupot/Setoran)", "amount": "Nominal rupiahnya berapa?"}},
    "face_tools": {"tool": "register_face", "vars": {"name": "Nama orangnya siapa, Bos?"}},
    "tools_media": {"tool": None, "vars": {}},
    "voice_tools": {"tool": None, "vars": {}},
    "insight": {"tool": None, "vars": {}},
}


def _log_activity(entry: dict):
    try:
        log = []
        if os.path.exists(ACTIVITY_LOG):
            with open(ACTIVITY_LOG, "r", encoding="utf-8") as f:
                log = json.load(f)
        entry["timestamp"] = datetime.now().isoformat()
        log.append(entry)
        with open(ACTIVITY_LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to log activity: {e}")

_MATH_PATTERN = re.compile(
    r"^\s*(hitung|hitungin|kalkulasi|berapa|hasil\s+dari|calculate|calc|math)?\s*"
    r"(.+?)\s*$",
    re.IGNORECASE,
)


def _try_compute(text: str) -> str | None:
    m = _MATH_PATTERN.match(text.strip())
    if not m:
        return None
    expr = m.group(2) or m.group(0)
    expr = expr.strip().rstrip("?")
    allowed = {
        "abs": abs, "round": round, "int": int, "float": float,
        "min": min, "max": max, "sum": sum, "pow": pow,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
        "log": math.log, "log10": math.log10, "log2": math.log2, "exp": math.exp,
        "pi": math.pi, "e": math.e, "inf": math.inf,
        "floor": math.floor, "ceil": math.ceil, "degrees": math.degrees, "radians": math.radians,
    }
    try:
        result = eval(expr, {"__builtins__": {}}, allowed)
        return f"Hasil: {result}"
    except Exception:
        return None


class InferenceEngine:
    def __init__(self, knowledge_base, vector_memory=None, gemini_engine=None):
        self.kb = knowledge_base
        self.vm = vector_memory
        self.gemini = gemini_engine

    def answer(self, user_input: str, threshold: float = 0.6) -> str:
        kb_results = self.kb.search(user_input, k=1, threshold=threshold)
        kb_hit = kb_results[0] if kb_results else None

        if kb_hit:
            tags = kb_hit.get("tags", [])
            skill_tag = next((t for t in tags if t not in ("just answer",)), None)
            if not skill_tag:
                logger.info(f"Inference: answered from KB (just answer)")
                return kb_hit["answer"]

            logger.info(f"Inference: KB hit with skill '{skill_tag}'")
            _log_activity({
                "type": "kb_hit",
                "skill": skill_tag,
                "user_input": user_input,
                "kb_answer": kb_hit["answer"],
            })

            param_spec = SKILL_PARAMS.get(skill_tag, {"tool": None, "vars": {}})
            if param_spec["vars"] and self.gemini:
                context_input = (
                    f"{user_input}\n\n---\n"
                    f"KB reference: {kb_hit['answer']}\n"
                    f"Gunakan tool yang sesuai jika Bos minta sesuatu yang butuh eksekusi."
                )
                try:
                    response = self.gemini.send(context_input)
                    _log_activity({
                        "type": "gemini_response",
                        "skill": skill_tag,
                        "user_input": user_input,
                        "response": response,
                    })
                    return response
                except Exception as e:
                    logger.error(f"Inference: Gemini fallback failed: {e}")
            return kb_hit["answer"]

        math_result = _try_compute(user_input)
        if math_result:
            logger.info("Inference: answered via local math evaluation")
            return math_result

        if self.vm and self.vm.count > 0:
            vm_results = self.vm.search(user_input, k=1)
            if vm_results and vm_results[0]["score"] >= threshold:
                logger.info(f"Inference: answered from vector memory (score={vm_results[0]['score']:.2f})")
                return vm_results[0]["text"]

        if self.gemini:
            logger.info("Inference: all local misses, using Gemini fallback")
            try:
                response = self.gemini.send(user_input)
                _log_activity({
                    "type": "gemini_only",
                    "user_input": user_input,
                    "response": response,
                })
                return response
            except Exception as e:
                logger.error(f"Inference: Gemini fallback failed: {e}")
                return "Maaf Bos, Bejo belum belajar tentang itu. Coba latih Bejo dulu lewat menu Training."

        return "Maaf Bos, Bejo belum belajar tentang itu. Coba latih Bejo dulu lewat menu Training."
