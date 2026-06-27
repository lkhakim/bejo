# Bejo AI — Agent Guide

## Run
- `pip install -r requirements.txt`
- `python src/main.py`
- Diagnostics: `python src/diagnostic.py`

## Structure
- **Entrypoint:** `src/main.py` — Tkinter main loop + Pygame character display
- **LLM:** `src/llm.py` — `create_engine(config, tools)` factory, `GeminiEngine` with auto-retry (429/503)
- **Knowledge Base:** `src/knowledge.py` — Q&A via turbovec `IdMapIndex` (3072-dim Gemini embedding), persisted to `knowledge_store/`
- **Vector Memory:** `src/vector_memory.py` — semantic memory (same turbovec setup), persisted to `memory_store/` (gitignored)
- **Inference:** `src/inference.py` — KB lookup first (threshold 0.6), then Gemini fallback
- **Tools:** `src/tools.py` (core), `osint_tools.py`, `tax_tools.py`, `tax_profiling.py`, `tax_audit.py`, `tools_media.py`, `face_tools.py`, `voice_tools.py` — all registered in `main.py:37-42`
- **UI:** `chat_window.py` (Tkinter), `display.py` (Pygame), `settings_window.py`, `training_window.py`

## Key architecture
- Wake word: regex `^(jo|bejo|jobejo)\b` — responds "Dalem Bos!" without calling LLM
- LLM engine switchable via settings GUI (no restart) — currently Gemini only; DeepSeek abstraction existed in v2.2 but engine factory only returns `GeminiEngine`
- TTS: edge-tts primary (gender-male), gTTS fallback, configurable in settings
- STT: Windows SAPI (winspeech) or Google Web Speech API (speech_recognition), Indonesian `id-ID`
- Face detection: OpenCV Haar cascade, optional face_recognition for ID
- `.env` must contain `GEMINI_API_KEY`
- `settings.json` at project root — hot-reloaded after settings GUI closes

## Important notes
- No tests, no linter, no type checker, no CI
- No package build — runs directly as `python src/main.py`
- Full Indonesian: system prompt, UI labels, tool names, comments, voice
- turbovec is a vendored sub-project at `turbovec/` (Rust + Python bindings)
- Embedding fallback: deterministic hash-based random vector when Gemini API fails
- `memory_store/`, `activity_log.json`, `bejo.log`, `faces_db.pkl`, `temp_voice.mp3`, `user_memory.json`, `taxpayer_profiles.json` are gitignored runtime data
- **Skill system:** `skills/*.md` (YAML frontmatter + markdown, agentskills.io format) auto-discovered by `SkillManager`. Skills appear in Training window dropdown alongside hardcoded tool modules. New skills can be added by creating `.md` files in `skills/`.
