"""
auth_views.py - Login and Registration screens
"""

import tkinter as tk
from tkinter import messagebox
import database as db
import theme as t


class AuthView(tk.Frame):
    """
    Handles Login / Register flow. Calls on_login(user_dict) when successful.
    """

    def __init__(self, parent, on_login):
        super().__init__(parent, bg=t.COLORS["bg"])
        self.on_login = on_login
        self._build_login()

    # ── Login ─────────────────────────────────────────────────────────────────

    def _build_login(self):
        self._clear()
        self.pack(fill="both", expand=True)

        # Left decorative panel
        left = tk.Frame(self, bg=t.COLORS["accent"], width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🛒", font=("Segoe UI", 64),
                 bg=t.COLORS["accent"], fg=t.COLORS["white"]).pack(pady=(80, 10))
        tk.Label(left, text="ShopVerse",
                 font=("Segoe UI", 28, "bold"),
                 bg=t.COLORS["accent"], fg=t.COLORS["white"]).pack()
        tk.Label(left, text="Your universe of deals",
                 font=("Segoe UI", 12),
                 bg=t.COLORS["accent"], fg="#C8BBFF").pack(pady=(4, 40))

        for feat in ["✦  10,000+ Products", "✦  Fast Delivery", "✦  Secure Checkout", "✦  Easy Returns"]:
            tk.Label(left, text=feat, font=("Segoe UI", 11),
                     bg=t.COLORS["accent"], fg="#D8CFFF",
                     anchor="w").pack(padx=40, pady=3, fill="x")

        # Right login form
        right = tk.Frame(self, bg=t.COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=t.COLORS["bg"])
        form.place(relx=0.5, rely=0.5, anchor="center")

        t.label(form, "Welcome back 👋", "h2").pack(anchor="w")
        t.label(form, "Sign in to your account", "body", t.COLORS["text2"]).pack(anchor="w", pady=(4, 28))

        # Username
        self._login_fields(form)

    def _login_fields(self, form):
        t.label(form, "Username", "body_sm", t.COLORS["text2"]).pack(anchor="w")
        self._u_entry, self._u_var = t.entry(form, width=32)
        self._u_entry.pack(pady=(4, 14), ipady=6)

        t.label(form, "Password", "body_sm", t.COLORS["text2"]).pack(anchor="w")
        self._p_entry, self._p_var = t.entry(form, show="●", width=32)
        self._p_entry.pack(pady=(4, 6), ipady=6)

        # Show password toggle
        self._show_pass = tk.BooleanVar()
        chk = tk.Checkbutton(
            form, text="Show password",
            variable=self._show_pass,
            command=lambda: self._p_entry.config(show="" if self._show_pass.get() else "●"),
            bg=t.COLORS["bg"], fg=t.COLORS["text2"],
            activebackground=t.COLORS["bg"], activeforeground=t.COLORS["text"],
            selectcolor=t.COLORS["surface2"],
            font=t.FONTS["caption"], cursor="hand2",
        )
        chk.pack(anchor="w", pady=(0, 18))

        t.StyledButton(form, "Sign In", self._do_login, "primary").pack(fill="x", pady=(0, 16))

        divider = tk.Frame(form, bg=t.COLORS["bg"])
        divider.pack(fill="x", pady=4)
        t.separator(divider).pack(fill="x", pady=8)

        bottom = tk.Frame(form, bg=t.COLORS["bg"])
        bottom.pack(fill="x")
        t.label(bottom, "Don't have an account?", "body_sm", t.COLORS["text2"]).pack(side="left")
        reg_btn = tk.Label(bottom, text="  Register", font=t.FONTS["body_sm"],
                           fg=t.COLORS["accent"], bg=t.COLORS["bg"], cursor="hand2")
        reg_btn.pack(side="left")
        reg_btn.bind("<Button-1>", lambda _: self._build_register())

        t.label(form, "─── Demo credentials ───", "caption", t.COLORS["text3"]).pack(pady=(20, 4))
        t.label(form, "admin / admin123  (admin panel access)", "caption", t.COLORS["text3"]).pack()

    def _do_login(self):
        u = self._u_var.get().strip()
        p = self._p_var.get().strip()
        if not u or not p:
            messagebox.showwarning("Input Error", "Please enter username and password.")
            return
        user = db.login_user(u, p)
        if user:
            self.on_login(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # ── Register ──────────────────────────────────────────────────────────────

    def _build_register(self):
        self._clear()

        left = tk.Frame(self, bg=t.COLORS["accent2"], width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🎉", font=("Segoe UI", 64),
                 bg=t.COLORS["accent2"], fg=t.COLORS["white"]).pack(pady=(80, 10))
        tk.Label(left, text="Join ShopVerse",
                 font=("Segoe UI", 26, "bold"),
                 bg=t.COLORS["accent2"], fg=t.COLORS["white"]).pack()
        tk.Label(left, text="Create your free account today",
                 font=("Segoe UI", 12),
                 bg=t.COLORS["accent2"], fg="#FFD0DA").pack(pady=(4, 0))

        right = tk.Frame(self, bg=t.COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=t.COLORS["bg"])
        form.place(relx=0.5, rely=0.5, anchor="center")

        t.label(form, "Create Account", "h2").pack(anchor="w")
        t.label(form, "Fill in your details to get started", "body", t.COLORS["text2"]).pack(anchor="w", pady=(4, 24))

        fields = [
            ("Full Name",  False, "_fn"),
            ("Username",   False, "_un"),
            ("Email",      False, "_em"),
            ("Password",   True,  "_pw"),
            ("Confirm Password", True, "_cp"),
        ]
        self._reg_vars = {}
        for label_text, is_pass, attr in fields:
            t.label(form, label_text, "body_sm", t.COLORS["text2"]).pack(anchor="w")
            e, v = t.entry(form, show="●" if is_pass else "", width=32)
            e.pack(pady=(4, 12), ipady=6)
            self._reg_vars[attr] = v

        t.StyledButton(form, "Create Account", self._do_register, "accent2").pack(fill="x", pady=(4, 14))

        bottom = tk.Frame(form, bg=t.COLORS["bg"])
        bottom.pack(fill="x")
        t.label(bottom, "Already have an account?", "body_sm", t.COLORS["text2"]).pack(side="left")
        back_btn = tk.Label(bottom, text="  Sign In", font=t.FONTS["body_sm"],
                            fg=t.COLORS["accent"], bg=t.COLORS["bg"], cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda _: self._build_login())

    def _do_register(self):
        v = self._reg_vars
        fn = v["_fn"].get().strip()
        un = v["_un"].get().strip()
        em = v["_em"].get().strip()
        pw = v["_pw"].get()
        cp = v["_cp"].get()

        if not all([fn, un, em, pw, cp]):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        if len(un) < 3:
            messagebox.showwarning("Validation", "Username must be at least 3 characters.")
            return
        if "@" not in em:
            messagebox.showwarning("Validation", "Please enter a valid email address.")
            return
        if len(pw) < 6:
            messagebox.showwarning("Validation", "Password must be at least 6 characters.")
            return
        if pw != cp:
            messagebox.showerror("Validation", "Passwords do not match.")
            return

        success, msg = db.register_user(un, pw, em, fn)
        if success:
            messagebox.showinfo("Success", f"{msg}\nYou can now sign in.")
            self._build_login()
        else:
            messagebox.showerror("Registration Failed", msg)

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()
            
if __name__ == "__main__":
    import tkinter as tk

    def handle_login(user):
        print("Logged in user:", user)
        # You can later switch to shop view here

    root = tk.Tk()
    root.title("ShopVerse")
    root.geometry("900x500")  # optional but helps your UI

    app = AuthView(root, handle_login)  # ✅ FIXED
    root.mainloop()