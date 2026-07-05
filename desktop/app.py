import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

try:
    from .themes import BASE_UI, appliquer_theme
except ImportError:
    from themes import BASE_UI, appliquer_theme


# Bloc de configuration des colonnes selon le module actif.
TABLE_COLUMNS = {
    "Logiviande": ["Lot", "Date", "Poids carcasse", "Poids découpe", "Classement", "Rendement%", "Alerte"],
    "Silos": ["Apport", "Date", "Site", "Céréale", "Poids net", "Humidité%", "Alerte"],
}


# Bloc principal de la fenêtre unique.
class AgroNormalizerApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AGRO-NORMALIZER")
        self.resize(1220, 780)
        self.setMinimumSize(1024, 680)

        self.current_module = "Logiviande"

        # Bloc racine et disposition générale.
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Bloc d'en-tête avec le titre et le sélecteur de module.
        layout.addWidget(self._build_header())

        # Bloc central avec import et résultats.
        central = QHBoxLayout()
        central.setSpacing(12)
        central.addWidget(self._build_import_section(), 0)
        central.addWidget(self._build_results_section(), 1)
        layout.addLayout(central, 1)

        # Bloc journal en bas de la fenêtre.
        layout.addWidget(self._build_log_section(), 0)

        # Bloc de connexion des signaux et initialisation visuelle.
        self._connect_signals()
        appliquer_theme(self, self.current_module)
        self._update_table_columns(self.current_module)
        self._append_log(self.current_module, "Interface prête")

    # Bloc d'en-tête.
    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("header")

        title = QLabel("AGRO-NORMALIZER")
        title.setObjectName("title")

        subtitle = QLabel("Supervision locale des flux Logiviande et Silos")
        subtitle.setObjectName("subtitle")

        self.module_combo = QComboBox()
        self.module_combo.addItems(["Logiviande", "Silos"])

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(2)
        left.addWidget(title)
        left.addWidget(subtitle)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(4)
        right.addWidget(QLabel("Module actif"))
        right.addWidget(self.module_combo)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        layout.addLayout(left, 1)
        layout.addLayout(right, 0)

        return header

    # Bloc d'import.
    def _build_import_section(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("importPanel")
        panel.setMinimumWidth(330)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Import")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.choose_file_button = QPushButton("Choisir un fichier")
        layout.addWidget(self.choose_file_button)

        self.file_path_label = QLabel("Aucun fichier sélectionné")
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setObjectName("filePathLabel")
        layout.addWidget(self.file_path_label)

        self.llm_checkbox = QCheckBox("Utiliser l'Adapter LLM")
        layout.addWidget(self.llm_checkbox)

        self.process_button = QPushButton("Traiter le fichier")
        layout.addWidget(self.process_button)

        layout.addStretch(1)
        return panel

    # Bloc de résultats.
    def _build_results_section(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("resultsPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Résultats")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.results_table = QTableWidget(0, len(TABLE_COLUMNS[self.current_module]))
        self.results_table.setHorizontalHeaderLabels(TABLE_COLUMNS[self.current_module])
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setFont(QFont("Consolas", 9))
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table, 1)

        return panel

    # Bloc journal.
    def _build_log_section(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("logPanel")
        panel.setMinimumHeight(170)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Journal")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("log")
        layout.addWidget(self.log, 1)

        return panel

    # Bloc de connexion des signaux.
    def _connect_signals(self) -> None:
        self.module_combo.currentTextChanged.connect(self._on_module_changed)
        self.choose_file_button.clicked.connect(self._choose_file)
        self.process_button.clicked.connect(self._process_file)

    # Bloc de changement de module.
    def _on_module_changed(self, module: str) -> None:
        self.current_module = module
        appliquer_theme(self, module)
        self._update_table_columns(module)
        self._append_log(module, f"Module actif changé vers {module}")

    # Bloc de sélection de fichier.
    def _choose_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un fichier",
            "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)",
        )

        if not file_path:
            self._append_log(self.current_module, "Sélection de fichier annulée")
            return

        self.file_path_label.setText(file_path)
        self._append_log(self.current_module, f"Fichier sélectionné: {file_path}")

    # Bloc de traitement simulé.
    def _process_file(self) -> None:
        if self.file_path_label.text() == "Aucun fichier sélectionné":
            self._append_log(self.current_module, "Aucun fichier à traiter")
            return

        mode_llm = "activé" if self.llm_checkbox.isChecked() else "désactivé"
        self._append_log(self.current_module, f"Traitement demandé avec Adapter LLM {mode_llm}")

    # Bloc d'adaptation des colonnes.
    def _update_table_columns(self, module: str) -> None:
        columns = TABLE_COLUMNS[module]
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # Bloc d'écriture du journal.
    def _append_log(self, module: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"{timestamp} — [{module}] — {message}")


# Bloc d'entrée de l'application.
def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AgroNormalizerApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
