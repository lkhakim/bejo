import os
import json
import math
import logging
import signal
from functools import wraps
from duckduckgo_search import DDGS

logger = logging.getLogger("bejo.tools")

MEMORY_FILE = "user_memory.json"
TOOL_TIMEOUT = 30


def timeout_handler(seconds=TOOL_TIMEOUT):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if os.name == "nt":
                return func(*args, **kwargs)
            try:
                signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError("Tool timeout")))
                signal.alarm(seconds)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    signal.alarm(0)
            except Exception as e:
                return f"Tool timeout atau error: {e}"
        return wrapper
    return decorator


def create_file(filename: str, content: str) -> str:
    """Membuat file baru dengan konten yang ditentukan.
    Args:
        filename: Nama file (misal: 'catatan.txt')
        content: Isi dari file tersebut.
    """
    try:
        filepath = os.path.join(os.getcwd(), filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Created file: {filename}")
        return f"Berhasil membuat file: {filename}"
    except Exception as e:
        logger.error(f"Failed to create file {filename}: {e}")
        return f"Gagal membuat file: {e}"


def read_file(filename: str) -> str:
    """Membaca isi dari sebuah file.
    Args:
        filename: Nama file yang ingin dibaca.
    """
    try:
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'r') as f:
            content = f.read()
        logger.info(f"Read file: {filename}")
        return content
    except Exception as e:
        logger.error(f"Failed to read file {filename}: {e}")
        return f"Gagal membaca file: {e}"


def list_files() -> str:
    """Melihat daftar file di direktori saat ini."""
    try:
        files = os.listdir(os.getcwd())
        logger.info("Listed files")
        return "\n".join(files) if files else "Folder kosong."
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return f"Gagal melist file: {e}"


def web_search(query: str) -> str:
    """Mencari informasi di internet menggunakan DuckDuckGo.
    Args:
        query: Kata kunci pencarian.
    """
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            logger.info(f"Web search no results: {query}")
            return "Tidak ditemukan hasil pencarian."

        search_summary = []
        for r in results:
            search_summary.append(f"Title: {r['title']}\nSnippet: {r['body']}\nLink: {r['href']}\n")

        logger.info(f"Web search completed: {query[:60]}...")
        return "\n---\n".join(search_summary)
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Gagal melakukan pencarian web: {e}"


def save_user_fact(fact_key: str, fact_value: str) -> str:
    """Menyimpan fakta atau preferensi tentang user ke memori jangka panjang.
    Args:
        fact_key: Kategori fakta (misal: 'nama', 'hobi', 'bahasa_favorit')
        fact_value: Isi dari fakta tersebut.
    """
    try:
        memory = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                memory = json.load(f)

        memory[fact_key] = fact_value

        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=4)

        logger.info(f"Saved user fact: {fact_key} = {fact_value[:50]}...")
        return f"Saya sudah ingat bahwa {fact_key} Anda adalah {fact_value}."
    except Exception as e:
        logger.error(f"Failed to save user fact: {e}")
        return f"Gagal menyimpan memori: {e}"


def get_user_facts() -> str:
    """Mengambil semua fakta yang diketahui tentang user."""
    try:
        if not os.path.exists(MEMORY_FILE):
            return "Saya belum mengenal Anda lebih dalam. Beritahu saya sesuatu tentang Anda!"

        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)

        if not memory:
            return "Memori saya masih kosong."

        facts = [f"{k}: {v}" for k, v in memory.items()]
        logger.info(f"Retrieved {len(memory)} user facts")
        return "Berikut yang saya ingat tentang Anda:\n" + "\n".join(facts)
    except Exception as e:
        logger.error(f"Failed to get user facts: {e}")
        return f"Gagal mengambil memori: {e}"


def vector_search(query: str, k: int = 5) -> str:
    """Mencari informasi dari memori vektor (semantic search) untuk mengambil konteks percakapan atau fakta yang relevan.
    Args:
        query: Kata kunci atau pertanyaan untuk mencari memori.
        k: Jumlah hasil yang dikembalikan (default: 5).
    """
    try:
        from vector_memory import SemanticMemory
        vm = SemanticMemory()
        if vm.count == 0:
            return "Memori vektor masih kosong. Belum ada riwayat yang tersimpan."

        results = vm.search(query, k=k)
        if not results:
            return "Tidak ditemukan hasil yang relevan di memori vektor."

        output = [f"--- Hasil Pencarian Memori ({len(results)}) ---"]
        for i, r in enumerate(results, 1):
            text = r.get("text", "")[:300]
            score = r.get("score", 0)
            meta = r.get("metadata", {})
            meta_str = f" | {meta}" if meta else ""
            output.append(f"{i}. [Relevansi: {score:.2f}]{meta_str}\n   {text}")

        logger.info(f"Vector search returned {len(results)} results for: {query[:50]}...")
        return "\n\n".join(output)
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return f"Gagal mencari memori vektor: {e}"


def calculate(expression: str) -> str:
    """Menghitung ekspresi matematika (aritmetika, trigonometri, log, akar, dll).
    Args:
        expression: Ekspresi matematika, misal: '2 + 3 * 4' atau 'sqrt(16) + sin(pi/2)'
    """
    try:
        allowed = {
            "abs": abs, "round": round, "int": int, "float": float,
            "min": min, "max": max, "sum": sum, "pow": pow,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
            "log": math.log, "log10": math.log10, "log2": math.log2, "exp": math.exp,
            "pi": math.pi, "e": math.e, "inf": math.inf,
            "floor": math.floor, "ceil": math.ceil, "degrees": math.degrees, "radians": math.radians,
        }
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"Hasil: {result}"
    except Exception as e:
        return f"Gagal menghitung: {e}"


tools_list = [create_file, read_file, list_files, web_search, save_user_fact, get_user_facts, vector_search, calculate]
