"""
theme.py - Design system: colors, fonts, and reusable styled widgets
"""

import tkinter as tk
from tkinter import ttk

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":           "#0F0F13",      # near-black background
    "surface":      "#1A1A24",      # card/panel background
    "surface2":     "#22222F",      # elevated surface
    "border":       "#2E2E40",      # subtle borders
    "accent":       "#7C5CFC",      # purple primary
    "accent_hover": "#9B7EFF",      # lighter purple on hover
    "accent2":      "#FC5C7D",      # pink secondary accent
    "success":      "#2DD4BF",      # teal success
    "warning":      "#F59E0B",      # amber warning
    "danger":       "#EF4444",      # red danger
    "text":         "#F0EEFF",      # primary text
    "text2":        "#A09BB8",      # secondary/muted text
    "text3":        "#6B6680",      # placeholder/faint text
    "gold":         "#FFD700",      # star ratings
    "white":        "#FFFFFF",
}

# ── Font Definitions ──────────────────────────────────────────────────────────
FONTS = {
    "h1":      ("Segoe UI", 26, "bold"),
    "h2":      ("Segoe UI", 20, "bold"),
    "h3":      ("Segoe UI", 15, "bold"),
    "h4":      ("Segoe UI", 12, "bold"),
    "body":    ("Segoe UI", 11),
    "body_sm": ("Segoe UI", 10),
    "caption": ("Segoe UI", 9),
    "mono":    ("Consolas", 11),
    "price":   ("Segoe UI", 14, "bold"),
    "btn":     ("Segoe UI", 11, "bold"),
    "btn_sm":  ("Segoe UI", 10, "bold"),
}


def apply_theme():
    """Configure ttk styles globally."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"],
                    font=FONTS["body"], borderwidth=0, relief="flat")

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=COLORS["surface2"], troughcolor=COLORS["bg"],
                    arrowcolor=COLORS["text3"], bordercolor=COLORS["bg"],
                    relief="flat", width=8)
    style.map("Vertical.TScrollbar", background=[("active", COLORS["border"])])

    # Combobox
    style.configure("TCombobox",
                    fieldbackground=COLORS["surface2"],
                    background=COLORS["surface2"],
                    foreground=COLORS["text"],
                    selectbackground=COLORS["accent"],
                    selectforeground=COLORS["white"],
                    arrowcolor=COLORS["text2"],
                    bordercolor=COLORS["border"],
                    relief="flat", padding=6)
    style.map("TCombobox",
              fieldbackground=[("readonly", COLORS["surface2"])],
              foreground=[("readonly", COLORS["text"])])

    # Entry
    style.configure("TEntry",
                    fieldbackground=COLORS["surface2"],
                    foreground=COLORS["text"],
                    insertcolor=COLORS["text"],
                    bordercolor=COLORS["border"],
                    relief="flat", padding=8)


# ── Reusable Widget Builders ──────────────────────────────────────────────────

def frame(parent, bg=None, **kwargs):
    return tk.Frame(parent, bg=bg or COLORS["bg"], **kwargs)


def surface_frame(parent, **kwargs):
    return tk.Frame(parent, bg=COLORS["surface"],
                    highlightbackground=COLORS["border"],
                    highlightthickness=1, **kwargs)


def label(parent, text, font_key="body", color=None, bg=None, **kwargs):
    return tk.Label(
        parent, text=text,
        font=FONTS[font_key],
        fg=color or COLORS["text"],
        bg=bg or COLORS["bg"],
        **kwargs,
    )


def entry(parent, textvariable=None, placeholder="", show="", width=28, **kwargs):
    var = textvariable or tk.StringVar()
    e = tk.Entry(
        parent,
        textvariable=var,
        font=FONTS["body"],
        bg=COLORS["surface2"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        bd=0,
        show=show,
        width=width,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        **kwargs,
    )
    if placeholder and not textvariable:
        _add_placeholder(e, var, placeholder)
    return e, var


def _add_placeholder(e, var, placeholder):
    e.insert(0, placeholder)
    e.config(fg=COLORS["text3"])

    def on_focus_in(_):
        if var.get() == placeholder:
            e.delete(0, tk.END)
            e.config(fg=COLORS["text"])

    def on_focus_out(_):
        if not var.get():
            e.insert(0, placeholder)
            e.config(fg=COLORS["text3"])

    e.bind("<FocusIn>", on_focus_in)
    e.bind("<FocusOut>", on_focus_out)


class StyledButton(tk.Button):
    """A custom themed button with hover effects."""

    PRESETS = {
        "primary": (COLORS["accent"],       COLORS["accent_hover"], COLORS["white"]),
        "danger":  (COLORS["danger"],        "#FF6B6B",              COLORS["white"]),
        "success": (COLORS["success"],       "#34D9C6",              COLORS["bg"]),
        "ghost":   (COLORS["surface2"],      COLORS["border"],       COLORS["text"]),
        "accent2": (COLORS["accent2"],       "#FF7D95",              COLORS["white"]),
        "warning": (COLORS["warning"],       "#FBBF24",              COLORS["bg"]),
    }

    def __init__(self, parent, text, command=None, preset="primary",
                 font_key="btn", padx=18, pady=8, **kwargs):
        bg, hover_bg, fg = self.PRESETS.get(preset, self.PRESETS["primary"])
        super().__init__(
            parent, text=text, command=command,
            font=FONTS[font_key],
            bg=bg, fg=fg,
            activebackground=hover_bg, activeforeground=fg,
            relief="flat", bd=0,
            padx=padx, pady=pady,
            cursor="hand2",
            **kwargs,
        )
        self._bg = bg
        self._hover = hover_bg
        self.bind("<Enter>", lambda _: self.config(bg=self._hover))
        self.bind("<Leave>", lambda _: self.config(bg=self._bg))


def scrollable_frame(parent, bg=None):
    """Returns (outer_frame, inner_frame, canvas) for a scrollable area."""
    bg = bg or COLORS["bg"]
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                               style="Vertical.TScrollbar")
    inner = tk.Frame(canvas, bg=bg)

    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def on_configure(_):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_resize(e):
        canvas.itemconfig(inner_id, width=e.width)

    inner.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_canvas_resize)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    def on_mousewheel(e):
        # Only scroll if there is actually content beyond the visible area
        top, bottom = canvas.yview()
        if top == 0.0 and bottom == 1.0:
            return
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    return outer, inner, canvas


def separator(parent, color=None, thickness=1, orient="horizontal", **kwargs):
    if orient == "horizontal":
        return tk.Frame(parent, bg=color or COLORS["border"], height=thickness, **kwargs)
    return tk.Frame(parent, bg=color or COLORS["border"], width=thickness, **kwargs)


def badge(parent, text, color=None, bg=None, **kwargs):
    return tk.Label(
        parent, text=text,
        font=FONTS["caption"],
        fg=color or COLORS["white"],
        bg=bg or COLORS["accent"],
        padx=6, pady=2,
        **kwargs,
    )


def star_rating(parent, rating, bg=None):
    """Returns a frame displaying star rating."""
    bg = bg or COLORS["surface"]
    f = tk.Frame(parent, bg=bg)
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    stars = "★" * full + "½" * half + "☆" * empty
    tk.Label(f, text=stars, font=FONTS["caption"],
             fg=COLORS["gold"], bg=bg).pack(side="left")
    tk.Label(f, text=f" {rating:.1f}", font=FONTS["caption"],
             fg=COLORS["text2"], bg=bg).pack(side="left")
    return f


def load_product_image(path: str, size: tuple) -> "tk.PhotoImage | None":
    """
    Loads a product image from a local file path and returns a resized PhotoImage.
    Returns None if the path is empty or the file cannot be opened.
    Requires: pip install pillow

    Usage — set image_url in database.py seed data to a relative or absolute path:
        "image_url": "images/headphones.png"
    Place your image files in an 'images/' folder next to main.py.
    Supported formats: PNG, JPG, WEBP, GIF, BMP, etc.
    Leave "image_url" as "" to use the emoji fallback instead.
    """
    if not path or not path.strip():
        return None
    try:
        from PIL import Image, ImageTk
        img = Image.open(path.strip()).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def product_image_widget(parent, prod: dict, size: tuple, bg: str) -> tk.Widget:
    """
    Returns a Label showing the product image (from image_url as a local file path)
    or the emoji fallback if the path is blank or the file is missing.
    """
    photo = load_product_image(prod.get("image_url", ""), size)
    if photo:
        lbl = tk.Label(parent, image=photo, bg=bg)
        lbl._photo = photo  # prevent garbage collection
    else:
        emoji_size = max(10, size[1] // 3)
        lbl = tk.Label(parent, text=prod.get("image_emoji", "🛍️"),
                       font=("Segoe UI Emoji", emoji_size), bg=bg)
    return lbl


def toast(root, message, kind="success", duration=2500):
    """Show a floating toast notification."""
    color_map = {
        "success": COLORS["success"],
        "error":   COLORS["danger"],
        "info":    COLORS["accent"],
        "warning": COLORS["warning"],
    }
    color = color_map.get(kind, COLORS["accent"])

    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.configure(bg=color)

    tk.Label(t, text=message, font=FONTS["body"],
             fg=COLORS["white"], bg=color,
             padx=20, pady=12).pack()

    t.update_idletasks()
    w, h = t.winfo_width(), t.winfo_height()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    t.geometry(f"+{sw - w - 30}+{sh - h - 60}")

    root.after(duration, t.destroy)