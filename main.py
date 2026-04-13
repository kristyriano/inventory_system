import tkinter as tk

from tkinter import ttk, messagebox
 
 
class InventoryApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Invntra - Inventory Registra")

        self.root.configure(bg="#f3f6fb")
 
        # --- START MAXIMISED (system window with OS controls) ---
        self.root.state("zoomed")
 
        self.products = []

        # --- DAMAGE LOG ---
        # Each entry: {product, category, qty, reason, timestamp}
        self.depletion_log = []
 
        # --- EDIT STATE ---

        self.edit_mode = False

        self.edit_index = None

        # --- SEARCH STATE ---
        # Holds the current search string; empty string means no filter active.
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_search_filter())

        # --- LOW STOCK THRESHOLD ---
        # Products with quantity <= this value are flagged as low stock.
        self.low_stock_threshold = 20
 
        self.configure_styles()

        self.build_ui()
 
    def configure_styles(self):

        style = ttk.Style()

        style.theme_use("clam")
 
        style.configure(

            "Treeview",

            background="white",

            foreground="#1f2937",

            fieldbackground="white",

            rowheight=34,

            borderwidth=0,

            font=("Segoe UI", 12),

        )
 
        style.configure(

            "Treeview.Heading",

            background="#e8eef9",

            foreground="#1e3a8a",

            font=("Segoe UI", 12, "bold"),

            relief="flat",

        )
 
        style.map(

            "Treeview",

            background=[("selected", "#dbeafe")],

            foreground=[("selected", "#111827")],

        )
 
    def build_ui(self):

        # ── Header ──────────────────────────────────────────────────────────

        header = tk.Frame(self.root, bg="#1e3a8a", height=80)

        header.pack(fill="x")

        header.pack_propagate(False)
 
        title = tk.Label(

            header,

            text="Invntra - Inventory Registra",

            font=("Segoe UI", 22, "bold"),

            bg="#1e3a8a",

            fg="white",

        )

        title.pack(side="left", padx=30, pady=20)
 

 
        # ── Main container ───────────────────────────────────────────────────

        main_container = tk.Frame(self.root, bg="#f3f6fb")

        main_container.pack(fill="both", expand=True, padx=24, pady=24)
 
        # ── Left card – form ─────────────────────────────────────────────────

        self.form_card = tk.Frame(

            main_container,

            bg="white",

            bd=0,

            highlightthickness=1,

            highlightbackground="#dbe3f0",

        )

        self.form_card.pack(side="left", fill="y", padx=(0, 18))
 
        self.form_title_label = tk.Label(

            self.form_card,

            text="Product Information",

            font=("Segoe UI", 16, "bold"),

            bg="white",

            fg="#1f2937",

        )

        self.form_title_label.pack(anchor="w", padx=24, pady=(24, 8))
 
        self.form_description_label = tk.Label(

            self.form_card,

            text="Fill in the fields below to add a new product.",

            font=("Segoe UI", 12),

            bg="white",

            fg="#6b7280",

        )

        self.form_description_label.pack(anchor="w", padx=24, pady=(0, 18))
 
        self.name_entry = self.create_labeled_input(self.form_card, "Product Name")

        self.category_entry = self.create_labeled_input(self.form_card, "Category")

        self.price_entry = self.create_labeled_input(self.form_card, "Price")

        self.quantity_entry = self.create_labeled_input(self.form_card, "Quantity")
 
        self.primary_button = tk.Button(

            self.form_card,

            text="Add Product",

            font=("Segoe UI", 12, "bold"),

            bg="#2563eb",

            fg="white",

            activebackground="#1d4ed8",

            activeforeground="white",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=14,

            pady=12,

            command=self.handle_primary_action,

        )

        self.primary_button.pack(fill="x", padx=24, pady=(14, 10))
 
        self.secondary_button = tk.Button(

            self.form_card,

            text="Clear Fields",

            font=("Segoe UI", 12),

            bg="#eef2f7",

            fg="#1f2937",

            activebackground="#e5e7eb",

            activeforeground="#111827",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=14,

            pady=12,

            command=self.handle_secondary_action,

        )

        self.secondary_button.pack(fill="x", padx=24, pady=(0, 24))
 
        # ── Right section ────────────────────────────────────────────────────

        right_section = tk.Frame(main_container, bg="#f3f6fb")

        right_section.pack(side="right", fill="both", expand=True)
 
        # Summary card

        summary_card = tk.Frame(

            right_section,

            bg="white",

            bd=0,

            highlightthickness=1,

            highlightbackground="#dbe3f0",

            height=90,

        )

        summary_card.pack(fill="x", pady=(0, 18))

        summary_card.pack_propagate(False)

        # Confirmation / status message — far right of summary card
        self.status_label = tk.Label(
            summary_card,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#1f2937",
        )
        self.status_label.pack(side="right", padx=24)
 
        self.total_products_label = tk.Label(

            summary_card,

            text="0",

            font=("Segoe UI", 24, "bold"),

            bg="white",

            fg="#1e3a8a",

        )

        self.total_products_label.pack(side="left", padx=(24, 8), pady=20)
 
        summary_text = tk.Label(

            summary_card,

            text="Products currently in inventory",

            font=("Segoe UI", 12),

            bg="white",

            fg="#4b5563",

        )

        summary_text.pack(side="left", pady=28)

        # Vertical divider
        tk.Frame(summary_card, bg="#e5e7eb", width=1).pack(
            side="left", fill="y", padx=24, pady=16
        )

        # Low-stock count + inline threshold control grouped together
        self.low_stock_count_label = tk.Label(
            summary_card,
            text="0",
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg="#b45309",
        )
        self.low_stock_count_label.pack(side="left", padx=(0, 8), pady=20)

        tk.Label(
            summary_card,
            text="Low stock",
            font=("Segoe UI", 12),
            bg="white",
            fg="#4b5563",
        ).pack(side="left", pady=28)

        # Vertical divider
        tk.Frame(summary_card, bg="#e5e7eb", width=1).pack(
            side="left", fill="y", padx=24, pady=16
        )

        # depletion items count — clicking the count or label toggles the log
        self.depletion_count_label = tk.Label(
            summary_card,
            text="0",
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg="#854d0e",
            cursor="hand2",
        )
        self.depletion_count_label.pack(side="left", padx=(0, 8), pady=20)
        self.depletion_count_label.bind("<Button-1>", lambda e: self.toggle_depletion_log())

        self.depletion_text_btn = tk.Label(
            summary_card,
            text="Depletion  ▾",
            font=("Segoe UI", 12),
            bg="white",
            fg="#854d0e",
            cursor="hand2",
        )
        self.depletion_text_btn.pack(side="left", pady=28)
        self.depletion_text_btn.bind("<Button-1>", lambda e: self.toggle_depletion_log())

        # Table card

        table_card = tk.Frame(

            right_section,

            bg="white",

            bd=0,

            highlightthickness=1,

            highlightbackground="#dbe3f0",

        )

        table_card.pack(fill="both", expand=True)

        # ── Depletion log panel ─────────────────────────────────────────────────
        self.depletion_panel_visible = False

        self.depletion_panel = tk.Frame(
            right_section,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#fde68a",
        )
        # Not packed initially — shown/hidden via toggle_depletion_log()

        depletion_panel_header = tk.Frame(self.depletion_panel, bg="#fefce8")
        depletion_panel_header.pack(fill="x")

        tk.Label(
            depletion_panel_header,
            text="⚠  Depletion Log",
            font=("Segoe UI", 12, "bold"),
            bg="#fefce8",
            fg="#854d0e",
        ).pack(side="left", padx=16, pady=10)

        tk.Button(
            depletion_panel_header,
            text="✕  Close",
            font=("Segoe UI", 9),
            bg="#fefce8",
            fg="#854d0e",
            activebackground="#fef9c3",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.toggle_depletion_log,
        ).pack(side="right", padx=12, pady=8)

        depletion_log_container = tk.Frame(self.depletion_panel, bg="white")
        depletion_log_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        depletion_scrollbar = ttk.Scrollbar(depletion_log_container)
        depletion_scrollbar.pack(side="right", fill="y")

        self.depletion_tree = ttk.Treeview(
            depletion_log_container,
            columns=("timestamp", "product", "category", "qty", "reason"),
            show="headings",
            height=6,
            yscrollcommand=depletion_scrollbar.set,
        )
        self.depletion_tree.pack(fill="both", expand=True)
        depletion_scrollbar.config(command=self.depletion_tree.yview)

        self.depletion_tree.heading("timestamp", text="Date & Time")
        self.depletion_tree.heading("product",   text="Product")
        self.depletion_tree.heading("category",  text="Category")
        self.depletion_tree.heading("qty",       text="Qty depletion")
        self.depletion_tree.heading("reason",    text="Reason")

        self.depletion_tree.column("timestamp", width=140, anchor="center", stretch=False)
        self.depletion_tree.column("product",   width=160, anchor="center", stretch=True)
        self.depletion_tree.column("category",  width=120, anchor="center", stretch=True)
        self.depletion_tree.column("qty",       width=90,  anchor="center", stretch=False)
        self.depletion_tree.column("reason",    width=200, anchor="center", stretch=True)

        table_header = tk.Frame(table_card, bg="white")

        table_header.pack(fill="x", padx=20, pady=(20, 8))
 
        table_title = tk.Label(

            table_header,

            text="Inventory Products",

            font=("Segoe UI", 16, "bold"),

            bg="white",

            fg="#1f2937",

        )

        table_title.pack(side="left")
 
        self.edit_button = tk.Button(

            table_header,

            text="✏  Edit",

            font=("Segoe UI", 12, "bold"),

            bg="#f0f6ff",

            fg="#1e3a8a",

            activebackground="#dbeafe",

            activeforeground="#1e3a8a",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=8,

            pady=4,

            highlightthickness=1,

            highlightbackground="#bfdbfe",

            command=self.load_selected_for_edit,

        )

        self.edit_button.pack(side="right", padx=(0, 8))
 
        self.restock_button = tk.Button(

            table_header,

            text="📦  Restock",

            font=("Segoe UI", 12, "bold"),

            bg="#eff6ff",

            fg="#1d4ed8",

            activebackground="#dbeafe",

            activeforeground="#1e3a8a",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=8,

            pady=4,

            highlightthickness=1,

            highlightbackground="#93c5fd",

            command=self.restock_stock_dialog,

        )

        self.restock_button.pack(side="right", padx=(0, 8))
 
        self.sell_button = tk.Button(

            table_header,

            text="🛒  Sell",

            font=("Segoe UI", 12, "bold"),

            bg="#f0fdf4",

            fg="#15803d",

            activebackground="#dcfce7",

            activeforeground="#14532d",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=8,

            pady=4,

            highlightthickness=1,

            highlightbackground="#86efac",

            command=self.sell_stock_dialog,

        )

        self.sell_button.pack(side="right", padx=(0, 8))

        # Depletion report button
        self.depletion_button = tk.Button(
            table_header,
            text="⚠  Depletion",
            font=("Segoe UI", 12, "bold"),
            bg="#fefce8",
            fg="#854d0e",
            activebackground="#fef9c3",
            activeforeground="#713f12",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=4,
            highlightthickness=1,
            highlightbackground="#fde68a",
            command=self.report_depletion_dialog,
        )
        self.depletion_button.pack(side="right", padx=(0, 8))

        self.remove_button = tk.Button(

            table_header,

            text="🗑  Remove",

            font=("Segoe UI", 12, "bold"),

            bg="#fff1f2",

            fg="#be123c",

            activebackground="#ffe4e6",

            activeforeground="#9f1239",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=8,

            pady=4,

            highlightthickness=1,

            highlightbackground="#fecdd3",

            command=self.remove_selected_product,

        )

        self.remove_button.pack(side="right", padx=(0, 8))
 
        # ── Search / filter bar ─────────────────────────────────────────────
        search_bar = tk.Frame(table_card, bg="white")
        search_bar.pack(fill="x", padx=20, pady=(0, 10))

        search_icon = tk.Label(
            search_bar,
            text="🔍",
            font=("Segoe UI", 12),
            bg="white",
            fg="#6b7280",
        )
        search_icon.pack(side="left", padx=(0, 4))

        tk.Label(
            search_bar,
            text="Search",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#374151",
        ).pack(side="left", padx=(0, 8))

        self.search_entry = tk.Entry(
            search_bar,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            bg="#f8fafc",
            fg="#111827",
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#cbd5e1",
            highlightcolor="#3b82f6",
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=6)

        self.search_clear_btn = tk.Button(
            search_bar,
            text="✕",
            font=("Segoe UI", 9, "bold"),
            bg="#f1f5f9",
            fg="#6b7280",
            activebackground="#e2e8f0",
            activeforeground="#1f2937",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self._clear_search,
        )
        self.search_clear_btn.pack(side="left", padx=(6, 0))

        self.search_results_label = tk.Label(
            search_bar,
            text="",
            font=("Segoe UI", 9),
            bg="white",
            fg="#6b7280",
        )
        self.search_results_label.pack(side="left", padx=(10, 0))

        table_container = tk.Frame(table_card, bg="white")

        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
 
        scrollbar = ttk.Scrollbar(table_container)

        scrollbar.pack(side="right", fill="y")
 
        self.tree = ttk.Treeview(

            table_container,

            columns=("name", "category", "price", "quantity"),

            show="headings",

            yscrollcommand=scrollbar.set,

        )

        self.tree.pack(fill="both", expand=True)
 
        scrollbar.config(command=self.tree.yview)
 
        self.tree.heading("name", text="Product Name")

        self.tree.heading("category", text="Category")

        self.tree.heading("price", text="Price")

        self.tree.heading("quantity", text="Quantity")
 
        self.tree.column("name", minwidth=220, anchor="center", stretch=True)

        self.tree.column("category", minwidth=180, anchor="center", stretch=True)

        self.tree.column("price", minwidth=120, anchor="center", stretch=True)

        self.tree.column("quantity", minwidth=120, anchor="center", stretch=True)

        # Row colour tags for low-stock highlighting
        self.tree.tag_configure("low_stock",  background="#fff7ed", foreground="#92400e")
        self.tree.tag_configure("out_of_stock", background="#fff1f2", foreground="#9f1239")
 
    # ── Helper ───────────────────────────────────────────────────────────────
 
    def create_labeled_input(self, parent, label_text):

        label = tk.Label(

            parent,

            text=label_text,

            font=("Segoe UI", 12, "bold"),

            bg="white",

            fg="#374151",

        )

        label.pack(anchor="w", padx=24, pady=(0, 6))
 
        entry = tk.Entry(

            parent,

            font=("Segoe UI", 12),

            bg="white",

            fg="#111827",

            relief="solid",

            bd=1,

            highlightthickness=1,

            highlightbackground="#cbd5e1",

            highlightcolor="#3b82f6",

            width=28,

        )

        entry.pack(fill="x", padx=24, pady=(0, 14), ipady=8)
 
        return entry
 
    # ── Add product ───────────────────────────────────────────────────────────
 
    def add_product(self):

        name, category, price, quantity = self._read_fields()

        if name is None:

            return
 
        duplicate_index = next(

            (

                i

                for i, p in enumerate(self.products)

                if p["name"].lower() == name.lower()

            ),

            None,

        )
 
        if duplicate_index is not None:

            confirm = messagebox.askyesno(

                "Product Already Exists",

                f'"{name}" is already in the inventory.\n\n'

                "Would you like to edit the existing product instead?",

            )

            if confirm:

                self.edit_index = duplicate_index

                product = self.products[self.edit_index]

                self._set_field(self.name_entry, product["name"])

                self._set_field(self.category_entry, product["category"])

                self._set_field(self.price_entry, str(product["price"]))

                self._set_field(self.quantity_entry, str(product["quantity"]))

                self.edit_mode = True

                self._apply_edit_mode_ui()

                self.status_label.config(text=f"Editing existing: {name}")

            return
 
        product = {

            "name": name,

            "category": category,

            "price": price,

            "quantity": quantity,

        }
 
        self.products.append(product)

        self.refresh_table()

        self.update_summary()

        self.clear_fields()

        self.status_label.config(text=f"Added: {name}")
 
    # ── Edit / Update logic ───────────────────────────────────────────────────
 
    def load_selected_for_edit(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(

                "No Selection",

                "Please select a product row in the table before clicking Edit.",

            )

            return
 
        all_items = self.tree.get_children()

        self.edit_index = list(all_items).index(selected[0])

        product = self.products[self.edit_index]
 
        self._set_field(self.name_entry, product["name"])

        self._set_field(self.category_entry, product["category"])

        self._set_field(self.price_entry, str(product["price"]))

        self._set_field(self.quantity_entry, str(product["quantity"]))
 
        self.edit_mode = True

        self._apply_edit_mode_ui()
 
    def save_edited_product(self):

        name, category, price, quantity = self._read_fields()

        if name is None:

            return
 
        self.products[self.edit_index] = {

            "name": name,

            "category": category,

            "price": price,

            "quantity": quantity,

        }
 
        self.refresh_table()

        self.update_summary()

        self._exit_edit_mode()

        self.status_label.config(text=f"Updated: {name}")
 
    def cancel_edit(self):

        self._exit_edit_mode()

        self.status_label.config(text="Edit cancelled.")
 
    # ── Remove product ────────────────────────────────────────────────────────
 
    def remove_selected_product(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(

                "No Selection",

                "Please select a product row in the table before removing.",

            )

            return
 
        all_items = self.tree.get_children()

        del_index = list(all_items).index(selected[0])

        product = self.products[del_index]
 
        confirm = messagebox.askyesno(

            "Remove Product",

            f'Are you sure you want to remove "{product["name"]}" from the inventory?\n\n'

            "This action cannot be undone.",

        )

        if not confirm:

            return
 
        removed_name = product["name"]
 
        if self.edit_mode and self.edit_index == del_index:

            self._exit_edit_mode()
 
        del self.products[del_index]

        self.refresh_table()

        self.update_summary()

        self.status_label.config(text=f"Removed: {removed_name}")
 
    # ── Restock ───────────────────────────────────────────────────────────────
 
    def restock_stock_dialog(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(

                "No Selection",

                "Please select a product row in the table before restocking.",

            )

            return
 
        all_items = self.tree.get_children()

        restock_index = list(all_items).index(selected[0])

        product = self.products[restock_index]
 
        dialog = tk.Toplevel(self.root)

        dialog.title("Restock Product")

        dialog.geometry("360x260")

        dialog.resizable(False, False)

        dialog.configure(bg="white")

        dialog.grab_set()
 
        self.root.update_idletasks()

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 180

        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 130

        dialog.geometry(f"+{x}+{y}")
 
        dialog_header = tk.Frame(dialog, bg="#1d4ed8", height=48)

        dialog_header.pack(fill="x")

        dialog_header.pack_propagate(False)

        tk.Label(

            dialog_header,

            text="Restock Product",

            font=("Segoe UI", 13, "bold"),

            bg="#1d4ed8",

            fg="white",

        ).pack(side="left", padx=16, pady=12)
 
        info_frame = tk.Frame(dialog, bg="white")

        info_frame.pack(fill="x", padx=20, pady=(16, 0))
 
        tk.Label(

            info_frame,

            text=f"Product:  {product['name']}",

            font=("Segoe UI", 10, "bold"),

            bg="white",

            fg="#1f2937",

        ).pack(anchor="w")
 
        tk.Label(

            info_frame,

            text=f"Current Stock:  {product['quantity']} units",

            font=("Segoe UI", 10),

            bg="white",

            fg="#6b7280",

        ).pack(anchor="w", pady=(4, 0))
 
        entry_frame = tk.Frame(dialog, bg="white")

        entry_frame.pack(fill="x", padx=20, pady=(14, 0))
 
        tk.Label(

            entry_frame,

            text="Units Received",

            font=("Segoe UI", 10, "bold"),

            bg="white",

            fg="#374151",

        ).pack(anchor="w")
 
        qty_entry = tk.Entry(

            entry_frame,

            font=("Segoe UI", 11),

            bg="white",

            fg="#111827",

            relief="solid",

            bd=1,

            highlightthickness=1,

            highlightbackground="#cbd5e1",

            highlightcolor="#1d4ed8",

            width=16,

        )

        qty_entry.pack(anchor="w", pady=(6, 0), ipady=6)

        qty_entry.focus_set()
 
        def confirm_restock():

            raw = qty_entry.get().strip()

            try:

                units_received = int(raw)

                if units_received <= 0:

                    raise ValueError

            except ValueError:

                messagebox.showerror(

                    "Invalid Input",

                    "Units received must be a positive whole number.",

                    parent=dialog,

                )

                return
 
            self.products[restock_index]["quantity"] += units_received

            new_qty = self.products[restock_index]["quantity"]
 
            self.refresh_table()

            self.update_summary()

            dialog.destroy()
 
            self.status_label.config(

                text=f"Restocked {units_received} unit(s) of {product['name']} — {new_qty} in stock"

            )
 
        btn_frame = tk.Frame(dialog, bg="white")

        btn_frame.pack(fill="x", padx=20, pady=(16, 0))
 
        tk.Button(

            btn_frame,

            text="Confirm Restock",

            font=("Segoe UI", 10, "bold"),

            bg="#1d4ed8",

            fg="white",

            activebackground="#1e3a8a",

            activeforeground="white",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=14,

            pady=8,

            command=confirm_restock,

        ).pack(side="left")
 
        tk.Button(

            btn_frame,

            text="Cancel",

            font=("Segoe UI", 10),

            bg="#eef2f7",

            fg="#1f2937",

            activebackground="#e5e7eb",

            activeforeground="#111827",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=14,

            pady=8,

            command=dialog.destroy,

        ).pack(side="left", padx=(10, 0))
 
        dialog.bind("<Return>", lambda e: confirm_restock())
 
    # ── Sell ──────────────────────────────────────────────────────────────────
 
    def sell_stock_dialog(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(

                "No Selection",

                "Please select a product row in the table before recording a sale.",

            )

            return
 
        all_items = self.tree.get_children()

        sell_index = list(all_items).index(selected[0])

        product = self.products[sell_index]
 
        if product["quantity"] == 0:

            messagebox.showwarning(

                "Out of Stock",

                f'"{product["name"]}" is already out of stock and cannot be sold.',

            )

            return
 
        dialog = tk.Toplevel(self.root)

        dialog.title("Record Sale")

        dialog.geometry("360x260")

        dialog.resizable(False, False)

        dialog.configure(bg="white")

        dialog.grab_set()
 
        self.root.update_idletasks()

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 180

        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 130

        dialog.geometry(f"+{x}+{y}")
 
        dialog_header = tk.Frame(dialog, bg="#15803d", height=48)

        dialog_header.pack(fill="x")

        dialog_header.pack_propagate(False)

        tk.Label(

            dialog_header,

            text="Record Sale",

            font=("Segoe UI", 13, "bold"),

            bg="#15803d",

            fg="white",

        ).pack(side="left", padx=16, pady=12)
 
        info_frame = tk.Frame(dialog, bg="white")

        info_frame.pack(fill="x", padx=20, pady=(16, 0))
 
        tk.Label(

            info_frame,

            text=f"Product:  {product['name']}",

            font=("Segoe UI", 10, "bold"),

            bg="white",

            fg="#1f2937",

        ).pack(anchor="w")
 
        tk.Label(

            info_frame,

            text=f"Current Stock:  {product['quantity']} units",

            font=("Segoe UI", 10),

            bg="white",

            fg="#6b7280",

        ).pack(anchor="w", pady=(4, 0))
 
        entry_frame = tk.Frame(dialog, bg="white")

        entry_frame.pack(fill="x", padx=20, pady=(14, 0))
 
        tk.Label(

            entry_frame,

            text="Units Sold",

            font=("Segoe UI", 10, "bold"),

            bg="white",

            fg="#374151",

        ).pack(anchor="w")
 
        qty_entry = tk.Entry(

            entry_frame,

            font=("Segoe UI", 11),

            bg="white",

            fg="#111827",

            relief="solid",

            bd=1,

            highlightthickness=1,

            highlightbackground="#cbd5e1",

            highlightcolor="#15803d",

            width=16,

        )

        qty_entry.pack(anchor="w", pady=(6, 0), ipady=6)

        qty_entry.focus_set()
 
        def confirm_sale():

            raw = qty_entry.get().strip()

            try:

                units_sold = int(raw)

                if units_sold <= 0:

                    raise ValueError

            except ValueError:

                messagebox.showerror(

                    "Invalid Input",

                    "Units sold must be a positive whole number.",

                    parent=dialog,

                )

                return
 
            if units_sold > product["quantity"]:

                messagebox.showwarning(

                    "Insufficient Stock",

                    f'Only {product["quantity"]} unit(s) of "{product["name"]}" '

                    f"are in stock.\nYou cannot sell {units_sold} unit(s).",

                    parent=dialog,

                )

                return
 
            self.products[sell_index]["quantity"] -= units_sold

            new_qty = self.products[sell_index]["quantity"]
 
            self.refresh_table()

            self.update_summary()

            dialog.destroy()
 
            if new_qty == 0:

                messagebox.showinfo(

                    "Out of Stock",

                    f'"{product["name"]}" is now out of stock.',

                )

                self.status_label.config(text=f"Out of stock: {product['name']}")

            else:

                self.status_label.config(

                    text=f"Sold {units_sold} unit(s) of {product['name']} — {new_qty} remaining"

                )
 
        btn_frame = tk.Frame(dialog, bg="white")

        btn_frame.pack(fill="x", padx=20, pady=(16, 0))
 
        tk.Button(

            btn_frame,

            text="Confirm Sale",

            font=("Segoe UI", 10, "bold"),

            bg="#15803d",

            fg="white",

            activebackground="#14532d",

            activeforeground="white",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=14,

            pady=8,

            command=confirm_sale,

        ).pack(side="left")
 
        tk.Button(

            btn_frame,

            text="Cancel",

            font=("Segoe UI", 10),

            bg="#eef2f7",

            fg="#1f2937",

            activebackground="#e5e7eb",

            activeforeground="#111827",

            relief="flat",

            bd=0,

            cursor="hand2",

            padx=14,

            pady=8,

            command=dialog.destroy,

        ).pack(side="left", padx=(10, 0))
 
        dialog.bind("<Return>", lambda e: confirm_sale())
 
    # ── Depletion report ─────────────────────────────────────────────────────────

    def report_depletion_dialog(self):
        """
        Opens a modal dialog for the employee to enter the number of depletion
        units and a reason. Deducts from stock and logs the entry.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a product row in the table before reporting depletion.",
            )
            return

        all_items   = self.tree.get_children()
        dmg_index   = list(all_items).index(selected[0])
        product     = self.products[dmg_index]

        if product["quantity"] == 0:
            messagebox.showwarning(
                "No Stock",
                f'"{product["name"]}" has no stock to report as depleted.',
            )
            return

        # Build dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Report depletion Items")
        dialog.geometry("380x320")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.grab_set()

        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - 190
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 160
        dialog.geometry(f"+{x}+{y}")

        # Header
        hdr = tk.Frame(dialog, bg="#854d0e", height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr,
            text="⚠  Report depletion Items",
            font=("Segoe UI", 12, "bold"),
            bg="#854d0e",
            fg="white",
        ).pack(side="left", padx=16, pady=12)

        # Product info
        info = tk.Frame(dialog, bg="white")
        info.pack(fill="x", padx=20, pady=(14, 0))
        tk.Label(
            info, text=f"Product:  {product['name']}",
            font=("Segoe UI", 10, "bold"), bg="white", fg="#1f2937",
        ).pack(anchor="w")
        tk.Label(
            info, text=f"Current Stock:  {product['quantity']} units",
            font=("Segoe UI", 10), bg="white", fg="#6b7280",
        ).pack(anchor="w", pady=(4, 0))

        # Units depletion
        ef = tk.Frame(dialog, bg="white")
        ef.pack(fill="x", padx=20, pady=(12, 0))
        tk.Label(
            ef, text="Units depletion",
            font=("Segoe UI", 10, "bold"), bg="white", fg="#374151",
        ).pack(anchor="w")
        qty_entry = tk.Entry(
            ef, font=("Segoe UI", 11), bg="white", fg="#111827",
            relief="solid", bd=1, highlightthickness=1,
            highlightbackground="#cbd5e1", highlightcolor="#854d0e", width=16,
        )
        qty_entry.pack(anchor="w", pady=(6, 0), ipady=6)
        qty_entry.focus_set()

        # Reason
        rf = tk.Frame(dialog, bg="white")
        rf.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(
            rf, text="Reason",
            font=("Segoe UI", 10, "bold"), bg="white", fg="#374151",
        ).pack(anchor="w")
        reason_entry = tk.Entry(
            rf, font=("Segoe UI", 11), bg="white", fg="#111827",
            relief="solid", bd=1, highlightthickness=1,
            highlightbackground="#cbd5e1", highlightcolor="#854d0e",
        )
        reason_entry.pack(fill="x", pady=(6, 0), ipady=6)

        def confirm_depletion():
            # Validate quantity
            raw = qty_entry.get().strip()
            try:
                units_depletion = int(raw)
                if units_depletion <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Units depletion must be a positive whole number.",
                    parent=dialog,
                )
                return

            if units_depletion > product["quantity"]:
                messagebox.showwarning(
                    "Exceeds Stock",
                    f'Only {product["quantity"]} unit(s) available. '
                    f'Cannot report {units_depletion} depletion unit(s).',
                    parent=dialog,
                )
                return

            reason = reason_entry.get().strip() or "No reason provided"

            # Deduct from stock
            self.products[dmg_index]["quantity"] -= units_depletion
            new_qty = self.products[dmg_index]["quantity"]

            # Log the depletion report
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.depletion_log.append({
                "timestamp": timestamp,
                "product":   product["name"],
                "category":  product["category"],
                "qty":       units_depletion,
                "reason":    reason,
            })

            self.refresh_table()
            self.update_summary()
            self._refresh_depletion_tree()
            dialog.destroy()

            self.status_label.config(
                text=f"Depletion reported: {units_depletion} unit(s) of {product['name']} — {new_qty} remaining"
            )

        # Buttons
        bf = tk.Frame(dialog, bg="white")
        bf.pack(fill="x", padx=20, pady=(14, 0))
        tk.Button(
            bf, text="Submit Report",
            font=("Segoe UI", 10, "bold"),
            bg="#854d0e", fg="white",
            activebackground="#713f12", activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            padx=14, pady=8, command=confirm_depletion,
        ).pack(side="left")
        tk.Button(
            bf, text="Cancel",
            font=("Segoe UI", 10),
            bg="#eef2f7", fg="#1f2937",
            activebackground="#e5e7eb", activeforeground="#111827",
            relief="flat", bd=0, cursor="hand2",
            padx=14, pady=8, command=dialog.destroy,
        ).pack(side="left", padx=(10, 0))
        dialog.bind("<Return>", lambda e: confirm_depletion())

    def toggle_depletion_log(self):
        """Show or hide the depletion log panel below the table card."""
        self.depletion_panel_visible = not self.depletion_panel_visible
        if self.depletion_panel_visible:
            self.depletion_panel.pack(fill="x", pady=(8, 0))
            self.depletion_text_btn.config(text="Depletion  ▴")
        else:
            self.depletion_panel.pack_forget()
            self.depletion_text_btn.config(text="Depletion  ▾")

    def _refresh_depletion_tree(self):
        """Repopulate the depletion log Treeview from self.depletion_log."""
        for row in self.depletion_tree.get_children():
            self.depletion_tree.delete(row)
        for entry in reversed(self.depletion_log):   # most recent first
            self.depletion_tree.insert(
                "", "end",
                values=(
                    entry["timestamp"],
                    entry["product"],
                    entry["category"],
                    entry["qty"],
                    entry["reason"],
                ),
            )
        # Update the summary card depletion count
        total_depletion = sum(e["qty"] for e in self.depletion_log)
        if hasattr(self, "depletion_count_label"):
            self.depletion_count_label.config(text=str(total_depletion))

    # ── UI mode helpers ───────────────────────────────────────────────────────

    def _apply_edit_mode_ui(self):

        self.status_label.config(text="Edit mode — modify fields and click Save Changes")

        self.form_title_label.config(text="Edit Product", fg="#b45309")

        self.form_description_label.config(

            text="Modify the fields below and click Save Changes."

        )

        self.primary_button.config(

            text="Save Changes",

            bg="#d97706",

            activebackground="#b45309",

        )

        self.secondary_button.config(text="Cancel Edit")

        self.form_card.config(highlightbackground="#fcd34d")
 
    def _exit_edit_mode(self):

        self.edit_mode = False

        self.edit_index = None

        self.clear_fields()
 
        self.status_label.config(text="")

        self.form_title_label.config(text="Product Information", fg="#1f2937")

        self.form_description_label.config(

            text="Fill in the fields below to add a new product."

        )

        self.primary_button.config(

            text="Add Product",

            bg="#2563eb",

            activebackground="#1d4ed8",

        )

        self.secondary_button.config(text="Clear Fields")

        self.form_card.config(highlightbackground="#dbe3f0")
 
    # ── Shared button handlers ────────────────────────────────────────────────
 
    def handle_primary_action(self):

        if self.edit_mode:

            self.save_edited_product()

        else:

            self.add_product()
 
    def handle_secondary_action(self):

        if self.edit_mode:

            self.cancel_edit()

        else:

            self.clear_fields()
 
    # ── Field helpers ─────────────────────────────────────────────────────────
 
    def _read_fields(self):

        name = self.name_entry.get().strip()

        category = self.category_entry.get().strip()

        price = self.price_entry.get().strip()

        quantity = self.quantity_entry.get().strip()
 
        if not name or not category or not price or not quantity:

            messagebox.showwarning("Missing Information", "Please complete all fields.")

            return None, None, None, None
 
        try:

            price_value = float(price)

            quantity_value = int(quantity)

            if price_value < 0 or quantity_value < 0:

                messagebox.showwarning(

                    "Invalid Values", "Price and quantity must be positive."

                )

                return None, None, None, None

        except ValueError:

            messagebox.showerror(

                "Invalid Input",

                "Price must be numeric and quantity must be an integer.",

            )

            return None, None, None, None
 
        return name, category, price_value, quantity_value
 
    def _set_field(self, entry, value):

        entry.delete(0, tk.END)

        entry.insert(0, value)
 
    # ── Table helpers ─────────────────────────────────────────────────────────
 
    def refresh_table(self):
        """Repopulate the Treeview, respecting any active search filter."""
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""

        for row in self.tree.get_children():
            self.tree.delete(row)

        matched = 0
        for product in self.products:
            # Match against name OR category (case-insensitive)
            if query and query not in product["name"].lower() and query not in product["category"].lower():
                continue
            # Determine row tag based on stock level
            qty = product["quantity"]
            threshold = self.low_stock_threshold if hasattr(self, "low_stock_threshold") else 5
            if qty == 0:
                tag = ("out_of_stock",)
            elif qty <= threshold:
                tag = ("low_stock",)
            else:
                tag = ()

            self.tree.insert(
                "",
                "end",
                values=(
                    product["name"],
                    product["category"],
                    f"${product['price']:.2f}",
                    product["quantity"],
                ),
                tags=tag,
            )
            matched += 1

        # Update the results count label if it exists
        if hasattr(self, "search_results_label"):
            if query:
                self.search_results_label.config(
                    text=f"{matched} of {len(self.products)} product(s) found"
                )
            else:
                self.search_results_label.config(text="")
 
    def apply_search_filter(self):
        """Called automatically whenever the search field changes."""
        self.refresh_table()

    def _clear_search(self):
        """Clear the search field and restore the full product list."""
        self.search_var.set("")
        self.search_entry.focus_set()

    def update_summary(self):

        self.total_products_label.config(text=str(len(self.products)))

        # Count products at or below the low-stock threshold (including out of stock)
        if hasattr(self, "low_stock_threshold") and hasattr(self, "low_stock_count_label"):
            low_count = sum(
                1 for p in self.products if p["quantity"] <= self.low_stock_threshold
            )
            self.low_stock_count_label.config(
                text=str(low_count),
                fg="#b45309" if low_count == 0 else "#b45309",
            )
 
    def clear_fields(self):

        self.name_entry.delete(0, tk.END)

        self.category_entry.delete(0, tk.END)

        self.price_entry.delete(0, tk.END)

        self.quantity_entry.delete(0, tk.END)
 
 
if __name__ == "__main__":

    root = tk.Tk()

    app = InventoryApp(root)

    root.mainloop()