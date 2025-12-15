"""
Modern Professional Theme for PekoCMS
Designed for Windows with beautiful colors, shadows, and typography
"""

from PySide6 import QtGui, QtCore

# Color Palette
class Colors:
    # Primary Colors
    PRIMARY = "#1E5A96"           # Professional blue
    PRIMARY_LIGHT = "#2E7CB8"     # Lighter blue
    PRIMARY_DARK = "#164378"      # Darker blue
    
    # Accent Colors
    ACCENT = "#0078D4"            # Windows accent blue
    ACCENT_LIGHT = "#4DA3FF"      # Light accent blue
    ACCENT_DARK = "#005A9E"       # Dark accent blue
    
    # Success Color
    SUCCESS = "#107C10"           # Green
    SUCCESS_LIGHT = "#28A745"     # Light green
    
    # Warning Color
    WARNING = "#FFB900"           # Orange/Gold
    
    # Danger Color
    DANGER = "#D13438"            # Red
    
    # Neutral Colors
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F3F3F3"        # Very light gray (backgrounds)
    EXTRA_LIGHT_GRAY = "#FAFAFA"  # Extra light for alternating rows
    LIGHT_YELLOW = "#FFFEF0"      # Very light yellow for special tables
    PALE_YELLOW = "#FFFFF8"       # Pale yellow for alternating rows
    GRAY = "#A4A4A4"              # Medium gray
    DARK_GRAY = "#605E5C"         # Dark gray
    DARKER_GRAY = "#323130"       # Very dark gray
    
    # Text Colors
    TEXT_PRIMARY = "#323130"      # Dark text for readability
    TEXT_SECONDARY = "#605E5C"    # Medium gray text
    TEXT_LIGHT = "#FFFFFF"        # White text
    
    # Border Color
    BORDER = "#D2D2D2"            # Light border

# Font Configuration
class Fonts:
    # Font family
    FAMILY = "Segoe UI"
    
    # Font sizes (in points)
    TINY = 9
    SMALL = 10
    BASE = 11
    MEDIUM = 12
    LARGE = 13
    XLARGE = 14
    TITLE = 16
    HEADING = 18
    HUGE = 20

def get_stylesheet():
    """
    Returns a comprehensive stylesheet for the entire application
    """
    return f"""
    /* ===== GLOBAL STYLING ===== */
    QWidget {{
        font-family: {Fonts.FAMILY};
        font-size: {Fonts.BASE}pt;
        color: {Colors.TEXT_PRIMARY};
        background-color: {Colors.LIGHT_GRAY};
    }}
    
    QMainWindow {{
        background-color: {Colors.LIGHT_GRAY};
    }}
    
    QDialog {{
        background-color: {Colors.WHITE};
    }}
    
    /* ===== PUSH BUTTONS ===== */
    QPushButton {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        font-size: {Fonts.MEDIUM}pt;
    }}
    
    QPushButton:hover {{
        background-color: {Colors.ACCENT_LIGHT};
    }}
    
    QPushButton:pressed {{
        background-color: {Colors.ACCENT_DARK};
    }}
    
    QPushButton:disabled {{
        background-color: {Colors.LIGHT_GRAY};
        color: {Colors.TEXT_SECONDARY};
    }}
    
    /* Primary button variant */
    QPushButton#primaryButton {{
        background-color: {Colors.ACCENT};
    }}
    
    /* Success button variant */
    QPushButton#successButton {{
        background-color: {Colors.SUCCESS};
    }}
    
    QPushButton#successButton:hover {{
        background-color: {Colors.SUCCESS_LIGHT};
    }}
    
    /* Danger button variant */
    QPushButton#dangerButton {{
        background-color: {Colors.DANGER};
    }}
    
    QPushButton#dangerButton:hover {{
        background-color: #EC7063;
    }}
    
    /* ===== LINE EDITS ===== */
    QLineEdit, QDoubleSpinBox, QSpinBox, QTimeEdit, QDateEdit {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
        padding: 6px;
        font-size: {Fonts.BASE}pt;
    }}
    
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QTimeEdit:focus, QDateEdit:focus {{
        border: 2px solid {Colors.ACCENT};
        outline: none;
    }}
    
    /* ===== TEXT EDITS ===== */
    QTextEdit, QPlainTextEdit {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
        padding: 6px;
        font-size: {Fonts.BASE}pt;
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {Colors.ACCENT};
    }}
    
    /* ===== COMBO BOXES ===== */
    QComboBox {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
        padding: 6px;
        font-size: {Fonts.BASE}pt;
    }}
    
    QComboBox:focus {{
        border: 2px solid {Colors.ACCENT};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        width: 0;
        height: 0;
    }}
    
    /* ===== LABELS ===== */
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.BASE}pt;
    }}
    
    QLabel#heading {{
        font-size: {Fonts.HEADING}pt;
        font-weight: bold;
        color: {Colors.PRIMARY};
    }}
    
    QLabel#subheading {{
        font-size: {Fonts.LARGE}pt;
        font-weight: bold;
        color: {Colors.PRIMARY_LIGHT};
    }}
    
    /* ===== GROUP BOXES ===== */
    QGroupBox {{
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
        background-color: {Colors.WHITE};
        font-weight: bold;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
        color: {Colors.PRIMARY};
    }}
    
    /* ===== FRAMES ===== */
    QFrame {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
    }}
    
    /* ===== TABLES ===== */
    QTableWidget, QTableView {{
        background-color: {Colors.WHITE};
        alternate-background-color: {Colors.EXTRA_LIGHT_GRAY};
        gridline-color: {Colors.BORDER};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
    }}
    
    QTableWidget::item {{
        padding: 4px;
        border: none;
        color: {Colors.TEXT_PRIMARY};
        background-color: {Colors.WHITE};
    }}
    
    QTableWidget::item:alternate {{
        background-color: {Colors.EXTRA_LIGHT_GRAY};
    }}
    
    QTableWidget::item:selected {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
    }}
    
    QHeaderView::section {{
        background-color: {Colors.PRIMARY};
        color: {Colors.TEXT_LIGHT};
        padding: 6px 4px;
        border: 1px solid {Colors.BORDER};
        font-weight: bold;
    }}
    
    /* ===== LIST VIEWS ===== */
    QListWidget, QListView {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
    }}
    
    QListWidget::item:selected, QListView::item:selected {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
    }}
    
    /* ===== TREE VIEWS ===== */
    QTreeWidget, QTreeView {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
    }}
    
    QTreeWidget::item:selected, QTreeView::item:selected {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
    }}
    
    /* ===== TABS ===== */
    QTabWidget::pane {{
        border: 1px solid {Colors.BORDER};
    }}
    
    QTabBar::tab {{
        background-color: {Colors.LIGHT_GRAY};
        color: {Colors.TEXT_PRIMARY};
        padding: 8px 16px;
        margin: 0;
        border-bottom: 2px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        background-color: {Colors.WHITE};
        color: {Colors.ACCENT};
        border-bottom: 2px solid {Colors.ACCENT};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: #D5DBDB;
    }}
    
    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        border: none;
        background-color: {Colors.LIGHT_GRAY};
        width: 12px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {Colors.GRAY};
        border-radius: 6px;
        min-height: 20px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {Colors.DARK_GRAY};
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background-color: {Colors.LIGHT_GRAY};
        height: 12px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {Colors.GRAY};
        border-radius: 6px;
        min-width: 20px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {Colors.DARK_GRAY};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}
    
    /* ===== SPINBOX AND SCROLL CONTROLS ===== */
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        border: none;
        background-color: {Colors.LIGHT_GRAY};
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        border: none;
        background-color: {Colors.LIGHT_GRAY};
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {Colors.GRAY};
    }}
    
    /* ===== MENU BAR AND MENUS ===== */
    QMenuBar {{
        background-color: {Colors.LIGHT_GRAY};
        color: {Colors.TEXT_PRIMARY};
        border-bottom: 1px solid {Colors.BORDER};
    }}
    
    QMenuBar::item:selected {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
    }}
    
    QMenu {{
        background-color: {Colors.WHITE};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
    }}
    
    QMenu::item:selected {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
    }}
    
    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {Colors.PRIMARY};
        color: {Colors.TEXT_LIGHT};
        border-top: 1px solid {Colors.BORDER};
    }}
    
    /* ===== DIALOGS ===== */
    QMessageBox QLabel {{
        color: {Colors.TEXT_PRIMARY};
    }}
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {{
        background-color: {Colors.BORDER};
    }}
    
    QSplitter::handle:hover {{
        background-color: {Colors.GRAY};
    }}
    
    /* ===== PROGRESS BAR ===== */
    QProgressBar {{
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
        background-color: {Colors.LIGHT_GRAY};
    }}
    
    QProgressBar::chunk {{
        background-color: {Colors.ACCENT};
        border-radius: 3px;
    }}
    
    /* ===== SLIDERS ===== */
    QSlider::groove:horizontal {{
        border: 1px solid {Colors.BORDER};
        height: 6px;
        background: {Colors.LIGHT_GRAY};
        margin: 2px 0;
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {Colors.ACCENT};
        border: 1px solid {Colors.ACCENT_DARK};
        width: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {Colors.ACCENT_LIGHT};
    }}
    
    /* ===== CHECK BOXES ===== */
    QCheckBox {{
        spacing: 5px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
    }}
    
    QCheckBox::indicator:unchecked {{
        background-color: {Colors.WHITE};
        border: 2px solid {Colors.BORDER};
        border-radius: 3px;
    }}
    
    QCheckBox::indicator:unchecked:hover {{
        border: 2px solid {Colors.ACCENT};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {Colors.ACCENT};
        border: 2px solid {Colors.ACCENT};
        border-radius: 3px;
    }}
    
    /* ===== RADIO BUTTONS ===== */
    QRadioButton {{
        spacing: 5px;
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
    }}
    
    QRadioButton::indicator:unchecked {{
        background-color: {Colors.WHITE};
        border: 2px solid {Colors.BORDER};
        border-radius: 9px;
    }}
    
    QRadioButton::indicator:unchecked:hover {{
        border: 2px solid {Colors.ACCENT};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {Colors.WHITE};
        border: 2px solid {Colors.ACCENT};
        border-radius: 9px;
    }}
    
    QRadioButton::indicator:checked::after {{
        width: 8px;
        height: 8px;
        border-radius: 4px;
        image: none;
        background-color: {Colors.ACCENT};
    }}
    
    /* ===== SPECIAL YELLOW TABLE (for selected items) ===== */
    QTableWidget#yellowTable, QTableView#yellowTable {{
        background-color: {Colors.LIGHT_YELLOW};
        alternate-background-color: {Colors.PALE_YELLOW};
        gridline-color: {Colors.BORDER};
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
    }}
    
    QTableWidget#yellowTable::item {{
        padding: 4px;
        border: none;
        color: {Colors.TEXT_PRIMARY};
        background-color: {Colors.LIGHT_YELLOW};
    }}
    
    QTableWidget#yellowTable::item:alternate {{
        background-color: {Colors.PALE_YELLOW};
    }}
    
    QTableWidget#yellowTable::item:selected {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_LIGHT};
    }}
    
    /* ===== LIGHT HEADER ===== */
    QFrame#lightHeader {{
        background-color: {Colors.WHITE};
        border-bottom: 1px solid {Colors.BORDER};
    }}
    
    /* ===== LIGHT AVAILABLE TESTS GROUP ===== */
    QGroupBox#availableTestsGroup {{
        background-color: {Colors.WHITE};
    }}
    """

def apply_stylesheet(app):
    """
    Apply the stylesheet to the entire application
    
    Usage:
        from theme import apply_stylesheet
        app = QtWidgets.QApplication(sys.argv)
        apply_stylesheet(app)
    """
    from PySide6 import QtWidgets
    app.setStyle('Fusion')
    app.setStyleSheet(get_stylesheet())

def set_window_appearance(window, title="Nidaan"):
    """
    Set window appearance with modern styling
    
    Usage:
        set_window_appearance(my_window)
    """
    window.setWindowTitle(title)
    # Modern icon if available
    try:
        from PySide6 import QtGui
        window.setWindowIcon(QtGui.QIcon())
    except:
        pass

def get_palette():
    """
    Get a QPalette object with theme colors
    """
    from PySide6 import QtGui, QtCore
    
    palette = QtGui.QPalette()
    
    # Window colors
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(Colors.WHITE))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(Colors.TEXT_PRIMARY))
    
    # Base colors
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(Colors.WHITE))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(Colors.LIGHT_GRAY))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(Colors.TEXT_PRIMARY))
    
    # Button colors
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(Colors.ACCENT))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(Colors.TEXT_LIGHT))
    
    # Highlight colors
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(Colors.ACCENT))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(Colors.TEXT_LIGHT))
    
    return palette
