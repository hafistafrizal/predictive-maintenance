# File: ui/torque_view.py
# Deskripsi: Mengimplementasikan kelas TampilanTorque yang digunakan untuk mengelola data spesifikasi kendaraan
#            (CRUD: Simpan, Perbarui, Hapus, Batal) dan menampilkannya dalam tabel database.

from PySide6.QtWidgets import *
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from database.models import ProfileKendaraan
from ui.styles import STYLE_HEADER_CARD


class TampilanTorque(QWidget):
    """
    Kelas widget utama untuk mengelola database parameter torsi dan spesifikasi kendaraan.
    Menghubungkan form input data ke operasi CRUD pada database.
    """
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.nama_terpilih = None
        self.atur_tampilan()
        self.data_tabel()

    def atur_tampilan(self):
        """Menyusun struktur tata letak utama halaman pengelolaan spesifikasi kendaraan."""
        layout_utama = QHBoxLayout(self)
        layout_utama.setContentsMargins(15, 15, 15, 15)
        layout_utama.setSpacing(20)

        # Inisialisasi masing-masing panel secara modular
        panel_kiri = self._init_panel_form()
        panel_kanan = self._init_panel_tabel()

        # Menambahkan sub-layout ke tata letak utama (Kiri: Form input, Kanan: Tabel data)
        # Menggunakan faktor stretch (1, 2) untuk alokasi lebar horizontal
        layout_utama.addWidget(panel_kiri, 1)
        layout_utama.addWidget(panel_kanan, 2)

    def _init_panel_form(self) -> QWidget:
        """Inisialisasi panel kiri: Form input pengaturan profil kendaraan."""
        wadah = QWidget()
        layout_kiri = QVBoxLayout(wadah)
        layout_kiri.setContentsMargins(0, 0, 0, 0)

        grup_form = QGroupBox()
        layout_form = QVBoxLayout(grup_form)
        layout_form.setContentsMargins(15, 15, 15, 15)
        layout_form.setSpacing(12)

        lbl_head_form = QLabel("Pengaturan Profil Kendaraan")
        lbl_head_form.setStyleSheet(STYLE_HEADER_CARD)
        layout_form.addWidget(lbl_head_form)

        self.input_nama = QLineEdit()
        self.input_idle_rpm = QLineEdit()
        self.input_max_torque = QLineEdit()
        self.input_max_rpm = QLineEdit()

        layout_form.addWidget(QLabel("Nama Kendaraan:"))
        layout_form.addWidget(self.input_nama)
        layout_form.addWidget(QLabel("RPM Idle (Stasioner):"))
        layout_form.addWidget(self.input_idle_rpm)
        layout_form.addWidget(QLabel("Torsi Puncak (Nm):"))
        layout_form.addWidget(self.input_max_torque)
        layout_form.addWidget(QLabel("RPM Batas Maksimal (Redline):"))
        layout_form.addWidget(self.input_max_rpm)

        # Mengatur tata letak tombol aksi
        layout_tombol = QHBoxLayout()
        layout_tombol.setSpacing(15)

        self.tombol_batal = QPushButton("BATAL")
        self.tombol_batal.setObjectName("btn_batal")
        self.tombol_batal.setCursor(Qt.PointingHandCursor)
        self.tombol_batal.clicked.connect(self.aksi_batal)

        self.tombol_hapus = QPushButton("HAPUS")
        self.tombol_hapus.setObjectName("btn_hapus")
        self.tombol_hapus.setCursor(Qt.PointingHandCursor)
        self.tombol_hapus.clicked.connect(self.aksi_hapus)

        self.tombol_update = QPushButton("PERBARUI")
        self.tombol_update.setObjectName("btn_update")
        self.tombol_update.setCursor(Qt.PointingHandCursor)
        self.tombol_update.clicked.connect(self.aksi_update)

        self.tombol_simpan = QPushButton("SIMPAN PROFIL")
        self.tombol_simpan.setObjectName("btn_simpan")
        self.tombol_simpan.setCursor(Qt.PointingHandCursor)
        self.tombol_simpan.clicked.connect(self.aksi_simpan)

        # Sembunyikan tombol batal, hapus, dan perbarui secara default (hanya muncul saat memilih baris tabel)
        self.tombol_update.hide()
        self.tombol_hapus.hide()
        self.tombol_batal.hide()

        layout_tombol.addWidget(self.tombol_batal)
        layout_tombol.addStretch()
        layout_tombol.addWidget(self.tombol_hapus)
        layout_tombol.addWidget(self.tombol_update)
        layout_tombol.addWidget(self.tombol_simpan)

        layout_form.addSpacing(15)
        layout_form.addLayout(layout_tombol)

        layout_kiri.addWidget(grup_form)
        layout_kiri.addStretch()
        
        return wadah

    def _init_panel_tabel(self) -> QWidget:
        """Inisialisasi panel kanan: Tabel daftar data spesifikasi kendaraan."""
        wadah = QWidget()
        layout_kanan = QVBoxLayout(wadah)
        layout_kanan.setContentsMargins(0, 0, 0, 0)

        grup_tabel = QGroupBox()
        layout_tabel_grup = QVBoxLayout(grup_tabel)
        layout_tabel_grup.setContentsMargins(15, 15, 15, 15)

        lbl_head_tabel = QLabel("Database Parameter Torsi")
        lbl_head_tabel.setStyleSheet(STYLE_HEADER_CARD)
        layout_tabel_grup.addWidget(lbl_head_tabel)

        self.tabel = QTableWidget()
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels(["NAMA KENDARAAN", "RPM IDLE", "MAX TORQUE", "MAX RPM"])

        # Menyesuaikan perilaku kolom tabel
        self.tabel.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabel.verticalHeader().setVisible(False)
        self.tabel.setShowGrid(False)
        self.tabel.verticalHeader().setDefaultSectionSize(40)
        self.tabel.cellClicked.connect(self.klik_tabel)

        layout_tabel_grup.addWidget(self.tabel)
        layout_kanan.addWidget(grup_tabel)
        
        return wadah

    def aksi_simpan(self):
        """Menyimpan data profil kendaraan baru ke database."""
        nama, idle, max_t, max_r = self.input_nama.text(), self.input_idle_rpm.text(), self.input_max_torque.text(), self.input_max_rpm.text()
        if not nama or not idle or not max_t or not max_r:
            QMessageBox.warning(self, "Peringatan", "Semua kolom harus diisi.")
            return
        try:
            berhasil, pesan = self.db.simpan_data(ProfileKendaraan(nama, int(idle), float(max_t), int(max_r)))
            if berhasil:
                self.aksi_batal()
                self.data_tabel()
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Format angka tidak valid.")

    def data_tabel(self):
        """Memuat ulang tabel dengan semua data kendaraan terdaftar dari database."""
        daftar_kendaraan = self.db.ambil_data()
        self.tabel.setRowCount(0)
        for baris, kendaraan in enumerate(daftar_kendaraan):
            self.tabel.insertRow(baris)
            item_nama = QTableWidgetItem(kendaraan.nama)
            item_idle = QTableWidgetItem(f"{kendaraan.idle_rpm} RPM")
            item_torsi = QTableWidgetItem(f"{kendaraan.max_torque} Nm")
            item_max_rpm = QTableWidgetItem(f"{kendaraan.max_rpm} RPM")

            for item in [item_idle, item_torsi, item_max_rpm]:
                item.setTextAlignment(Qt.AlignCenter)

            self.tabel.setItem(baris, 0, item_nama)
            self.tabel.setItem(baris, 1, item_idle)
            self.tabel.setItem(baris, 2, item_torsi)
            self.tabel.setItem(baris, 3, item_max_rpm)

    def klik_tabel(self, baris, kolom):
        """Mengisi formulir input dengan data baris tabel yang dipilih dan menampilkan tombol CRUD."""
        self.input_nama.setText(self.tabel.item(baris, 0).text())
        self.input_idle_rpm.setText(self.tabel.item(baris, 1).text().replace(" RPM", ""))
        self.input_max_torque.setText(self.tabel.item(baris, 2).text().replace(" Nm", ""))
        self.input_max_rpm.setText(self.tabel.item(baris, 3).text().replace(" RPM", ""))
        self.nama_terpilih = self.tabel.item(baris, 0).text()

        # Menampilkan tombol Perbarui, Hapus, Batal, serta menyembunyikan Simpan
        self.tombol_simpan.hide()
        self.tombol_update.show()
        self.tombol_hapus.show()
        self.tombol_batal.show()

    def aksi_batal(self):
        """Mengosongkan form input dan memulihkan kondisi tombol ke default."""
        self.input_nama.clear()
        self.input_idle_rpm.clear()
        self.input_max_torque.clear()
        self.input_max_rpm.clear()
        self.nama_terpilih = None
        self.tabel.clearSelection()

        self.tombol_simpan.show()
        self.tombol_update.hide()
        self.tombol_hapus.hide()
        self.tombol_batal.hide()

    def aksi_update(self):
        """Memperbarui spesifikasi profil kendaraan yang sedang dipilih."""
        if not self.nama_terpilih: 
            return
        nama, idle, max_t, max_r = self.input_nama.text(), self.input_idle_rpm.text(), self.input_max_torque.text(), self.input_max_rpm.text()
        try:
            berhasil, pesan = self.db.update_data(self.nama_terpilih,
                                                   ProfileKendaraan(nama, int(idle), float(max_t), int(max_r)))
            if berhasil:
                self.aksi_batal()
                self.data_tabel()
        except ValueError:
            pass

    def aksi_hapus(self):
        """Menghapus profil kendaraan yang terpilih dari basis data."""
        if not self.nama_terpilih: 
            return
        konfirmasi = QMessageBox.question(self, "Hapus", f"Yakin hapus {self.nama_terpilih}?",
                                          QMessageBox.Yes | QMessageBox.No)
        if konfirmasi == QMessageBox.Yes:
            berhasil, pesan = self.db.hapus_data(self.nama_terpilih)
            if berhasil:
                self.aksi_batal()
                self.data_tabel()