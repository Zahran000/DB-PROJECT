"""
student course registration system
main.py — entry point: role selection, login, and register screens
"""

import tkinter as tk
from tkinter import messagebox
from app.auth import login_student, login_admin, register_student


# ─── colour palette ───────────────────────────────────────────────────────────
BG       = "#0f1923"
PANEL    = "#162032"
ACCENT   = "#00bfff"
ACCENT2  = "#007acc"
GOLD     = "#f0a500"
TEXT     = "#e8f4fd"
SUBTEXT  = "#7a9ab5"
SUCCESS  = "#00c97a"
DANGER   = "#ff4f5e"
ENTRY_BG = "#1e2e42"
BORDER   = "#1e3a5f"


def _entry(parent, show=None, width=32):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Consolas", 12), show=show or "",
                 width=width)
    e.configure(highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT)
    return e


def _btn(parent, text, cmd, color=ACCENT2, hover=ACCENT, fg=TEXT):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, relief="flat",
                  font=("Consolas", 11, "bold"), padx=16, pady=9,
                  activebackground=hover, activeforeground=TEXT,
                  cursor="hand2")
    return b


def _label(parent, text, size=11, color=TEXT, bold=False):
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=BG, fg=color,
                    font=("Consolas", size, weight))


# ─── role selection screen ────────────────────────────────────────────────────
class RoleScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("student course registration system")
        self.root.configure(bg=BG)
        self.root.geometry("560x480")
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        # decorative top strip
        tk.Frame(self.root, bg=ACCENT2, height=5).pack(fill="x")

        # logo / title block
        tk.Label(self.root, text="\n◈ FAST NUCES\nStudent Course Registration System",
                 bg=BG, fg=TEXT,
                 font=("Consolas", 14, "bold"),
                 justify="center").pack(pady=(40, 6))

        _label(self.root, "Karachi Campus  ·  4th Semester  ·  DB & SDA Project",
               size=9, color=SUBTEXT).pack()

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=60, pady=30)

        _label(self.root, "Select your role to continue", size=11,
               color=SUBTEXT).pack(pady=(0, 24))

        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack()

        student_btn = _btn(btn_frame, "  Student Login  ",
                           lambda: LoginScreen(self.root, role="student"),
                           color=ACCENT2, hover=ACCENT)
        student_btn.grid(row=0, column=0, padx=16)

        admin_btn = _btn(btn_frame, "  Admin Login  ",
                         lambda: LoginScreen(self.root, role="admin"),
                         color="#7a5500", hover=GOLD, fg=TEXT)
        admin_btn.grid(row=0, column=1, padx=16)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=60, pady=34)

        _label(self.root,
               "Mohammad Burair · Maaz Iqbal · Syed Zahran Ali Chishti",
               size=9, color=SUBTEXT).pack()
        _label(self.root, "24K-0775 · 24K-0542 · 24K-0672",
               size=9, color=SUBTEXT).pack(pady=2)


# ─── login screen ─────────────────────────────────────────────────────────────
class LoginScreen:
    def __init__(self, root, role="student"):
        self.root = root
        self.role = role
        self._clear()
        self._build()

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _build(self):
        self.root.configure(bg=BG)

        color = ACCENT if self.role == "student" else GOLD
        title = "Student Login" if self.role == "student" else "Admin Login"
        tk.Frame(self.root, bg=color, height=5).pack(fill="x")

        _label(self.root, f"\n{title}", 16, color, bold=True).pack(pady=(26, 4))
        _label(self.root, "FAST NUCES — Registration System",
               9, SUBTEXT).pack()

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=60, pady=24)

        form = tk.Frame(self.root, bg=BG)
        form.pack()

        _label(form, "email address", color=SUBTEXT).grid(
            row=0, column=0, sticky="w", pady=(0, 4))
        email_e = _entry(form)
        email_e.grid(row=1, column=0, ipady=5, pady=(0, 14))
        email_e.focus()

        _label(form, "password", color=SUBTEXT).grid(
            row=2, column=0, sticky="w", pady=(0, 4))
        pass_e = _entry(form, show="•")
        pass_e.grid(row=3, column=0, ipady=5)

        msg_var = tk.StringVar()
        msg_label = tk.Label(self.root, textvariable=msg_var,
                             bg=BG, fg=DANGER, font=("Consolas", 10))
        msg_label.pack(pady=6)

        def attempt_login():
            email = email_e.get().strip()
            pwd   = pass_e.get().strip()
            if not email or not pwd:
                msg_var.set("please enter email and password.")
                return
            if self.role == "student":
                user = login_student(email, pwd)
                if user:
                    self._open_student(user)
                else:
                    msg_var.set("invalid email or password.")
            else:
                user = login_admin(email, pwd)
                if user:
                    self._open_admin(user)
                else:
                    msg_var.set("invalid admin credentials.")

        pass_e.bind("<Return>", lambda e: attempt_login())

        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(pady=6)
        _btn(btn_row, " Login ", attempt_login, color=color, hover=ACCENT).pack(side="left", padx=8)
        _btn(btn_row, " Back  ", lambda: self._go_back(), color="#1e3a5f", hover=BORDER).pack(side="left")

        if self.role == "student":
            tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=60, pady=20)
            _label(self.root, "don't have an account?", 9, SUBTEXT).pack()
            _btn(self.root, " Register as Student ",
                 lambda: RegisterScreen(self.root),
                 color="#003a1f", hover=SUCCESS).pack(pady=6)

    def _go_back(self):
        for w in self.root.winfo_children():
            w.destroy()
        RoleScreen(self.root)

    def _open_student(self, user):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.geometry("900x600")
        from app.student_portal import StudentPortal
        StudentPortal(self.root, user)

    def _open_admin(self, user):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.geometry("960x620")
        from app.admin_portal import AdminPortal
        AdminPortal(self.root, user)


# ─── register screen ──────────────────────────────────────────────────────────
class RegisterScreen:
    def __init__(self, root):
        self.root = root
        self._clear()
        self._build()

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _build(self):
        self.root.configure(bg=BG)
        tk.Frame(self.root, bg=SUCCESS, height=5).pack(fill="x")

        _label(self.root, "\nStudent Registration", 16, SUCCESS, bold=True).pack(pady=(26, 4))
        _label(self.root, "create your account", 9, SUBTEXT).pack()
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=60, pady=20)

        form = tk.Frame(self.root, bg=BG)
        form.pack()

        fields = [
            ("full name",     None,  ""),
            ("email address", None,  ""),
            ("password",      "•",   ""),
            ("semester",      None,  "(1 – 8)"),
        ]
        entries = {}
        for i, (label, show, hint) in enumerate(fields):
            _label(form, label, color=SUBTEXT).grid(
                row=i*2, column=0, sticky="w", pady=(8, 2))
            e = _entry(form, show=show)
            if hint:
                e.insert(0, hint)
                e.configure(fg=SUBTEXT)
                def _fi(ev, en=e, h=hint):
                    if en.get() == h:
                        en.delete(0, "end")
                        en.configure(fg=TEXT)
                def _fo(ev, en=e, h=hint):
                    if not en.get():
                        en.insert(0, h)
                        en.configure(fg=SUBTEXT)
                e.bind("<FocusIn>", _fi)
                e.bind("<FocusOut>", _fo)
            e.grid(row=i*2+1, column=0, ipady=5)
            entries[label] = (e, hint)

        msg_var = tk.StringVar()
        tk.Label(self.root, textvariable=msg_var,
                 bg=BG, fg=DANGER, font=("Consolas", 10)).pack(pady=4)

        def attempt_register():
            def val(key):
                e, hint = entries[key]
                v = e.get().strip()
                return "" if v == hint else v

            name     = val("full name")
            email    = val("email address")
            password = val("password")
            semester = val("semester")

            if not all([name, email, password, semester]):
                msg_var.set("all fields are required.")
                return
            try:
                sem = int(semester)
                if not 1 <= sem <= 8:
                    raise ValueError
            except ValueError:
                msg_var.set("semester must be a number between 1 and 8.")
                return

            ok, message = register_student(name, email, password, sem)
            if ok:
                messagebox.showinfo("registered!", "account created. please login.")
                for w in self.root.winfo_children():
                    w.destroy()
                self.root.geometry("560x480")
                LoginScreen(self.root, role="student")
            else:
                msg_var.set(message)

        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(pady=8)
        _btn(btn_row, " Register ", attempt_register,
             color=SUCCESS, hover="#00a060", fg="#000").pack(side="left", padx=8)
        _btn(btn_row, " Back ", lambda: _back(),
             color="#1e3a5f", hover=BORDER).pack(side="left")

        def _back():
            for w in self.root.winfo_children():
                w.destroy()
            self.root.geometry("560x480")
            LoginScreen(self.root, role="student")


# ─── launch ───────────────────────────────────────────────────────────────────
def launch():
    root = tk.Tk()
    root.geometry("560x480")
    root.resizable(False, False)
    RoleScreen(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
