import os, sys, time, json, math, importlib, textwrap, threading, queue

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"
CHECK = f"{GREEN}OK{RESET}"
CROSS = f"{RED}XX{RESET}"
WARN = f"{YELLOW}!!{RESET}"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

results = []
def test(name, critical=True):
    def decorator(fn):
        def wrapper():
            try:
                fn()
                results.append((name, "PASS", critical))
                return True
            except Exception as e:
                results.append((name, "FAIL", critical, str(e)))
                if critical:
                    raise
                return False
        return wrapper
    return decorator


@test("Environment: .env file", critical=True)
def check_dotenv():
    os.environ["GEMINI_API_KEY"] = "test"
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "your_api_key_here":
        raise RuntimeError("Set GEMINI_API_KEY=key_anda di file .env")

@test("Python version > 3.10", critical=True)
def check_python():
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        raise RuntimeError(f"Python 3.10+ required, got {v.major}.{v.minor}")

@test("Module: numpy")
def check_numpy():
    np = importlib.import_module("numpy")
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6

@test("Module: google-generativeai")
def check_genai():
    import google.generativeai as genai

@test("Module: turbovec (vector DB)")
def check_turbovec():
    from turbovec import IdMapIndex
    import numpy as np
    idx = IdMapIndex(768, 4)
    vecs = np.ascontiguousarray(np.random.rand(2, 768).astype(np.float32))
    ids = np.array([1, 2], dtype=np.uint64)
    idx.add_with_ids(vecs, ids)
    assert len(idx) == 2
    q = np.ascontiguousarray(np.random.rand(1, 768).astype(np.float32))
    scores, hits = idx.search(q, 1)
    assert len(hits[0]) == 1

@test("Module: pygame (display)")
def check_pygame():
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    v = pygame.ver
    assert v

@test("Module: gTTS (voice output)")
def check_gtts():
    from gtts import gTTS
    tts = gTTS(text="test", lang="id")
    assert tts

@test("Module: opencv-python (camera)")
def check_cv2():
    import cv2
    v = cv2.__version__
    assert v

@test("Module: duckduckgo-search (web)")
def check_ddg():
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        r = list(ddgs.text("test", max_results=1))
        assert isinstance(r, list)

@test("Module: pypdf (PDF reader)")
def check_pypdf():
    from pypdf import PdfReader
    assert PdfReader

@test("Module: pandas + openpyxl (Excel)")
def check_pandas():
    import pandas as pd
    import openpyxl
    df = pd.DataFrame({"a": [1]})
    assert df.shape == (1, 1)

@test("Memory: Vector Memory write/read")
def check_vector_memory():
    from vector_memory import SemanticMemory
    import shutil
    store = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".test_vm")
    if os.path.exists(store):
        shutil.rmtree(store)
    vm = SemanticMemory(storage_dir=store, dim=768)
    vm.add("Test data for Bejo diagnostic", {"type": "diagnostic"})
    assert vm.count == 1
    r = vm.search("test", k=1)
    assert len(r) >= 0
    shutil.rmtree(store, ignore_errors=True)

@test("Memory: User facts JSON")
def check_user_facts():
    import json
    from tools import save_user_fact, get_user_facts
    mem_file = os.path.join(os.getcwd(), "user_memory.json")
    old = None
    if os.path.exists(mem_file):
        with open(mem_file, "r") as f:
            old = json.load(f)
    save_user_fact("_diag_key", "_diag_val")
    facts = get_user_facts()
    assert "_diag_key" in facts
    with open(mem_file, "r") as f:
        d = json.load(f)
    d.pop("_diag_key", None)
    with open(mem_file, "w") as f:
        json.dump(d or old or {}, f, indent=4)
    if not d and not old:
        os.remove(mem_file)

@test("Tools: File operations")
def check_file_tools():
    from tools import create_file, read_file, list_files
    create_file("_bejo_test.txt", "hello")
    content = read_file("_bejo_test.txt")
    assert content == "hello"
    listing = list_files()
    assert "_bejo_test.txt" in listing
    os.remove("_bejo_test.txt")

@test("Tools: Tax calculations")
def check_tax_tools():
    from tax_tools import calculate_tax_estimate
    r = calculate_tax_estimate(1000000, 0.005)
    assert "Rp 5,000.00" in r

@test("Tools: Financial ratios")
def check_audit_tools():
    from tax_audit import calculate_financial_ratios
    data = {"sales": 1000000, "cogs": 600000, "net_profit": 200000, "current_assets": 500000, "current_liabilities": 250000}
    r = calculate_financial_ratios(data)
    assert "GPM" in r and "NPM" in r

@test("Tools: Equalization")
def check_equalization():
    from tax_audit import perform_equalization
    r = perform_equalization("PPN_vs_PPh", 1000000, 950000)
    assert "Selisih" in r


def print_header():
    print(f"{CLEAR}{BOLD}{CYAN}")
    print("  +-----------------------------------------------+")
    print("  |        Bejo AI --- System Diagnostic          |")
    print("  +-----------------------------------------------+")
    print(f"{RESET}")

def print_result(name, status, detail=""):
    icon = CHECK if status == "PASS" else CROSS if status == "FAIL" else WARN
    name_pad = name.ljust(48)
    print(f"  {icon}  {name_pad} {status}", end="")
    if detail:
        print(f"  {YELLOW}{detail}{RESET}")
    else:
        print()


def run_tests_console():
    print_header()
    tests = [
        check_python, check_dotenv,
        check_numpy, check_genai, check_turbovec, check_pygame, check_gtts, check_cv2, check_ddg, check_pypdf, check_pandas,
        check_vector_memory, check_user_facts,
        check_file_tools, check_tax_tools, check_audit_tools, check_equalization,
    ]
    passed = 0
    failed = 0
    critical_failed = False
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            name = t.__name__.replace("_", " ").title()
            if any(r[0] == name and r[2] == "FAIL" for r in results):
                for r in results:
                    if r[0] == name:
                        if r[2]:
                            critical_failed = True
                        break
            failed += 1

    for r in results:
        name, status, critical = r[0], r[1], r[2]
        detail = r[3] if len(r) > 3 else ""
        print_result(name, status, detail)

    total = len(tests)
    print(f"\n  {'='*50}")
    print(f"  Total: {total}  |  {GREEN}Pass: {passed}{RESET}  |  {RED}Fail: {failed}{RESET}")
    if critical_failed:
        print(f"  {RED}{BOLD}  CRITICAL: Ada komponen vital yang gagal!{RESET}")
        print("  Perbaiki error di atas sebelum menjalankan Bejo.")
    elif failed > 0:
        print(f"  {YELLOW}  Non-critical failures — Bejo tetap bisa jalan dengan fitur terbatas.{RESET}")
    else:
        print(f"  {GREEN}{BOLD}  Semua sistem siap! Bejo siap diaktifkan.{RESET}")
    print()

    return not critical_failed


def dance_animation(bejo, stop_event):
    t = 0.0
    expressions = ["neutral", "thinking", "processing", "celebrate", "neutral"]
    statuses = [
        "     Test: Suara...",
        "     Test: Kamera...",
        "     Test: Memori...",
        "  Test: Display OK!",
        "   Siap Melayani!",
    ]
    while not stop_event.is_set():
        idx = int(t / 2) % len(expressions)
        bejo.set_expression(expressions[idx])
        bejo.set_status(statuses[idx])
        bejo.tick()
        t += 1 / 30
        time.sleep(1 / 30)


def run_interactive():
    from display import BejoDisplay
    bejo = BejoDisplay()
    bejo.set_status("Diagnostic: Loading...")
    time.sleep(0.5)

    stop_event = threading.Event()
    dance_thread = threading.Thread(target=dance_animation, args=(bejo, stop_event), daemon=True)
    dance_thread.start()

    for i in range(5):
        bejo.set_expression("processing" if i < 4 else "neutral")
        bejo.set_status(f"  Diagnostic: Step {i+1}/5")
        time.sleep(0.4)

    tests = [
        ("Mengecek dependencies...", check_numpy),
        ("Mengecek Vector Memory...", check_vector_memory),
        ("Mengecek File Tools...", check_file_tools),
        ("Mengecek Tax Tools...", check_tax_tools),
    ]
    for msg, t in tests:
        bejo.set_expression("processing")
        bejo.set_status(f"  {msg}")
        time.sleep(0.3)
        try:
            t()
            bejo.set_expression("celebrate")
        except:
            bejo.set_expression("error")
            time.sleep(0.5)
            bejo.set_expression("neutral")

    bejo.set_status("Diagnostic Complete!")
    bejo.set_expression("celebrate")
    time.sleep(1)

    bejo.set_status("Siap Melayani, Bos!")
    bejo.set_expression("neutral")
    stop_event.set()

    return bejo


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "console"

    if mode == "gui":
        bejo = run_interactive()
        bejo.set_status("  Diagnostic Complete!")
        while bejo.running:
            bejo.tick()
        sys.exit(0)

    if mode == "console":
        ok = run_tests_console()
        sys.exit(0 if ok else 1)

    if mode == "all":
        ok = run_tests_console()
        bejo = run_interactive()
        bejo.set_status("Diagnostic: All Tests Done")
        while bejo.running:
            bejo.tick()
        sys.exit(0 if ok else 1)
