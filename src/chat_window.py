import time
import tkinter as tk
from tkinter import scrolledtext
import threading

CHAT_FONT = ("Segoe UI", 11)
USER_COLOR = "#d4edda"
BEJO_COLOR = "#cce5ff"
SYSTEM_COLOR = "#fff3cd"
BG = "#f0f2f5"
HEADER_BG = "#2c3e50"
HEADER_FG = "#ffffff"


class ChatWindow:
    def __init__(self, on_send=None, on_mic=None, on_settings=None, on_training=None):
        self.root = tk.Tk()
        self.root.title("Bejo AI - Chat")
        self.root.geometry("520x620")
        self.root.minsize(400, 400)
        self.root.configure(bg=BG)

        self._on_send = on_send
        self._on_mic = on_mic
        self._on_settings = on_settings
        self._on_training = on_training
        self._closed = False
        self._mic_active = False
        self._auto_listen = False
        self._mic_paused = False
        self._idle_time = 0
        self._idle_max = 60

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.entry.bind("<Return>", lambda e: self._send())

    def _build_ui(self):
        header = tk.Frame(self.root, bg=HEADER_BG, height=38)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(header, text="Bejo AI", font=("Segoe UI", 12, "bold"),
                 fg=HEADER_FG, bg=HEADER_BG).pack(side=tk.LEFT, padx=14, pady=4)

        self.indicator = tk.Label(header, text="Siap", font=("Segoe UI", 9),
                                  fg="#a0d0a0", bg=HEADER_BG)
        self.indicator.pack(side=tk.RIGHT, padx=14, pady=4)

        if self._on_training:
            tk.Button(header, text="\U0001F4D6", font=("Segoe UI", 12),
                      fg=HEADER_FG, bg=HEADER_BG, bd=0, cursor="hand2",
                      activebackground="#3a5068", activeforeground="white",
                      command=lambda: self._on_training()).pack(side=tk.RIGHT, padx=(0, 2))

        if self._on_settings:
            tk.Button(header, text="\u2699", font=("Segoe UI", 12),
                      fg=HEADER_FG, bg=HEADER_BG, bd=0, cursor="hand2",
                      activebackground="#3a5068", activeforeground="white",
                      command=lambda: self._on_settings()).pack(side=tk.RIGHT, padx=(0, 4))

        chat_frame = tk.Frame(self.root, bg=BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=CHAT_FONT,
            bg="#ffffff", fg="#1a1a2e", bd=1, relief=tk.SOLID,
            highlightthickness=0, padx=10, pady=10,
            state=tk.DISABLED,
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(self.root, bg=BG, height=48)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=(6, 10))
        input_frame.pack_propagate(False)

        if self._on_mic:
            self.mic_btn = tk.Button(
                input_frame, text="\U0001F3A4", font=("Segoe UI", 14),
                bg="#e8eaed", fg="#555555", bd=0, padx=10, pady=2,
                activebackground="#d4edda", activeforeground="#2c3e50",
                cursor="hand2", command=self._toggle_mic,
            )
            self.mic_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.entry = tk.Entry(input_frame, font=CHAT_FONT, bd=1,
                              relief=tk.SOLID, highlightthickness=0,
                              bg="#ffffff", fg="#1a1a2e")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self.entry.focus()

        self.send_btn = tk.Button(
            input_frame, text="Kirim", font=("Segoe UI", 10, "bold"),
            bg="#2c3e50", fg="#ffffff", bd=0, padx=18, pady=4,
            activebackground="#1a2a3a", activeforeground="#ffffff",
            cursor="hand2", command=self._send,
        )
        self.send_btn.pack(side=tk.RIGHT)

    def _toggle_mic(self):
        if self._auto_listen:
            self.stop_auto_listen()
        else:
            self.start_mic()

    def start_mic(self):
        if not self._on_mic:
            return
        if self._mic_active:
            return
        self._mic_active = True
        self.mic_btn.config(bg="#d4edda", fg="#2c3e50", text="\U0001F3A4 \u25CF")
        self.set_status("Mendengarkan...")

        def stt_thread():
            text = self._on_mic()
            self.root.after(0, lambda: self._on_stt_done(text))

        threading.Thread(target=stt_thread, daemon=True).start()

    def start_auto_listen(self, idle_max=60, listen_timeout=5):
        if not self._on_mic:
            return
        if self._auto_listen:
            return
        self._auto_listen = True
        self._idle_time = 0
        self._idle_max = idle_max
        self._listen_timeout = listen_timeout
        self._mic_active = True
        self.mic_btn.config(bg="#d4edda", fg="#2c3e50", text="\U0001F3A4 \u25CF")
        self.set_status("Mendengarkan...")

        def loop():
            while self._auto_listen:
                while self._mic_paused and self._auto_listen:
                    time.sleep(0.1)
                if not self._auto_listen:
                    break
                text = self._on_mic()
                if not self._auto_listen:
                    break
                if text is None:
                    self._idle_time += self._listen_timeout
                    if self._idle_time >= self._idle_max:
                        self.root.after(0, self._on_auto_idle)
                    continue
                self._idle_time = 0
                if text.startswith("ERR:"):
                    self.root.after(0, lambda t=text: self._on_auto_error(t))
                    continue
                self.root.after(0, lambda t=text: self._on_auto_result(t))
            self.root.after(0, self._on_auto_stopped)

        threading.Thread(target=loop, daemon=True).start()

    def stop_auto_listen(self):
        self._auto_listen = False

    def pause_mic(self):
        self._mic_paused = True

    def resume_mic(self):
        self._mic_paused = False

    def _on_auto_idle(self):
        self._auto_listen = False
        self._mic_active = False
        self.mic_btn.config(bg="#e8eaed", fg="#555555", text="\U0001F3A4")
        self.set_status("Idle — panggil Bejo dulu")

    def _on_auto_error(self, text):
        self.add_message("System", text.split("ERR:", 1)[1].strip(), SYSTEM_COLOR)

    def _on_auto_result(self, text):
        self._mic_active = False
        self.mic_btn.config(bg="#e8eaed", fg="#555555", text="\U0001F3A4")
        self.set_status("Siap")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self._send()

    def _on_auto_stopped(self):
        self._mic_active = False
        self.mic_btn.config(bg="#e8eaed", fg="#555555", text="\U0001F3A4")

    def _on_stt_done(self, text):
        self._mic_active = False
        self.mic_btn.config(bg="#e8eaed", fg="#555555", text="\U0001F3A4")
        if text is None:
            self.set_status("Tidak terdengar")
            self.root.after(1500, lambda: self.set_status("Siap"))
            return
        if text.startswith("ERR:"):
            self.add_message("System", text.split("ERR:", 1)[1].strip(), SYSTEM_COLOR)
            self.set_status("Error mic")
            self.root.after(2000, lambda: self.set_status("Siap"))
            return
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.set_status("Siap")
        self._send()

    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.add_message("Anda", text, USER_COLOR)
        if self._on_send:
            self._on_send(text)

    def add_message(self, sender, text, color=BEJO_COLOR):
        self.chat_area.config(state=tk.NORMAL)
        tag = f"msg_{id(text)}"
        self.chat_area.insert(tk.END, f"{sender}: ", (f"{tag}_sender",))
        self.chat_area.insert(tk.END, f"{text}\n\n", (f"{tag}_text",))
        self.chat_area.tag_config(f"{tag}_sender", font=("Segoe UI", 10, "bold"),
                                  foreground="#2c3e50", spacing1=2)
        self.chat_area.tag_config(f"{tag}_text", font=CHAT_FONT, foreground="#1a1a2e",
                                  lmargin1=16, spacing2=2)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def set_status(self, text):
        self.indicator.config(text=text)

    def set_expression(self, expr):
        colors = {"neutral": "#a0d0a0", "thinking": "#f0d060",
                  "processing": "#80c080", "celebrate": "#80d0ff", "error": "#e08080"}
        self.indicator.config(fg=colors.get(expr, "#a0d0a0"))

    @property
    def closed(self):
        return self._closed

    def _on_close(self):
        self._auto_listen = False
        self._closed = True
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def stop(self):
        self._auto_listen = False
        if not self._closed:
            self.root.quit()
            self.root.destroy()
