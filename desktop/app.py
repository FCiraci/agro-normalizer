import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    from .themes import appliquer_theme
except ImportError:
    from themes import appliquer_theme


class AgroNormalizerApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Agro Normalizer")
        self.resize(1050, 650)
        self.setMinimumSize(900, 560)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        layout.addWidget(self._build_header())

        content = QHBoxLayout()
        content.setSpacing(8)
        content.addWidget(self._build_import_panel(), 0)
        content.addWidget(self._build_preview_panel(), 1)
        layout.addLayout(content, 1)

        layout.addWidget(self._build_log_panel(), 0)

        self.module_combo.currentTextChanged.connect(
            lambda module: appliquer_theme(self, module)
        )
        appliquer_theme(self, self.module_combo.currentText())

        self.statusBar().showMessage("Pret")

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("header")

        title = QLabel("AGRO-NORMALIZER")
        title.setObjectName("title")

        subtitle = QLabel("Normalisation de flux agro-alimentaires - poste local")
        subtitle.setObjectName("subtitle")

        status = QLabel("API: attente  |  Mode: simulation  |  Alertes: 0")
        status.setObjectName("headerStatus")
        status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(1)
        left.addWidget(title)
        left.addWidget(subtitle)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addLayout(left, 1)
        layout.addWidget(status, 0)

        return header

    def _build_import_panel(self) -> QWidget:
        panel = QGroupBox("Import")
        panel.setFixedWidth(300)

        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        form = QGridLayout()
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)

        self.module_combo = QComboBox()
        self.module_combo.addItems(["Logiviande - pesees", "Silos - apports"])

        self.adapter_combo = QComboBox()
        self.adapter_combo.addItems(["Mapping dur", "Mapping LLM"])

        self.source_combo = QComboBox()
        self.source_combo.addItems(["Auto", "Bizerba", "Dini Argeo", "Multivac", "Site silo"])

        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Aucun fichier selectionne")

        browse_button = QPushButton("Choisir fichier")
        browse_button.clicked.connect(self._select_file)

        form.addWidget(QLabel("Module"), 0, 0)
        form.addWidget(self.module_combo, 0, 1)
        form.addWidget(QLabel("Adapter"), 1, 0)
        form.addWidget(self.adapter_combo, 1, 1)
        form.addWidget(QLabel("Source"), 2, 0)
        form.addWidget(self.source_combo, 2, 1)
        form.addWidget(QLabel("Fichier"), 3, 0)
        form.addWidget(self.file_input, 3, 1)
        form.addWidget(browse_button, 4, 0, 1, 2)

        layout.addLayout(form)

        actions = QHBoxLayout()
        preview_button = QPushButton("Previsualiser")
        normalize_button = QPushButton("Normaliser")
        preview_button.clicked.connect(lambda: self._append_log("Previsualisation demandee"))
        normalize_button.clicked.connect(lambda: self._append_log("Normalisation simulee"))
        actions.addWidget(preview_button)
        actions.addWidget(normalize_button)
        layout.addLayout(actions)

        self.summary = QLabel(
            "Etat\n"
            "Flux: non charge\n"
            "Lignes: 0\n"
            "Alertes: 0"
        )
        self.summary.setObjectName("summary")
        self.summary.setAlignment(Qt.AlignTop)
        layout.addWidget(self.summary)

        layout.addStretch(1)
        return panel

    def _build_preview_panel(self) -> QWidget:
        panel = QGroupBox("Previsualisation")
        layout = QVBoxLayout(panel)

        self.table = QTableWidget(4, 6)
        self.table.setHorizontalHeaderLabels(
            ["Source", "Module", "Champ", "Valeur brute", "Valeur normalisee", "Statut"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setFont(QFont("Consolas", 9))

        rows = [
            ["BIZERBA_P01.csv", "Logiviande", "lot", "L-2407", "L-2407", "OK"],
            ["BIZERBA_P01.csv", "Logiviande", "poids_carcasse", "312,4 kg", "312.4", "OK"],
            ["BIZERBA_P01.csv", "Logiviande", "poids_decoupe", "198,6 kg", "198.6", "OK"],
            ["SILO_NORD.csv", "Silos", "humidite", "17,2%", "17.2", "A controler"],
        ]
        self._fill_table(rows)

        layout.addWidget(self.table)
        return panel

    def _build_log_panel(self) -> QWidget:
        panel = QGroupBox("Journal")
        panel.setFixedHeight(150)

        layout = QVBoxLayout(panel)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("log")
        self.log.setPlainText(
            "08:00:00  INIT        Application chargee\n"
            "08:00:01  SYSTEM      En attente d'un fichier source"
        )
        layout.addWidget(self.log)

        return panel

    def _select_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selectionner un fichier source",
            "",
            "Flux (*.csv *.txt *.xlsx);;Tous les fichiers (*.*)",
        )

        if not file_name:
            return

        self.file_input.setText(file_name)
        self.summary.setText(
            "Etat\n"
            "Flux: charge\n"
            "Lignes: simulation\n"
            "Alertes: simulation"
        )
        self._append_log(f"Fichier selectionne: {file_name}")

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"{timestamp}  INFO        {message}")
        self.statusBar().showMessage(message)

    def _fill_table(self, rows: list[list[str]]) -> None:
        for row_index, row in enumerate(rows):
            is_alert = row[-1] != "OK"
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if is_alert:
                    item.setData(Qt.UserRole, "alerte")
                self.table.setItem(row_index, column_index, item)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AgroNormalizerApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
