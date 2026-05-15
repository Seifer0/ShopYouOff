"""
shop_views.py - Catalog, Product Detail, Cart, Wishlist, Orders screens
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import database as db
import theme as t


# ── Catalog ───────────────────────────────────────────────────────────────────

class CatalogView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self._category_id = None
        self._search_var = tk.StringVar()
        self._build()

    def _build(self):
        # ── Toolbar ──
        toolbar = tk.Frame(self, bg=t.COLORS["surface"], pady=12, padx=16)
        toolbar.pack(fill="x")

        t.label(toolbar, "🛍️  All Products", "h3", bg=t.COLORS["surface"]).pack(side="left")

        # Search
        search_frame = tk.Frame(toolbar, bg=t.COLORS["surface2"],
                                highlightbackground=t.COLORS["border"],
                                highlightthickness=1)
        search_frame.pack(side="right", padx=(0, 8))

        tk.Label(search_frame, text="🔍", font=t.FONTS["body"],
                 bg=t.COLORS["surface2"], fg=t.COLORS["text2"]).pack(side="left", padx=(8, 2))
        se = tk.Entry(search_frame, textvariable=self._search_var,
                      font=t.FONTS["body"],
                      bg=t.COLORS["surface2"], fg=t.COLORS["text"],
                      insertbackground=t.COLORS["text"],
                      relief="flat", bd=0, width=22)
        se.pack(side="left", ipady=6, pady=4, padx=(0, 8))
        se.bind("<Return>", lambda _: self.refresh())

        t.StyledButton(toolbar, "Search", self.refresh, "primary",
                       font_key="btn_sm", padx=12, pady=6).pack(side="right", padx=4)

        # ── Category bar ──
        cat_bar = tk.Frame(self, bg=t.COLORS["surface"], pady=8)
        cat_bar.pack(fill="x")

        cats = db.get_categories()
        self._cat_btns = {}

        all_btn = tk.Label(cat_bar, text="All",
                           font=t.FONTS["btn_sm"],
                           bg=t.COLORS["accent"], fg=t.COLORS["white"],
                           padx=14, pady=5, cursor="hand2")
        all_btn.pack(side="left", padx=(16, 4))
        all_btn.bind("<Button-1>", lambda _, b=all_btn: self._set_category(None, b))
        self._cat_btns[None] = all_btn

        for cat in cats:
            lbl = tk.Label(
                cat_bar,
                text=f"{cat['icon']} {cat['name']}",
                font=t.FONTS["btn_sm"],
                bg=t.COLORS["surface2"], fg=t.COLORS["text2"],
                padx=12, pady=5, cursor="hand2",
            )
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda _, cid=cat["id"], b=lbl: self._set_category(cid, b))
            self._cat_btns[cat["id"]] = lbl

        # ── Product grid ──
        outer, self._inner, _ = t.scrollable_frame(self)
        outer.pack(fill="both", expand=True, padx=16, pady=12)

        self.refresh()

    def _set_category(self, cat_id, btn):
        # Reset all
        for b in self._cat_btns.values():
            b.config(bg=t.COLORS["surface2"], fg=t.COLORS["text2"])
        btn.config(bg=t.COLORS["accent"], fg=t.COLORS["white"])
        self._category_id = cat_id
        self.refresh()

    def refresh(self):
        for w in self._inner.winfo_children():
            w.destroy()

        products = db.get_products(self._search_var.get(), self._category_id)

        if not products:
            t.label(self._inner, "😔  No products found", "h3", t.COLORS["text3"]).pack(pady=60)
            return

        # Grid: 4 columns
        cols = 4
        for i, prod in enumerate(products):
            row, col = divmod(i, cols)
            card = self._product_card(self._inner, prod)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        for c in range(cols):
            self._inner.columnconfigure(c, weight=1)

    def _product_card(self, parent, prod):
        card = tk.Frame(parent, bg=t.COLORS["surface"],
                        highlightbackground=t.COLORS["border"],
                        highlightthickness=1, cursor="hand2")

        # Image area (URL image or emoji fallback)
        img_frame = tk.Frame(card, bg=t.COLORS["surface2"], height=110)
        img_frame.pack(fill="x")
        img_frame.pack_propagate(False)
        img_lbl = t.product_image_widget(img_frame, prod, (110, 110), t.COLORS["surface2"])
        img_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Wishlist heart button
        wished = db.is_wishlisted(self.app.user["id"], prod["id"])
        heart = tk.Label(img_frame,
                         text="❤️" if wished else "🤍",
                         font=t.FONTS["body"],
                         bg=t.COLORS["surface2"], cursor="hand2")
        heart.place(relx=1.0, rely=0.0, anchor="ne", x=-6, y=6)
        heart.bind("<Button-1>", lambda _, pid=prod["id"], h=heart: self._toggle_wish(pid, h))

        body = tk.Frame(card, bg=t.COLORS["surface"], padx=10, pady=8)
        body.pack(fill="both", expand=True)

        # Category badge
        if prod.get("category_name"):
            t.badge(body, f"{prod.get('category_icon','')} {prod['category_name']}",
                    t.COLORS["text3"], t.COLORS["surface2"]).pack(anchor="w", pady=(0, 4))

        # Name
        name_lbl = tk.Label(body, text=prod["name"],
                             font=t.FONTS["h4"],
                             fg=t.COLORS["text"], bg=t.COLORS["surface"],
                             wraplength=170, justify="left", anchor="w")
        name_lbl.pack(fill="x")

        # Stars
        t.star_rating(body, prod["rating"], t.COLORS["surface"]).pack(anchor="w", pady=(2, 6))

        # Price + Cart
        bottom = tk.Frame(body, bg=t.COLORS["surface"])
        bottom.pack(fill="x", pady=(4, 0))

        tk.Label(bottom, text=f"${prod['price']:.2f}",
                 font=t.FONTS["price"],
                 fg=t.COLORS["accent"], bg=t.COLORS["surface"]).pack(side="left")

        stock_color = t.COLORS["success"] if prod["stock"] > 0 else t.COLORS["danger"]
        stock_txt = f"{'In Stock' if prod['stock'] > 0 else 'Out'}"
        tk.Label(bottom, text=stock_txt, font=t.FONTS["caption"],
                 fg=stock_color, bg=t.COLORS["surface"]).pack(side="right")

        cart_btn = t.StyledButton(body, "🛒  Add to Cart",
                                  lambda pid=prod["id"]: self._add_to_cart(pid),
                                  "primary" if prod["stock"] > 0 else "ghost",
                                  font_key="btn_sm", padx=10, pady=5)
        cart_btn.pack(fill="x", pady=(8, 0))
        if prod["stock"] == 0:
            cart_btn.config(state="disabled")

        # Click card → detail
        for w in [card, img_frame, body, name_lbl]:
            w.bind("<Button-1>", lambda _, pid=prod["id"]: self.app.open_product(pid))

        # Hover effect
        def on_enter(_):
            card.config(highlightbackground=t.COLORS["accent"])
        def on_leave(_):
            card.config(highlightbackground=t.COLORS["border"])
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        return card

    def _add_to_cart(self, product_id):
        db.add_to_cart(self.app.user["id"], product_id)
        self.app.update_cart_badge()
        t.toast(self.app.root, "Added to cart ✓", "success")

    def _toggle_wish(self, product_id, heart_lbl):
        added = db.toggle_wishlist(self.app.user["id"], product_id)
        heart_lbl.config(text="❤️" if added else "🤍")
        t.toast(self.app.root,
                "Added to wishlist ♥" if added else "Removed from wishlist",
                "info")


# ── Product Detail ─────────────────────────────────────────────────────────────

class ProductDetailView(tk.Frame):

    def __init__(self, parent, app, product_id, on_back):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self.on_back = on_back
        self.prod = db.get_product(product_id)
        self._qty_var = tk.IntVar(value=1)
        self._build()

    def _build(self):
        p = self.prod

        # Back bar
        bar = tk.Frame(self, bg=t.COLORS["surface"], pady=10, padx=16)
        bar.pack(fill="x")
        t.StyledButton(bar, "← Back", self.on_back, "ghost",
                       font_key="btn_sm", padx=12, pady=5).pack(side="left")
        t.label(bar, p["name"], "h4", bg=t.COLORS["surface"]).pack(side="left", padx=16)

        outer, inner, _ = t.scrollable_frame(self)
        outer.pack(fill="both", expand=True)

        content = tk.Frame(inner, bg=t.COLORS["bg"], padx=40, pady=30)
        content.pack(fill="both", expand=True)

        # Two-column layout
        left = tk.Frame(content, bg=t.COLORS["bg"], width=340)
        left.pack(side="left", fill="y", padx=(0, 30))
        left.pack_propagate(False)

        # Big emoji image
        img_box = tk.Frame(left, bg=t.COLORS["surface"],
                           highlightbackground=t.COLORS["border"],
                           highlightthickness=1, width=300, height=280)
        img_box.pack(pady=(0, 16))
        img_box.pack_propagate(False)
        detail_img = t.product_image_widget(img_box, p, (280, 260), t.COLORS["surface"])
        detail_img.place(relx=0.5, rely=0.5, anchor="center")

        right = tk.Frame(content, bg=t.COLORS["bg"])
        right.pack(side="left", fill="both", expand=True)

        if p.get("category_name"):
            t.badge(right, f"{p.get('category_icon','')} {p['category_name']}",
                    t.COLORS["text2"], t.COLORS["surface2"]).pack(anchor="w", pady=(0, 8))

        t.label(right, p["name"], "h1").pack(anchor="w")
        t.star_rating(right, p["rating"]).pack(anchor="w", pady=(6, 4))

        t.label(right, f"${p['price']:.2f}", "h2", t.COLORS["accent"]).pack(anchor="w", pady=(8, 4))

        stock_c = t.COLORS["success"] if p["stock"] > 5 else (t.COLORS["warning"] if p["stock"] > 0 else t.COLORS["danger"])
        stock_t = f"✔ In Stock ({p['stock']} available)" if p["stock"] > 0 else "✖ Out of Stock"
        t.label(right, stock_t, "body", stock_c).pack(anchor="w", pady=(0, 16))

        t.separator(right).pack(fill="x", pady=12)

        t.label(right, "Description", "h4").pack(anchor="w", pady=(0, 6))
        t.label(right, p["description"] or "No description available.",
                "body", t.COLORS["text2"], wraplength=500, justify="left").pack(anchor="w")

        t.separator(right).pack(fill="x", pady=16)

        # Quantity + buttons
        qty_row = tk.Frame(right, bg=t.COLORS["bg"])
        qty_row.pack(anchor="w", pady=(0, 16))

        t.label(qty_row, "Qty:", "body").pack(side="left", padx=(0, 10))

        tk.Button(qty_row, text="−", font=t.FONTS["h4"],
                  bg=t.COLORS["surface2"], fg=t.COLORS["text"],
                  relief="flat", bd=0, padx=10, pady=3, cursor="hand2",
                  command=lambda: self._qty_var.set(max(1, self._qty_var.get() - 1))
                  ).pack(side="left")

        tk.Label(qty_row, textvariable=self._qty_var,
                 font=t.FONTS["h4"], bg=t.COLORS["surface2"],
                 fg=t.COLORS["text"], width=3, pady=3).pack(side="left")

        tk.Button(qty_row, text="+", font=t.FONTS["h4"],
                  bg=t.COLORS["surface2"], fg=t.COLORS["text"],
                  relief="flat", bd=0, padx=10, pady=3, cursor="hand2",
                  command=lambda: self._qty_var.set(min(p["stock"], self._qty_var.get() + 1))
                  ).pack(side="left")

        btn_row = tk.Frame(right, bg=t.COLORS["bg"])
        btn_row.pack(anchor="w")

        if p["stock"] > 0:
            t.StyledButton(btn_row, "🛒  Add to Cart", self._add_to_cart, "primary").pack(side="left", padx=(0, 12))
        else:
            t.StyledButton(btn_row, "Out of Stock", None, "ghost").pack(side="left", padx=(0, 12))

        wished = db.is_wishlisted(self.app.user["id"], p["id"])
        self._wish_btn = t.StyledButton(btn_row,
                                        "❤️ Wishlisted" if wished else "🤍 Wishlist",
                                        self._toggle_wish, "accent2")
        self._wish_btn.pack(side="left")

        # ── Comment section ───────────────────────────────────────────────────
        t.separator(inner, thickness=2).pack(fill="x", pady=(24, 0))

        comments_wrapper = tk.Frame(inner, bg=t.COLORS["bg"], padx=40, pady=20)
        comments_wrapper.pack(fill="both", expand=True)

        t.label(comments_wrapper, "💬  Customer Reviews", "h2").pack(anchor="w", pady=(0, 16))

        # ── Write a comment ──
        write_box = tk.Frame(comments_wrapper, bg=t.COLORS["surface"],
                             highlightbackground=t.COLORS["border"],
                             highlightthickness=1)
        write_box.pack(fill="x", pady=(0, 20))

        header_row = tk.Frame(write_box, bg=t.COLORS["surface"], padx=16, pady=12)
        header_row.pack(fill="x")
        t.label(header_row, "Write a Review", "h4", bg=t.COLORS["surface"]).pack(side="left")

        t.separator(write_box).pack(fill="x")

        form_area = tk.Frame(write_box, bg=t.COLORS["surface"], padx=16, pady=12)
        form_area.pack(fill="x")

        # Star picker
        star_row = tk.Frame(form_area, bg=t.COLORS["surface"])
        star_row.pack(anchor="w", pady=(0, 8))
        t.label(star_row, "Rating: ", "body_sm", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(side="left")
        self._comment_rating = tk.IntVar(value=5)
        self._star_btns = []
        for i in range(1, 6):
            sb = tk.Label(star_row, text="★", font=("Segoe UI", 18),
                          fg=t.COLORS["gold"], bg=t.COLORS["surface"],
                          cursor="hand2")
            sb.pack(side="left", padx=1)
            sb.bind("<Button-1>", lambda _, v=i: self._set_star(v))
            sb.bind("<Enter>",    lambda _, v=i: self._hover_star(v))
            sb.bind("<Leave>",    lambda _:      self._hover_star(self._comment_rating.get()))
            self._star_btns.append(sb)
        self._hover_star(5)

        # Text box
        t.label(form_area, "Your comment", "body_sm", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w")
        self._comment_text = tk.Text(
            form_area, height=4, width=60,
            font=t.FONTS["body"],
            bg=t.COLORS["surface2"], fg=t.COLORS["text"],
            insertbackground=t.COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t.COLORS["border"],
            highlightcolor=t.COLORS["accent"],
            wrap="word", padx=8, pady=6,
        )
        self._comment_text.pack(anchor="w", pady=(4, 10))

        t.StyledButton(form_area, "Post Review", self._post_comment, "primary",
                       font_key="btn_sm", padx=14, pady=6).pack(anchor="w")

        # ── Existing comments ──
        self._comments_frame = tk.Frame(comments_wrapper, bg=t.COLORS["bg"])
        self._comments_frame.pack(fill="both", expand=True)
        self._load_comments()

    def _set_star(self, value):
        self._comment_rating.set(value)
        self._hover_star(value)

    def _hover_star(self, value):
        for i, sb in enumerate(self._star_btns):
            sb.config(fg=t.COLORS["gold"] if i < value else t.COLORS["text3"])

    def _post_comment(self):
        text = self._comment_text.get("1.0", "end").strip()
        if not text:
            t.toast(self.app.root, "Please write something first.", "warning")
            return
        db.add_comment(self.app.user["id"], self.prod["id"],
                       text, self._comment_rating.get())
        self._comment_text.delete("1.0", "end")
        self._set_star(5)
        t.toast(self.app.root, "Review posted ✓", "success")
        self._load_comments()

    def _load_comments(self):
        for w in self._comments_frame.winfo_children():
            w.destroy()

        comments = db.get_comments(self.prod["id"])

        if not comments:
            empty = tk.Frame(self._comments_frame, bg=t.COLORS["bg"])
            empty.pack(pady=20)
            t.label(empty, "No reviews yet — be the first!", "body", t.COLORS["text3"]).pack()
            return

        t.label(self._comments_frame,
                f"{len(comments)} Review{'s' if len(comments) != 1 else ''}",
                "h4", t.COLORS["text2"]).pack(anchor="w", pady=(0, 10))

        for c in comments:
            card = tk.Frame(self._comments_frame, bg=t.COLORS["surface"],
                            highlightbackground=t.COLORS["border"],
                            highlightthickness=1)
            card.pack(fill="x", pady=5)

            top = tk.Frame(card, bg=t.COLORS["surface"], padx=14, pady=10)
            top.pack(fill="x")

            # Avatar circle (initials)
            initial = c["full_name"][0].upper() if c.get("full_name") else "?"
            av = tk.Label(top, text=initial,
                          font=("Segoe UI", 12, "bold"),
                          fg=t.COLORS["white"], bg=t.COLORS["accent"],
                          width=3, pady=4)
            av.pack(side="left", padx=(0, 10))

            meta = tk.Frame(top, bg=t.COLORS["surface"])
            meta.pack(side="left", fill="y")
            t.label(meta, c.get("full_name", c["username"]), "h4",
                    bg=t.COLORS["surface"]).pack(anchor="w")
            t.label(meta, f"@{c['username']}  ·  {c['created_at'][:16]}",
                    "caption", t.COLORS["text3"], bg=t.COLORS["surface"]).pack(anchor="w")

            # Star display
            if c.get("rating"):
                stars = "★" * c["rating"] + "☆" * (5 - c["rating"])
                tk.Label(top, text=stars, font=("Segoe UI", 12),
                         fg=t.COLORS["gold"], bg=t.COLORS["surface"]).pack(side="right")

            # Delete button (own comment or admin)
            is_owner = str(c.get("user_id", "")) == str(self.app.user.get("id", ""))
            is_admin  = self.app.user.get("role") == "admin"
            if is_owner or is_admin:
                t.StyledButton(top, "🗑", lambda cid=c["_id"]: self._delete_comment(cid),
                               "danger", font_key="btn_sm", padx=6, pady=2).pack(side="right", padx=(0, 6))

            t.separator(card).pack(fill="x")

            body = tk.Frame(card, bg=t.COLORS["surface"], padx=14, pady=10)
            body.pack(fill="x")
            t.label(body, c["text"], "body", t.COLORS["text"],
                    bg=t.COLORS["surface"], wraplength=680, justify="left").pack(anchor="w")

    def _delete_comment(self, comment_id):
        db.delete_comment(comment_id)
        t.toast(self.app.root, "Review deleted", "info")
        self._load_comments()

    def _add_to_cart(self):
        db.add_to_cart(self.app.user["id"], self.prod["id"], self._qty_var.get())
        self.app.update_cart_badge()
        t.toast(self.app.root, f"Added {self._qty_var.get()}× to cart ✓", "success")

    def _toggle_wish(self):
        added = db.toggle_wishlist(self.app.user["id"], self.prod["id"])
        self._wish_btn.config(text="❤️ Wishlisted" if added else "🤍 Wishlist")
        t.toast(self.app.root, "Wishlisted ♥" if added else "Removed from wishlist", "info")


# ── Cart ──────────────────────────────────────────────────────────────────────

class CartView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=t.COLORS["surface"], pady=14, padx=20)
        header.pack(fill="x")
        t.label(header, "🛒  Your Cart", "h2", bg=t.COLORS["surface"]).pack(side="left")

        # Two-panel layout
        panel = tk.Frame(self, bg=t.COLORS["bg"])
        panel.pack(fill="both", expand=True, padx=16, pady=12)

        # Left: items list
        list_outer, self._list_inner, _ = t.scrollable_frame(panel)
        list_outer.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # Right: order summary
        summary = tk.Frame(panel, bg=t.COLORS["surface"],
                           highlightbackground=t.COLORS["border"],
                           highlightthickness=1, width=280)
        summary.pack(side="right", fill="y")
        summary.pack_propagate(False)
        self._summary = summary

        self.refresh()

    def refresh(self):
        for w in self._list_inner.winfo_children():
            w.destroy()
        for w in self._summary.winfo_children():
            w.destroy()

        cart = db.get_cart(self.app.user["id"])

        if not cart:
            empty_frame = tk.Frame(self._list_inner, bg=t.COLORS["bg"])
            empty_frame.pack(pady=80)
            tk.Label(empty_frame, text="🛒", font=("Segoe UI Emoji", 60),
                     bg=t.COLORS["bg"], fg=t.COLORS["text3"]).pack()
            t.label(empty_frame, "Your cart is empty", "h3", t.COLORS["text3"]).pack(pady=10)
            t.label(empty_frame, "Add some products to get started!", "body", t.COLORS["text3"]).pack()
        else:
            for item in cart:
                self._cart_row(item)

        self._build_summary(cart)
        self.app.update_cart_badge()

    def _cart_row(self, item):
        row = tk.Frame(self._list_inner, bg=t.COLORS["surface"],
                       highlightbackground=t.COLORS["border"],
                       highlightthickness=1)
        row.pack(fill="x", pady=6)

        # Image (URL or emoji fallback)
        cart_img = t.product_image_widget(row, item, (56, 56), t.COLORS["surface"])
        cart_img.pack(side="left", padx=12, pady=12)

        info = tk.Frame(row, bg=t.COLORS["surface"])
        info.pack(side="left", fill="both", expand=True, pady=12)

        t.label(info, item["name"], "h4", bg=t.COLORS["surface"]).pack(anchor="w")
        t.label(info, f"${item['price']:.2f} each", "body_sm",
                t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w")

        # Qty controls
        ctrl = tk.Frame(row, bg=t.COLORS["surface"])
        ctrl.pack(side="right", padx=16)

        subtotal = item["price"] * item["quantity"]
        t.label(ctrl, f"${subtotal:.2f}", "h4", t.COLORS["accent"],
                bg=t.COLORS["surface"]).pack(anchor="e", pady=(8, 4))

        qty_row = tk.Frame(ctrl, bg=t.COLORS["surface"])
        qty_row.pack(anchor="e")

        for symbol, delta in [("−", -1), ("+", 1)]:
            btn = tk.Button(qty_row, text=symbol, font=t.FONTS["body"],
                            bg=t.COLORS["surface2"], fg=t.COLORS["text"],
                            relief="flat", bd=0, padx=8, pady=2, cursor="hand2",
                            command=lambda cid=item["id"], d=delta: self._change_qty(cid, item["quantity"] + d))
            if symbol == "−":
                btn.pack(side="left")
            tk.Label(qty_row, text=str(item["quantity"]),
                     font=t.FONTS["body"],
                     bg=t.COLORS["surface2"], fg=t.COLORS["text"],
                     padx=10, pady=2).pack(side="left")
            if symbol == "+":
                btn.pack(side="left")

        t.StyledButton(ctrl, "Remove", lambda cid=item["id"]: self._remove(cid),
                       "danger", font_key="btn_sm", padx=8, pady=3).pack(anchor="e", pady=(6, 8))

    def _change_qty(self, cart_id, new_qty):
        db.update_cart_qty(cart_id, new_qty)
        self.refresh()

    def _remove(self, cart_id):
        db.remove_from_cart(cart_id)
        self.refresh()
        t.toast(self.app.root, "Item removed", "info")

    def _build_summary(self, cart):
        s = self._summary
        tk.Frame(s, bg=t.COLORS["surface"], height=16).pack()
        t.label(s, "Order Summary", "h3", bg=t.COLORS["surface"]).pack(padx=16, anchor="w")
        t.separator(s, thickness=1).pack(fill="x", pady=10)

        subtotal = sum(i["price"] * i["quantity"] for i in cart)
        shipping = 4.99 if cart else 0
        tax = round(subtotal * 0.08, 2)
        total = subtotal + shipping + tax

        for lbl, val in [("Subtotal", subtotal), ("Shipping", shipping), ("Tax (8%)", tax)]:
            row = tk.Frame(s, bg=t.COLORS["surface"])
            row.pack(fill="x", padx=16, pady=3)
            t.label(row, lbl, "body", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(side="left")
            t.label(row, f"${val:.2f}", "body", bg=t.COLORS["surface"]).pack(side="right")

        t.separator(s, t.COLORS["accent"], 2).pack(fill="x", pady=10)

        total_row = tk.Frame(s, bg=t.COLORS["surface"])
        total_row.pack(fill="x", padx=16, pady=(0, 16))
        t.label(total_row, "Total", "h4", bg=t.COLORS["surface"]).pack(side="left")
        t.label(total_row, f"${total:.2f}", "h3", t.COLORS["accent"], bg=t.COLORS["surface"]).pack(side="right")

        if cart:
            t.StyledButton(s, "Proceed to Checkout →", self._checkout, "primary").pack(
                fill="x", padx=16, pady=8)
            t.StyledButton(s, "Clear Cart", self._clear_cart, "danger",
                           font_key="btn_sm").pack(fill="x", padx=16, pady=(0, 8))
        else:
            t.StyledButton(s, "Browse Products", lambda: self.app.show_page("catalog"),
                           "ghost").pack(fill="x", padx=16, pady=8)

    def _clear_cart(self):
        if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            db.clear_cart(self.app.user["id"])
            self.refresh()

    def _checkout(self):
        cart = db.get_cart(self.app.user["id"])
        if not cart:
            return
        self.app.show_checkout()


# ── Checkout ──────────────────────────────────────────────────────────────────

class CheckoutView(tk.Frame):

    def __init__(self, parent, app, on_success):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self.on_success = on_success
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=t.COLORS["surface"], pady=14, padx=20)
        header.pack(fill="x")
        t.StyledButton(header, "← Back to Cart",
                       lambda: self.app.show_page("cart"),
                       "ghost", font_key="btn_sm", padx=12, pady=5).pack(side="left")
        t.label(header, "Checkout", "h2", bg=t.COLORS["surface"]).pack(side="left", padx=16)

        outer, inner, _ = t.scrollable_frame(self)
        outer.pack(fill="both", expand=True)

        content = tk.Frame(inner, bg=t.COLORS["bg"], padx=60, pady=30)
        content.pack()

        # Delivery address
        addr_box = t.surface_frame(content)
        addr_box.pack(fill="x", pady=(0, 16))
        tk.Frame(addr_box, bg=t.COLORS["surface"], height=8).pack()
        t.label(addr_box, "📍  Delivery Address", "h3", bg=t.COLORS["surface"]).pack(anchor="w", padx=16)
        t.separator(addr_box).pack(fill="x", pady=10)

        fields = [
            ("Full Name",    "_name"),
            ("Street Address", "_street"),
            ("City",         "_city"),
            ("ZIP / Postal Code", "_zip"),
            ("Country",      "_country"),
        ]
        self._addr_vars = {}
        for lbl, key in fields:
            t.label(addr_box, lbl, "body_sm", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w", padx=16)
            e, v = t.entry(addr_box, width=50)
            e.pack(anchor="w", padx=16, pady=(4, 12), ipady=6)
            self._addr_vars[key] = v

        # Pre-fill name
        self._addr_vars["_name"].set(self.app.user["full_name"])

        # Payment (mock)
        pay_box = t.surface_frame(content)
        pay_box.pack(fill="x", pady=(0, 16))
        tk.Frame(pay_box, bg=t.COLORS["surface"], height=8).pack()
        t.label(pay_box, "💳  Payment Method", "h3", bg=t.COLORS["surface"]).pack(anchor="w", padx=16)
        t.separator(pay_box).pack(fill="x", pady=10)

        self._payment_var = tk.StringVar(value="card")
        for val, lbl in [("card", "💳  Credit / Debit Card"),
                          ("paypal", "🔵  PayPal"),
                          ("cod", "💵  Cash on Delivery")]:
            rb = tk.Radiobutton(pay_box, text=lbl,
                                variable=self._payment_var, value=val,
                                font=t.FONTS["body"],
                                bg=t.COLORS["surface"], fg=t.COLORS["text"],
                                activebackground=t.COLORS["surface"],
                                selectcolor=t.COLORS["surface2"],
                                cursor="hand2")
            rb.pack(anchor="w", padx=20, pady=4)

        # Card fields (mock)
        card_frame = tk.Frame(pay_box, bg=t.COLORS["surface"])
        card_frame.pack(anchor="w", padx=20, pady=(0, 12))

        for lbl in ["Card Number", "Expiry (MM/YY)", "CVV"]:
            t.label(card_frame, lbl, "body_sm", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w")
            e, _ = t.entry(card_frame, width=40)
            e.pack(anchor="w", pady=(4, 10), ipady=6)

        # Order summary
        cart = db.get_cart(self.app.user["id"])
        subtotal = sum(i["price"] * i["quantity"] for i in cart)
        tax = round(subtotal * 0.08, 2)
        total = subtotal + 4.99 + tax

        summ = t.surface_frame(content)
        summ.pack(fill="x")
        tk.Frame(summ, bg=t.COLORS["surface"], height=8).pack()
        t.label(summ, "🧾  Order Total", "h3", bg=t.COLORS["surface"]).pack(anchor="w", padx=16)
        t.separator(summ).pack(fill="x", pady=8)

        row = tk.Frame(summ, bg=t.COLORS["surface"])
        row.pack(fill="x", padx=16, pady=(0, 12))
        t.label(row, f"{len(cart)} item(s)", "body", t.COLORS["text2"], bg=t.COLORS["surface"]).pack(side="left")
        t.label(row, f"${total:.2f}", "h2", t.COLORS["accent"], bg=t.COLORS["surface"]).pack(side="right")

        t.StyledButton(content, f"✅  Place Order — ${total:.2f}",
                       self._place_order, "success").pack(fill="x", pady=16)

    def _place_order(self):
        v = self._addr_vars
        parts = [v["_name"].get(), v["_street"].get(), v["_city"].get(),
                 v["_zip"].get(), v["_country"].get()]
        if not all(p.strip() for p in parts):
            messagebox.showwarning("Address Required", "Please fill in all address fields.")
            return
        address = ", ".join(p.strip() for p in parts)
        order_id = db.place_order(self.app.user["id"], address)
        if order_id:
            self.on_success(order_id)
        else:
            messagebox.showerror("Error", "Could not place order. Cart may be empty.")


# ── Orders ────────────────────────────────────────────────────────────────────

class OrdersView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=t.COLORS["surface"], pady=14, padx=20)
        header.pack(fill="x")
        t.label(header, "📦  My Orders", "h2", bg=t.COLORS["surface"]).pack(side="left")

        outer, inner, _ = t.scrollable_frame(self)
        outer.pack(fill="both", expand=True, padx=16, pady=12)

        orders = db.get_orders(self.app.user["id"])

        if not orders:
            tk.Label(inner, text="📭", font=("Segoe UI Emoji", 60),
                     bg=t.COLORS["bg"]).pack(pady=(60, 12))
            t.label(inner, "No orders yet", "h3", t.COLORS["text3"]).pack()
            t.label(inner, "Your order history will appear here", "body", t.COLORS["text3"]).pack()
            return

        STATUS_COLOR = {
            "pending":   t.COLORS["warning"],
            "processing": t.COLORS["accent"],
            "shipped":   t.COLORS["success"],
            "delivered": "#22C55E",
            "cancelled": t.COLORS["danger"],
        }

        for order in orders:
            card = t.surface_frame(inner)
            card.pack(fill="x", pady=8)

            head = tk.Frame(card, bg=t.COLORS["surface"], pady=10, padx=16)
            head.pack(fill="x")

            t.label(head, f"Order #{order['id']}", "h4", bg=t.COLORS["surface"]).pack(side="left")
            status_c = STATUS_COLOR.get(order["status"], t.COLORS["text2"])
            t.badge(head, order["status"].upper(), t.COLORS["white"], status_c).pack(side="right")
            t.label(head, order["created_at"][:16], "body_sm",
                    t.COLORS["text2"], bg=t.COLORS["surface"]).pack(side="right", padx=12)

            t.separator(card).pack(fill="x")

            items = db.get_order_items(order["id"])
            for item in items[:3]:
                row = tk.Frame(card, bg=t.COLORS["surface"], padx=16, pady=6)
                row.pack(fill="x")
                order_img = t.product_image_widget(row, item, (32, 32), t.COLORS["surface"])
                order_img.pack(side="left", padx=(0, 10))
                t.label(row, item["name"], "body", bg=t.COLORS["surface"]).pack(side="left")
                t.label(row, f"×{item['quantity']}", "body", t.COLORS["text2"],
                        bg=t.COLORS["surface"]).pack(side="left", padx=6)
                t.label(row, f"${item['price'] * item['quantity']:.2f}",
                        "body", t.COLORS["accent"], bg=t.COLORS["surface"]).pack(side="right")

            if len(items) > 3:
                t.label(card, f"  + {len(items)-3} more items",
                        "caption", t.COLORS["text3"], bg=t.COLORS["surface"]).pack(anchor="w", padx=16)

            t.separator(card).pack(fill="x")

            foot = tk.Frame(card, bg=t.COLORS["surface"], padx=16, pady=10)
            foot.pack(fill="x")
            t.label(foot, f"📍 {order['address']}", "caption",
                    t.COLORS["text2"], bg=t.COLORS["surface"], wraplength=500).pack(side="left", anchor="w")
            t.label(foot, f"Total: ${order['total']:.2f}", "h4",
                    t.COLORS["accent"], bg=t.COLORS["surface"]).pack(side="right")


# ── Wishlist ──────────────────────────────────────────────────────────────────

class WishlistView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=t.COLORS["surface"], pady=14, padx=20)
        header.pack(fill="x")
        t.label(header, "❤️  My Wishlist", "h2", bg=t.COLORS["surface"]).pack(side="left")

        outer, inner, _ = t.scrollable_frame(self)
        outer.pack(fill="both", expand=True, padx=16, pady=12)

        items = db.get_wishlist(self.app.user["id"])

        if not items:
            tk.Label(inner, text="🤍", font=("Segoe UI Emoji", 60),
                     bg=t.COLORS["bg"]).pack(pady=(60, 12))
            t.label(inner, "Your wishlist is empty", "h3", t.COLORS["text3"]).pack()
            return

        for prod in items:
            row = t.surface_frame(inner)
            row.pack(fill="x", pady=5)

            wish_img = t.product_image_widget(row, prod, (60, 60), t.COLORS["surface"])
            wish_img.pack(side="left", padx=12, pady=12)

            info = tk.Frame(row, bg=t.COLORS["surface"])
            info.pack(side="left", fill="both", expand=True, pady=12)
            t.label(info, prod["name"], "h4", bg=t.COLORS["surface"]).pack(anchor="w")
            t.label(info, prod.get("category_name", ""), "caption",
                    t.COLORS["text2"], bg=t.COLORS["surface"]).pack(anchor="w")
            t.star_rating(info, prod["rating"], t.COLORS["surface"]).pack(anchor="w", pady=3)

            ctrl = tk.Frame(row, bg=t.COLORS["surface"])
            ctrl.pack(side="right", padx=16, pady=12)

            t.label(ctrl, f"${prod['price']:.2f}", "h3",
                    t.COLORS["accent"], bg=t.COLORS["surface"]).pack(anchor="e")
            t.StyledButton(ctrl, "🛒  Add to Cart",
                           lambda pid=prod["id"]: self._add(pid),
                           "primary", font_key="btn_sm", padx=10, pady=5).pack(pady=(8, 4))
            t.StyledButton(ctrl, "Remove",
                           lambda pid=prod["id"]: self._remove(pid),
                           "ghost", font_key="btn_sm", padx=10, pady=4).pack()

    def _add(self, product_id):
        db.add_to_cart(self.app.user["id"], product_id)
        self.app.update_cart_badge()
        t.toast(self.app.root, "Added to cart ✓", "success")

    def _remove(self, product_id):
        db.toggle_wishlist(self.app.user["id"], product_id)
        for w in self.winfo_children():
            w.destroy()
        self._build()