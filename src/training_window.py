import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import logging

logger = logging.getLogger("bejo.training")


class TrainingWindow:
    SKILLS = [
        "just answer",
        "tools",
        "face_tools",
        "osint_tools",
        "tax_tools",
        "tax_profiling",
        "tax_audit",
        "tools_media",
        "voice_tools",
    ]

    def __init__(self, parent, knowledge_base, gemini_engine=None, skill_manager=None, on_close=None):
        self.win = tk.Toplevel(parent)
        self.win.title("Training Bejo — Knowledge Base")
        self.win.geometry("1024x680")
        self.win.minsize(800, 500)
        self.win.transient(parent)
        self.win.grab_set()

        self.kb = knowledge_base
        self.gemini = gemini_engine
        self.skill_manager = skill_manager
        self.on_close = on_close
        self._editing_id = None
        self._skill_var = tk.StringVar(value="just answer")

        self._build_ui()
        self._refresh_list()
        self.win.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self):
        self.win.configure(bg="#f0f2f5")

        paned = tk.PanedWindow(self.win, orient=tk.HORIZONTAL, bg="#f0f2f5",
                                sashrelief=tk.RAISED, sashwidth=3)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.Frame(paned, bg="#f0f2f5")
        paned.add(left, stretch="always")

        header_l = tk.Frame(left, bg="#f0f2f5")
        header_l.pack(fill=tk.X, pady=(0, 8))
        tk.Label(header_l, text="Form Knowledge", font=("Segoe UI", 11, "bold"),
                 bg="#f0f2f5", fg="#2c3e50").pack(side=tk.LEFT)

        self.edit_indicator = tk.Label(header_l, text="", font=("Segoe UI", 9),
                                       bg="#f0f2f5", fg="#27ae60")
        self.edit_indicator.pack(side=tk.RIGHT)

        tk.Label(left, text="Pertanyaan", font=("Segoe UI", 10, "bold"),
                 bg="#f0f2f5", anchor="w").pack(fill=tk.X)
        self.q_entry = tk.Entry(left, font=("Segoe UI", 11), bd=1, relief=tk.SOLID,
                                bg="#ffffff", fg="#1a1a2e")
        self.q_entry.pack(fill=tk.X, ipady=6, pady=(2, 10))

        tk.Label(left, text="Jawaban", font=("Segoe UI", 10, "bold"),
                 bg="#f0f2f5", anchor="w").pack(fill=tk.X)
        self.a_text = scrolledtext.ScrolledText(
            left, wrap=tk.WORD, font=("Segoe UI", 11),
            height=12, bd=1, relief=tk.SOLID,
            bg="#ffffff", fg="#1a1a2e", padx=8, pady=8,
        )
        self.a_text.pack(fill=tk.BOTH, expand=True, pady=(2, 10))

        all_skills = list(self.SKILLS)
        if self.skill_manager:
            for s in self.skill_manager.skill_names():
                if s not in all_skills:
                    all_skills.append(s)
        skill_row = tk.Frame(left, bg="#f0f2f5")
        skill_row.pack(fill=tk.X)
        tk.Label(skill_row, text="Skill", font=("Segoe UI", 10, "bold"),
                 bg="#f0f2f5", anchor="w").pack(side=tk.LEFT, padx=(0, 8))
        self.skill_combo = ttk.Combobox(skill_row, textvariable=self._skill_var,
                                        values=all_skills, state="readonly",
                                        font=("Segoe UI", 10), width=20)
        self.skill_combo.pack(side=tk.LEFT)
        tk.Label(skill_row, text="(just answer = langsung jawab tanpa tool)", font=("Segoe UI", 8),
                 bg="#f0f2f5", fg="#888888", anchor="w").pack(side=tk.LEFT, padx=(8, 0))

        btn_row = tk.Frame(left, bg="#f0f2f5")
        btn_row.pack(fill=tk.X)

        tk.Button(btn_row, text="\U0001f4cb Baru", font=("Segoe UI", 9),
                  bg="#7f8c8d", fg="white", bd=0, padx=14, pady=5,
                  cursor="hand2", command=self._new_entry).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_row, text="\U0001f4be Simpan", font=("Segoe UI", 9, "bold"),
                  bg="#27ae60", fg="white", bd=0, padx=18, pady=5,
                  cursor="hand2", command=self._save).pack(side=tk.LEFT, padx=(0, 6))

        if self.gemini:
            tk.Button(btn_row, text="\U0001f916 Generate", font=("Segoe UI", 9),
                      bg="#2c3e50", fg="white", bd=0, padx=12, pady=5,
                      cursor="hand2", command=self._generate).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_row, text="\U0001f5d1 Hapus", font=("Segoe UI", 9),
                  bg="#e74c3c", fg="white", bd=0, padx=14, pady=5,
                  cursor="hand2", command=self._delete).pack(side=tk.RIGHT)

        self.status_lbl = tk.Label(left, text="", font=("Segoe UI", 9),
                                   bg="#f0f2f5", fg="#555555", anchor="w")
        self.status_lbl.pack(fill=tk.X, pady=(6, 0))

        right = tk.Frame(paned, bg="#f0f2f5")
        paned.add(right, stretch="never")
        paned.sash_place(0, 580, 0)

        header_r = tk.Frame(right, bg="#f0f2f5")
        header_r.pack(fill=tk.X)
        tk.Label(header_r, text="Daftar Pengetahuan", font=("Segoe UI", 11, "bold"),
                 bg="#f0f2f5", fg="#2c3e50").pack(side=tk.LEFT)
        self.count_lbl = tk.Label(header_r, text=f"0 entri", font=("Segoe UI", 9),
                                  bg="#f0f2f5", fg="#888888")
        self.count_lbl.pack(side=tk.RIGHT)

        search_row = tk.Frame(right, bg="#f0f2f5")
        search_row.pack(fill=tk.X, pady=(6, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_list())
        tk.Entry(search_row, textvariable=self.search_var, font=("Segoe UI", 10),
                 bd=1, relief=tk.SOLID, bg="#ffffff").pack(fill=tk.X, ipady=4)

        list_frame = tk.Frame(right, bg="#ffffff", bd=1, relief=tk.SOLID)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(list_frame, font=("Segoe UI", 10),
                                  bg="#ffffff", fg="#2c3e50", bd=0,
                                  selectbackground="#d4edda", selectforeground="#2c3e50",
                                  highlightthickness=0, activestyle="none")
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        bottom_right = tk.Frame(right, bg="#f0f2f5")
        bottom_right.pack(fill=tk.X, pady=(8, 0))

        tk.Button(bottom_right, text="\U0001f4e4 Export JSON", font=("Segoe UI", 9),
                  bg="#7f8c8d", fg="white", bd=0, padx=8, pady=3,
                  cursor="hand2", command=self._export).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(bottom_right, text="\U0001f4e5 Import JSON", font=("Segoe UI", 9),
                  bg="#7f8c8d", fg="white", bd=0, padx=8, pady=3,
                  cursor="hand2", command=self._import_kb).pack(side=tk.LEFT)

    def _set_status(self, msg):
        try:
            if self.status_lbl.winfo_exists():
                self.status_lbl.config(text=msg)
                self.win.after(3000, self._clear_status)
        except tk.TclError:
            pass

    def _clear_status(self):
        try:
            if self.status_lbl.winfo_exists():
                self.status_lbl.config(text="")
        except tk.TclError:
            pass

    def _new_entry(self):
        self._editing_id = None
        self.q_entry.delete(0, tk.END)
        self.a_text.delete("1.0", tk.END)
        self._skill_var.set("just answer")
        self.listbox.selection_clear(0, tk.END)
        self.edit_indicator.config(text="")
        self.q_entry.focus_set()

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        data = self.listbox.get(0, tk.END)
        if idx >= len(data):
            return
        label = data[idx]
        label = label.replace("\u2014 ", "").strip()
        try:
            eid = int(label.split(".")[0].strip("#"))
        except (ValueError, IndexError):
            return
        entry = next((e for e in self.kb.list_all() if e["id"] == eid), None)
        if not entry:
            return
        self._editing_id = eid
        self.q_entry.delete(0, tk.END)
        self.q_entry.insert(0, entry["question"])
        self.a_text.delete("1.0", tk.END)
        self.a_text.insert("1.0", entry["answer"])
        tags = entry.get("tags", [])
        all_skill_names = set(self.SKILLS)
        if self.skill_manager:
            all_skill_names.update(self.skill_manager.skill_names())
        skill_tag = next((t for t in tags if t in all_skill_names), "just answer")
        self._skill_var.set(skill_tag)
        self.edit_indicator.config(text=f"\u270f Mengedit #{eid}")

    def _save(self):
        q = self.q_entry.get().strip()
        a = self.a_text.get("1.0", tk.END).strip()
        if not q:
            messagebox.showwarning("Kosong", "Pertanyaan tidak boleh kosong.")
            return
        if not a:
            messagebox.showwarning("Kosong", "Jawaban tidak boleh kosong.")
            return
        if self._editing_id is not None:
            self.kb.remove(self._editing_id)
        skill = self._skill_var.get()
        tags = [skill] if skill != "just answer" else []
        self.kb.add(q, a, tags=tags)
        self._editing_id = None
        self.q_entry.delete(0, tk.END)
        self.a_text.delete("1.0", tk.END)
        self.edit_indicator.config(text="")
        self._refresh_list()
        self._set_status("Disimpan!")

    def _delete(self):
        if self._editing_id is None:
            self._set_status("Pilih entri dulu dari daftar di sebelah kanan.")
            return
        if messagebox.askyesno("Hapus", f"Yakin mau hapus entri #{self._editing_id}?"):
            self.kb.remove(self._editing_id)
            self._editing_id = None
            self.q_entry.delete(0, tk.END)
            self.a_text.delete("1.0", tk.END)
            self.edit_indicator.config(text="")
            self._refresh_list()
            self._set_status("Dihapus.")

    def _generate(self):
        q = self.q_entry.get().strip()
        if not q:
            messagebox.showwarning("Kosong", "Isi pertanyaan dulu.")
            return
        if not self.gemini:
            self._set_status("Gemini tidak tersedia.")
            return
        self._set_status("Menghasilkan jawaban...")

        def task():
            prompt = (
                f"Kamu adalah Bejo, asisten AI. Jawab pertanyaan berikut dengan singkat, jelas, "
                f"dan dalam Bahasa Indonesia. Panggil user 'Bos'.\n\nPertanyaan: {q}"
            )
            try:
                answer = self.gemini.send(prompt)
                self.win.after(0, self._populate_answer, answer)
            except Exception as e:
                self.win.after(0, lambda: self._set_status(f"Error: {str(e)[:50]}"))

        threading.Thread(target=task, daemon=True).start()

    def _populate_answer(self, answer):
        try:
            if self.win.winfo_exists():
                self.a_text.delete("1.0", tk.END)
                self.a_text.insert("1.0", answer.strip())
                self._set_status("Jawaban siap. Simpan jika sesuai.")
        except tk.TclError:
            pass

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        query = self.search_var.get().strip().lower()
        entries = self.kb.list_all()
        if query:
            entries = [e for e in entries if query in e["question"].lower()]
        for e in entries:
            q = e["question"]
            if len(q) > 60:
                q = q[:57] + "..."
            all_skill_names = set(self.SKILLS)
            if self.skill_manager:
                all_skill_names.update(self.skill_manager.skill_names())
            tags = e.get("tags", [])
            skill = next((t for t in tags if t in all_skill_names), None)
            skill_tag = f" [{skill}]" if skill else ""
            self.listbox.insert(tk.END, f"#{e['id']}.{skill_tag} {q}")
        self.count_lbl.config(text=f"{self.kb.count()} entri")

    def _export(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if not path:
            return
        entries = self.kb.list_all()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        self._set_status(f"Diexport ke {os.path.basename(path)} ({len(entries)} entri)")

    def _import_kb(self):
        path = filedialog.askopenfilename(defaultextension=".json",
                                          filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = 0
            for item in data:
                q = item.get("question", "").strip()
                a = item.get("answer", "").strip()
                tags = item.get("tags", [])
                if q and a:
                    self.kb.add(q, a, tags=tags)
                    count += 1
            self._refresh_list()
            self._set_status(f"Diimport {count} entri dari {os.path.basename(path)}.")
        except Exception as e:
            messagebox.showerror("Gagal", f"Gagal import: {e}")

    def _close(self):
        try:
            for cb in self.win.tk.call("after", "info"):
                self.win.after_cancel(cb)
        except Exception:
            pass
        try:
            self.win.grab_release()
        except Exception:
            pass
        try:
            self.win.destroy()
        except Exception:
            pass
        if self.on_close:
            self.on_close()
