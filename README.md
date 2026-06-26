# Bejo AI: Personal Assistant Agent

Bejo is a Jarvis-like personal AI assistant powered by the Gemini LLM. It is designed to be efficient, proactive, and capable of managing tasks through tool integration and long-term memory.

## 🚀 Vision
To create a local-first, intelligent assistant that can reason through complex tasks and interact with the user's environment seamlessly.

## 🏗️ Design & Architecture
The project follows a **Reasoning -> Action -> Memory** loop:
1. **Brain (LLM):** Gemini (Google AI) handles natural language understanding and reasoning.
2. **Tools (Function Calling):**
   - File System Management (Read/Write/Search)
   - Web Search (Real-time information)
   - Shell Execution (Automation)
3. **Memory System:**
   - **Short-term:** Conversation context.
   - **Long-term:** Persistent storage in Markdown/Vector DB for preferences and history.

## ✨ Features (Planned & Current)
- [x] Natural Language Chat with funny & friendly personality.
- [x] File and Workspace Management (Create, Read, List).
- [x] Web search integration (DuckDuckGo).
- [x] Long-term Memory (User facts and preferences).
- [x] Visual Recognition (Register and Identify faces via Webcam).
- [x] OSINT & Digital Forensics specialist support.
- [x] Tax AR & Senior Auditor expertise (Financial Statement Analysis).
- [x] Taxpayer Profiling (SPT, Invoices, Payments reconciliation).
- [x] Advanced Tax Audit (Benchmarking Ratios & Equalization).
- [x] Voice Interface (Indonesian TTS).
- [ ] Voice interface (STT).
- [ ] Proactive notifications and reminders.

## 🛠️ Requirements
- Python 3.10+
- `google-generativeai` (Gemini SDK)
- `python-dotenv` (For environment variable management)
- Gemini API Key
- Internet connection

## 📖 Usage
*Instructions will be added as implementation progresses.*
