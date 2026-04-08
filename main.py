import tkinter as tk
from tkinter import ttk, messagebox


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1100x680")
        self.root.configure(bg="#f3f6fb")
        self.root.resizable(False, False)

        self.products = []

        # --- EDIT STATE ---
        # Tracks whether we are in "edit mode" and which product index is being edited.
        self.edit_mode = False
        self.edit_index = None

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
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview.Heading",
            background="#e8eef9",
            foreground="#1e3a8a",
            font=("Segoe UI", 10, "bold"),
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
            text="Inventory Management System",
            font=("Segoe UI", 22, "bold"),
            bg="#1e3a8a",
            fg="white",
        )
        title.pack(side="left", padx=30, pady=20)

        # Subtitle label is stored so we can update it during edit mode
        self.subtitle_label = tk.Label(
            header,
            text="Add New Products",
            font=("Segoe UI", 11),
            bg="#1e3a8a",
            fg="#dbeafe",
        )
        self.subtitle_label.pack(side="right", padx=30, pady=28)

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
            font=("Segoe UI", 10),
            bg="white",
            fg="#6b7280",
        )
        self.form_description_label.pack(anchor="w", padx=24, pady=(0, 18))

        self.name_entry     = self.create_labeled_input(self.form_card, "Product Name")
        self.category_entry = self.create_labeled_input(self.form_card, "Category")
        self.price_entry    = self.create_labeled_input(self.form_card, "Price")
        self.quantity_entry = self.create_labeled_input(self.form_card, "Quantity")

        # Primary action button – label/command change between Add and Save modes
        self.primary_button = tk.Button(
            self.form_card,
            text="Add Product",
            font=("Segoe UI", 11, "bold"),
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

        # Clear / Cancel button – label changes in edit mode
        self.secondary_button = tk.Button(
            self.form_card,
            text="Clear Fields",
            font=("Segoe UI", 10),
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
            font=("Segoe UI", 11),
            bg="white",
            fg="#4b5563",
        )
        summary_text.pack(side="left", pady=28)

        # Table card
        table_card = tk.Frame(
            right_section,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#dbe3f0",
        )
        table_card.pack(fill="both", expand=True)

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

        self.status_label = tk.Label(
            table_header,
            text="Ready",
            font=("Segoe UI", 10),
            bg="white",
            fg="#6b7280",
        )
        self.status_label.pack(side="right")

        self.edit_button = tk.Button(
            table_header,
            text="✏  Edit Selected",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f6ff",
            fg="#1e3a8a",
            activebackground="#dbeafe",
            activeforeground="#1e3a8a",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            highlightthickness=1,
            highlightbackground="#bfdbfe",
            command=self.load_selected_for_edit,
        )
        self.edit_button.pack(side="right", padx=(0, 12))

        # Restock / increase stock button
        self.restock_button = tk.Button(
            table_header,
            text="📦  Restock Selected",
            font=("Segoe UI", 10, "bold"),
            bg="#eff6ff",
            fg="#1d4ed8",
            activebackground="#dbeafe",
            activeforeground="#1e3a8a",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            highlightthickness=1,
            highlightbackground="#93c5fd",
            command=self.restock_stock_dialog,
        )
        self.restock_button.pack(side="right", padx=(0, 8))

        # IS-8: Sell / decrease stock button
        self.sell_button = tk.Button(
            table_header,
            text="🛒  Sell Selected",
            font=("Segoe UI", 10, "bold"),
            bg="#f0fdf4",
            fg="#15803d",
            activebackground="#dcfce7",
            activeforeground="#14532d",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            highlightthickness=1,
            highlightbackground="#86efac",
            command=self.sell_stock_dialog,
        )
        self.sell_button.pack(side="right", padx=(0, 8))

        # IS-6: Remove discontinued product button
        self.remove_button = tk.Button(
            table_header,
            text="🗑  Remove Selected",
            font=("Segoe UI", 10, "bold"),
            bg="#fff1f2",
            fg="#be123c",
            activebackground="#ffe4e6",
            activeforeground="#9f1239",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            highlightthickness=1,
            highlightbackground="#fecdd3",
            command=self.remove_selected_product,
        )
        self.remove_button.pack(side="right", padx=(0, 8))

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

        self.tree.heading("name",     text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("price",    text="Price")
        self.tree.heading("quantity", text="Quantity")

        self.tree.column("name",     width=220, anchor="center")
        self.tree.column("category", width=180, anchor="center")
        self.tree.column("price",    width=120, anchor="center")
        self.tree.column("quantity", width=120, anchor="center")



    # ── Helper ───────────────────────────────────────────────────────────────

    def create_labeled_input(self, parent, label_text):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#374151",
        )
        label.pack(anchor="w", padx=24, pady=(0, 6))

        entry = tk.Entry(
            parent,
            font=("Segoe UI", 11),
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

        # ── Duplicate check: match by product name (case-insensitive) ──────
        duplicate_index = next(
            (i for i, p in enumerate(self.products)
             if p["name"].lower() == name.lower()),
            None,
        )

        if duplicate_index is not None:
            # Ask the manager whether to switch to editing the existing product
            confirm = messagebox.askyesno(
                "Product Already Exists",
                f'"{name}" is already in the inventory.\n\n'
                "Would you like to edit the existing product instead?",
            )
            if confirm:
                # Load the existing product into edit mode
                self.edit_index = duplicate_index
                product = self.products[self.edit_index]
                self._set_field(self.name_entry,     product["name"])
                self._set_field(self.category_entry, product["category"])
                self._set_field(self.price_entry,    str(product["price"]))
                self._set_field(self.quantity_entry, str(product["quantity"]))
                self.edit_mode = True
                self._apply_edit_mode_ui()
                self.status_label.config(text=f"Editing existing: {name}")
            # If "No", do nothing — manager can correct the name themselves
            return

        # No duplicate — add as new product
        product = {
            "name":     name,
            "category": category,
            "price":    price,
            "quantity": quantity,
        }

        self.products.append(product)
        self.refresh_table()
        self.update_summary()
        self.clear_fields()
        self.status_label.config(text=f"Added: {name}")

    # ── NEW: Edit / Update logic ──────────────────────────────────────────────

    def load_selected_for_edit(self):
        """
        Reads the currently selected row in the Treeview, pre-fills the form
        fields with that product's data, and switches the UI into edit mode.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a product row in the table before clicking Edit.",
            )
            return

        # Map the Treeview row ID to the index in self.products
        all_items = self.tree.get_children()
        self.edit_index = list(all_items).index(selected[0])
        product = self.products[self.edit_index]

        # Pre-fill form fields with existing values
        self._set_field(self.name_entry,     product["name"])
        self._set_field(self.category_entry, product["category"])
        self._set_field(self.price_entry,    str(product["price"]))
        self._set_field(self.quantity_entry, str(product["quantity"]))

        # Switch UI to edit mode
        self.edit_mode = True
        self._apply_edit_mode_ui()

    def save_edited_product(self):
        """
        Validates the form, updates the product at self.edit_index in
        self.products, refreshes the table, and exits edit mode.
        """
        name, category, price, quantity = self._read_fields()
        if name is None:
            return

        # Update the existing product in-place
        self.products[self.edit_index] = {
            "name":     name,
            "category": category,
            "price":    price,
            "quantity": quantity,
        }

        self.refresh_table()
        self.update_summary()
        self._exit_edit_mode()
        self.status_label.config(text=f"Updated: {name}")

    def cancel_edit(self):
        """Discard any changes in the form and exit edit mode."""
        self._exit_edit_mode()
        self.status_label.config(text="Edit cancelled.")

    # ── IS-6: Remove discontinued product ────────────────────────────────────

    def remove_selected_product(self):
        """
        Removes the selected product from self.products after confirming
        with the manager. If the product being removed is currently loaded
        in edit mode, edit mode is cancelled first to keep state consistent.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a product row in the table before removing.",
            )
            return

        # Resolve the selected row to its index in self.products
        all_items  = self.tree.get_children()
        del_index  = list(all_items).index(selected[0])
        product    = self.products[del_index]

        # Ask for confirmation before permanently deleting
        confirm = messagebox.askyesno(
            "Remove Product",
            f'Are you sure you want to remove "{product["name"]}" from the inventory?\n\n'
            "This action cannot be undone.",
        )
        if not confirm:
            return

        removed_name = product["name"]

        # If this product is currently open in edit mode, exit edit mode first
        if self.edit_mode and self.edit_index == del_index:
            self._exit_edit_mode()

        # Remove from the data list and refresh the UI
        del self.products[del_index]
        self.refresh_table()
        self.update_summary()
        self.status_label.config(text=f"Removed: {removed_name}")


    # ── Restock: Increase stock when new inventory arrives ─────────────────────

    def restock_stock_dialog(self):
        """
        Opens a modal dialog for the manager to enter the number of units
        received for the selected product. Adds the amount to the product's
        quantity so the inventory reflects the newly arrived stock.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a product row in the table before restocking.",
            )
            return

        all_items     = self.tree.get_children()
        restock_index = list(all_items).index(selected[0])
        product       = self.products[restock_index]

        # ── Build the restock dialog ──────────────────────────────────────
        dialog = tk.Toplevel(self.root)
        dialog.title("Restock Product")
        dialog.geometry("360x260")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.grab_set()

        # Center over main window
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - 180
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 130
        dialog.geometry(f"+{x}+{y}")

        # Dialog header bar — indigo to distinguish from the green sell dialog
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

        # Product info (read-only)
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

        # Units received entry
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

        # ── Inner confirm logic ───────────────────────────────────────────
        def confirm_restock():
            raw = qty_entry.get().strip()

            # Validate: must be a positive integer
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

            # Add stock
            self.products[restock_index]["quantity"] += units_received
            new_qty = self.products[restock_index]["quantity"]

            self.refresh_table()
            self.update_summary()
            dialog.destroy()

            self.status_label.config(
                text=f"Restocked {units_received} unit(s) of {product['name']} — {new_qty} in stock"
            )

        # Confirm / Cancel buttons
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

        # Allow Enter key to confirm
        dialog.bind("<Return>", lambda e: confirm_restock())

    # ── IS-8: Decrease stock when items are sold ─────────────────────────────

    def sell_stock_dialog(self):
        """
        Opens a modal dialog for the manager to enter the number of units sold
        for the selected product. Deducts the amount from the product's quantity,
        warns if stock is insufficient, and flags the product as out-of-stock
        if quantity reaches zero.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a product row in the table before recording a sale.",
            )
            return

        all_items   = self.tree.get_children()
        sell_index  = list(all_items).index(selected[0])
        product     = self.products[sell_index]

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
        x = self.root.winfo_x() + (self.root.winfo_width()  // 2) - 180
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


    # ── UI mode helpers ───────────────────────────────────────────────────────

    def _apply_edit_mode_ui(self):
        """Update labels, button text, and colours to signal edit mode."""
        self.subtitle_label.config(text="Editing Product")
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
        self.form_card.config(highlightbackground="#fcd34d")   # amber border

    def _exit_edit_mode(self):
        """Reset the form and all labels back to add-product mode."""
        self.edit_mode  = False
        self.edit_index = None
        self.clear_fields()

        self.subtitle_label.config(text="Add New Products")
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
        self.form_card.config(highlightbackground="#dbe3f0")   # original border

    # ── Shared button handlers ────────────────────────────────────────────────

    def handle_primary_action(self):
        """Routes the primary button to Add or Save depending on mode."""
        if self.edit_mode:
            self.save_edited_product()
        else:
            self.add_product()

    def handle_secondary_action(self):
        """Routes the secondary button to Clear or Cancel depending on mode."""
        if self.edit_mode:
            self.cancel_edit()
        else:
            self.clear_fields()

    # ── Shared field helpers ──────────────────────────────────────────────────

    def _read_fields(self):
        """
        Reads and validates all four form entries.
        Returns (name, category, price_float, qty_int) on success,
        or (None, None, None, None) if validation fails.
        """
        name     = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        price    = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not name or not category or not price or not quantity:
            messagebox.showwarning("Missing Information", "Please complete all fields.")
            return None, None, None, None

        try:
            price_value    = float(price)
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
        """Clears an Entry widget and inserts a new value."""
        entry.delete(0, tk.END)
        entry.insert(0, value)

    # ── Original helpers (unchanged) ─────────────────────────────────────────

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for product in self.products:
            self.tree.insert(
                "",
                "end",
                values=(
                    product["name"],
                    product["category"],
                    f"${product['price']:.2f}",
                    product["quantity"],
                ),
            )

    def update_summary(self):
        self.total_products_label.config(text=str(len(self.products)))

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()