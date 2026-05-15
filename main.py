"""
main.py - Entry point for the ShopVerse Tkinter E-Commerce App
Run this file: python main.py
"""

import tkinter as tk
from tkinter import messagebox
import os, sys

# Make sure imports find sibling modules
sys.path.insert(0, os.path.dirname(__file__))

import database as db
import theme as t
from auth_views import AuthView
from shop_views import CatalogView, ProductDetailView, CartView, CheckoutView, OrdersView, WishlistView
from admin_views import AdminView


class ShopVerseApp:
    """Root application controller - owns the window and manages page routing."""

    def __init__(self):
        # ── Init DB first (creates tables + seeds data) ──
        db.init_db()

        # ── Root window ──
        self.root = tk.Tk()
        self.root.title("ShopVerse 🛒")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=t.COLORS["bg"])

        # Apply ttk theme
        t.apply_theme()

        self.user = None
        self._pages = {}
        self._current_page = None

        # Start with auth screen
        self._show_auth()

        self.root.mainloop()

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _show_auth(self):
        """Display the login/register screen."""
        for w in self.root.winfo_children():
            w.destroy()
        self._pages = {}
        AuthView(self.root, self._on_login)

    def _on_login(self, user: dict):
        self.user = user
        self._build_shell()
        self.show_page("catalog")

    # ── App shell ─────────────────────────────────────────────────────────────

    def _build_shell(self):
        """Build the persistent navigation bar + content area."""
        for w in self.root.winfo_children():
            w.destroy()

        # ── Top navbar ──
        navbar = tk.Frame(self.root, bg=t.COLORS["surface"],
                          highlightbackground=t.COLORS["border"],
                          highlightthickness=1)
        navbar.pack(fill="x", side="top")

        # Brand
        tk.Label(navbar, text="🛒 ShopVerse",
                 font=("Segoe UI", 16, "bold"),
                 bg=t.COLORS["surface"], fg=t.COLORS["accent"],
                 padx=20, pady=12).pack(side="left")

        # Nav links
        nav_links = [
            ("🏪 Shop",      "catalog"),
            ("❤️ Wishlist",  "wishlist"),
            ("📦 Orders",    "orders"),
        ]
        if self.user.get("role") == "admin":
            nav_links.append(("⚙️ Admin", "admin"))

        self._nav_btns = {}
        for label, page in nav_links:
            btn = tk.Button(
                navbar, text=label,
                font=t.FONTS["body"],
                bg=t.COLORS["surface"], fg=t.COLORS["text2"],
                activebackground=t.COLORS["surface2"],
                activeforeground=t.COLORS["accent"],
                relief="flat", bd=0,
                padx=14, pady=14,
                cursor="hand2",
                command=lambda p=page: self.show_page(p),
            )
            btn.pack(side="left")
            self._nav_btns[page] = btn

        # Right side: cart badge + user info + logout
        right = tk.Frame(navbar, bg=t.COLORS["surface"])
        right.pack(side="right", padx=16)

        # Cart button with badge
        self._cart_btn_frame = tk.Frame(right, bg=t.COLORS["surface"])
        self._cart_btn_frame.pack(side="left", padx=8)
        self._cart_main_btn = tk.Button(
            self._cart_btn_frame, text="🛒",
            font=("Segoe UI Emoji", 16),
            bg=t.COLORS["surface"], fg=t.COLORS["text"],
            activebackground=t.COLORS["surface2"],
            relief="flat", bd=0, padx=6, pady=8,
            cursor="hand2",
            command=lambda: self.show_page("cart"),
        )
        self._cart_main_btn.pack(side="left")
        self._cart_badge = tk.Label(
            self._cart_btn_frame, text="",
            font=t.FONTS["caption"],
            fg=t.COLORS["white"], bg=t.COLORS["accent2"],
            padx=5, pady=1,
        )
        self._cart_badge.pack(side="left")
        self.update_cart_badge()

        t.separator(right, orient="vertical").pack(side="left", fill="y", padx=8)

        # User name
        tk.Label(right, text=f"👤 {self.user['full_name'].split()[0]}",
                 font=t.FONTS["body"],
                 bg=t.COLORS["surface"], fg=t.COLORS["text2"],
                 pady=12).pack(side="left", padx=6)

        # Logout
        tk.Button(
            right, text="Sign Out",
            font=t.FONTS["btn_sm"],
            bg=t.COLORS["danger"], fg=t.COLORS["white"],
            activebackground="#FF6B6B", activeforeground=t.COLORS["white"],
            relief="flat", bd=0, padx=12, pady=6,
            cursor="hand2",
            command=self._logout,
        ).pack(side="left", pady=8)

        # ── Content area ──
        self._content = tk.Frame(self.root, bg=t.COLORS["bg"])
        self._content.pack(fill="both", expand=True)

    # ── Page routing ──────────────────────────────────────────────────────────

    def show_page(self, name: str):
        """Switch the visible page. Lazily creates pages."""
        # Highlight active nav btn
        for pg, btn in self._nav_btns.items():
            btn.config(
                bg=t.COLORS["surface2"] if pg == name else t.COLORS["surface"],
                fg=t.COLORS["accent"] if pg == name else t.COLORS["text2"],
            )

        # Tear down current page
        for w in self._content.winfo_children():
            w.destroy()

        self._current_page = name

        if name == "catalog":
            CatalogView(self._content, self).pack(fill="both", expand=True)

        elif name == "cart":
            CartView(self._content, self).pack(fill="both", expand=True)

        elif name == "wishlist":
            WishlistView(self._content, self).pack(fill="both", expand=True)

        elif name == "orders":
            OrdersView(self._content, self).pack(fill="both", expand=True)

        elif name == "admin":
            if self.user.get("role") == "admin":
                AdminView(self._content, self).pack(fill="both", expand=True)
            else:
                self.show_page("catalog")

    def open_product(self, product_id: int):
        """Navigate to a product detail page."""
        for w in self._content.winfo_children():
            w.destroy()
        ProductDetailView(
            self._content, self, product_id,
            on_back=lambda: self.show_page("catalog")
        ).pack(fill="both", expand=True)

    def show_checkout(self):
        """Navigate to checkout."""
        for w in self._content.winfo_children():
            w.destroy()
        CheckoutView(
            self._content, self,
            on_success=self._on_order_placed
        ).pack(fill="both", expand=True)

    def _on_order_placed(self, order_id: int):
        """Called after a successful order."""
        self.update_cart_badge()
        # Show success screen
        for w in self._content.winfo_children():
            w.destroy()

        frame = tk.Frame(self._content, bg=t.COLORS["bg"])
        frame.pack(fill="both", expand=True)

        box = tk.Frame(frame, bg=t.COLORS["bg"])
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="🎉", font=("Segoe UI Emoji", 72),
                 bg=t.COLORS["bg"]).pack()
        t.label(box, "Order Placed!", "h1", t.COLORS["success"]).pack(pady=(10, 6))
        t.label(box, f"Order #{order_id} has been confirmed.", "h3",
                t.COLORS["text2"]).pack()
        t.label(box, "Thank you for shopping with ShopVerse!", "body",
                t.COLORS["text2"]).pack(pady=(4, 24))

        btn_row = tk.Frame(box, bg=t.COLORS["bg"])
        btn_row.pack()
        t.StyledButton(btn_row, "📦 View My Orders",
                       lambda: self.show_page("orders"), "primary").pack(side="left", padx=8)
        t.StyledButton(btn_row, "🏪 Continue Shopping",
                       lambda: self.show_page("catalog"), "ghost").pack(side="left", padx=8)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def update_cart_badge(self):
        count = db.get_cart_count(self.user["id"])
        self._cart_badge.config(text=str(count) if count else "")

    def _logout(self):
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            self.user = None
            self._show_auth()


if __name__ == "__main__":
    ShopVerseApp()