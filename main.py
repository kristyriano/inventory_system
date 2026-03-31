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
        # Header
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

        subtitle = tk.Label(
            header,
            text="Add New Products",
            font=("Segoe UI", 11),
            bg="#1e3a8a",
            fg="#dbeafe",
        )
        subtitle.pack(side="right", padx=30, pady=28)

        # Main area
        main_container = tk.Frame(self.root, bg="#f3f6fb")
        main_container.pack(fill="both", expand=True, padx=24, pady=24)

        # Left card - form
        form_card = tk.Frame(
            main_container,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#dbe3f0",
        )
        form_card.pack(side="left", fill="y", padx=(0, 18))

        form_title = tk.Label(
            form_card,
            text="Product Information",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#1f2937",
        )
        form_title.pack(anchor="w", padx=24, pady=(24, 8))

        form_description = tk.Label(
            form_card,
            text="Fill in the fields below to add a new product.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#6b7280",
        )
        form_description.pack(anchor="w", padx=24, pady=(0, 18))

        self.name_entry = self.create_labeled_input(form_card, "Product Name")
        self.category_entry = self.create_labeled_input(form_card, "Category")
        self.price_entry = self.create_labeled_input(form_card, "Price")
        self.quantity_entry = self.create_labeled_input(form_card, "Quantity")

        add_button = tk.Button(
            form_card,
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
            command=self.add_product,
        )
        add_button.pack(fill="x", padx=24, pady=(14, 10))

        clear_button = tk.Button(
            form_card,
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
            command=self.clear_fields,
        )
        clear_button.pack(fill="x", padx=24, pady=(0, 24))

        # Right side
        right_section = tk.Frame(main_container, bg="#f3f6fb")
        right_section.pack(side="right", fill="both", expand=True)

        # Top summary card
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
            table_header, text="Ready", font=("Segoe UI", 10), bg="white", fg="#6b7280"
        )
        self.status_label.pack(side="right")

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

        self.tree.column("name", width=220, anchor="center")
        self.tree.column("category", width=180, anchor="center")
        self.tree.column("price", width=120, anchor="center")
        self.tree.column("quantity", width=120, anchor="center")

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

    def add_product(self):
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not name or not category or not price or not quantity:
            messagebox.showwarning("Missing Information", "Please complete all fields.")
            return

        try:
            price_value = float(price)
            quantity_value = int(quantity)

            if price_value < 0 or quantity_value < 0:
                messagebox.showwarning(
                    "Invalid Values", "Price and quantity must be positive."
                )
                return

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Price must be numeric and quantity must be an integer.",
            )
            return

        product = {
            "name": name,
            "category": category,
            "price": price_value,
            "quantity": quantity_value,
        }

        self.products.append(product)
        self.refresh_table()
        self.update_summary()
        self.clear_fields()
        self.status_label.config(text=f"Added: {name}")

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
