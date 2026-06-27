# Bejo AI Project Memory

This file serves as the "State of Mind" and activity log for the development of Bejo. It ensures that any model or developer can understand the project's history and current status.

## 📅 Project Started: 2026-06-26

---

## 📝 Activity Log

### 2026-06-26: Initial Setup & Foundations
- **Activity:** Project initialization and tech stack selection (Python).
- **Details:** Created README, Memory log, and base Python structure.

### 2026-06-26: Core Tools & Security
- **Activity:** Implemented File Management, Web Search, and secured API keys.
- **Details:** Integrated Gemini 2.5 Flash as the primary reasoning engine.

### 2026-06-26: Specialist Skills Expansion
- **Activity:** Added Face Recognition, OSINT, and Digital Forensics tools.

### 2026-06-26: Tax AR & Audit Transformation
- **Activity:** Transformed Bejo into a Senior Auditor and Account Representative.
- **Details:** 
    - Added financial statement analysis (PDF/Excel).
    - Implemented Taxpayer Profiling (SPT, Invoices, Payments).
    - Added Advanced Audit tools (Benchmarking, Equalization).

### 2026-06-26: Final Implementation & Test
- **Activity:** Activated Indonesian TTS and conducted a successful test chat for a Tax Case.
- **Details:** Bejo analyzed a local cafe case, identifying tax risks and providing audit recommendations.
- **Status:** Project Version 1.0 - STABLE & FULLY FUNCTIONAL.

---

### 2026-06-26: Multi-LLM & Wake Word (v2.2)
- **Activity:** LLM engine abstraction, DeepSeek V4 Flash Free support, wake word detection.
- **Details:**
    - **LLM Abstraction:** `llm.py` — unified `send()` interface untuk Gemini & DeepSeek. `create_engine()` factory function.
    - **DeepSeek V4 Flash Free:** OpenAI-compatible API (`api.deepseek.com`), model `deepseek-chat`/`deepseek-reasoner`. Configurable base URL.
    - **Wake Word:** Regex `^(jo|bejo|jobejo)\b` case-insensitive. Deteksi di main loop sebelum LLM → respons instan "Dalem Bos!" tanpa panggil API.
    - **Settings:** Dropdown pilih engine LLM (Gemini/DeepSeek), model per-engine, base URL DeepSeek.
    - **Dynamic Switch:** Ganti engine via settings tanpa restart — engine baru diinisialisasi on-the-fly.
- **Status:** Version 2.2 - STABLE.

### 2026-06-26: STT, TTS Settings & GUI Chat (v2.1)
- **Activity:** Speech-to-Text integration, settings management GUI, chat window improvements.
- **Details:**
    - **STT (Speech-to-Text):** `stt.py` via SpeechRecognition + PyAudio. Google Web Speech API (gratis, no key). Bahasa Indonesia (`id-ID`). Background listening support.
    - **Settings:** `settings_window.py` — Tkinter dialog untuk TTS (engine, bahasa, on/off), STT (engine, bahasa, timeout, phrase limit), tampilan karakter. Disimpan ke `settings.json`.
    - **Config:** `config.py` — load/save JSON settings, merge dengan default.
    - **Chat Window:** Tombol mic (🎤) untuk voice input. Tombol settings (⚙) di header. Status indicator untuk STT.
    - **Voice Tools:** `voice_tools.py` — settings-aware, pilih engine TTS.
    - **Architecture:** Settings di-load saat startup, bisa diubah via GUI tanpa restart.
- **Status:** Version 2.1 - STABLE.

### 2026-06-26: Vector Memory & Conversation Management (v2.0)
- **Activity:** Implemented semantic memory with Turbovec, conversation management, and package restructure.
- **Details:**
    - **Vector Memory (RAG):** Connected `turbovec.IdMapIndex` via `vector_memory.py`. Gemini embeddings (768-dim) enable semantic search across conversation archives and user facts. Persisted to `memory_store/`.
    - **Conversation Manager:** Sliding window (`conversation.py`) prunes old turns, archives them to vector memory, and injects relevant context on new queries.
    - **Logging:** Replaced bare `print()` with `logging` (file + console). Structured logging across all modules.
    - **Package Structure:** Added `__init__.py` to `src/`, `.env.example` template, updated `.gitignore`.
    - **New Tool:** `vector_search()` registered with Gemini for semantic memory retrieval.
    - **Visual Display:** `display.py` renders Bejo character (from `assets/bejo-ai.svg`) via Pygame window — bulat berbulu toska, mata besar, blangkon batik. Ekspresi berubah: neutral (hijau toska), processing (hijau), error (merah). Mata berkedip otomatis. Status text real-time. Window resizable + title bar.
    - **GUI Chat:** `chat_window.py` — Tkinter-based chat window. Scrollable conversation, send button, status indicator. Dual-window: chat (tkinter) + karakter (pygame), keduanya bisa di-drag.
    - **Architecture:** Main thread = Tkinter (chat + pygame tick via `after`). Background thread = Gemini API calls. Queue-based message passing.
- **Status:** Version 2.0 - STABLE.

---

## 🗺️ Roadmap & Next Steps
1. **Phase 1-10: Completed** [x]
2. **Vector Memory (RAG):** [x]
3. **Conversation Management:** [x]
4. **Logging & Error Handling:** [x]
5. **Package Restructure:** [x]
6. **Voice Recognition (STT):** [x] — SpeechRecognition + PyAudio, Google Web Speech API, bahasa Indonesia
7. **Settings GUI:** [x] — TTS engine/bahasa, STT on/off/timeout, tampilan karakter
8. **Multi-LLM Support:** [x] — Gemini (default) & DeepSeek V4 Flash Free via OpenAI-compatible API. Pilih engine di settings.
9. **Wake Word:** [x] — Ketik "JO" / "BEJO" / "JOBEJO" → langsung balas "Dalem Bos!"
10. **Next: Automated SP2DK Document Generator** [ ]
11. **Next: Tax Risk Analytics Dashboard** [ ]

---

## 🛠️ Decisions & Tech Stack
- **Language:** Python 3.10+
- **Primary LLM:** Gemini 2.5 Flash
- **Tools:** Modular (tools, face_tools, osint_tools, tax_tools, tax_profiling, tax_audit, voice_tools)
- **Environment:** .env for API security.
