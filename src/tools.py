import os
import json
from duckduckgo_search import DDGS

MEMORY_FILE = "user_memory.json"

def create_file(filename: str, content: str) -> str:
    """Membuat file baru dengan konten yang ditentukan.
    Args:
        filename: Nama file (misal: 'catatan.txt')
        content: Isi dari file tersebut.
    """
    try:
        # Pastikan kita tetap di dalam folder project untuk keamanan
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Berhasil membuat file: {filename}"
    except Exception as e:
        return f"Gagal membuat file: {e}"

def read_file(filename: str) -> str:
    """Membaca isi dari sebuah file.
    Args:
        filename: Nama file yang ingin dibaca.
    """
    try:
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Gagal membaca file: {e}"

def list_files() -> str:
    """Melihat daftar file di direktori saat ini."""
    try:
        files = os.listdir(os.getcwd())
        return "\n".join(files) if files else "Folder kosong."
    except Exception as e:
        return f"Gagal melist file: {e}"

def web_search(query: str) -> str:
    """Mencari informasi di internet menggunakan DuckDuckGo.
    Args:
        query: Kata kunci pencarian.
    """
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "Tidak ditemukan hasil pencarian."
        
        search_summary = []
        for r in results:
            search_summary.append(f"Title: {r['title']}\nSnippet: {r['body']}\nLink: {r['href']}\n")
        
        return "\n---\n".join(search_summary)
    except Exception as e:
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
        
        return f"Saya sudah ingat bahwa {fact_key} Anda adalah {fact_value}."
    except Exception as e:
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
        return "Berikut yang saya ingat tentang Anda:\n" + "\n".join(facts)
    except Exception as e:
        return f"Gagal mengambil memori: {e}"

# Kumpulan tools yang akan diekspos ke Bejo
tools_list = [create_file, read_file, list_files, web_search, save_user_fact, get_user_facts]
