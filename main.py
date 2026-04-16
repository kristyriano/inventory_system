import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
import hashlib
import platform

# ── Platform helpers ──────────────────────────────────────────────────────────
import platform as _platform
_SYS = _platform.system()

def _font(size: int, weight: str = "normal") -> tuple:
    if _SYS == "Darwin":
        family = "Helvetica Neue"
    elif _SYS == "Windows":
        family = "Segoe UI"
    else:
        family = "DejaVu Sans"
    return (family, size, weight) if weight == "bold" else (family, size)

def _maximize(root: tk.Tk):
    try:
        root.state("zoomed")
    except Exception:
        root.update_idletasks()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+0+0")

def _emoji_font(size: int) -> tuple:
    if _SYS == "Darwin":
        return ("Apple Color Emoji", size)
    return ("Segoe UI Emoji", size)


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

USERS_FILE = "invntra_users.json"
BACKUP_DIR = "invntra_backups"

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    default = {
        "admin": {
            "password": _hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    }
    save_users(default)
    return default

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ── Login Window ──────────────────────────────────────────────────────────────

class LoginWindow:
    def __init__(self, on_success):
        self.on_success = on_success
        self.users = load_users()

        self.root = tk.Tk()
        self.root.title("Invntra — Login")
        self.root.configure(bg="#f3f6fb")
        self.root.resizable(False, False)

        w, h = 420, 580
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self._build()
        self.root.mainloop()

    def _build(self):
        card = tk.Frame(self.root, bg="white", bd=0,
                        highlightthickness=1, highlightbackground="#dbe3f0")
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=520)

        # Top accent bar
        tk.Frame(card, bg="#1e3a8a", height=6).pack(fill="x")

        # Logo
        logo_frame = tk.Frame(card, bg="white")
        logo_frame.pack(pady=(28, 0))

        tk.Label(logo_frame, text="📦",
                 font=_emoji_font(40),
                 bg="white").pack()
        tk.Label(logo_frame, text="Invntra",
                 font=_font(22, "bold"),
                 bg="white", fg="#1e3a8a").pack()
        tk.Label(logo_frame, text="Inventory Registra",
                 font=_font(10),
                 bg="white", fg="#6b7280").pack(pady=(2, 0))

        tk.Frame(card, bg="#e5e7eb", height=1).pack(fill="x", padx=32, pady=20)

        form = tk.Frame(card, bg="white")
        form.pack(fill="x", padx=32)

        tk.Label(form, text="Username", font=_font(10, "bold"),
                 bg="white", fg="#374151").pack(anchor="w")
        self.user_entry = tk.Entry(form, font=_font(12),
                                   bg="#f8fafc", fg="#111827",
                                   relief="solid", bd=1,
                                   highlightthickness=1,
                                   highlightbackground="#cbd5e1",
                                   highlightcolor="#3b82f6")
        self.user_entry.pack(fill="x", ipady=8, pady=(4, 14))

        tk.Label(form, text="Password", font=_font(10, "bold"),
                 bg="white", fg="#374151").pack(anchor="w")
        self.pass_entry = tk.Entry(form, font=_font(12),
                                   bg="#f8fafc", fg="#111827",
                                   relief="solid", bd=1,
                                   highlightthickness=1,
                                   highlightbackground="#cbd5e1",
                                   highlightcolor="#3b82f6",
                                   show="*")
        self.pass_entry.pack(fill="x", ipady=8, pady=(4, 6))

        self.show_pass = tk.BooleanVar(value=False)
        tk.Checkbutton(form, text="Show password",
                       variable=self.show_pass,
                       font=_font(9), bg="white", fg="#6b7280",
                       activebackground="white", cursor="hand2",
                       command=self._toggle_password).pack(anchor="w", pady=(0, 14))

        self.error_label = tk.Label(form, text="", font=_font(10),
                                    bg="white", fg="#be123c")
        self.error_label.pack(anchor="w", pady=(0, 6))

        tk.Button(form, text="Log In",
                  font=_font(12, "bold"),
                  bg="#2563eb", fg="white",
                  activebackground="#1d4ed8", activeforeground="white",
                  relief="flat", bd=0, cursor="hand2",
                  pady=12, command=self._attempt_login).pack(fill="x")

        self.root.bind("<Return>", lambda e: self._attempt_login())
        self.user_entry.focus_set()

    def _toggle_password(self):
        self.pass_entry.config(show="" if self.show_pass.get() else "*")

    def _attempt_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        if not username or not password:
            self.error_label.config(text="Please enter username and password.")
            return
        user = self.users.get(username)
        if user and user["password"] == _hash_password(password):
            self.root.destroy()
            self.on_success(username, user["role"])
        else:
            self.error_label.config(text="Invalid username or password.")
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.focus_set()


# ── User Management Dialog ────────────────────────────────────────────────────

class UserManagementDialog:
    def __init__(self, parent, current_user: str):
        self.parent = parent
        self.current_user = current_user
        self.users = load_users()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Management")
        self.dialog.configure(bg="white")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        w, h = 720, 680
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  // 2) - w // 2
        y = parent.winfo_y() + (parent.winfo_height() // 2) - h // 2
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self.dialog, bg="#1e3a8a", height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="User Management", font=_font(14, "bold"),
                 bg="#1e3a8a", fg="white").pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.dialog, bg="white")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Left: create user
        left_outer = tk.Frame(body, bg="white", bd=0,
                              highlightthickness=1, highlightbackground="#dbe3f0")
        left_outer.pack(side="left", fill="y", padx=(0, 14))
        left_canvas = tk.Canvas(left_outer, bg="white", highlightthickness=0, width=260)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_sb = ttk.Scrollbar(left_outer, orient="vertical", command=left_canvas.yview)
        left_sb.pack(side="right", fill="y")
        left_canvas.configure(yscrollcommand=left_sb.set)
        left = tk.Frame(left_canvas, bg="white")
        left_canvas.create_window((0, 0), window=left, anchor="nw")
        left.bind("<Configure>", lambda e: left_canvas.configure(
            scrollregion=left_canvas.bbox("all")))

        tk.Label(left, text="Create New Account", font=_font(12, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w", padx=16, pady=(10, 2))
        tk.Label(left, text="Fill in the fields to add a user.",
                 font=_font(9), bg="white", fg="#6b7280").pack(anchor="w", padx=16, pady=(0, 8))

        def _lbl(p, t):
            tk.Label(p, text=t, font=_font(9, "bold"), bg="white", fg="#374151").pack(anchor="w", padx=16)

        def _ent(p, **kw):
            e = tk.Entry(p, font=_font(11), bg="#f8fafc", fg="#111827",
                         relief="solid", bd=1, highlightthickness=1,
                         highlightbackground="#cbd5e1", highlightcolor="#3b82f6", width=22, **kw)
            e.pack(fill="x", padx=16, ipady=6, pady=(4, 6))
            return e

        _lbl(left, "Username");   self.new_user_entry    = _ent(left)
        _lbl(left, "Password");   self.new_pass_entry    = _ent(left, show="*")
        _lbl(left, "Confirm Password"); self.confirm_pass_entry = _ent(left, show="*")

        _lbl(left, "Role")
        self.role_var = tk.StringVar(value="employee")
        rf = tk.Frame(left, bg="white")
        rf.pack(anchor="w", padx=16, pady=(4, 14))
        for r in ("admin", "manager", "employee"):
            row = tk.Frame(rf, bg="white")
            row.pack(anchor="w", pady=2)
            tk.Radiobutton(row, text=r.capitalize(), variable=self.role_var, value=r,
                           font=_font(10), bg="white", fg="#374151",
                           activebackground="white", activeforeground="#111827",
                           selectcolor="white",
                           cursor="hand2").pack(side="left")

        self.create_status = tk.Label(left, text="", font=_font(9),
                                      bg="white", fg="#15803d", wraplength=200)
        self.create_status.pack(anchor="w", padx=16)

        tk.Button(left, text="Create Account", font=_font(10, "bold"),
                  bg="#2563eb", fg="white", activebackground="#1d4ed8",
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=10,
                  command=self._create_user).pack(fill="x", padx=16, pady=(20, 16))

        # Right: user list
        right = tk.Frame(body, bg="white", bd=0,
                         highlightthickness=1, highlightbackground="#dbe3f0")
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="Existing Accounts", font=_font(12, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w", padx=16, pady=(14, 4))

        tf = tk.Frame(right, bg="white")
        tf.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        sb = ttk.Scrollbar(tf); sb.pack(side="right", fill="y")

        self.users_tree = ttk.Treeview(tf, columns=("username","role","created"),
                                        show="headings", height=10,
                                        yscrollcommand=sb.set)
        self.users_tree.pack(fill="both", expand=True)
        sb.config(command=self.users_tree.yview)
        for col, txt, w in [("username","Username",130),("role","Role",90),("created","Created",130)]:
            self.users_tree.heading(col, text=txt)
            self.users_tree.column(col, width=w, anchor="center")

        tk.Button(right, text="Delete Selected", font=_font(10, "bold"),
                  bg="#fff1f2", fg="#be123c", activebackground="#ffe4e6",
                  relief="flat", bd=0, cursor="hand2", padx=10, pady=6,
                  command=self._delete_user).pack(anchor="e", padx=12, pady=(0, 12))

        self._refresh_users_tree()

    def _refresh_users_tree(self):
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)
        for uname, info in self.users.items():
            self.users_tree.insert("", "end",
                                   values=(uname, info["role"], info.get("created_at", "—")))

    def _create_user(self):
        username = self.new_user_entry.get().strip()
        password = self.new_pass_entry.get()
        confirm  = self.confirm_pass_entry.get()
        role     = self.role_var.get()
        if not username or not password:
            self.create_status.config(text="Username and password required.", fg="#be123c"); return
        if username in self.users:
            self.create_status.config(text=f"'{username}' already exists.", fg="#be123c"); return
        if password != confirm:
            self.create_status.config(text="Passwords do not match.", fg="#be123c"); return
        if len(password) < 6:
            self.create_status.config(text="Password min. 6 characters.", fg="#be123c"); return
        self.users[username] = {"password": _hash_password(password), "role": role,
                                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        save_users(self.users)
        self.new_user_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        self.confirm_pass_entry.delete(0, tk.END)
        self.create_status.config(text=f"Account '{username}' created.", fg="#15803d")
        self._refresh_users_tree()

    def _delete_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a user to delete.", parent=self.dialog); return
        uname = self.users_tree.item(selected[0])["values"][0]
        if uname == self.current_user:
            messagebox.showwarning("Cannot Delete", "You cannot delete your own account.", parent=self.dialog); return
        if sum(1 for u in self.users.values() if u["role"] == "admin") == 1 and self.users[uname]["role"] == "admin":
            messagebox.showwarning("Cannot Delete", "Must keep at least one admin.", parent=self.dialog); return
        if messagebox.askyesno("Delete User", f'Delete "{uname}"? Cannot be undone.', parent=self.dialog):
            del self.users[uname]
            save_users(self.users)
            self._refresh_users_tree()


# ── Backup ────────────────────────────────────────────────────────────────────

def perform_backup(products, depletion_log) -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BACKUP_DIR, f"backup_{ts}.json")
    with open(path, "w") as f:
        json.dump({"backup_timestamp": ts, "products": products,
                   "depletion_log": depletion_log, "users": load_users()}, f, indent=2)
    return path

class BackupDialog:
    def __init__(self, parent, products, depletion_log):
        self.parent = parent
        self.products = products
        self.depletion_log = depletion_log

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Backup & Restore")
        self.dialog.configure(bg="white")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        w, h = 540, 420
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  // 2) - w // 2
        y = parent.winfo_y() + (parent.winfo_height() // 2) - h // 2
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self.dialog, bg="#1e3a8a", height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="Backup & Restore", font=_font(14, "bold"),
                 bg="#1e3a8a", fg="white").pack(side="left", padx=20, pady=12)

        info = tk.Frame(self.dialog, bg="#eff6ff", bd=0,
                        highlightthickness=1, highlightbackground="#bfdbfe")
        info.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(info, text=f"  {len(self.products)} product(s)  |  {len(self.depletion_log)} depletion record(s)",
                 font=_font(10), bg="#eff6ff", fg="#1d4ed8").pack(anchor="w", pady=10)

        bk = tk.Frame(self.dialog, bg="white", bd=0,
                      highlightthickness=1, highlightbackground="#dbe3f0")
        bk.pack(fill="x", padx=20, pady=(14, 0))
        tk.Label(bk, text="Create Backup", font=_font(12, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(bk, text="Saves products, depletion log and user accounts to a JSON file.",
                 font=_font(9), bg="white", fg="#6b7280").pack(anchor="w", padx=16)
        self.backup_status = tk.Label(bk, text="", font=_font(9),
                                      bg="white", fg="#15803d", wraplength=460)
        self.backup_status.pack(anchor="w", padx=16, pady=(4, 0))
        tk.Button(bk, text="Back Up Now", font=_font(10, "bold"),
                  bg="#2563eb", fg="white", activebackground="#1d4ed8",
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=9,
                  command=self._do_backup).pack(anchor="w", padx=16, pady=(10, 14))

        rc = tk.Frame(self.dialog, bg="white", bd=0,
                      highlightthickness=1, highlightbackground="#dbe3f0")
        rc.pack(fill="both", expand=True, padx=20, pady=(12, 20))
        tk.Label(rc, text="Existing Backups", font=_font(12, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w", padx=16, pady=(12, 4))
        lf = tk.Frame(rc, bg="white"); lf.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        sb = ttk.Scrollbar(lf); sb.pack(side="right", fill="y")
        self.backup_list = tk.Listbox(lf, font=_font(10), bg="white", fg="#1f2937",
                                      selectbackground="#dbeafe", selectforeground="#1e3a8a",
                                      relief="flat", bd=0, yscrollcommand=sb.set)
        self.backup_list.pack(fill="both", expand=True)
        sb.config(command=self.backup_list.yview)
        self._refresh_backup_list()

    def _refresh_backup_list(self):
        self.backup_list.delete(0, tk.END)
        if os.path.isdir(BACKUP_DIR):
            files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")], reverse=True)
            for f in files:
                self.backup_list.insert(tk.END, f"  {f}")
        if self.backup_list.size() == 0:
            self.backup_list.insert(tk.END, "  No backups found.")

    def _do_backup(self):
        try:
            path = perform_backup(self.products, self.depletion_log)
            self.backup_status.config(text=f"Saved: {os.path.basename(path)}", fg="#15803d")
            self._refresh_backup_list()
        except Exception as e:
            self.backup_status.config(text=f"Backup failed: {e}", fg="#be123c")


# ── Main Inventory App ────────────────────────────────────────────────────────

class InventoryApp:
    def __init__(self, root, current_user="admin", role="admin"):
        self.root = root
        self.current_user = current_user
        self.current_role = role

        self.root.title("Invntra - Inventory Registra")
        self.root.configure(bg="#f3f6fb")
        _maximize(self.root)

        self.products = []
        self.depletion_log = []
        self.edit_mode = False
        self.edit_index = None
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_search_filter())
        self.low_stock_threshold = 20

        self.configure_styles()
        self.build_ui()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1f2937",
                         fieldbackground="white", rowheight=34, borderwidth=0, font=_font(12))
        style.configure("Treeview.Heading", background="#e8eef9", foreground="#1e3a8a",
                         font=_font(12, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#dbeafe")],
                  foreground=[("selected", "#111827")])

    def build_ui(self):
        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#1e3a8a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Invntra - Inventory Registra",
                 font=_font(22, "bold"), bg="#1e3a8a", fg="white").pack(side="left", padx=30, pady=20)

        right_hdr = tk.Frame(header, bg="#1e3a8a")
        right_hdr.pack(side="right", padx=20)

        if self.current_role == "admin":
            tk.Button(right_hdr, text="Backup", font=_font(10, "bold"),
                      bg="#1d4ed8", fg="white", activebackground="#1e3a8a",
                      relief="flat", bd=0, cursor="hand2", padx=14, pady=7,
                      command=self._open_backup).pack(side="left", padx=(0, 8))
            tk.Button(right_hdr, text="Users", font=_font(10, "bold"),
                      bg="#1d4ed8", fg="white", activebackground="#1e3a8a",
                      relief="flat", bd=0, cursor="hand2", padx=14, pady=7,
                      command=self._open_user_mgmt).pack(side="left", padx=(0, 16))

        user_pill = tk.Frame(right_hdr, bg="#2563eb", bd=0,
                             highlightthickness=1, highlightbackground="#3b82f6")
        user_pill.pack(side="left", padx=(0, 8))
        badge = "ADMIN" if self.current_role == "admin" else "EMPLOYEE"
        color = "#fbbf24" if self.current_role == "admin" else "#93c5fd"
        tk.Label(user_pill, text=f"  {self.current_user}  [{badge}]  ",
                 font=_font(10, "bold"), bg="#2563eb", fg=color).pack(pady=6, padx=4)

        tk.Button(right_hdr, text="Log Out", font=_font(10),
                  bg="#1d4ed8", fg="white", activebackground="#1e3a8a",
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=7,
                  command=self._logout).pack(side="left")

        # ── Main container ─────────────────────────────────────────────────
        main_container = tk.Frame(self.root, bg="#f3f6fb")
        main_container.pack(fill="both", expand=True, padx=24, pady=24)

        # ── Left card – form ───────────────────────────────────────────────
        self.form_card = tk.Frame(main_container, bg="white", bd=0,
                                  highlightthickness=1, highlightbackground="#dbe3f0")
        self.form_card.pack(side="left", fill="y", padx=(0, 18))

        self.form_title_label = tk.Label(self.form_card, text="Product Information",
                                          font=_font(16, "bold"), bg="white", fg="#1f2937")
        self.form_title_label.pack(anchor="w", padx=24, pady=(24, 8))

        self.form_description_label = tk.Label(self.form_card,
                                               text="Fill in the fields below to add a new product.",
                                               font=_font(12), bg="white", fg="#6b7280")
        self.form_description_label.pack(anchor="w", padx=24, pady=(0, 18))

        self.name_entry     = self.create_labeled_input(self.form_card, "Product Name")
        self.category_entry = self.create_labeled_input(self.form_card, "Category")
        self.price_entry    = self.create_labeled_input(self.form_card, "Price")
        self.quantity_entry = self.create_labeled_input(self.form_card, "Quantity")

        self.primary_button = tk.Button(self.form_card, text="Add Product",
                                         font=_font(12, "bold"), bg="#2563eb", fg="white",
                                         activebackground="#1d4ed8", activeforeground="white",
                                         relief="flat", bd=0, cursor="hand2", padx=14, pady=12,
                                         command=self.handle_primary_action)
        self.primary_button.pack(fill="x", padx=24, pady=(14, 10))

        self.secondary_button = tk.Button(self.form_card, text="Clear Fields",
                                           font=_font(12), bg="#eef2f7", fg="#1f2937",
                                           activebackground="#e5e7eb", activeforeground="#111827",
                                           relief="flat", bd=0, cursor="hand2", padx=14, pady=12,
                                           command=self.handle_secondary_action)
        self.secondary_button.pack(fill="x", padx=24, pady=(0, 24))

        # ── Right section ──────────────────────────────────────────────────
        right_section = tk.Frame(main_container, bg="#f3f6fb")
        right_section.pack(side="right", fill="both", expand=True)

        # Summary card
        summary_card = tk.Frame(right_section, bg="white", bd=0,
                                highlightthickness=1, highlightbackground="#dbe3f0", height=90)
        summary_card.pack(fill="x", pady=(0, 18))
        summary_card.pack_propagate(False)

        self.status_label = tk.Label(summary_card, text="", font=_font(12, "bold"),
                                      bg="white", fg="#1f2937")
        self.status_label.pack(side="right", padx=24)

        self.total_products_label = tk.Label(summary_card, text="0",
                                              font=_font(24, "bold"), bg="white", fg="#1e3a8a")
        self.total_products_label.pack(side="left", padx=(24, 8), pady=20)
        tk.Label(summary_card, text="Products currently in inventory",
                 font=_font(12), bg="white", fg="#4b5563").pack(side="left", pady=28)

        tk.Frame(summary_card, bg="#e5e7eb", width=1).pack(side="left", fill="y", padx=24, pady=16)

        self.low_stock_count_label = tk.Label(summary_card, text="0",
                                               font=_font(24, "bold"), bg="white", fg="#b45309")
        self.low_stock_count_label.pack(side="left", padx=(0, 8), pady=20)
        tk.Label(summary_card, text="Low stock",
                 font=_font(12), bg="white", fg="#4b5563").pack(side="left", pady=28)

        tk.Frame(summary_card, bg="#e5e7eb", width=1).pack(side="left", fill="y", padx=24, pady=16)

        self.depletion_count_label = tk.Label(summary_card, text="0",
                                               font=_font(24, "bold"), bg="white",
                                               fg="#854d0e", cursor="hand2")
        self.depletion_count_label.pack(side="left", padx=(0, 8), pady=20)
        self.depletion_count_label.bind("<Button-1>", lambda e: self.toggle_depletion_log())

        self.depletion_text_btn = tk.Label(summary_card, text="Depletion  ▾",
                                           font=_font(12), bg="white", fg="#854d0e", cursor="hand2")
        self.depletion_text_btn.pack(side="left", pady=28)
        self.depletion_text_btn.bind("<Button-1>", lambda e: self.toggle_depletion_log())

        # Table card
        table_card = tk.Frame(right_section, bg="white", bd=0,
                              highlightthickness=1, highlightbackground="#dbe3f0")
        table_card.pack(fill="both", expand=True)

        # Depletion panel
        self.depletion_panel_visible = False
        self.depletion_panel = tk.Frame(right_section, bg="white", bd=0,
                                        highlightthickness=1, highlightbackground="#fde68a")
        dph = tk.Frame(self.depletion_panel, bg="#fefce8")
        dph.pack(fill="x")
        tk.Label(dph, text="Depletion Log", font=_font(12, "bold"),
                 bg="#fefce8", fg="#854d0e").pack(side="left", padx=16, pady=10)
        tk.Button(dph, text="Close", font=_font(9), bg="#fefce8", fg="#854d0e",
                  activebackground="#fef9c3", relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=4, command=self.toggle_depletion_log).pack(side="right", padx=12, pady=8)

        dlc = tk.Frame(self.depletion_panel, bg="white")
        dlc.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        dsb = ttk.Scrollbar(dlc); dsb.pack(side="right", fill="y")
        self.depletion_tree = ttk.Treeview(dlc,
                                            columns=("timestamp","product","category","qty","reason"),
                                            show="headings", height=6, yscrollcommand=dsb.set)
        self.depletion_tree.pack(fill="both", expand=True)
        dsb.config(command=self.depletion_tree.yview)
        for col, txt, w, st in [("timestamp","Date & Time",140,False),("product","Product",160,True),
                                  ("category","Category",120,True),("qty","Qty",90,False),("reason","Reason",200,True)]:
            self.depletion_tree.heading(col, text=txt)
            self.depletion_tree.column(col, width=w, anchor="center", stretch=st)

        # Table header
        table_header = tk.Frame(table_card, bg="white")
        table_header.pack(fill="x", padx=20, pady=(20, 8))
        tk.Label(table_header, text="Inventory Products",
                 font=_font(16, "bold"), bg="white", fg="#1f2937").pack(side="left")

        for txt, bg, fg, abg, hbg, cmd in [
            ("✏  Edit",      "#f0f6ff","#1e3a8a","#dbeafe","#bfdbfe", self.load_selected_for_edit),
            ("📦  Restock",  "#eff6ff","#1d4ed8","#dbeafe","#93c5fd", self.restock_stock_dialog),
            ("🛒  Sell",     "#f0fdf4","#15803d","#dcfce7","#86efac", self.sell_stock_dialog),
            ("⚠  Depletion","#fefce8","#854d0e","#fef9c3","#fde68a", self.report_depletion_dialog),
            ("🗑  Remove",   "#fff1f2","#be123c","#ffe4e6","#fecdd3", self.remove_selected_product),
        ]:
            tk.Button(table_header, text=txt, font=_font(12, "bold"),
                      bg=bg, fg=fg, activebackground=abg, activeforeground=fg,
                      relief="flat", bd=0, cursor="hand2", padx=8, pady=4,
                      highlightthickness=1, highlightbackground=hbg,
                      command=cmd).pack(side="right", padx=(0, 8))

        # Search bar
        sb_frame = tk.Frame(table_card, bg="white")
        sb_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(sb_frame, text="🔍", font=_emoji_font(13),
                 bg="white", fg="#6b7280").pack(side="left", padx=(0, 4))
        tk.Label(sb_frame, text="Search", font=_font(12, "bold"),
                 bg="white", fg="#374151").pack(side="left", padx=(0, 8))
        self.search_entry = tk.Entry(sb_frame, textvariable=self.search_var,
                                     font=_font(12), bg="#f8fafc", fg="#111827",
                                     relief="solid", bd=1, highlightthickness=1,
                                     highlightbackground="#cbd5e1", highlightcolor="#3b82f6")
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(sb_frame, text="✕", font=_font(9, "bold"),
                  bg="#f1f5f9", fg="#6b7280", activebackground="#e2e8f0",
                  relief="flat", bd=0, cursor="hand2", padx=8, pady=4,
                  command=self._clear_search).pack(side="left", padx=(6, 0))
        self.search_results_label = tk.Label(sb_frame, text="", font=_font(9),
                                              bg="white", fg="#6b7280")
        self.search_results_label.pack(side="left", padx=(10, 0))

        # Treeview
        tc = tk.Frame(table_card, bg="white")
        tc.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar = ttk.Scrollbar(tc); scrollbar.pack(side="right", fill="y")
        self.tree = ttk.Treeview(tc, columns=("name","category","price","quantity"),
                                  show="headings", yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        for col, txt in [("name","Product Name"),("category","Category"),
                         ("price","Price"),("quantity","Quantity")]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, minwidth=120, anchor="center", stretch=True)
        self.tree.tag_configure("low_stock",    background="#fff7ed", foreground="#92400e")
        self.tree.tag_configure("out_of_stock", background="#fff1f2", foreground="#9f1239")

    # ── Admin ─────────────────────────────────────────────────────────────────
    def _open_user_mgmt(self): UserManagementDialog(self.root, self.current_user)
    def _open_backup(self):    BackupDialog(self.root, self.products, self.depletion_log)
    def _logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.root.destroy(); _launch_login()

    # ── Input helper ──────────────────────────────────────────────────────────
    def create_labeled_input(self, parent, label_text):
        tk.Label(parent, text=label_text, font=_font(12, "bold"),
                 bg="white", fg="#374151").pack(anchor="w", padx=24, pady=(0, 6))
        entry = tk.Entry(parent, font=_font(12), bg="white", fg="#111827",
                         relief="solid", bd=1, highlightthickness=1,
                         highlightbackground="#cbd5e1", highlightcolor="#3b82f6", width=28)
        entry.pack(fill="x", padx=24, pady=(0, 14), ipady=8)
        return entry

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def add_product(self):
        name, category, price, quantity = self._read_fields()
        if name is None: return
        dup = next((i for i, p in enumerate(self.products) if p["name"].lower() == name.lower()), None)
        if dup is not None:
            if messagebox.askyesno("Product Already Exists",
                                   f'"{name}" already exists.\n\nEdit instead?'):
                self.edit_index = dup
                p = self.products[dup]
                for e, v in [(self.name_entry, p["name"]), (self.category_entry, p["category"]),
                             (self.price_entry, str(p["price"])), (self.quantity_entry, str(p["quantity"]))]:
                    self._set_field(e, v)
                self.edit_mode = True; self._apply_edit_mode_ui()
            return
        self.products.append({"name": name, "category": category, "price": price, "quantity": quantity})
        self.refresh_table(); self.update_summary(); self.clear_fields()
        self.status_label.config(text=f"Added: {name}")

    def load_selected_for_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product row before clicking Edit."); return
        self.edit_index = list(self.tree.get_children()).index(selected[0])
        p = self.products[self.edit_index]
        for e, v in [(self.name_entry, p["name"]), (self.category_entry, p["category"]),
                     (self.price_entry, str(p["price"])), (self.quantity_entry, str(p["quantity"]))]:
            self._set_field(e, v)
        self.edit_mode = True; self._apply_edit_mode_ui()

    def save_edited_product(self):
        name, category, price, quantity = self._read_fields()
        if name is None: return
        self.products[self.edit_index] = {"name": name, "category": category,
                                          "price": price, "quantity": quantity}
        self.refresh_table(); self.update_summary(); self._exit_edit_mode()
        self.status_label.config(text=f"Updated: {name}")

    def cancel_edit(self):
        self._exit_edit_mode(); self.status_label.config(text="Edit cancelled.")

    def remove_selected_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product row before removing."); return
        idx = list(self.tree.get_children()).index(selected[0])
        p = self.products[idx]
        if not messagebox.askyesno("Remove Product", f'Remove "{p["name"]}"? Cannot be undone.'): return
        if self.edit_mode and self.edit_index == idx: self._exit_edit_mode()
        del self.products[idx]
        self.refresh_table(); self.update_summary()
        self.status_label.config(text=f"Removed: {p['name']}")

    def restock_stock_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product row before restocking."); return
        idx = list(self.tree.get_children()).index(selected[0])
        product = self.products[idx]
        dialog = self._make_dialog("Restock Product", 360, 260, "#1d4ed8")
        info = tk.Frame(dialog, bg="white"); info.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(info, text=f"Product:  {product['name']}", font=_font(10, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w")
        tk.Label(info, text=f"Current Stock:  {product['quantity']} units", font=_font(10),
                 bg="white", fg="#6b7280").pack(anchor="w", pady=(4, 0))
        ef = tk.Frame(dialog, bg="white"); ef.pack(fill="x", padx=20, pady=(14, 0))
        tk.Label(ef, text="Units Received", font=_font(10, "bold"),
                 bg="white", fg="#374151").pack(anchor="w")
        qty_entry = tk.Entry(ef, font=_font(11), bg="white", fg="#111827", relief="solid", bd=1,
                             highlightthickness=1, highlightbackground="#cbd5e1",
                             highlightcolor="#1d4ed8", width=16)
        qty_entry.pack(anchor="w", pady=(6, 0), ipady=6); qty_entry.focus_set()
        def confirm():
            try:
                n = int(qty_entry.get().strip())
                if n <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Must be a positive integer.", parent=dialog); return
            self.products[idx]["quantity"] += n
            self.refresh_table(); self.update_summary(); dialog.destroy()
            self.status_label.config(text=f"Restocked {n} unit(s) of {product['name']}")
        bf = tk.Frame(dialog, bg="white"); bf.pack(fill="x", padx=20, pady=(16, 0))
        tk.Button(bf, text="Confirm Restock", font=_font(10, "bold"), bg="#1d4ed8", fg="white",
                  activebackground="#1e3a8a", relief="flat", bd=0, cursor="hand2",
                  padx=14, pady=8, command=confirm).pack(side="left")
        tk.Button(bf, text="Cancel", font=_font(10), bg="#eef2f7", fg="#1f2937",
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                  command=dialog.destroy).pack(side="left", padx=(10, 0))
        dialog.bind("<Return>", lambda e: confirm())

    def sell_stock_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product row before selling."); return
        idx = list(self.tree.get_children()).index(selected[0])
        product = self.products[idx]
        if product["quantity"] == 0:
            messagebox.showwarning("Out of Stock", f'"{product["name"]}" is out of stock.'); return
        dialog = self._make_dialog("Record Sale", 360, 260, "#15803d")
        info = tk.Frame(dialog, bg="white"); info.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(info, text=f"Product:  {product['name']}", font=_font(10, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w")
        tk.Label(info, text=f"Current Stock:  {product['quantity']} units", font=_font(10),
                 bg="white", fg="#6b7280").pack(anchor="w", pady=(4, 0))
        ef = tk.Frame(dialog, bg="white"); ef.pack(fill="x", padx=20, pady=(14, 0))
        tk.Label(ef, text="Units Sold", font=_font(10, "bold"),
                 bg="white", fg="#374151").pack(anchor="w")
        qty_entry = tk.Entry(ef, font=_font(11), bg="white", fg="#111827", relief="solid", bd=1,
                             highlightthickness=1, highlightbackground="#cbd5e1",
                             highlightcolor="#15803d", width=16)
        qty_entry.pack(anchor="w", pady=(6, 0), ipady=6); qty_entry.focus_set()
        def confirm():
            try:
                n = int(qty_entry.get().strip())
                if n <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Must be a positive integer.", parent=dialog); return
            if n > product["quantity"]:
                messagebox.showwarning("Insufficient Stock",
                                       f'Only {product["quantity"]} unit(s) available.', parent=dialog); return
            self.products[idx]["quantity"] -= n
            new_qty = self.products[idx]["quantity"]
            self.refresh_table(); self.update_summary(); dialog.destroy()
            if new_qty == 0:
                messagebox.showinfo("Out of Stock", f'"{product["name"]}" is now out of stock.')
                self.status_label.config(text=f"Out of stock: {product['name']}")
            else:
                self.status_label.config(text=f"Sold {n} unit(s) — {new_qty} remaining")
        bf = tk.Frame(dialog, bg="white"); bf.pack(fill="x", padx=20, pady=(16, 0))
        tk.Button(bf, text="Confirm Sale", font=_font(10, "bold"), bg="#15803d", fg="white",
                  activebackground="#14532d", relief="flat", bd=0, cursor="hand2",
                  padx=14, pady=8, command=confirm).pack(side="left")
        tk.Button(bf, text="Cancel", font=_font(10), bg="#eef2f7", fg="#1f2937",
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                  command=dialog.destroy).pack(side="left", padx=(10, 0))
        dialog.bind("<Return>", lambda e: confirm())

    def report_depletion_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product row before reporting."); return
        idx = list(self.tree.get_children()).index(selected[0])
        product = self.products[idx]
        if product["quantity"] == 0:
            messagebox.showwarning("No Stock", f'"{product["name"]}" has no stock.'); return
        dialog = self._make_dialog("Report Depletion", 380, 320, "#854d0e")
        info = tk.Frame(dialog, bg="white"); info.pack(fill="x", padx=20, pady=(14, 0))
        tk.Label(info, text=f"Product:  {product['name']}", font=_font(10, "bold"),
                 bg="white", fg="#1f2937").pack(anchor="w")
        tk.Label(info, text=f"Current Stock:  {product['quantity']} units", font=_font(10),
                 bg="white", fg="#6b7280").pack(anchor="w", pady=(4, 0))
        ef = tk.Frame(dialog, bg="white"); ef.pack(fill="x", padx=20, pady=(12, 0))
        tk.Label(ef, text="Units Depleted", font=_font(10, "bold"),
                 bg="white", fg="#374151").pack(anchor="w")
        qty_entry = tk.Entry(ef, font=_font(11), bg="white", fg="#111827", relief="solid", bd=1,
                             highlightthickness=1, highlightbackground="#cbd5e1",
                             highlightcolor="#854d0e", width=16)
        qty_entry.pack(anchor="w", pady=(6, 0), ipady=6); qty_entry.focus_set()
        rf = tk.Frame(dialog, bg="white"); rf.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(rf, text="Reason", font=_font(10, "bold"),
                 bg="white", fg="#374151").pack(anchor="w")
        reason_entry = tk.Entry(rf, font=_font(11), bg="white", fg="#111827", relief="solid", bd=1,
                                highlightthickness=1, highlightbackground="#cbd5e1",
                                highlightcolor="#854d0e")
        reason_entry.pack(fill="x", pady=(6, 0), ipady=6)
        def confirm():
            try:
                n = int(qty_entry.get().strip())
                if n <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Must be a positive integer.", parent=dialog); return
            if n > product["quantity"]:
                messagebox.showwarning("Exceeds Stock",
                                       f'Only {product["quantity"]} unit(s) available.', parent=dialog); return
            reason = reason_entry.get().strip() or "No reason provided"
            self.products[idx]["quantity"] -= n
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.depletion_log.append({"timestamp": ts, "product": product["name"],
                                       "category": product["category"], "qty": n, "reason": reason})
            self.refresh_table(); self.update_summary(); self._refresh_depletion_tree(); dialog.destroy()
            self.status_label.config(text=f"Depletion: {n} unit(s) of {product['name']}")
        bf = tk.Frame(dialog, bg="white"); bf.pack(fill="x", padx=20, pady=(14, 0))
        tk.Button(bf, text="Submit Report", font=_font(10, "bold"), bg="#854d0e", fg="white",
                  activebackground="#713f12", relief="flat", bd=0, cursor="hand2",
                  padx=14, pady=8, command=confirm).pack(side="left")
        tk.Button(bf, text="Cancel", font=_font(10), bg="#eef2f7", fg="#1f2937",
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                  command=dialog.destroy).pack(side="left", padx=(10, 0))
        dialog.bind("<Return>", lambda e: confirm())

    def toggle_depletion_log(self):
        self.depletion_panel_visible = not self.depletion_panel_visible
        if self.depletion_panel_visible:
            self.depletion_panel.pack(fill="x", pady=(8, 0))
            self.depletion_text_btn.config(text="Depletion  ▴")
        else:
            self.depletion_panel.pack_forget()
            self.depletion_text_btn.config(text="Depletion  ▾")

    def _refresh_depletion_tree(self):
        for row in self.depletion_tree.get_children():
            self.depletion_tree.delete(row)
        for entry in reversed(self.depletion_log):
            self.depletion_tree.insert("", "end",
                                       values=(entry["timestamp"], entry["product"],
                                               entry["category"], entry["qty"], entry["reason"]))
        total = sum(e["qty"] for e in self.depletion_log)
        if hasattr(self, "depletion_count_label"):
            self.depletion_count_label.config(text=str(total))

    def _apply_edit_mode_ui(self):
        self.status_label.config(text="Edit mode — modify fields and click Save Changes")
        self.form_title_label.config(text="Edit Product", fg="#b45309")
        self.form_description_label.config(text="Modify the fields below and click Save Changes.")
        self.primary_button.config(text="Save Changes", bg="#d97706", activebackground="#b45309")
        self.secondary_button.config(text="Cancel Edit")
        self.form_card.config(highlightbackground="#fcd34d")

    def _exit_edit_mode(self):
        self.edit_mode = False; self.edit_index = None; self.clear_fields()
        self.status_label.config(text="")
        self.form_title_label.config(text="Product Information", fg="#1f2937")
        self.form_description_label.config(text="Fill in the fields below to add a new product.")
        self.primary_button.config(text="Add Product", bg="#2563eb", activebackground="#1d4ed8")
        self.secondary_button.config(text="Clear Fields")
        self.form_card.config(highlightbackground="#dbe3f0")

    def handle_primary_action(self):
        self.save_edited_product() if self.edit_mode else self.add_product()

    def handle_secondary_action(self):
        self.cancel_edit() if self.edit_mode else self.clear_fields()

    def _read_fields(self):
        name = self.name_entry.get().strip(); category = self.category_entry.get().strip()
        price = self.price_entry.get().strip(); quantity = self.quantity_entry.get().strip()
        if not all([name, category, price, quantity]):
            messagebox.showwarning("Missing Information", "Please complete all fields.")
            return None, None, None, None
        try:
            pv = float(price); qv = int(quantity)
            if pv < 0 or qv < 0:
                messagebox.showwarning("Invalid Values", "Price and quantity must be positive.")
                return None, None, None, None
        except ValueError:
            messagebox.showerror("Invalid Input", "Price must be numeric; quantity must be an integer.")
            return None, None, None, None
        return name, category, pv, qv

    def _set_field(self, entry, value):
        entry.delete(0, tk.END); entry.insert(0, value)

    def refresh_table(self):
        query = self.search_var.get().strip().lower()
        for row in self.tree.get_children(): self.tree.delete(row)
        matched = 0
        for p in self.products:
            if query and query not in p["name"].lower() and query not in p["category"].lower(): continue
            qty = p["quantity"]
            tag = ("out_of_stock",) if qty == 0 else ("low_stock",) if qty <= self.low_stock_threshold else ()
            self.tree.insert("", "end",
                             values=(p["name"], p["category"], f"${p['price']:.2f}", qty), tags=tag)
            matched += 1
        if hasattr(self, "search_results_label"):
            self.search_results_label.config(
                text=f"{matched} of {len(self.products)} product(s) found" if query else "")

    def apply_search_filter(self): self.refresh_table()

    def _clear_search(self):
        self.search_var.set(""); self.search_entry.focus_set()

    def update_summary(self):
        self.total_products_label.config(text=str(len(self.products)))
        low = sum(1 for p in self.products if p["quantity"] <= self.low_stock_threshold)
        self.low_stock_count_label.config(text=str(low))

    def clear_fields(self):
        for e in [self.name_entry, self.category_entry, self.price_entry, self.quantity_entry]:
            e.delete(0, tk.END)

    def _make_dialog(self, title, w, h, hdr_color):
        dialog = tk.Toplevel(self.root)
        dialog.title(title); dialog.geometry(f"{w}x{h}")
        dialog.resizable(False, False); dialog.configure(bg="white"); dialog.grab_set()
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - w // 2
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - h // 2
        dialog.geometry(f"+{x}+{y}")
        hdr = tk.Frame(dialog, bg=hdr_color, height=48); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text=title, font=_font(13, "bold"),
                 bg=hdr_color, fg="white").pack(side="left", padx=16, pady=12)
        return dialog


# ── Entry point ───────────────────────────────────────────────────────────────

def _launch_login():
    def on_login(username, role):
        root = tk.Tk()
        InventoryApp(root, current_user=username, role=role)
        root.mainloop()
    LoginWindow(on_success=on_login)

if __name__ == "__main__":
    _launch_login()
