import sys
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QMessageBox,
    QFrame,
    QHeaderView,
    QStackedWidget,
    QFileDialog,
)


from core.scanner import PortScanner
from core.history import save_scan, get_history


# ============================================================
# SCAN WORKER
# ============================================================

class ScanWorker(QThread):

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, target, start_port, end_port):
        super().__init__()

        self.target = target
        self.start_port = start_port
        self.end_port = end_port

    def run(self):

        try:

            scanner = PortScanner(
                target=self.target,
                start_port=self.start_port,
                end_port=self.end_port
            )

            result = scanner.scan()

            self.finished.emit(result)

        except Exception as e:

            self.error.emit(str(e))


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "NetScan — Network Security Scanner"
        )

        self.setMinimumSize(
            1150,
            750
        )

        self.worker = None
        self.last_result = None

        self.setup_ui()
        self.apply_styles()

    # ========================================================
    # MAIN UI
    # ========================================================

    def setup_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            245
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            20,
            28,
            20,
            20
        )

        sidebar_layout.setSpacing(
            8
        )

        # Logo

        logo = QLabel(
            "◉ NetScan"
        )

        logo.setObjectName(
            "logo"
        )

        logo.setFont(
            QFont(
                "Segoe UI",
                22,
                QFont.Bold
            )
        )

        subtitle = QLabel(
            "NETWORK SECURITY"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        sidebar_layout.addWidget(
            logo
        )

        sidebar_layout.addWidget(
            subtitle
        )

        sidebar_layout.addSpacing(
            30
        )

        # Navigation

        self.dashboard_button = self.create_nav_button(
            "▣   Dashboard"
        )

        self.scanner_button = self.create_nav_button(
            "◉   Port Scanner"
        )

        self.history_button = self.create_nav_button(
            "◷   Scan History"
        )

        self.reports_button = self.create_nav_button(
            "▤   Reports"
        )

        self.settings_button = self.create_nav_button(
            "⚙   Settings"
        )

        self.about_button = self.create_nav_button(
            "ⓘ   About"
        )

        nav_buttons = [
            self.dashboard_button,
            self.scanner_button,
            self.history_button,
            self.reports_button,
            self.settings_button,
            self.about_button
        ]

        for button in nav_buttons:

            sidebar_layout.addWidget(
                button
            )

        sidebar_layout.addStretch()

        # System status

        status_frame = QFrame()

        status_frame.setObjectName(
            "statusFrame"
        )

        status_layout = QVBoxLayout(
            status_frame
        )

        status_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        status_title = QLabel(
            "SYSTEM STATUS"
        )

        status_title.setObjectName(
            "statusTitle"
        )

        self.status_label = QLabel(
            "●  System Ready"
        )

        self.status_label.setObjectName(
            "statusReady"
        )

        status_layout.addWidget(
            status_title
        )

        status_layout.addWidget(
            self.status_label
        )

        sidebar_layout.addWidget(
            status_frame
        )

        main_layout.addWidget(
            sidebar
        )

        # ====================================================
        # CONTENT
        # ====================================================

        self.pages = QStackedWidget()

        self.dashboard_page = (
            self.create_dashboard_page()
        )

        self.scanner_page = (
            self.create_scanner_page()
        )

        self.history_page = (
            self.create_history_page()
        )

        self.reports_page = (
            self.create_reports_page()
        )

        self.settings_page = (
            self.create_settings_page()
        )

        self.about_page = (
            self.create_about_page()
        )

        self.pages.addWidget(
            self.dashboard_page
        )

        self.pages.addWidget(
            self.scanner_page
        )

        self.pages.addWidget(
            self.history_page
        )

        self.pages.addWidget(
            self.reports_page
        )

        self.pages.addWidget(
            self.settings_page
        )

        self.pages.addWidget(
            self.about_page
        )

        main_layout.addWidget(
            self.pages
        )

        # Navigation connections

        self.dashboard_button.clicked.connect(
            lambda: self.navigate(
                0,
                self.dashboard_button
            )
        )

        self.scanner_button.clicked.connect(
            lambda: self.navigate(
                1,
                self.scanner_button
            )
        )

        self.history_button.clicked.connect(
            self.show_history
        )

        self.reports_button.clicked.connect(
            lambda: self.navigate(
                3,
                self.reports_button
            )
        )

        self.settings_button.clicked.connect(
            lambda: self.navigate(
                4,
                self.settings_button
            )
        )

        self.about_button.clicked.connect(
            lambda: self.navigate(
                5,
                self.about_button
            )
        )

        self.set_active_button(
            self.dashboard_button
        )

    # ========================================================
    # NAV BUTTON
    # ========================================================

    def create_nav_button(self, text):

        button = QPushButton(
            text
        )

        button.setObjectName(
            "navButton"
        )

        button.setMinimumHeight(
            45
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        return button

    # ========================================================
    # NAVIGATION
    # ========================================================

    def navigate(self, index, button):

        self.pages.setCurrentIndex(
            index
        )

        self.set_active_button(
            button
        )

    def set_active_button(self, active):

        buttons = [
            self.dashboard_button,
            self.scanner_button,
            self.history_button,
            self.reports_button,
            self.settings_button,
            self.about_button
        ]

        for button in buttons:

            button.setProperty(
                "active",
                button is active
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def create_dashboard_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(
            18
        )

        heading = QLabel(
            "Security Dashboard"
        )

        heading.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Monitor network scanning activity and security findings."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            heading
        )

        layout.addWidget(
            description
        )

        # Statistic cards

        cards = QHBoxLayout()

        cards.setSpacing(
            14
        )

        self.dashboard_target = (
            self.create_stat_card(
                "TARGET",
                "—"
            )
        )

        self.dashboard_ports = (
            self.create_stat_card(
                "PORTS SCANNED",
                "0"
            )
        )

        self.dashboard_open = (
            self.create_stat_card(
                "OPEN PORTS",
                "0"
            )
        )

        self.dashboard_duration = (
            self.create_stat_card(
                "SCAN TIME",
                "—"
            )
        )

        cards.addWidget(
            self.dashboard_target
        )

        cards.addWidget(
            self.dashboard_ports
        )

        cards.addWidget(
            self.dashboard_open
        )

        cards.addWidget(
            self.dashboard_duration
        )

        layout.addLayout(
            cards
        )

        findings_title = QLabel(
            "Recent Findings"
        )

        findings_title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            findings_title
        )

        self.dashboard_table = (
            self.create_table(
                [
                    "Port",
                    "State",
                    "Service"
                ]
            )
        )

        layout.addWidget(
            self.dashboard_table
        )

        return page

    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(
        self,
        title,
        value
    ):

        card = QFrame()

        card.setObjectName(
            "statCard"
        )

        card_layout = QVBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "statTitle"
        )

        value_label = QLabel(
            value
        )

        value_label.setObjectName(
            "statValue"
        )

        card_layout.addWidget(
            title_label
        )

        card_layout.addWidget(
            value_label
        )

        card.value_label = value_label

        return card

    # ========================================================
    # PORT SCANNER
    # ========================================================

    def create_scanner_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(
            16
        )

        heading = QLabel(
            "Port Scanner"
        )

        heading.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Identify open TCP ports and common services on authorized systems."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            heading
        )

        layout.addWidget(
            description
        )

        # Scanner controls

        control_frame = QFrame()

        control_frame.setObjectName(
            "controlCard"
        )

        control_layout = QHBoxLayout(
            control_frame
        )

        control_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        target_label = QLabel(
            "Target"
        )

        self.target_input = QLineEdit()

        self.target_input.setPlaceholderText(
            "127.0.0.1 or hostname"
        )

        self.target_input.setText(
            "127.0.0.1"
        )

        start_label = QLabel(
            "Start"
        )

        self.start_port = QSpinBox()

        self.start_port.setRange(
            1,
            65535
        )

        self.start_port.setValue(
            1
        )

        end_label = QLabel(
            "End"
        )

        self.end_port = QSpinBox()

        self.end_port.setRange(
            1,
            65535
        )

        self.end_port.setValue(
            1024
        )

        self.scan_button = QPushButton(
            "▶  START SCAN"
        )

        self.scan_button.setObjectName(
            "scanButton"
        )

        self.scan_button.setMinimumHeight(
            42
        )

        self.scan_button.setCursor(
            Qt.PointingHandCursor
        )

        self.scan_button.clicked.connect(
            self.start_scan
        )

        control_layout.addWidget(
            target_label
        )

        control_layout.addWidget(
            self.target_input,
            2
        )

        control_layout.addWidget(
            start_label
        )

        control_layout.addWidget(
            self.start_port
        )

        control_layout.addWidget(
            end_label
        )

        control_layout.addWidget(
            self.end_port
        )

        control_layout.addWidget(
            self.scan_button
        )

        layout.addWidget(
            control_frame
        )

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            0
        )

        self.progress.setVisible(
            False
        )

        layout.addWidget(
            self.progress
        )

        # Summary

        summary = QHBoxLayout()

        self.target_summary = QLabel(
            "TARGET: —"
        )

        self.ip_summary = QLabel(
            "IP: —"
        )

        self.open_summary = QLabel(
            "OPEN PORTS: 0"
        )

        summary.addWidget(
            self.target_summary
        )

        summary.addWidget(
            self.ip_summary
        )

        summary.addWidget(
            self.open_summary
        )

        summary.addStretch()

        layout.addLayout(
            summary
        )

        results_title = QLabel(
            "Scan Results"
        )

        results_title.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            results_title
        )

        self.results_table = (
            self.create_table(
                [
                    "Port",
                    "State",
                    "Service"
                ]
            )
        )

        layout.addWidget(
            self.results_table
        )

        warning = QLabel(
            "⚠  Only scan systems you own or have explicit permission to test."
        )

        warning.setObjectName(
            "warning"
        )

        warning.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            warning
        )

        return page

    # ========================================================
    # TABLE
    # ========================================================

    def create_table(self, headers):

        table = QTableWidget()

        table.setColumnCount(
            len(headers)
        )

        table.setHorizontalHeaderLabels(
            headers
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        table.verticalHeader().setVisible(
            False
        )

        return table

    # ========================================================
    # HISTORY
    # ========================================================

    def create_history_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(
            16
        )

        heading = QLabel(
            "Scan History"
        )

        heading.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Review previous network scans stored by NetScan."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            heading
        )

        layout.addWidget(
            description
        )

        refresh_button = QPushButton(
            "↻  REFRESH HISTORY"
        )

        refresh_button.setMaximumWidth(
            190
        )

        refresh_button.clicked.connect(
            self.show_history
        )

        layout.addWidget(
            refresh_button
        )

        self.history_table = (
            self.create_table(
                [
                    "Date",
                    "Target",
                    "IP",
                    "Port Range",
                    "Ports",
                    "Open",
                    "Duration"
                ]
            )
        )

        layout.addWidget(
            self.history_table
        )

        return page

    # ========================================================
    # REPORTS
    # ========================================================

    def create_reports_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(
            18
        )

        heading = QLabel(
            "Security Reports"
        )

        heading.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "Generate and export a report from the latest scan."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            heading
        )

        layout.addWidget(
            description
        )

        report_card = QFrame()

        report_card.setObjectName(
            "reportCard"
        )

        report_layout = QVBoxLayout(
            report_card
        )

        report_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        self.report_text = QLabel(
            "No scan report available."
        )

        self.report_text.setWordWrap(
            True
        )

        report_layout.addWidget(
            self.report_text
        )

        layout.addWidget(
            report_card
        )

        export_button = QPushButton(
            "⬇  EXPORT REPORT"
        )

        export_button.setMaximumWidth(
            190
        )

        export_button.clicked.connect(
            self.export_report
        )

        layout.addWidget(
            export_button
        )

        layout.addStretch()

        return page

    # ========================================================
    # SETTINGS
    # ========================================================

    def create_settings_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        heading = QLabel(
            "Settings"
        )

        heading.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "NetScan configuration and scanner information."
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(
            heading
        )

        layout.addWidget(
            description
        )

        layout.addSpacing(
            20
        )

        info = QLabel(
            "Scanner type: TCP Connect Scan\n"
            "Default range: 1–1024\n"
            "Service detection: Enabled\n"
            "Scan history: Enabled\n"
            "Report export: Enabled"
        )

        info.setObjectName(
            "infoText"
        )

        layout.addWidget(
            info
        )

        layout.addStretch()

        return page

    # ========================================================
    # ABOUT
    # ========================================================

    def create_about_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        heading = QLabel(
            "About NetScan"
        )

        heading.setObjectName(
            "pageTitle"
        )

        layout.addWidget(
            heading
        )

        layout.addSpacing(
            15
        )

        about = QLabel(
            "NetScan is a Python-based network security "
            "scanner designed for authorized TCP port "
            "scanning and basic service identification.\n\n"
            "Built with Python and PySide6.\n\n"
            "This project is intended for cybersecurity "
            "education, authorized testing, and portfolio use."
        )

        about.setObjectName(
            "infoText"
        )

        about.setWordWrap(
            True
        )

        layout.addWidget(
            about
        )

        layout.addStretch()

        return page

    # ========================================================
    # START SCAN
    # ========================================================

    def start_scan(self):

        target = self.target_input.text().strip()

        start_port = (
            self.start_port.value()
        )

        end_port = (
            self.end_port.value()
        )

        if not target:

            QMessageBox.warning(
                self,
                "Invalid Target",
                "Please enter a target."
            )

            return

        if start_port > end_port:

            QMessageBox.warning(
                self,
                "Invalid Port Range",
                "Start port must be less than or equal to end port."
            )

            return

        self.results_table.setRowCount(
            0
        )

        self.target_summary.setText(
            f"TARGET: {target}"
        )

        self.ip_summary.setText(
            "IP: SCANNING..."
        )

        self.open_summary.setText(
            "OPEN PORTS: 0"
        )

        self.scan_button.setEnabled(
            False
        )

        self.progress.setVisible(
            True
        )

        self.status_label.setText(
            "●  Scanning..."
        )

        self.status_label.setObjectName(
            "statusScanning"
        )

        self.status_label.style().unpolish(
            self.status_label
        )

        self.status_label.style().polish(
            self.status_label
        )

        self.worker = ScanWorker(
            target,
            start_port,
            end_port
        )

        self.worker.finished.connect(
            self.scan_finished
        )

        self.worker.error.connect(
            self.scan_error
        )

        self.worker.start()

    # ========================================================
    # SCAN FINISHED
    # ========================================================

    def scan_finished(self, result):

        self.progress.setVisible(
            False
        )

        self.scan_button.setEnabled(
            True
        )

        self.status_label.setText(
            "●  Scan Complete"
        )

        self.status_label.setObjectName(
            "statusReady"
        )

        self.status_label.style().unpolish(
            self.status_label
        )

        self.status_label.style().polish(
            self.status_label
        )

        self.last_result = result

        # Save history

        save_scan(
            result
        )

        self.target_summary.setText(
            f"TARGET: {result['target']}"
        )

        self.ip_summary.setText(
            f"IP: {result['ip']}"
        )

        open_ports = result[
            "results"
        ]

        self.open_summary.setText(
            f"OPEN PORTS: {len(open_ports)}"
        )

        # Scanner table

        self.results_table.setRowCount(
            len(open_ports)
        )

        # Dashboard table

        self.dashboard_table.setRowCount(
            len(open_ports)
        )

        for row, item in enumerate(
            open_ports
        ):

            port = str(
                item["port"]
            )

            state = item[
                "state"
            ]

            service = item[
                "service"
            ]

            self.results_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    port
                )
            )

            self.results_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    state
                )
            )

            self.results_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    service
                )
            )

            self.dashboard_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    port
                )
            )

            self.dashboard_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    state
                )
            )

            self.dashboard_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    service
                )
            )

        # Dashboard cards

        self.dashboard_target.value_label.setText(
            result["target"]
        )

        self.dashboard_ports.value_label.setText(
            str(
                result["total_ports"]
            )
        )

        self.dashboard_open.value_label.setText(
            str(
                result["open_ports"]
            )
        )

        self.dashboard_duration.value_label.setText(
            f"{result['scan_duration']}s"
        )

        # Report

        report = self.build_report(
            result
        )

        self.report_text.setText(
            report
        )

    # ========================================================
    # BUILD REPORT
    # ========================================================

    def build_report(self, result):

        lines = []

        lines.append(
            "NETSCAN SECURITY REPORT"
        )

        lines.append(
            "=" * 50
        )

        lines.append(
            f"Target: {result['target']}"
        )

        lines.append(
            f"IP Address: {result['ip']}"
        )

        lines.append(
            f"Port Range: {result['start_port']}-"
            f"{result['end_port']}"
        )

        lines.append(
            f"Ports Scanned: {result['total_ports']}"
        )

        lines.append(
            f"Open Ports: {result['open_ports']}"
        )

        lines.append(
            f"Scan Duration: "
            f"{result['scan_duration']} seconds"
        )

        lines.append("")
        lines.append(
            "OPEN PORTS"
        )

        lines.append(
            "-" * 50
        )

        if result["results"]:

            for item in result["results"]:

                lines.append(
                    f"Port {item['port']} | "
                    f"{item['state']} | "
                    f"{item['service']}"
                )

        else:

            lines.append(
                "No open ports detected."
            )

        lines.append("")
        lines.append(
            "Only scan systems you own or have explicit permission to test."
        )

        return "\n".join(
            lines
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_report(self):

        if not self.last_result:

            QMessageBox.information(
                self,
                "No Report",
                "Run a scan before exporting a report."
            )

            return

        default_name = (
            "netscan_report.txt"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Security Report",
            default_name,
            "Text Files (*.txt)"
        )

        if not file_path:

            return

        try:

            report = self.build_report(
                self.last_result
            )

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    report
                )

            QMessageBox.information(
                self,
                "Report Exported",
                "Security report exported successfully."
            )

        except OSError as e:

            QMessageBox.critical(
                self,
                "Export Error",
                str(e)
            )

    # ========================================================
    # HISTORY
    # ========================================================

    def show_history(self):

        history = get_history()

        self.history_table.setRowCount(
            len(history)
        )

        for row, record in enumerate(
            reversed(history)
        ):

            values = [
                record.get(
                    "timestamp",
                    "—"
                ),
                record.get(
                    "target",
                    "—"
                ),
                record.get(
                    "ip",
                    "—"
                ),
                (
                    f"{record.get('start_port', '—')}-"
                    f"{record.get('end_port', '—')}"
                ),
                str(
                    record.get(
                        "total_ports",
                        0
                    )
                ),
                str(
                    record.get(
                        "open_ports",
                        0
                    )
                ),
                f"{record.get('scan_duration', 0)}s"
            ]

            for column, value in enumerate(
                values
            ):

                self.history_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        value
                    )
                )

        self.pages.setCurrentIndex(
            2
        )

        self.set_active_button(
            self.history_button
        )

    # ========================================================
    # ERROR
    # ========================================================

    def scan_error(self, message):

        self.progress.setVisible(
            False
        )

        self.scan_button.setEnabled(
            True
        )

        self.status_label.setText(
            "●  Scan Error"
        )

        QMessageBox.critical(
            self,
            "Scan Error",
            message
        )

    # ========================================================
    # STYLES
    # ========================================================

    def apply_styles(self):

        self.setStyleSheet(

            """
            QWidget {
                background-color: #0b1120;
                color: #e5e7eb;
                font-family: "Segoe UI";
                font-size: 10pt;
            }

            QFrame#sidebar {
                background-color: #070d19;
                border-right: 1px solid #1e293b;
            }

            QLabel#logo {
                color: #f8fafc;
            }

            QLabel#subtitle {
                color: #64748b;
                font-size: 8pt;
                font-weight: bold;
                letter-spacing: 2px;
            }

            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #94a3b8;
                text-align: left;
                padding-left: 14px;
                font-size: 10pt;
            }

            QPushButton#navButton:hover {
                background-color: #111c2f;
                color: #f8fafc;
            }

            QPushButton#navButton[active="true"] {
                background-color: #172554;
                color: #60a5fa;
                border-left: 3px solid #3b82f6;
            }

            QFrame#statusFrame {
                background-color: #0d1728;
                border: 1px solid #1e293b;
                border-radius: 9px;
            }

            QLabel#statusTitle {
                color: #64748b;
                font-size: 8pt;
                font-weight: bold;
            }

            QLabel#statusReady {
                color: #34d399;
                font-weight: bold;
            }

            QLabel#statusScanning {
                color: #60a5fa;
                font-weight: bold;
            }

            QLabel#pageTitle {
                color: #f8fafc;
                font-size: 25pt;
                font-weight: bold;
            }

            QLabel#pageDescription {
                color: #64748b;
                font-size: 10pt;
            }

            QLabel#sectionTitle {
                color: #e2e8f0;
                font-size: 14pt;
                font-weight: bold;
            }

            QFrame#statCard {
                background-color: #101a2d;
                border: 1px solid #1e293b;
                border-radius: 10px;
            }

            QLabel#statTitle {
                color: #64748b;
                font-size: 8pt;
                font-weight: bold;
            }

            QLabel#statValue {
                color: #60a5fa;
                font-size: 19pt;
                font-weight: bold;
            }

            QFrame#controlCard {
                background-color: #101a2d;
                border: 1px solid #1e293b;
                border-radius: 10px;
            }

            QFrame#reportCard {
                background-color: #101a2d;
                border: 1px solid #1e293b;
                border-radius: 10px;
            }

            QLineEdit {
                background-color: #0b1324;
                border: 1px solid #334155;
                border-radius: 7px;
                padding: 9px;
                color: #f8fafc;
            }

            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }

            QSpinBox {
                background-color: #0b1324;
                border: 1px solid #334155;
                border-radius: 7px;
                padding: 7px;
                color: #f8fafc;
            }

            QPushButton {
                background-color: #172554;
                border: 1px solid #1d4ed8;
                border-radius: 7px;
                padding: 9px 15px;
                color: #bfdbfe;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1e3a8a;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }

            QPushButton:disabled {
                background-color: #111827;
                color: #475569;
                border-color: #1e293b;
            }

            QPushButton#scanButton {
                background-color: #1d4ed8;
                color: white;
                border: none;
                padding-left: 20px;
                padding-right: 20px;
            }

            QPushButton#scanButton:hover {
                background-color: #2563eb;
            }

            QProgressBar {
                background-color: #111827;
                border: 1px solid #1e293b;
                border-radius: 5px;
                height: 7px;
            }

            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 5px;
            }

            QTableWidget {
                background-color: #0d1728;
                border: 1px solid #1e293b;
                border-radius: 8px;
                gridline-color: #1e293b;
                selection-background-color: #172554;
                selection-color: #e2e8f0;
            }

            QHeaderView::section {
                background-color: #111c2f;
                color: #94a3b8;
                border: none;
                border-bottom: 1px solid #1e293b;
                padding: 10px;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #172033;
            }

            QLabel#warning {
                color: #f59e0b;
                font-size: 9pt;
            }

            QLabel#infoText {
                color: #94a3b8;
                font-size: 11pt;
                line-height: 1.5;
            }

            QScrollBar:vertical {
                background: #0b1120;
                width: 8px;
            }

            QScrollBar::handle:vertical {
                background: #334155;
                border-radius: 4px;
            }
            """
        )


# ============================================================
# APPLICATION ENTRY
# ============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )