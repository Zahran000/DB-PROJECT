"""
student course registration system
student_portal.py — all student-facing gui screens
"""

import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connection import get_connection
from datetime import date


# ─── colour palette ───────────────────────────────────────────────────────────
BG       = "#0f1923"
PANEL    = "#162032"
ACCENT   = "#00bfff"
ACCENT2  = "#007acc"
TEXT     = "#e8f4fd"
SUBTEXT  = "#7a9ab5"
SUCCESS  = "#00c97a"
DANGER   = "#ff4f5e"
ENTRY_BG = "#1e2e42"
BORDER   = "#1e3a5f"


def _style_button(btn, color=ACCENT2, hover=ACCENT):
    btn.configure(bg=color, fg=TEXT, relief="flat", cursor="hand2",
                  font=("Consolas", 10, "bold"), padx=14, pady=7,
                  activebackground=hover, activeforeground=TEXT)


def _entry(parent, show=None):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Consolas", 11), show=show or "")
    e.configure(highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT)
    return e


def _label(parent, text, size=11, color=TEXT, bold=False):
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=BG, fg=color,
                    font=("Consolas", size, weight))


# ─── student dashboard ────────────────────────────────────────────────────────
class StudentPortal:
    def __init__(self, root, student):
        self.root   = root
        self.student = student          # dict with student_id, name, etc.
        self._build_ui()

    def _build_ui(self):
        self.root.configure(bg=BG)
        self.root.title("student portal — registration system")

        # top bar
        top = tk.Frame(self.root, bg=ACCENT2, pady=10)
        top.pack(fill="x")
        tk.Label(top, text="  ◈  STUDENT PORTAL",
                 bg=ACCENT2, fg=TEXT,
                 font=("Consolas", 14, "bold")).pack(side="left", padx=10)
        tk.Label(top, text=f"logged in as: {self.student['name']}  ",
                 bg=ACCENT2, fg=TEXT,
                 font=("Consolas", 10)).pack(side="right")

        # sidebar
        sidebar = tk.Frame(self.root, bg=PANEL, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="\n MENU", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 11, "bold")).pack(anchor="w", padx=14)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        buttons = [
            ("▸  Browse Courses",    self.show_courses),
            ("▸  My Enrollments",    self.show_my_enrollments),
            ("▸  Search Course",     self.show_search),
        ]
        for label, cmd in buttons:
            b = tk.Button(sidebar, text=label, command=cmd, anchor="w",
                          bg=PANEL, fg=TEXT, relief="flat",
                          font=("Consolas", 10), padx=16, pady=10,
                          activebackground=BORDER, activeforeground=ACCENT,
                          cursor="hand2")
            b.pack(fill="x")

        tk.Frame(sidebar, bg=PANEL).pack(expand=True, fill="both")
        logout_btn = tk.Button(sidebar, text="  ⏻  Logout",
                               command=self._logout,
                               bg=DANGER, fg=TEXT, relief="flat",
                               font=("Consolas", 10, "bold"), pady=10,
                               cursor="hand2", activebackground="#c0392b",
                               activeforeground=TEXT)
        logout_btn.pack(fill="x", padx=10, pady=12)

        self.show_courses()

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── browse all courses ────────────────────────────────────────────────────
    def show_courses(self, search_term=None):
        self._clear()
        _label(self.content, "Available Courses", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 12))

        conn = get_connection()
        if not conn:
            _label(self.content, "db connection failed.", color=DANGER).pack()
            return

        cursor = conn.cursor(dictionary=True)
        if search_term:
            cursor.execute(
                "select *, (select count(*) from enrollment e where e.course_id=c.course_id and e.status='enrolled') as enrolled_count "
                "from course c where course_name like %s",
                (f"%{search_term}%",)
            )
        else:
            cursor.execute(
                "select *, (select count(*) from enrollment e where e.course_id=c.course_id and e.status='enrolled') as enrolled_count "
                "from course c"
            )
        courses = cursor.fetchall()
        conn.close()

        # table frame
        frame = tk.Frame(self.content, bg=PANEL)
        frame.pack(fill="both", expand=True)

        cols = ("course_id", "course_name", "instructor", "credits", "seats")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        self._style_tree(tree)

        tree.heading("course_id",   text="ID")
        tree.heading("course_name", text="Course Name")
        tree.heading("instructor",  text="Instructor")
        tree.heading("credits",     text="Credits")
        tree.heading("seats",       text="Seats Left")

        tree.column("course_id",   width=50,  anchor="center")
        tree.column("course_name", width=260)
        tree.column("instructor",  width=200)
        tree.column("credits",     width=70,  anchor="center")
        tree.column("seats",       width=90,  anchor="center")

        for c in courses:
            left = c["max_capacity"] - (c["enrolled_count"] or 0)
            tag  = "full" if left <= 0 else "ok"
            tree.insert("", "end",
                        values=(c["course_id"], c["course_name"],
                                c["instructor_name"], c["credit_hours"],
                                f"{left}/{c['max_capacity']}"),
                        tags=(tag,))

        tree.tag_configure("full", foreground=DANGER)
        tree.tag_configure("ok",   foreground=SUCCESS)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        btn_frame = tk.Frame(self.content, bg=BG)
        btn_frame.pack(anchor="w", pady=10)
        enroll_btn = tk.Button(btn_frame, text="  Enroll in Selected  ",
                               command=lambda: self._enroll(tree),
                               bg=SUCCESS, fg="#000", relief="flat",
                               font=("Consolas", 10, "bold"), padx=12, pady=7,
                               cursor="hand2", activebackground="#00a060")
        enroll_btn.pack(side="left", padx=(0, 10))
        _label(btn_frame, "← select a row first", 9, SUBTEXT).pack(side="left")

    def _enroll(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("no selection", "please select a course first.")
            return
        values     = tree.item(sel[0])["values"]
        course_id  = values[0]
        course_name = values[1]

        conn = get_connection()
        if not conn:
            messagebox.showerror("error", "db connection failed.")
            return
        try:
            cursor = conn.cursor(dictionary=True)
            # check capacity
            cursor.execute(
                "select max_capacity, (select count(*) from enrollment where course_id=%s and status='enrolled') as cnt "
                "from course where course_id=%s",
                (course_id, course_id)
            )
            row = cursor.fetchone()
            if row["cnt"] >= row["max_capacity"]:
                messagebox.showerror("full", f"'{course_name}' is at full capacity.")
                return
            # check duplicate
            cursor.execute(
                "select * from enrollment where student_id=%s and course_id=%s",
                (self.student["student_id"], course_id)
            )
            if cursor.fetchone():
                messagebox.showinfo("already enrolled", f"you are already enrolled in '{course_name}'.")
                return
            cursor.execute(
                "insert into enrollment (student_id, course_id, enrollment_date, status) values (%s,%s,%s,'enrolled')",
                (self.student["student_id"], course_id, date.today())
            )
            conn.commit()
            messagebox.showinfo("success", f"enrolled in '{course_name}' successfully!")
            self.show_courses()
        except Exception as e:
            messagebox.showerror("error", str(e))
        finally:
            conn.close()

    # ── my enrollments ────────────────────────────────────────────────────────
    def show_my_enrollments(self):
        self._clear()
        _label(self.content, "My Enrollments", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 12))

        conn = get_connection()
        if not conn:
            _label(self.content, "db connection failed.", color=DANGER).pack()
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "select e.enrollment_id, c.course_name, c.instructor_name, c.credit_hours, "
            "e.enrollment_date, e.status, e.course_id "
            "from enrollment e join course c on e.course_id=c.course_id "
            "where e.student_id=%s",
            (self.student["student_id"],)
        )
        rows = cursor.fetchall()
        conn.close()

        frame = tk.Frame(self.content, bg=PANEL)
        frame.pack(fill="both", expand=True)

        cols = ("enrollment_id", "course_name", "instructor", "credits", "date", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        self._style_tree(tree)

        tree.heading("enrollment_id", text="Enroll ID")
        tree.heading("course_name",   text="Course")
        tree.heading("instructor",    text="Instructor")
        tree.heading("credits",       text="Credits")
        tree.heading("date",          text="Enrolled On")
        tree.heading("status",        text="Status")

        tree.column("enrollment_id", width=80,  anchor="center")
        tree.column("course_name",   width=230)
        tree.column("instructor",    width=190)
        tree.column("credits",       width=65,  anchor="center")
        tree.column("date",          width=110, anchor="center")
        tree.column("status",        width=90,  anchor="center")

        for r in rows:
            tree.insert("", "end", values=(
                r["enrollment_id"], r["course_name"], r["instructor_name"],
                r["credit_hours"], str(r["enrollment_date"]), r["status"]
            ), tags=(r["status"],))

        tree.tag_configure("enrolled", foreground=SUCCESS)
        tree.tag_configure("dropped",  foreground=DANGER)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        drop_btn = tk.Button(self.content, text="  Drop Selected Course  ",
                             command=lambda: self._drop(tree, rows),
                             bg=DANGER, fg=TEXT, relief="flat",
                             font=("Consolas", 10, "bold"), padx=12, pady=7,
                             cursor="hand2", activebackground="#c0392b")
        drop_btn.pack(anchor="w", pady=10)

    def _drop(self, tree, rows):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("no selection", "select an enrollment to drop.")
            return
        values       = tree.item(sel[0])["values"]
        enrollment_id = values[0]
        course_name   = values[1]
        status        = values[5]

        if status == "dropped":
            messagebox.showinfo("already dropped", "this course is already dropped.")
            return

        if not messagebox.askyesno("confirm drop", f"drop '{course_name}'?"):
            return

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "update enrollment set status='dropped' where enrollment_id=%s",
                (enrollment_id,)
            )
            conn.commit()
            messagebox.showinfo("dropped", f"'{course_name}' has been dropped.")
            self.show_my_enrollments()
        except Exception as e:
            messagebox.showerror("error", str(e))
        finally:
            conn.close()

    # ── search courses ────────────────────────────────────────────────────────
    def show_search(self):
        self._clear()
        _label(self.content, "Search Courses", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 12))

        row = tk.Frame(self.content, bg=BG)
        row.pack(anchor="w", pady=(0, 12))
        _label(row, "course name: ", color=SUBTEXT).pack(side="left")
        entry = _entry(row)
        entry.pack(side="left", ipadx=10, ipady=4)
        entry.focus()

        def do_search():
            term = entry.get().strip()
            if not term:
                messagebox.showwarning("empty", "enter a search term.")
                return
            self.show_courses(search_term=term)

        btn = tk.Button(row, text=" Search ", command=do_search,
                        bg=ACCENT2, fg=TEXT, relief="flat",
                        font=("Consolas", 10, "bold"), padx=10, pady=5,
                        cursor="hand2", activebackground=ACCENT)
        btn.pack(side="left", padx=8)
        entry.bind("<Return>", lambda e: do_search())

    # ── treeview style ────────────────────────────────────────────────────────
    def _style_tree(self, tree):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=28,
                        font=("Consolas", 10))
        style.configure("Treeview.Heading",
                        background=BORDER, foreground=ACCENT,
                        font=("Consolas", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", ACCENT2)],
                  foreground=[("selected", TEXT)])

    def _logout(self):
        self.root.destroy()
        import app.main as main_module
        main_module.launch()
