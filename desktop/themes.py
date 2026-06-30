from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget


THEMES = {
    "logiviande": {
        # Couleurs d'identite Logiviande, appliquees en accents seulement.
        "fond_principal": "#7A0E0E",
        "fond_secondaire": "#5C0B0B",
        "accent": "#E8A0A0",
        "bouton_primaire": "#8B1212",
        "texte": "#FFFFFF",
        "alerte": "#FF4D4D",
        "titre": "#7A0E0E",
        "accent_fort": "#8B1212",
        "accent_doux": "#E8A0A0",
    },
    "silos": {
        # Couleurs d'identite Silos, appliquees en accents seulement.
        "fond_principal": "#6B4226",
        "fond_secondaire": "#4F2F1A",
        "accent": "#B5651D",
        "bouton_primaire": "#B5651D",
        "texte": "#FFFFFF",
        "alerte": "#FF4D4D",
        "titre": "#6B4226",
        "accent_fort": "#B5651D",
        "accent_doux": "#6B4226",
    },
}

BASE_UI = {
    "fond_principal": "#D7D8D1",
    "fond_header": "#BFC2BA",
    "fond_panneau": "#C8CBC2",
    "fond_champ": "#ECEEE7",
    "fond_table": "#E4E5DE",
    "fond_table_alt": "#D4D6CF",
    "fond_journal": "#1D211C",
    "fond_section": "#343A33",
    "texte": "#1D211C",
    "texte_secondaire": "#3F463D",
    "texte_inverse": "#F1F3ED",
    "bordure": "#4D554B",
    "selection": "#BFC2BA",
    "fond_ligne_alerte": "#F1D7D7",
}


def appliquer_theme(widget_principal, nom_module: str) -> None:
    """Applique uniquement le style visuel correspondant au module selectionne."""
    theme = THEMES[_cle_theme(nom_module)]
    widget_principal.setStyleSheet(_construire_qss(theme))
    _appliquer_style_tableaux(widget_principal, theme)


def _cle_theme(nom_module: str) -> str:
    module = nom_module.lower()
    if "silos" in module:
        return "silos"
    return "logiviande"


def _construire_qss(theme: dict[str, str]) -> str:
    return f"""
QWidget#root {{
    background: {BASE_UI["fond_principal"]};
    color: {BASE_UI["texte"]};
    font-family: "Segoe UI";
    font-size: 12px;
}}

QWidget {{
    color: {BASE_UI["texte"]};
}}

QFrame#header {{
    background: {BASE_UI["fond_header"]};
    border: 1px solid {theme["accent_fort"]};
}}

QLabel#title {{
    color: {theme["titre"]};
    font-size: 18px;
    font-weight: 800;
}}

QLabel#subtitle,
QLabel#headerStatus {{
    color: {BASE_UI["texte_secondaire"]};
    font-size: 11px;
    font-weight: 600;
}}

QGroupBox {{
    background: {BASE_UI["fond_panneau"]};
    border: 1px solid {BASE_UI["bordure"]};
    color: {BASE_UI["texte"]};
    margin-top: 18px;
    padding: 10px;
    font-weight: 800;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 2px 7px;
    background: {BASE_UI["fond_section"]};
    color: {theme["accent"]};
}}

QLabel {{
    color: {BASE_UI["texte"]};
    font-weight: 600;
}}

QLabel#summary {{
    background: {BASE_UI["fond_champ"]};
    border: 1px solid {BASE_UI["bordure"]};
    color: {BASE_UI["texte"]};
    font-family: Consolas;
    padding: 8px;
}}

QLineEdit,
QComboBox {{
    background: {BASE_UI["fond_champ"]};
    border: 1px solid {BASE_UI["bordure"]};
    color: {BASE_UI["texte"]};
    padding: 5px;
}}

QLineEdit:read-only {{
    color: {BASE_UI["texte"]};
}}

QLineEdit::placeholder {{
    color: {BASE_UI["texte_secondaire"]};
}}

QComboBox QAbstractItemView {{
    background: {BASE_UI["fond_champ"]};
    color: {BASE_UI["texte"]};
    selection-background-color: {BASE_UI["selection"]};
    selection-color: {BASE_UI["texte"]};
}}

QPushButton {{
    background: {BASE_UI["fond_champ"]};
    border: 1px solid {theme["bouton_primaire"]};
    color: {BASE_UI["texte"]};
    padding: 7px;
    font-weight: 700;
}}

QPushButton:hover {{
    background: {theme["accent_doux"]};
    color: {BASE_UI["texte"]};
}}

QPushButton:pressed {{
    background: {theme["bouton_primaire"]};
    color: {theme["texte"]};
}}

QTableWidget {{
    background: {BASE_UI["fond_table"]};
    alternate-background-color: {BASE_UI["fond_table_alt"]};
    border: 1px solid {BASE_UI["bordure"]};
    color: {BASE_UI["texte"]};
    gridline-color: #8C9289;
}}

QTableWidget::item {{
    color: {BASE_UI["texte"]};
}}

QTableWidget::item:selected {{
    background: {BASE_UI["selection"]};
    color: {BASE_UI["texte"]};
}}

QHeaderView::section {{
    background: {BASE_UI["fond_section"]};
    color: {BASE_UI["texte_inverse"]};
    border: 1px solid {theme["accent_fort"]};
    padding: 5px;
    font-weight: 700;
}}

QTextEdit#log {{
    background: {BASE_UI["fond_journal"]};
    color: {BASE_UI["texte_inverse"]};
    border: 1px solid {theme["accent_fort"]};
    font-family: Consolas;
    font-size: 12px;
}}

QStatusBar {{
    background: {BASE_UI["fond_section"]};
    color: {BASE_UI["texte_inverse"]};
}}
"""


def _appliquer_style_tableaux(widget_principal, theme: dict[str, str]) -> None:
    """Garde les lignes d'alerte lisibles quel que soit le theme actif."""
    for table in widget_principal.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            est_alerte = False
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item and item.data(Qt.UserRole) == "alerte":
                    est_alerte = True
                    break

            status_column = table.columnCount() - 1
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if not item:
                    continue

                if est_alerte:
                    item.setBackground(QColor(BASE_UI["fond_ligne_alerte"]))
                    item.setForeground(QColor(BASE_UI["texte"]))
                    if column == status_column:
                        item.setBackground(QColor(theme["alerte"]))
                        item.setForeground(QColor(theme["texte"]))
                else:
                    fond_ligne = BASE_UI["fond_table_alt"] if row % 2 else BASE_UI["fond_table"]
                    item.setBackground(QColor(fond_ligne))
                    item.setForeground(QColor(BASE_UI["texte"]))
