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
ACCENT      = "#845ef7"

QSS = f"""
* {{
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    color: {TEXT};
    outline: none;
}}

QMainWindow, QWidget#root, QDialog {{
    background-color: {BG};
}}

QCheckBox {{
    color: {TEXT};
    spacing: 10px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background-color: {SURFACE};
}}
QCheckBox::indicator:hover {{
    border-color: {PRIMARY};
}}
QCheckBox::indicator:checked {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
    image: none;
}}
QCheckBox::indicator:disabled {{
    background-color: {SURFACE_ALT};
    border-color: {BORDER};
}}
QCheckBox:disabled {{
    color: {TEXT_MUTED};
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
    padding: 8px 14px;
    color: {TEXT};
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#ghost:hover  {{ background-color: {SURFACE_ALT}; border-color: {PRIMARY}; }}
QPushButton#ghost:pressed{{ background-color: {SURFACE}; }}
QPushButton#ghost:checked {{
    background-color: rgba(132, 94, 247, 0.18);
    border-color: {ACCENT};
    color: {ACCENT};
    font-weight: 600;
}}
QPushButton#ghost:disabled {{
    color: {TEXT_MUTED};
    border-color: {BORDER};
}}

QPushButton#add {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px 14px;
    color: {TEXT};
    font-size: 12px;
}}
QPushButton#add:hover  {{ background-color: {SURFACE_ALT}; border-color: {ACCENT}; color: {ACCENT}; }}
QPushButton#add:checked {{
    background-color: rgba(132, 94, 247, 0.18);
    border-color: {ACCENT};
    color: {ACCENT};
    font-weight: 600;
}}

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
QFrame#card[installed="true"] {{
    border-color: rgba(81, 207, 102, 0.35);
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
QLabel#installedBadge {{
    color: {SUCCESS};
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(81, 207, 102, 0.12);
    border: 1px solid rgba(81, 207, 102, 0.35);
    border-radius: 8px;
    padding: 6px 12px;
}}
QLabel#upgradeBadge {{
    color: {ACCENT};
    font-size: 11px;
    font-weight: 600;
    background-color: rgba(132, 94, 247, 0.14);
    border: 1px solid rgba(132, 94, 247, 0.40);
    border-radius: 6px;
    padding: 3px 8px;
}}

/* === Danger button === */
QPushButton#danger {{
    background-color: transparent;
    border: 1px solid rgba(255, 107, 107, 0.45);
    border-radius: 10px;
    padding: 10px 16px;
    color: {DANGER};
    font-weight: 600;
    font-size: 13px;
}}
QPushButton#danger:hover {{
    background-color: rgba(255, 107, 107, 0.12);
    border-color: {DANGER};
}}
QPushButton#danger:pressed {{
    background-color: rgba(255, 107, 107, 0.20);
}}
QPushButton#danger:disabled {{
    color: {TEXT_MUTED};
    border-color: {BORDER};
}}

/* === Import dialog rows === */
QLabel#importName {{
    font-size: 13px;
    font-weight: 600;
}}
QLabel#importName[pending="true"] {{
    color: {TEXT_MUTED};
    font-style: italic;
    font-weight: 500;
}}
QLabel#importId {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

/* === Selection panel === */
QWidget#selectionPanel {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QLabel#selectionTitle {{
    font-size: 14px;
    font-weight: 700;
    letter-spacing: -0.2px;
}}
QLabel#selectionPlaceholder {{
    color: {TEXT_MUTED};
    font-size: 12px;
    padding: 20px 8px;
}}
QFrame#selectionRow {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QFrame#selectionRow:hover {{
    border-color: {ACCENT};
}}
QLabel#selectionName {{
    font-size: 12px;
    font-weight: 600;
}}
QLabel#selectionId {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}
QPushButton#selectionRemove {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 13px;
    color: {TEXT_MUTED};
    font-size: 13px;
    font-weight: 600;
    padding: 0;
}}
QPushButton#selectionRemove:hover {{
    background-color: rgba(255, 107, 107, 0.15);
    border-color: {DANGER};
    color: {DANGER};
}}

/* === Tabs === */
QTabWidget#mainTabs::pane {{
    border: none;
    background-color: {BG};
}}
QTabBar {{
    background-color: {BG};
    qproperty-drawBase: 0;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: none;
    padding: 12px 22px;
    font-size: 13px;
    font-weight: 600;
}}
QTabBar::tab:hover {{
    color: {TEXT};
}}
QTabBar::tab:selected {{
    color: {PRIMARY};
    border-bottom: 2px solid {PRIMARY};
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

/* === Progress bar === */
QProgressBar {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT};
    height: 16px;
}}
QProgressBar::chunk {{
    background-color: {PRIMARY};
    border-radius: 5px;
}}

/* === Message boxes === */
QMessageBox {{
    background-color: {SURFACE};
}}
QMessageBox QLabel {{
    color: {TEXT};
}}
"""
