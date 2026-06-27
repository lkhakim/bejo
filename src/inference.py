import re
import math
import logging

logger = logging.getLogger("bejo.inference")

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
        result = self.kb.answer(user_input, threshold=threshold)
        if result:
            logger.info(f"Inference: answered from KB (threshold={threshold})")
            return result

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
            logger.info("Inference: KB, local math & VM miss, using Gemini fallback")
            try:
                return self.gemini.send(user_input)
            except Exception as e:
                logger.error(f"Inference: Gemini fallback failed: {e}")
                return "Maaf Bos, Bejo belum belajar tentang itu. Coba latih Bejo dulu lewat menu Training."

        return "Maaf Bos, Bejo belum belajar tentang itu. Coba latih Bejo dulu lewat menu Training."
