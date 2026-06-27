import tkinter as tk
from tkinter import ttk
import logging

from config import load_config, save_config

logger = logging.getLogger("bejo.settings")

LABEL_W = 20
SECTION_FONT = ("Segoe UI", 10, "bold")


class SettingsWindow:
    def __init__(self, parent, on_close_callback=None):
        self.win = tk.Toplevel(parent)
        self.win.title("Pengaturan Bejo")
        self.win.geometry("540x620")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        self.on_close = on_close_callback
        self.config = load_config()

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._close)

    def _section(self, parent, title: str) -> tk.Frame:
        f = tk.Frame(parent, bg="#f0f2f5")
        tk.Label(f, text=title, font=SECTION_FONT, bg="#f0f2f5", fg="#2c3e50",
                 anchor="w").pack(fill=tk.X, padx=12, pady=(10, 2))
        sep = tk.Frame(f, height=1, bg="#c0c0c0")
        sep.pack(fill=tk.X, padx=12)
        return f

    def _row(self, parent, label: str) -> tk.Frame:
        r = tk.Frame(parent, bg="#f0f2f5")
        r.pack(fill=tk.X, padx=16, pady=3)
        tk.Label(r, text=label, width=LABEL_W, anchor="w",
                 bg="#f0f2f5", fg="#2c3e50", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        return r

    def _build_ui(self):
        main = tk.Frame(self.win, bg="#f0f2f5")
        main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        canvas = tk.Canvas(main, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#f0f2f5")

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=520)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        sec_llm = self._section(scrollable, "Model AI (Gemini)")
        sec_llm.pack(fill=tk.X, pady=(0, 4))

        f0b = self._row(sec_llm, "Model Gemini")
        self.gemini_model_var = tk.StringVar(value=self.config["llm"]["gemini_model"])
        ttk.Combobox(f0b, textvariable=self.gemini_model_var,
                     values=["gemini-3.0-flash", "gemini-3.0-flash-lite",
                             "gemini-2.5-flash", "gemini-2.5-flash-lite",
                             "gemini-2.0-flash", "gemini-2.0-flash-lite",
                             "gemini-1.5-flash", "gemini-1.5-pro",
                             "gemma-3-27b-it", "gemma-3-12b-it",
                             "gemma-2-27b-it", "gemma-2-9b-it"],
                     state="readonly", width=22).pack(side=tk.LEFT)

        f0d = self._row(sec_llm, "API Key")
        self.gemini_key_var = tk.StringVar(value=self.config["llm"]["gemini_api_key"])
        tk.Entry(f0d, textvariable=self.gemini_key_var, width=26, bd=1,
                 relief=tk.SOLID).pack(side=tk.LEFT)

        sec_tts = self._section(scrollable, "TTS (Text-to-Speech)")
        sec_tts.pack(fill=tk.X, pady=(0, 4))

        f1 = self._row(sec_tts, "Aktifkan TTS")
        self.tts_var = tk.BooleanVar(value=self.config["tts"]["enabled"])
        ttk.Checkbutton(f1, variable=self.tts_var).pack(side=tk.LEFT)

        f2 = self._row(sec_tts, "Engine")
        self.tts_engine_var = tk.StringVar(value=self.config["tts"]["engine"])
        ttm = ttk.Combobox(f2, textvariable=self.tts_engine_var,
                           values=["edge-tts", "gtts"], state="readonly", width=14)
        ttm.pack(side=tk.LEFT)
        ttm.bind("<<ComboboxSelected>>", lambda e: self._toggle_tts_fields())

        f2b = self._row(sec_tts, "Gender Suara")
        self.tts_gender_var = tk.StringVar(value=self.config["tts"]["voice_gender"])
        ttk.Combobox(f2b, textvariable=self.tts_gender_var,
                     values=["male", "female"], state="readonly", width=14).pack(side=tk.LEFT)
        self.tts_gender_frame = f2b

        f2c = self._row(sec_tts, "Voice ID")
        self.tts_voice_var = tk.StringVar(value=self.config["tts"]["voice"])
        tk.Entry(f2c, textvariable=self.tts_voice_var, width=26, bd=1,
                 relief=tk.SOLID).pack(side=tk.LEFT)
        self.tts_voice_frame = f2c

        f3 = self._row(sec_tts, "Bahasa")
        self.tts_lang_var = tk.StringVar(value=self.config["tts"]["lang"])
        ttc = ttk.Combobox(f3, textvariable=self.tts_lang_var,
                           values=["id", "en", "ja", "ko", "zh-CN", "ar"],
                           state="readonly", width=14)
        ttc.pack(side=tk.LEFT)

        self._toggle_tts_fields()

        sec_stt = self._section(scrollable, "STT (Speech-to-Text)")
        sec_stt.pack(fill=tk.X, pady=(8, 4))

        f4 = self._row(sec_stt, "Aktifkan STT")
        self.stt_var = tk.BooleanVar(value=self.config["stt"]["enabled"])
        ttk.Checkbutton(f4, variable=self.stt_var).pack(side=tk.LEFT)

        f5 = self._row(sec_stt, "Engine")
        self.stt_engine_var = tk.StringVar(value=self.config["stt"]["engine"])
        ttc2 = ttk.Combobox(f5, textvariable=self.stt_engine_var,
                            values=["google", "windows"], state="readonly", width=14)
        ttc2.pack(side=tk.LEFT)

        f6 = self._row(sec_stt, "Bahasa")
        self.stt_lang_var = tk.StringVar(value=self.config["stt"]["lang"])
        ttc3 = ttk.Combobox(f6, textvariable=self.stt_lang_var,
                            values=["id-ID", "en-US", "ja-JP", "ko-KR", "zh-CN", "ar-SA"],
                            state="readonly", width=14)
        ttc3.pack(side=tk.LEFT)

        f7 = self._row(sec_stt, "Timeout (detik)")
        self.stt_timeout_var = tk.IntVar(value=self.config["stt"]["timeout"])
        tk.Spinbox(f7, from_=2, to=15, textvariable=self.stt_timeout_var, width=6).pack(side=tk.LEFT)

        f8 = self._row(sec_stt, "Maks durasi (detik)")
        self.stt_phrase_var = tk.IntVar(value=self.config["stt"]["phrase_limit"])
        tk.Spinbox(f8, from_=3, to=30, textvariable=self.stt_phrase_var, width=6).pack(side=tk.LEFT)

        sec_face = self._section(scrollable, "Deteksi Wajah (Kamera)")
        sec_face.pack(fill=tk.X, pady=(0, 4))

        f9a = self._row(sec_face, "Aktifkan Kamera")
        self.face_var = tk.BooleanVar(value=self.config["face"]["enabled"])
        ttk.Checkbutton(f9a, variable=self.face_var).pack(side=tk.LEFT)

        f9b = self._row(sec_face, "Interval deteksi (dtk)")
        self.face_interval_var = tk.DoubleVar(value=self.config["face"]["interval"])
        tk.Spinbox(f9b, from_=1.0, to=10.0, increment=0.5,
                   textvariable=self.face_interval_var, width=6).pack(side=tk.LEFT)

        f9c = self._row(sec_face, "Cooldown sapa (dtk)")
        self.face_cooldown_var = tk.DoubleVar(value=self.config["face"]["cooldown"])
        tk.Spinbox(f9c, from_=5.0, to=120.0, increment=5.0,
                   textvariable=self.face_cooldown_var, width=6).pack(side=tk.LEFT)

        f9d = self._row(sec_face, "Sapaan")
        self.face_greeting_var = tk.StringVar(value=self.config["face"]["greeting"])
        tk.Entry(f9d, textvariable=self.face_greeting_var, width=26, bd=1,
                 relief=tk.SOLID).pack(side=tk.LEFT)

        sec_display = self._section(scrollable, "Tampilan")
        sec_display.pack(fill=tk.X, pady=(8, 4))

        f9 = self._row(sec_display, "Tampilkan Karakter")
        self.display_var = tk.BooleanVar(value=self.config["display"]["show_character"])
        ttk.Checkbutton(f9, variable=self.display_var).pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.win, bg="#f0f2f5", height=50)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_frame.pack_propagate(False)

        tk.Button(btn_frame, text="Simpan", command=self._save,
                  bg="#2c3e50", fg="white", bd=0, padx=24, pady=6,
                  font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side=tk.RIGHT, padx=16, pady=8)
        tk.Button(btn_frame, text="Batal", command=self._close,
                  bg="#cccccc", fg="#333333", bd=0, padx=20, pady=6,
                  font=("Segoe UI", 10), cursor="hand2").pack(side=tk.RIGHT, padx=6, pady=8)

    def _toggle_tts_fields(self):
        engine = self.tts_engine_var.get()
        if engine == "edge-tts":
            self.tts_gender_frame.pack(fill=tk.X, padx=16, pady=2)
            self.tts_voice_frame.pack(fill=tk.X, padx=16, pady=2)
        else:
            self.tts_gender_frame.pack_forget()
            self.tts_voice_frame.pack_forget()

    def _save(self):
        self.config["llm"]["gemini_model"] = self.gemini_model_var.get()
        self.config["llm"]["gemini_api_key"] = self.gemini_key_var.get()
        self.config["tts"]["enabled"] = self.tts_var.get()
        self.config["tts"]["engine"] = self.tts_engine_var.get()
        self.config["tts"]["lang"] = self.tts_lang_var.get()
        self.config["tts"]["voice_gender"] = self.tts_gender_var.get()
        self.config["tts"]["voice"] = self.tts_voice_var.get()
        self.config["stt"]["enabled"] = self.stt_var.get()
        self.config["stt"]["engine"] = self.stt_engine_var.get()
        self.config["stt"]["lang"] = self.stt_lang_var.get()
        self.config["stt"]["timeout"] = self.stt_timeout_var.get()
        self.config["stt"]["phrase_limit"] = self.stt_phrase_var.get()
        self.config["display"]["show_character"] = self.display_var.get()
        self.config["face"]["enabled"] = self.face_var.get()
        self.config["face"]["interval"] = self.face_interval_var.get()
        self.config["face"]["cooldown"] = self.face_cooldown_var.get()
        self.config["face"]["greeting"] = self.face_greeting_var.get()
        save_config(self.config)
        logger.info("Settings saved via GUI")
        self._close()

    def _close(self):
        try:
            self.win.grab_release()
        except:
            pass
        try:
            self.win.destroy()
        except:
            pass
        if self.on_close:
            self.on_close()
