"""Thème sombre moderne (style Fluent / Mantine)."""

BG          = "#16171b"
SURFACE     = "#1e1f24"
SURFACE_ALT = "#25262b"
BORDER      = "#2e3036"
PRIMARY     = "#4dabf7"
PRIMARY_HOV = "#74c0fc"
PRIMARY_PRS = "#339af0"
TEXT        = "#e9ecef"
TEXT_MUTED  = "#909296"
SUCCESS     = "#51cf66"
DANGER      = "#ff6b6b"

QSS = f"""
* {{
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    color: {TEXT};
    outline: none;
}}

QMainWindow, QWidget#root {{
    background-color: {BG};
}}

QLabel#title {{
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.3px;
}}
QLabel#subtitle {{
    color: {TEXT_MUTED};
    font-size: 13px;
}}
QLabel#status {{
    color: {TEXT_MUTED};
    font-size: 12px;
    padding: 6px 12px;
}}

/* === Search input === */
QLineEdit#search {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: {PRIMARY};
}}
QLineEdit#search:focus {{
    border: 1px solid {PRIMARY};
    background-color: {SURFACE_ALT};
}}

/* === Buttons === */
QPushButton#primary {{
    background-color: {PRIMARY};
    color: #0b1320;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton#primary:hover  {{ background-color: {PRIMARY_HOV}; }}
QPushButton#primary:pressed{{ background-color: {PRIMARY_PRS}; }}
QPushButton#primary:disabled {{
    background-color: {SURFACE_ALT};
    color: {TEXT_MUTED};
}}

QPushButton#ghost {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 14px;
    color: {TEXT};
    font-size: 12px;
}}
QPushButton#ghost:hover  {{ background-color: {SURFACE_ALT}; border-color: {PRIMARY}; }}
QPushButton#ghost:pressed{{ background-color: {SURFACE}; }}

/* === Package cards === */
QFrame#card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QFrame#card:hover {{
    background-color: {SURFACE_ALT};
    border-color: #3a3d44;
}}
QLabel#cardName {{
    font-size: 15px;
    font-weight: 600;
}}
QLabel#cardId {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QLabel#cardVersion {{
    color: {PRIMARY};
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(77, 171, 247, 0.12);
    border-radius: 6px;
    padding: 3px 8px;
}}
QLabel#cardSource {{
    color: {TEXT_MUTED};
    font-size: 11px;
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 3px 8px;
}}

/* === Scroll area === */
QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #4a4d55; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
"""
