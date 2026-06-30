import sys

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
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class OperatorConsole(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Agro Normalizer - Console operateur")
        self.resize(1280, 760)
        self.setMinimumSize(1040, 640)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        layout.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setSpacing(8)
        body.addWidget(self._build_control_panel(), 1)
        body.addWidget(self._build_supervision_panel(), 3)
        body.addWidget(self._build_alarm_panel(), 1)
        layout.addLayout(body, 1)

        layout.addWidget(self._build_log_panel())

        self.statusBar().showMessage("Console prete - aucun flux traite")

    def _build_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("header")
        layout = QGridLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setHorizontalSpacing(8)

        title = QLabel("AGRO-NORMALIZER / CONSOLE OPERATEUR")
        title.setObjectName("mainTitle")
        subtitle = QLabel("Moteur de normalisation heterogene - mode simulation")
        subtitle.setObjectName("smallLabel")

        title_block = QVBoxLayout()
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        layout.addLayout(title_block, 0, 0, 2, 1)

        layout.addWidget(self._status_tile("API LOTS", "ATTENTE", "warn"), 0, 1)
        layout.addWidget(self._status_tile("MODE", "LOCAL", "ok"), 0, 2)
        layout.addWidget(self._status_tile("FILE", "004 FLUX", "info"), 0, 3)
        layout.addWidget(self._status_tile("ALARMES", "003", "alarm"), 0, 4)

        return frame

    def _status_tile(self, label: str, value: str, state: str) -> QWidget:
        tile = QFrame()
        tile.setObjectName("statusTile")

        lamp = QLabel()
        lamp.setObjectName(f"lamp_{state}")
        lamp.setFixedSize(14, 14)

        label_widget = QLabel(label)
        label_widget.setObjectName("smallLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("statusValue")

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(lamp)
        row.addWidget(value_widget, 1)

        layout = QVBoxLayout(tile)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(2)
        layout.addWidget(label_widget)
        layout.addLayout(row)

        return tile

    def _build_control_panel(self) -> QWidget:
        group = QGroupBox("PUPITRE")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        module_box = QGroupBox("MODULE")
        module_layout = QVBoxLayout(module_box)
        logiviande_radio = QRadioButton("Logiviande - pesees")
        logiviande_radio.setChecked(True)
        module_layout.addWidget(logiviande_radio)
        module_layout.addWidget(QRadioButton("Silos - apports cerealiers"))
        layout.addWidget(module_box)

        adapter_box = QGroupBox("ADAPTER")
        adapter_layout = QVBoxLayout(adapter_box)
        hard_mapping_radio = QRadioButton("Mapping dur")
        hard_mapping_radio.setChecked(True)
        adapter_layout.addWidget(hard_mapping_radio)
        adapter_layout.addWidget(QRadioButton("Mapping LLM"))
        layout.addWidget(adapter_box)

        source_box = QGroupBox("SOURCE")
        source_layout = QGridLayout(source_box)
        profile = QComboBox()
        profile.addItems(["Auto", "Bizerba", "Dini Argeo", "Multivac", "Site silo"])
        self.file_field = QLineEdit("Aucun fichier charge")
        self.file_field.setReadOnly(True)
        browse = QPushButton("PARCOURIR")
        browse.clicked.connect(self._select_file)
        source_layout.addWidget(QLabel("Profil"), 0, 0)
        source_layout.addWidget(profile, 0, 1)
        source_layout.addWidget(QLabel("Fichier"), 1, 0)
        source_layout.addWidget(self.file_field, 1, 1)
        source_layout.addWidget(browse, 2, 0, 1, 2)
        layout.addWidget(source_box)

        action_box = QGroupBox("CYCLE")
        action_layout = QGridLayout(action_box)
        start = QPushButton("LANCER CYCLE")
        stop = QPushButton("ARRET TRAITEMENT")
        validate = QPushButton("VALIDER LOT")
        start.clicked.connect(lambda: self._append_log("Cycle manuel demande par operateur"))
        stop.clicked.connect(lambda: self._append_log("Arret traitement demande"))
        validate.clicked.connect(lambda: self._append_log("Validation lot simulee"))
        action_layout.addWidget(start, 0, 0)
        action_layout.addWidget(stop, 1, 0)
        action_layout.addWidget(validate, 2, 0)
        layout.addWidget(action_box)

        layout.addStretch(1)
        return group

    def _build_supervision_panel(self) -> QWidget:
        group = QGroupBox("SUPERVISION FLUX")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        metrics = QGridLayout()
        metrics.setSpacing(8)
        metrics.addWidget(self._metric("FICHIERS RECUS", "004"), 0, 0)
        metrics.addWidget(self._metric("LIGNES NORMALISEES", "501"), 0, 1)
        metrics.addWidget(self._metric("CONFIANCE LLM", "91%"), 0, 2)
        metrics.addWidget(self._metric("CYCLE", "00:14"), 0, 3)
        layout.addLayout(metrics)

        self.flow_table = QTableWidget(4, 6)
        self.flow_table.setHorizontalHeaderLabels(
            ["Source", "Module", "Adapter", "Lignes", "Statut", "Alerte"]
        )
        flow_rows = [
            ["BIZERBA_P01_2026-06-30.csv", "Logiviande", "Mapping dur", "128", "Pret", "Rendement bas"],
            ["DINIA_P02_EXPORT.txt", "Logiviande", "LLM", "64", "A controler", "Colonnes inconnues"],
            ["SILO_NORD_APPORTS.xlsx", "Silos", "Mapping dur", "217", "Pret", "Humidite haute"],
            ["SITE_OUEST_20260630.csv", "Silos", "LLM", "92", "Simulation", "Aucune"],
        ]
        self._fill_table(self.flow_table, flow_rows)
        layout.addWidget(self.flow_table, 2)

        self.mapping_table = QTableWidget(4, 4)
        self.mapping_table.setHorizontalHeaderLabels(
            ["Champ normalise", "Mapping dur", "Mapping LLM", "Confiance"]
        )
        mapping_rows = [
            ["lot", "Lot", "numero_lot", "96%"],
            ["poids_carcasse", "Poids carc.", "kg_carcasse", "91%"],
            ["poids_decoupe", "Poids decoupe", "kg_decoupe", "89%"],
            ["classement", "EUROP", "classe_europ", "94%"],
        ]
        self._fill_table(self.mapping_table, mapping_rows)
        layout.addWidget(self.mapping_table, 1)

        return group

    def _metric(self, label: str, value: str) -> QWidget:
        frame = QFrame()
        frame.setObjectName("metric")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        caption = QLabel(label)
        caption.setObjectName("smallLabel")
        number = QLabel(value)
        number.setObjectName("metricValue")
        layout.addWidget(caption)
        layout.addWidget(number)
        return frame

    def _build_alarm_panel(self) -> QWidget:
        group = QGroupBox("ALARMES")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        alarms = [
            ("HAUT", "Logiviande / LOT-2407", "Rendement 61.8%"),
            ("MOYEN", "Silos / AP-8831", "Humidite 17.2%"),
            ("MOYEN", "Logiviande / SRC-DINIA", "Format source atypique"),
        ]
        for level, reference, message in alarms:
            layout.addWidget(self._alarm_row(level, reference, message))

        channels = QGroupBox("CANAUX")
        channels_layout = QGridLayout(channels)
        channels_layout.addWidget(self._status_tile("PYTHON ETL", "OK", "ok"), 0, 0)
        channels_layout.addWidget(self._status_tile("SPRING API", "WAIT", "warn"), 0, 1)
        channels_layout.addWidget(self._status_tile("LLM", "SIM", "info"), 1, 0)
        channels_layout.addWidget(self._status_tile("H2", "OK", "ok"), 1, 1)
        layout.addWidget(channels)

        layout.addStretch(1)
        return group

    def _alarm_row(self, level: str, reference: str, message: str) -> QWidget:
        frame = QFrame()
        frame.setObjectName("alarmRow")
        layout = QGridLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        level_label = QLabel(level)
        level_label.setObjectName("alarmHigh" if level == "HAUT" else "alarmMedium")
        level_label.setAlignment(Qt.AlignCenter)
        level_label.setFixedWidth(68)

        text = QLabel(f"{reference}\n{message}")
        text.setObjectName("alarmText")

        time = QLabel("11:24")
        time.setObjectName("alarmTime")
        time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(level_label, 0, 0)
        layout.addWidget(text, 0, 1)
        layout.addWidget(time, 0, 2)

        return frame

    def _build_log_panel(self) -> QWidget:
        group = QGroupBox("JOURNAL MACHINE")
        layout = QVBoxLayout(group)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("machineLog")
        self.log.setPlainText(
            "\n".join(
                [
                    "11:24:12  CYCLE INIT      profil=Auto module=Logiviande adapter=Mapping dur",
                    "11:24:13  SOURCE SCAN     4 flux detectes dans data/samples",
                    "11:24:14  NORMALIZER      mapping candidat charge",
                    "11:24:15  CONTROL         3 alertes en attente de validation",
                    "11:24:16  API             canal Spring Boot non connecte dans cette maquette",
                ]
            )
        )
        layout.addWidget(self.log)
        return group

    def _select_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selectionner un flux source",
            "",
            "Flux (*.csv *.txt *.xlsx);;Tous les fichiers (*.*)",
        )
        if file_name:
            self.file_field.setText(file_name)
            self._append_log(f"Fichier selectionne: {file_name}")

    def _append_log(self, message: str) -> None:
        self.log.append(f"11:25:00  OPERATEUR      {message}")
        self.statusBar().showMessage(message)

    def _fill_table(self, table: QTableWidget, rows: list[list[str]]) -> None:
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setFont(QFont("Consolas", 9))

        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_index, column_index, item)


STYLE = """
QWidget#root {
    background: #d4d5cf;
    color: #191c18;
    font-family: "Segoe UI";
    font-size: 12px;
}

QFrame#header,
QGroupBox {
    background: #c4c6be;
    border: 2px solid #555a51;
}

QGroupBox {
    margin-top: 18px;
    padding: 9px;
    font-weight: 800;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 3px 8px;
    background: #30342f;
    color: #eef0e8;
}

QLabel#mainTitle {
    font-size: 17px;
    font-weight: 900;
    color: #161915;
}

QLabel#smallLabel {
    color: #555b52;
    font-size: 10px;
    font-weight: 900;
}

QLabel#statusValue,
QLabel#metricValue {
    color: #10130f;
    font-family: Consolas;
    font-size: 17px;
    font-weight: 900;
}

QFrame#statusTile,
QFrame#metric {
    background: #dedfd9;
    border: 1px solid #555a51;
}

QLabel#lamp_ok,
QLabel#lamp_warn,
QLabel#lamp_alarm,
QLabel#lamp_info {
    border: 1px solid #10130f;
}

QLabel#lamp_ok {
    background: #287a3e;
}

QLabel#lamp_warn {
    background: #b48618;
}

QLabel#lamp_alarm {
    background: #b13d2a;
}

QLabel#lamp_info {
    background: #28536b;
}

QPushButton {
    background: #e0e1dc;
    border: 2px solid #565b52;
    padding: 8px;
    font-weight: 900;
}

QPushButton:hover {
    background: #f2f3ed;
    border-color: #20241f;
}

QPushButton:pressed {
    background: #b7bab1;
}

QLineEdit,
QComboBox {
    background: #eceee7;
    border: 1px solid #555a51;
    padding: 5px;
    font-family: Consolas;
}

QTableWidget {
    background: #e3e4de;
    alternate-background-color: #d2d5cd;
    border: 2px solid #555a51;
    gridline-color: #8b9087;
    font-family: Consolas;
}

QHeaderView::section {
    background: #30342f;
    color: #eef0e8;
    border: 1px solid #555a51;
    padding: 5px;
    font-weight: 900;
}

QFrame#alarmRow {
    background: #dedfd9;
    border: 1px solid #555a51;
}

QLabel#alarmHigh {
    background: #b13d2a;
    color: white;
    font-family: Consolas;
    font-weight: 900;
    padding: 8px;
}

QLabel#alarmMedium {
    background: #b48618;
    color: #15150f;
    font-family: Consolas;
    font-weight: 900;
    padding: 8px;
}

QLabel#alarmText {
    padding: 6px;
    font-weight: 800;
}

QLabel#alarmTime {
    padding: 6px;
    font-family: Consolas;
    font-weight: 900;
}

QTextEdit#machineLog {
    background: #171a17;
    color: #d9e1d3;
    border: 2px solid #555a51;
    font-family: Consolas;
    font-size: 12px;
}

QStatusBar {
    background: #30342f;
    color: #eef0e8;
    font-family: Consolas;
}
"""


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = OperatorConsole()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
