# File: main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QStyle

from database.db_koneksi import DatabaseKendaraan
from ui.diagnostics_view import TampilanDiagnosa
from ui.history_view import TampilanRiwayat
from ui.torque_view import TampilanTorque


class JendelaUtama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Predictive Maintenance AI")
        self.resize(1000, 750)

        self.db = DatabaseKendaraan()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_database = TampilanTorque(self.db)
        self.tab_diagnosa = TampilanDiagnosa(self.db)
        self.tab_riwayat = TampilanRiwayat(self.db)

        # Menggunakan Ikon Bawaan Sistem PySide6 untuk Tab yang lebih modern
        ikon_db = self.style().standardIcon(QStyle.SP_DriveFDIcon)
        ikon_ai = self.style().standardIcon(QStyle.SP_ComputerIcon)
        ikon_log = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)

        self.tabs.addTab(self.tab_diagnosa, ikon_ai, "Diagnosa AI")
        self.tabs.addTab(self.tab_database, ikon_db, "Database Torsi")
        self.tabs.addTab(self.tab_riwayat, ikon_log, "Log Riwayat")

        self.tabs.currentChanged.connect(self.tab_berubah)

    def tab_berubah(self, indeks):
        if indeks == 0:  # Diagnosa AI
            self.tab_diagnosa.muat_daftar_mobil()
            self.tab_diagnosa.muat_riwayat_mini()
        elif indeks == 1:  # Database Torsi
            self.tab_database.data_tabel()
        elif indeks == 2:  # Log Riwayat
            self.tab_riwayat.muat_data_log()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
        print("[UI] Tema berhasil dimuat.")
    except FileNotFoundError:
        print("[UI] File style.qss tidak ditemukan, menggunakan tema bawaan.")

    jendela = JendelaUtama()
    jendela.show()
    sys.exit(app.exec())