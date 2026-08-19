from PyQt6.QtWidgets import QCheckBox, QFrame, QLabel, QLineEdit, QListWidget, QPlainTextEdit, QPushButton, QSpinBox, QTabWidget, QWidget


C_BG = "#0d0f14"


C_SURFACE = "#151922"


C_SURFACE_2 = "#1c212c"


C_BORDER = "#252b38"


C_TEXT = "#e7eaf2"


C_MUTED = "#8b93a7"


C_ACCENT = "#6d7cff"


C_ACCENT_2 = "#a55cff"


C_OK = "#31d0a5"


C_ERR = "#ff5d6c"


C_WARN = "#ffb454"


STYLE = """
QWidget { background: %(bg)s; color: %(text)s;
          font-family: 'Segoe UI'; font-size: 12px; }
QLabel { background: transparent; }
QFrame#header { background: %(surface)s; border-bottom: 1px solid %(border)s; }
QFrame#panel  { background: %(surface)s; border: 1px solid %(border)s; border-radius: 14px; }
QFrame#taskCard { background: %(surface2)s; border: 1px solid %(border)s; border-radius: 14px; }
QFrame#taskCard:hover { border-color: #3a4358; background: #202634; }
QFrame#toast { background: %(surface2)s; border: 1px solid %(accent)s; border-radius: 14px; }
QLineEdit, QPlainTextEdit, QSpinBox {
    background: #11151d; border: 1px solid %(border)s; border-radius: 9px;
    padding: 8px 10px; selection-background-color: %(accent)s; color: %(text)s; }
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus { border: 1px solid %(accent)s; }
QPushButton {
    background: %(surface2)s; border: 1px solid %(border)s; border-radius: 10px;
    padding: 9px 16px; color: %(text)s; font-weight: 600; }
QPushButton:hover { background: #2a3244; border-color: #46506a; }
QPushButton:pressed { background: #333d54; }
QPushButton:disabled { color: #565d70; background: #171c26; border-color: #212734; }
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 %(accent)s, stop:1 %(accent2)s);
    border: none; color: white; }
QPushButton#primary:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7d8aff, stop:1 #b673ff); }
QPushButton#primary:disabled { background: #2a3143; color: #6a7288; }
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { border: none; margin: 0px; }
QListWidget::item:selected { background: transparent; }
QCheckBox { spacing: 8px; color: %(muted)s; outline: none; border: none;
             background: transparent; }
QCheckBox:focus { outline: none; }
QCheckBox::indicator { width: 17px; height: 17px; border-radius: 5px;
    border: 1px solid %(border)s; background: #11151d; }
QCheckBox::indicator:checked { background: %(accent)s; border-color: %(accent)s; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
QScrollBar::handle:vertical { background: #2c3446; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #3b4560; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QLabel#h1 { font-size: 19px; font-weight: 800; }
QLabel#sub { color: %(muted)s; font-size: 11px; }
QTabWidget::pane { border: none; background: transparent; }
QTabBar { background: transparent; qproperty-drawBase: 0; }
QTabBar::tab {
    background: %(surface2)s; color: %(muted)s; border: 1px solid %(border)s;
    border-bottom: none; border-top-left-radius: 10px; border-top-right-radius: 10px;
    padding: 9px 26px; margin-right: 4px; margin-top: 6px; font-weight: 600; }
QTabBar::tab:hover { color: %(text)s; background: #232a38; }
QTabBar::tab:selected {
    color: white; border-color: %(accent)s;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 %(accent)s, stop:1 %(accent2)s); }
QToolTip { background: %(surface2)s; color: %(text)s; border: 1px solid %(border)s;
           padding: 5px; border-radius: 6px; }
""" % dict(bg=C_BG, surface=C_SURFACE, surface2=C_SURFACE_2, border=C_BORDER,
           text=C_TEXT, muted=C_MUTED, accent=C_ACCENT, accent2=C_ACCENT_2)
