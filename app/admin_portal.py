"""
student course registration system
admin_portal.py — all admin-facing gui screens
prepared by mohammad burair | fast nuces karachi | 4th semester
"""

import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connection import get_connection


# ─── colour palette (same as student portal) ──────────────────────────────────
BG       = "#0f1923"
PANEL    = "#162032"
ACCENT   = "#f0a500"
ACCENT2  = "#b87800"
TEXT     = "#e8f4fd"
SUBTEXT  = "#7a9ab5"
SUCCESS  = "#00c97a"
DANGER   = "#ff4f5e"
ENTRY_BG = "#1e2e42"
BORDER   = "#1e3a5f"


def _entry(parent, show=None, width=30):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Consolas", 11), show=show or "",
                 width=width)
    e.configure(highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT)
    return e


def _label(parent, text, size=11, color=TEXT, bold=False):
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=BG, fg=color,
                    font=("Consolas", size, weight))


class AdminPortal:
    def __init__(self, root, admin):
        self.root  = root
        self.admin = admin
        self._build_ui()

    def _build_ui(self):
        self.root.configure(bg=BG)
        self.root.title("admin portal — registration system")

        top = tk.Frame(self.root, bg=ACCENT2, pady=10)
        top.pack(fill="x")
        tk.Label(top, text="  ◆  ADMIN PORTAL",
                 bg=ACCENT2, fg=TEXT,
                 font=("Consolas", 14, "bold")).pack(side="left", padx=10)
        tk.Label(top, text=f"admin: {self.admin['name']}  ",
                 bg=ACCENT2, fg=TEXT,
                 font=("Consolas", 10)).pack(side="right")

        sidebar = tk.Frame(self.root, bg=PANEL, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="\n MENU", bg=PANEL, fg=ACCENT,
                 font=("Consolas", 11, "bold")).pack(anchor="w", padx=14)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        buttons = [
            ("▸  All Courses",       self.show_courses),
            ("▸  Add Course",        self.show_add_course),
            ("▸  All Enrollments",   self.show_all_enrollments),
            ("▸  Enrollments by Course", self.show_by_course),
        ]
        for label, cmd in buttons:
            b = tk.Button(sidebar, text=label, command=cmd, anchor="w",
                          bg=PANEL, fg=TEXT, relief="flat",
                          font=("Consolas", 10), padx=16, pady=10,
                          activebackground=BORDER, activeforeground=ACCENT,
                          cursor="hand2")
            b.pack(fill="x")

        tk.Frame(sidebar, bg=PANEL).pack(expand=True, fill="both")
        tk.Button(sidebar, text="  ⏻  Logout",
                  command=self._logout,
                  bg=DANGER, fg=TEXT, relief="flat",
                  font=("Consolas", 10, "bold"), pady=10,
                  cursor="hand2", activebackground="#c0392b",
                  activeforeground=TEXT).pack(fill="x", padx=10, pady=12)

        self.show_courses()

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

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

    # ── all courses ───────────────────────────────────────────────────────────
    def show_courses(self):
        self._clear()
        _label(self.content, "Manage Courses", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 12))

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "select c.*, (select count(*) from enrollment e where e.course_id=c.course_id and e.status='enrolled') as enrolled "
            "from course c"
        )
        courses = cursor.fetchall()
        conn.close()

        frame = tk.Frame(self.content, bg=PANEL)
        frame.pack(fill="both", expand=True)

        cols = ("course_id", "course_name", "instructor", "credits", "capacity", "enrolled")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        self._style_tree(tree)

        headings = [("course_id","ID",60), ("course_name","Course Name",250),
                    ("instructor","Instructor",190), ("credits","Credits",70),
                    ("capacity","Max Cap",80), ("enrolled","Enrolled",80)]
        for col, head, w in headings:
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center" if w < 150 else "w")

        for c in courses:
            tree.insert("", "end", values=(
                c["course_id"], c["course_name"], c["instructor_name"],
                c["credit_hours"], c["max_capacity"], c["enrolled"] or 0
            ))

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        btn_frame = tk.Frame(self.content, bg=BG)
        btn_frame.pack(anchor="w", pady=10)

        tk.Button(btn_frame, text=" Edit Selected ",
                  command=lambda: self._edit_course(tree, courses),
                  bg=ACCENT2, fg=TEXT, relief="flat",
                  font=("Consolas", 10, "bold"), padx=10, pady=7,
                  cursor="hand2", activebackground=ACCENT).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text=" Delete Selected ",
                  command=lambda: self._delete_course(tree),
                  bg=DANGER, fg=TEXT, relief="flat",
                  font=("Consolas", 10, "bold"), padx=10, pady=7,
                  cursor="hand2", activebackground="#c0392b").pack(side="left")

    def _delete_course(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("no selection", "select a course to delete.")
            return
        values    = tree.item(sel[0])["values"]
        course_id = values[0]
        name      = values[1]

        if not messagebox.askyesno("confirm", f"delete '{name}'? this removes all enrollments too."):
            return
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("delete from course where course_id=%s", (course_id,))
            conn.commit()
            messagebox.showinfo("deleted", f"'{name}' deleted.")
            self.show_courses()
        except Exception as e:
            messagebox.showerror("error", str(e))
        finally:
            conn.close()

    def _edit_course(self, tree, courses):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("no selection", "select a course to edit.")
            return
        values    = tree.item(sel[0])["values"]
        course_id = values[0]
        course    = next((c for c in courses if c["course_id"] == course_id), None)
        if not course:
            return

        win = tk.Toplevel(self.root)
        win.title("edit course")
        win.configure(bg=BG)
        win.geometry("400x320")
        win.resizable(False, False)

        fields = [
            ("course name",   course["course_name"]),
            ("instructor",    course["instructor_name"]),
            ("credit hours",  course["credit_hours"]),
            ("max capacity",  course["max_capacity"]),
        ]
        entries = {}
        for label, val in fields:
            tk.Label(win, text=label, bg=BG, fg=SUBTEXT,
                     font=("Consolas", 10)).pack(anchor="w", padx=20, pady=(10, 2))
            e = _entry(win)
            e.insert(0, str(val))
            e.pack(fill="x", padx=20, ipady=4)
            entries[label] = e

        def save():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "update course set course_name=%s, instructor_name=%s, credit_hours=%s, max_capacity=%s where course_id=%s",
                    (
                        entries["course name"].get().strip(),
                        entries["instructor"].get().strip(),
                        int(entries["credit hours"].get()),
                        int(entries["max capacity"].get()),
                        course_id
                    )
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("saved", "course updated.")
                win.destroy()
                self.show_courses()
            except Exception as e:
                messagebox.showerror("error", str(e))

        tk.Button(win, text=" Save Changes ", command=save,
                  bg=SUCCESS, fg="#000", relief="flat",
                  font=("Consolas", 10, "bold"), pady=8,
                  cursor="hand2").pack(pady=18)

    # ── add course ────────────────────────────────────────────────────────────
    def show_add_course(self):
        self._clear()
        _label(self.content, "Add New Course", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 20))

        form = tk.Frame(self.content, bg=BG)
        form.pack(anchor="w")

        fields = [
            ("course name",   "e.g. Artificial Intelligence"),
            ("instructor",    "e.g. Dr. Zara Ahmed"),
            ("credit hours",  "e.g. 3"),
            ("max capacity",  "e.g. 40"),
        ]
        entries = {}
        for label, placeholder in fields:
            _label(form, label, color=SUBTEXT).grid(row=len(entries), column=0,
                                                     sticky="w", pady=8, padx=(0, 20))
            e = _entry(form, width=36)
            e.grid(row=len(entries), column=1, ipady=5)
            e.insert(0, placeholder)
            e.configure(fg=SUBTEXT)

            def on_focus_in(event, en=e, ph=placeholder):
                if en.get() == ph:
                    en.delete(0, "end")
                    en.configure(fg=TEXT)

            def on_focus_out(event, en=e, ph=placeholder):
                if not en.get():
                    en.insert(0, ph)
                    en.configure(fg=SUBTEXT)

            e.bind("<FocusIn>",  on_focus_in)
            e.bind("<FocusOut>", on_focus_out)
            entries[label] = (e, placeholder)

        def add():
            vals = {}
            for key, (en, ph) in entries.items():
                v = en.get().strip()
                if v == ph or not v:
                    messagebox.showwarning("missing", f"please fill '{key}'.")
                    return
                vals[key] = v
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "insert into course (course_name, instructor_name, credit_hours, max_capacity) "
                    "values (%s,%s,%s,%s)",
                    (vals["course name"], vals["instructor"],
                     int(vals["credit hours"]), int(vals["max capacity"]))
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("added", "course added successfully.")
                self.show_courses()
            except Exception as e:
                messagebox.showerror("error", str(e))

        tk.Button(form, text=" Add Course ", command=add,
                  bg=SUCCESS, fg="#000", relief="flat",
                  font=("Consolas", 11, "bold"), padx=14, pady=9,
                  cursor="hand2").grid(row=len(fields), column=0,
                                      columnspan=2, pady=24, sticky="w")

    # ── all enrollments ───────────────────────────────────────────────────────
    def show_all_enrollments(self):
        self._clear()
        _label(self.content, "All Enrollment Records", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 12))

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "select e.enrollment_id, s.name as student_name, s.email, "
            "c.course_name, e.enrollment_date, e.status "
            "from enrollment e "
            "join student s on e.student_id=s.student_id "
            "join course  c on e.course_id =c.course_id "
            "order by e.enrollment_date desc"
        )
        rows = cursor.fetchall()
        conn.close()

        frame = tk.Frame(self.content, bg=PANEL)
        frame.pack(fill="both", expand=True)

        cols = ("eid", "student", "email", "course", "date", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        self._style_tree(tree)

        for col, head, w in [("eid","ID",55), ("student","Student",160),
                              ("email","Email",190), ("course","Course",200),
                              ("date","Date",110), ("status","Status",90)]:
            tree.heading(col, text=head)
            tree.column(col, width=w)

        for r in rows:
            tree.insert("", "end", values=(
                r["enrollment_id"], r["student_name"], r["email"],
                r["course_name"], str(r["enrollment_date"]), r["status"]
            ), tags=(r["status"],))

        tree.tag_configure("enrolled", foreground=SUCCESS)
        tree.tag_configure("dropped",  foreground=DANGER)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── enrollments by course ─────────────────────────────────────────────────
    def show_by_course(self):
        self._clear()
        _label(self.content, "Enrollments by Course", 14, ACCENT, bold=True).pack(anchor="w", pady=(0, 12))

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("select course_id, course_name from course order by course_name")
        courses = cursor.fetchall()
        conn.close()

        row = tk.Frame(self.content, bg=BG)
        row.pack(anchor="w", pady=(0, 14))
        _label(row, "select course: ", color=SUBTEXT).pack(side="left")

        var = tk.StringVar()
        names = [f"{c['course_id']} — {c['course_name']}" for c in courses]
        combo = ttk.Combobox(row, textvariable=var, values=names,
                             font=("Consolas", 10), width=36, state="readonly")
        combo.pack(side="left", padx=8)

        result_frame = tk.Frame(self.content, bg=PANEL)
        result_frame.pack(fill="both", expand=True)

        def load(_=None):
            for w in result_frame.winfo_children():
                w.destroy()
            sel = var.get()
            if not sel:
                return
            cid = int(sel.split(" — ")[0])

            conn2 = get_connection()
            if not conn2:
                return
            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute(
                "select s.student_id, s.name, s.email, s.semester, e.enrollment_date, e.status "
                "from enrollment e join student s on e.student_id=s.student_id "
                "where e.course_id=%s", (cid,)
            )
            students = cursor2.fetchall()
            conn2.close()

            cols2 = ("sid","name","email","semester","date","status")
            tree = ttk.Treeview(result_frame, columns=cols2, show="headings", height=14)
            self._style_tree(tree)

            for col2, head, w in [("sid","ID",55),("name","Name",160),
                                   ("email","Email",200),("semester","Sem",60),
                                   ("date","Date",110),("status","Status",90)]:
                tree.heading(col2, text=head)
                tree.column(col2, width=w)

            for s in students:
                tree.insert("", "end", values=(
                    s["student_id"], s["name"], s["email"],
                    s["semester"], str(s["enrollment_date"]), s["status"]
                ), tags=(s["status"],))

            tree.tag_configure("enrolled", foreground=SUCCESS)
            tree.tag_configure("dropped",  foreground=DANGER)

            sb = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sb.set)
            tree.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

        combo.bind("<<ComboboxSelected>>", load)
        tk.Button(row, text=" Load ", command=load,
                  bg=ACCENT2, fg=TEXT, relief="flat",
                  font=("Consolas", 10, "bold"), padx=10, pady=5,
                  cursor="hand2").pack(side="left")

    def _logout(self):
        self.root.destroy()
        import app.main as main_module
        main_module.launch()
