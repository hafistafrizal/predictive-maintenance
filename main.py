# File: main.py
# Deskripsi: Titik masuk utama aplikasi (main entry point) yang menginisialisasi GUI QMainWindow,
#            koneksi basis data, tab-tab navigasi, serta pemuatan tema visual QSS.
#
# Urutan inisialisasi:
#   1. QApplication → sistem event loop Qt
#   2. Muat style.qss → tema visual dark mode seluruh aplikasi
#   3. JendelaUtama  → inisialisasi DB + semua tab widget
#   4. app.exec()    → jalankan event loop (blocking sampai window ditutup)

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QStyle

from database.db_koneksi import DatabaseKendaraan
from ui.diagnostics_view import TampilanDiagnosa
from ui.history_view import TampilanRiwayat
from ui.torque_view import TampilanTorque


class JendelaUtama(QMainWindow):
    """
    Window utama aplikasi Predictive Maintenance ML.
    Mengatur QTabWidget dengan 3 tab:
    - Tab 0: Diagnosa AI    → input telemetri + hasil prediksi KNN
    - Tab 1: Database Torsi → CRUD profil spesifikasi kendaraan
    - Tab 2: Log Riwayat    → tabel seluruh riwayat diagnosa
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Predictive Maintenance ML")
        self.resize(1000, 750)

        # Inisialisasi koneksi database MySQL dan buat tabel jika belum ada
        self.db = DatabaseKendaraan()

        # QTabWidget sebagai widget pusat yang memuat semua tab
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Inisialisasi semua tab widget dan teruskan instance database ke masing-masing
        self.tab_database = TampilanTorque(self.db)
        self.tab_diagnosa = TampilanDiagnosa(self.db)
        self.tab_riwayat  = TampilanRiwayat(self.db)

        # Ikon tab menggunakan ikon bawaan sistem Qt (tidak perlu file eksternal)
        ikon_db  = self.style().standardIcon(QStyle.SP_DriveFDIcon)
        ikon_ai  = self.style().standardIcon(QStyle.SP_ComputerIcon)
        ikon_log = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)

        # Tambahkan tab dalam urutan logis penggunaan: Diagnosa → DB → Riwayat
        self.tabs.addTab(self.tab_diagnosa, ikon_ai,  "Diagnosa AI")
        self.tabs.addTab(self.tab_database, ikon_db,  "Database Torsi")
        self.tabs.addTab(self.tab_riwayat,  ikon_log, "Log Riwayat")

        # Hubungkan signal pergantian tab ke handler yang memuat ulang data relevan
        self.tabs.currentChanged.connect(self.tab_berubah)

    def tab_berubah(self, indeks: int):
        """
        Handler yang dipanggil setiap kali pengguna berpindah tab.
        Memuat ulang data yang relevan agar selalu sinkron dengan database.

        Parameter:
        ----------
        indeks : int - indeks tab yang baru aktif (0=Diagnosa, 1=Database, 2=Riwayat)
        """
        if indeks == 0:
            # Tab Diagnosa AI: muat ulang daftar kendaraan dan riwayat mini
            self.tab_diagnosa.muat_daftar_mobil()
            self.tab_diagnosa.muat_riwayat_mini()
        elif indeks == 1:
            # Tab Database Torsi: muat ulang tabel data kendaraan
            self.tab_database.data_tabel()
        elif indeks == 2:
            # Tab Log Riwayat: muat ulang seluruh log dari database
            self.tab_riwayat.muat_data_log()


if __name__ == "__main__":
    # Entry point: hanya dijalankan jika file ini dieksekusi langsung (bukan di-import)
    app = QApplication(sys.argv)

    # Muat tema visual dark mode dari file QSS (Qt Style Sheet)
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
        print("[UI] Tema berhasil dimuat.")
    except FileNotFoundError:
        print("[UI] File style.qss tidak ditemukan, menggunakan tema bawaan.")

    jendela = JendelaUtama()
    jendela.show()

    # app.exec() memulai event loop Qt → program berjalan sampai window ditutup
    sys.exit(app.exec())