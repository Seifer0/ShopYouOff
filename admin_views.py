"""
admin_views.py - Admin dashboard: stats, product management, order management
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import database as db
import theme as t


class AdminView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        sidebar = tk.Frame(self, bg=t.COLORS["surface"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="⚙️ Admin",
                 font=t.FONTS["h3"],
                 bg=t.COLORS["surface"], fg=t.COLORS["accent"],
                 pady=20).pack(fill="x")
        t.separator(sidebar).pack(fill="x")

        self._tab_btns = {}
        tabs = [
            ("dashboard", "📊  Dashboard"),
            ("products",  "📦  Products"),
            ("orders",    "🚚  Orders"),
        ]
        for key, label in tabs:
            btn = tk.Button(
                sidebar, text=label,
                font=t.FONTS["body"],
                bg=t.COLORS["surface"], fg=t.COLORS["text2"],
                activebackground=t.COLORS["surface2"],
                activeforeground=t.COLORS["text"],
                relief="flat", bd=0,
                padx=16, pady=12,
                anchor="w", cursor="hand2",
                command=lambda k=key: self._switch_tab(k),
            )
            btn.pack(fill="x")
            self._tab_btns[key] = btn

        self._main = tk.Frame(self, bg=t.COLORS["bg"])
        self._main.pack(side="right", fill="both", expand=True)

        self._switch_tab("dashboard")

    def _switch_tab(self, key):
        for k, b in self._tab_btns.items():
            b.config(bg=t.COLORS["accent"] if k == key else t.COLORS["surface"],
                     fg=t.COLORS["white"] if k == key else t.COLORS["text2"])
        for w in self._main.winfo_children():
            w.destroy()
        if key == "dashboard":
            self._build_dashboard()
        elif key == "products":
            self._build_products()
        elif key == "orders":
            self._build_orders()

    # ── Dashboard ─────────────────────────────────────────────────────────────

    def _build_dashboard(self):
        outer, inner, _ = t.scrollable_frame(self._main)
        outer.pack(fill="both", expand=True)
        content = tk.Frame(inner, bg=t.COLORS["bg"], padx=24, pady=20)
        content.pack(fill="both", expand=True)

        t.label(content, "Dashboard Overview", "h2").pack(anchor="w", pady=(0, 20))

        stats = db.admin_get_stats()
        stat_items = [
            ("💰 Revenue",   f"${stats['revenue']:,.2f}", t.COLORS["success"]),
            ("📦 Orders",    str(stats["orders"]),        t.COLORS["accent"]),
            ("👥 Customers", str(stats["users"]),         t.COLORS["accent2"]),
            ("🛍️ Products", str(stats["products"]),      t.COLORS["warning"]),
        ]

        cards_row = tk.Frame(content, bg=t.COLORS["bg"])
        cards_row.pack(fill="x", pady=(0, 24))
        for title, value, color in stat_items:
            card = tk.Frame(cards_row, bg=t.COLORS["surface"],
                            highlightbackground=color, highlightthickness=2,
                            padx=20, pady=16)
            card.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(card, text=value, font=("Segoe UI", 24, "bold"),
                     fg=color, bg=t.COLORS["surface"]).pack(anchor="w")
            t.label(card, title, "body", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w")

        t.label(content, "Recent Orders", "h3").pack(anchor="w", pady=(0, 10))
        self._draw_orders_table(content, db.admin_get_all_orders()[:10])

    # ── Products ──────────────────────────────────────────────────────────────

    def _build_products(self):
        header = tk.Frame(self._main, bg=t.COLORS["surface"], pady=12, padx=16)
        header.pack(fill="x")
        t.label(header, "📦  Product Management", "h3", bg=t.COLORS["surface"]).pack(side="left")
        t.StyledButton(header, "+ Add Product", self._add_product_dialog,
                       "primary", font_key="btn_sm").pack(side="right")

        outer, inner, _ = t.scrollable_frame(self._main)
        outer.pack(fill="both", expand=True, padx=16, pady=12)

        products = db.get_products()
        if not products:
            t.label(inner, "No products yet.", "h3", t.COLORS["text3"]).pack(pady=40)
            return

        hrow = tk.Frame(inner, bg=t.COLORS["surface2"], pady=8)
        hrow.pack(fill="x", pady=(0, 4))
        for text, w in [("", 4), ("Product", 30), ("Price", 10), ("Stock", 8), ("Actions", 20)]:
            tk.Label(hrow, text=text, font=t.FONTS["h4"],
                     fg=t.COLORS["text2"], bg=t.COLORS["surface2"],
                     width=w, anchor="w").pack(side="left", padx=4)

        for prod in products:
            row = tk.Frame(inner, bg=t.COLORS["surface"],
                           highlightbackground=t.COLORS["border"],
                           highlightthickness=1)
            row.pack(fill="x", pady=3)

            admin_img = t.product_image_widget(row, prod, (40, 40), t.COLORS["surface"])
            admin_img.pack(side="left", padx=8, pady=8)

            info = tk.Frame(row, bg=t.COLORS["surface"])
            info.pack(side="left", fill="y", pady=8, expand=True)
            t.label(info, prod["name"], "h4", bg=t.COLORS["surface"]).pack(anchor="w")
            t.label(info, prod.get("category_name", "—"), "caption",
                    t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w")

            t.label(row, f"${prod['price']:.2f}", "body",
                    t.COLORS["accent"], bg=t.COLORS["surface"]).pack(side="left", padx=16)

            sc = t.COLORS["success"] if prod["stock"] > 5 else (
                 t.COLORS["warning"] if prod["stock"] > 0 else t.COLORS["danger"])
            t.label(row, str(prod["stock"]), "body", sc,
                    bg=t.COLORS["surface"]).pack(side="left", padx=16)

            btns = tk.Frame(row, bg=t.COLORS["surface"])
            btns.pack(side="right", padx=12, pady=8)
            t.StyledButton(btns, "Edit",
                           lambda pid=prod["id"]: self._edit_product_dialog(pid),
                           "ghost", font_key="btn_sm", padx=10, pady=4).pack(side="left", padx=2)
            t.StyledButton(btns, "Delete",
                           lambda pid=prod["id"]: self._delete_product(pid),
                           "danger", font_key="btn_sm", padx=10, pady=4).pack(side="left", padx=2)

    def _product_form_dialog(self, title, defaults=None):
        """Opens a Toplevel form; returns dict of values or None if cancelled."""
        d = defaults or {}
        win = tk.Toplevel()
        win.title(title)
        win.configure(bg=t.COLORS["bg"])
        win.geometry("480x560")
        win.grab_set()

        t.label(win, title, "h3").pack(pady=(20, 10))
        t.separator(win).pack(fill="x", padx=20)

        form = tk.Frame(win, bg=t.COLORS["bg"], padx=30, pady=16)
        form.pack(fill="both", expand=True)

        vars_ = {}
        fields = [
            ("Name",        "name",        False),
            ("Description", "description", False),
            ("Price",       "price",       False),
            ("Stock",       "stock",       False),
            ("Emoji (shown if no image is set in code)", "image_emoji", False),
        ]
        for lbl, key, _ in fields:
            t.label(form, lbl, "body_sm", t.COLORS["text2"]).pack(anchor="w")
            v = tk.StringVar(value=str(d.get(key, "")))
            e = tk.Entry(form, textvariable=v, font=t.FONTS["body"],
                         bg=t.COLORS["surface2"], fg=t.COLORS["text"],
                         insertbackground=t.COLORS["text"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=t.COLORS["border"],
                         highlightcolor=t.COLORS["accent"], width=40)
            e.pack(pady=(4, 12), ipady=6)
            vars_[key] = v

        # Category dropdown
        t.label(form, "Category", "body_sm", t.COLORS["text2"]).pack(anchor="w")
        cats = db.get_categories()
        cat_names = [c["name"] for c in cats]
        cat_ids   = [c["id"]   for c in cats]
        cat_var = tk.StringVar()
        current_cat_id = d.get("category_id")
        if current_cat_id and current_cat_id in cat_ids:
            cat_var.set(cat_names[cat_ids.index(current_cat_id)])
        elif cat_names:
            cat_var.set(cat_names[0])
        cb = ttk.Combobox(form, textvariable=cat_var,
                          values=cat_names, state="readonly", width=38)
        cb.pack(pady=(4, 16), ipady=4)

        result = {}

        def on_save():
            try:
                price = float(vars_["price"].get())
                stock = int(vars_["stock"].get())
            except ValueError:
                messagebox.showwarning("Input Error", "Price must be a number, Stock must be an integer.", parent=win)
                return
            cat_name = cat_var.get()
            cat_id = cat_ids[cat_names.index(cat_name)] if cat_name in cat_names else None
            result.update({
                "name":        vars_["name"].get().strip(),
                "description": vars_["description"].get().strip(),
                "price":       price,
                "stock":       stock,
                "image_emoji": vars_["image_emoji"].get().strip() or "🛍️",
                "category_id": cat_id,
            })
            win.destroy()

        def on_cancel():
            win.destroy()

        btn_row = tk.Frame(win, bg=t.COLORS["bg"])
        btn_row.pack(pady=(0, 20))
        t.StyledButton(btn_row, "Save", on_save, "primary").pack(side="left", padx=8)
        t.StyledButton(btn_row, "Cancel", on_cancel, "ghost").pack(side="left", padx=8)

        win.wait_window()
        return result if result else None

    def _add_product_dialog(self):
        data = self._product_form_dialog("Add New Product")
        if data:
            db.admin_add_product(data["name"], data["description"],
                                 data["price"], data["stock"],
                                 data["category_id"], data["image_emoji"])
            t.toast(self.app.root, "Product added ✓", "success")
            self._switch_tab("products")

    def _edit_product_dialog(self, product_id):
        prod = db.get_product(product_id)
        if not prod:
            return
        data = self._product_form_dialog("Edit Product", prod)
        if data:
            db.admin_update_product(product_id, data["name"], data["description"],
                                    data["price"], data["stock"],
                                    data["category_id"], data["image_emoji"])
            t.toast(self.app.root, "Product updated ✓", "success")
            self._switch_tab("products")

    def _delete_product(self, product_id):
        prod = db.get_product(product_id)
        if prod and messagebox.askyesno("Confirm Delete",
                                        f"Delete '{prod['name']}'? This cannot be undone."):
            db.admin_delete_product(product_id)
            t.toast(self.app.root, "Product deleted", "warning")
            self._switch_tab("products")

    # ── Orders ────────────────────────────────────────────────────────────────

    def _build_orders(self):
        header = tk.Frame(self._main, bg=t.COLORS["surface"], pady=12, padx=16)
        header.pack(fill="x")
        t.label(header, "🚚  Order Management", "h3", bg=t.COLORS["surface"]).pack(side="left")

        outer, inner, _ = t.scrollable_frame(self._main)
        outer.pack(fill="both", expand=True, padx=16, pady=12)
        self._draw_orders_table(inner, db.admin_get_all_orders(), show_actions=True)

    def _draw_orders_table(self, parent, orders, show_actions=False):
        STATUS_COLOR = {
            "pending":    t.COLORS["warning"],
            "processing": t.COLORS["accent"],
            "shipped":    t.COLORS["success"],
            "delivered":  "#22C55E",
            "cancelled":  t.COLORS["danger"],
        }
        STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]

        if not orders:
            t.label(parent, "No orders found.", "body", t.COLORS["text3"]).pack(pady=20)
            return

        hrow = tk.Frame(parent, bg=t.COLORS["surface2"], pady=8)
        hrow.pack(fill="x")
        headers = ["ID", "Customer", "Total", "Status", "Date"]
        widths   = [6,    18,         10,       12,        16]
        if show_actions:
            headers.append("Change Status")
            widths.append(20)
        for h, w in zip(headers, widths):
            tk.Label(hrow, text=h, font=t.FONTS["h4"],
                     fg=t.COLORS["text2"], bg=t.COLORS["surface2"],
                     width=w, anchor="w").pack(side="left", padx=4)

        for o in orders:
            row = tk.Frame(parent, bg=t.COLORS["surface"],
                           highlightbackground=t.COLORS["border"],
                           highlightthickness=1)
            row.pack(fill="x", pady=3)

            sc = STATUS_COLOR.get(o["status"], t.COLORS["text2"])
            for val, w in zip(
                [f"#{o['id']}", o.get("username", "—"), f"${o['total']:.2f}",
                 o["status"].upper(), o["created_at"][:16]],
                [6, 18, 10, 12, 16]
            ):
                color = sc if val == o["status"].upper() else t.COLORS["text"]
                tk.Label(row, text=val, font=t.FONTS["body"],
                         fg=color, bg=t.COLORS["surface"],
                         width=w, anchor="w").pack(side="left", padx=4, pady=8)

            if show_actions:
                sv = tk.StringVar(value=o["status"])
                cb = ttk.Combobox(row, textvariable=sv, values=STATUSES,
                                  state="readonly", width=14)
                cb.pack(side="left", padx=4)

                def make_updater(oid, svar):
                    def _update(_=None):
                        db.admin_update_order_status(oid, svar.get())
                        t.toast(self.app.root, f"Order #{oid} → {svar.get()}", "info")
                    return _update

                cb.bind("<<ComboboxSelected>>", make_updater(o["id"], sv))