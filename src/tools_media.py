import os
import glob
import random
import threading
import time
import logging
import webbrowser

logger = logging.getLogger("bejo.tools_media")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from vector_memory import SemanticMemory

MUSIC_DIR = os.path.join(os.path.expanduser("~"), "Music")

_music_playing = False
_music_paused = False
_music_thread = None


def _music_state():
    return _music_playing, _music_paused


def pause_music_playback():
    global _music_paused
    was = _music_playing and not _music_paused
    if _music_playing:
        _music_paused = True
        try:
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.music.pause()
        except Exception:
            pass
    return was


def resume_music_playback():
    global _music_paused
    if _music_playing and _music_paused:
        _music_paused = False
        try:
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.music.unpause()
        except Exception:
            pass


def browser_search(query: str) -> str:
    """Membuka browser untuk mencari informasi di internet, mengambil hasilnya, dan menyimpannya ke memori vektor.
    Args:
        query: Kata kunci pencarian.
    """
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)

    content = f"Browser opened for: {query}"
    if REQUESTS_AVAILABLE:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            if BS4_AVAILABLE:
                soup = BeautifulSoup(resp.text, "html.parser")
                snippets = []
                for g in soup.select("[class*='g']")[:5]:
                    h3 = g.select_one("h3")
                    span = g.select_one("[data-sncf]")
                    if h3:
                        snip = span.text if span else ""
                        snippets.append(f"{h3.text}: {snip}")
                content = "\n".join(snippets) if snippets else resp.text[:1500]
            else:
                content = resp.text[:1500]
        except Exception as e:
            content = f"Browser opened. Fetch error: {e}"

    try:
        vm = SemanticMemory()
        vm.add(f"Hasil pencarian: {query}\n{content}", {"type": "web_search", "query": query})
        return f"Pencarian '{query}' dibuka di browser dan hasilnya disimpan ke memori vektor."
    except Exception as e:
        return f"Browser dibuka untuk '{query}', tapi gagal simpan ke memori: {e}"


def web_fetch(url: str) -> str:
    """Mengambil konten dari URL tertentu dan menyimpannya ke memori vektor. Browser juga dibuka.
    Args:
        url: URL lengkap halaman web.
    """
    webbrowser.open(url)
    if not REQUESTS_AVAILABLE:
        try:
            vm = SemanticMemory()
            vm.add(f"Dibuka: {url}", {"type": "web_fetch", "url": url})
        except Exception:
            pass
        return f"Browser dibuka ke {url}. Install requests untuk mengambil konten otomatis."

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if BS4_AVAILABLE:
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)[:3000]
        else:
            text = resp.text[:1500]
        vm = SemanticMemory()
        vm.add(f"Konten dari {url}\n{text}", {"type": "web_fetch", "url": url})
        return f"Konten dari {url} berhasil diambil dan disimpan ke memori vektor."
    except Exception as e:
        return f"Gagal mengambil konten dari {url}: {e}"


def play_music(query: str = "") -> str:
    """Memutar musik dari folder Music. Bisa mencari lagu berdasarkan nama.
    Args:
        query: Nama lagu atau kata kunci (opsional). Kosongkan untuk memutar semua lagu secara shuffle.
    """
    global _music_playing, _music_paused, _music_thread

    if not PYGAME_AVAILABLE:
        return "Pygame tidak tersedia untuk memutar musik."

    stop_music()

    music_ext = ("*.mp3", "*.wav", "*.ogg", "*.flac", "*.m4a", "*.wma")
    files = []
    for ext in music_ext:
        files.extend(glob.glob(os.path.join(MUSIC_DIR, "**", ext), recursive=True))
    files = [f for f in files if os.path.isfile(f)]

    if not files:
        return "Tidak ada file musik ditemukan di folder Music."

    if query:
        q = query.lower()
        files = [f for f in files if q in os.path.basename(f).lower()]
        if not files:
            return f"Tidak ditemukan lagu dengan kata '{query}'."
        random.shuffle(files)
    else:
        random.shuffle(files)

    def _loop(playlist):
        global _music_playing, _music_paused
        _music_playing = True
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except Exception:
            _music_playing = False
            return

        for song in playlist:
            if not _music_playing:
                break
            try:
                pygame.mixer.music.load(song)
                pygame.mixer.music.play()
                name = os.path.basename(song)
                logger.info(f"Music playing: {name}")
                while pygame.mixer.music.get_busy():
                    if not _music_playing:
                        pygame.mixer.music.fadeout(500)
                        break
                    if _music_paused:
                        pygame.mixer.music.pause()
                        while _music_paused and _music_playing:
                            time.sleep(0.1)
                        if _music_playing and not _music_paused:
                            pygame.mixer.music.unpause()
                    time.sleep(0.3)
                pygame.mixer.music.unload()
            except Exception as e:
                logger.warning(f"Music error on {song}: {e}")
                continue
        _music_playing = False

    _music_thread = threading.Thread(target=_loop, args=(files,), daemon=True)
    _music_thread.start()

    total = len(files)
    if query:
        return f"Memutar {total} lagu yang cocok dengan '{query}'."
    return f"Memutar {total} lagu secara acak dari folder Music."


def stop_music() -> str:
    """Menghentikan pemutaran musik."""
    global _music_playing, _music_paused
    _music_playing = False
    _music_paused = False
    try:
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    except Exception:
        pass
    return "Musik dihentikan."


def pause_music() -> str:
    """Menjeda pemutaran musik."""
    global _music_paused
    if not _music_playing:
        return "Tidak ada musik yang sedang diputar."
    _music_paused = True
    return "Musik dijeda."


def resume_music() -> str:
    """Melanjutkan pemutaran musik yang sedang dijeda."""
    global _music_paused
    if not _music_playing:
        return "Tidak ada musik yang sedang dijeda."
    _music_paused = False
    return "Musik dilanjutkan."


def list_music() -> str:
    """Menampilkan daftar musik yang tersedia di folder Music."""
    music_ext = ("*.mp3", "*.wav", "*.ogg", "*.flac", "*.m4a", "*.wma")
    count = 0
    folders = set()
    for ext in music_ext:
        for f in glob.glob(os.path.join(MUSIC_DIR, "**", ext), recursive=True):
            if os.path.isfile(f):
                count += 1
                folders.add(os.path.dirname(f))
    if count == 0:
        return "Tidak ada file musik di folder Music."
    folder_list = ", ".join(sorted(os.path.basename(f) for f in folders)[:8])
    return f"Ditemukan {count} file musik di {len(folders)} folder.\nFolder: {folder_list}"


def shutdown_computer(delay: int = 60) -> str:
    """Mematikan komputer. Gunakan dengan hati-hati!
    Args:
        delay: Waktu tunggu dalam detik sebelum shutdown (default: 60).
    """
    try:
        os.system(f"shutdown /s /t {delay} /c \"Bejo AI: Shutdown by user request\"")
        if delay > 0:
            return f"Komputer akan mati dalam {delay} detik. Jalankan cancel_shutdown() untuk membatalkan."
        return "Komputer akan mati sekarang."
    except Exception as e:
        return f"Gagal shutdown: {e}"


def restart_computer(delay: int = 60) -> str:
    """Me-restart komputer. Gunakan dengan hati-hati!
    Args:
        delay: Waktu tunggu dalam detik sebelum restart (default: 60).
    """
    try:
        os.system(f"shutdown /r /t {delay} /c \"Bejo AI: Restart by user request\"")
        if delay > 0:
            return f"Komputer akan restart dalam {delay} detik. Jalankan cancel_shutdown() untuk membatalkan."
        return "Komputer akan restart sekarang."
    except Exception as e:
        return f"Gagal restart: {e}"


def cancel_shutdown() -> str:
    """Membatalkan shutdown atau restart yang tertunda."""
    try:
        os.system("shutdown /a")
        return "Shutdown/restart yang tertunda dibatalkan."
    except Exception as e:
        return f"Gagal membatalkan: {e}"


media_tools = [browser_search, web_fetch, play_music, stop_music, pause_music, resume_music, list_music,
               shutdown_computer, restart_computer, cancel_shutdown]
