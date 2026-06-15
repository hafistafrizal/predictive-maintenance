from PySide6.QtWidgets import *
from database.models import ProfileKendaraan

class TampilanTorque(QWidget):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.nama_terpilih = None
        self.atur_tampilan()
        self.data_tabel()

    def atur_tampilan(self):
        layout_utama = QVBoxLayout(self)

        # FORM IMPUTAN
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Contoh: Toyota Avanza 1.5L")

        self.input_idle_rpm = QLineEdit()
        self.input_idle_rpm.setPlaceholderText("Contoh: 800")

        self.input_max_torque = QLineEdit()
        self.input_max_torque.setPlaceholderText("Contoh: 136")

        self.input_max_rpm = QLineEdit()
        self.input_max_rpm.setPlaceholderText("Contoh: 4200")

        # KUMPULAN TOMBOL
        layout_tombol = QHBoxLayout()

        self.tombol_simpan = QPushButton("Simpan")
        self.tombol_simpan.clicked.connect(self.aksi_simpan)

        self.tombol_update = QPushButton("Update")
        self.tombol_update.clicked.connect(self.aksi_update)
        self.tombol_update.hide()

        self.tombol_hapus = QPushButton("Delete")
        self.tombol_hapus.clicked.connect(self.aksi_hapus)
        self.tombol_hapus.hide()

        self.tombol_batal = QPushButton("Batal")
        self.tombol_batal.clicked.connect(self.aksi_batal)

        # TOMBOL LAYOUT HORIZONTAL
        layout_tombol.addWidget(self.tombol_batal)

        layout_tombol.addWidget(self.tombol_hapus)
        layout_tombol.addWidget(self.tombol_update)
        layout_tombol.addWidget(self.tombol_simpan)

        # FORM LAYOUT VERTIKAL
        layout_utama.addWidget(QLabel("Nama Kendaraan: "))
        layout_utama.addWidget(self.input_nama)
        layout_utama.addWidget(QLabel("Idle RPM: "))
        layout_utama.addWidget(self.input_idle_rpm)
        layout_utama.addWidget(QLabel("Max Torque: "))
        layout_utama.addWidget(self.input_max_torque)
        layout_utama.addWidget(QLabel("Max RPM: "))
        layout_utama.addWidget(self.input_max_rpm)

        layout_utama.addLayout(layout_tombol)

        # TABEL DATA TORSI KENDARAAN
        self.tabel = QTableWidget()

        self.tabel.setColumnCount(5)
        self.tabel.setHorizontalHeaderLabels(["NO", "NAMA", "RPM IDLE", "MAX TORQUE", "MAX RPM"])
        self.tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabel.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabel.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabel.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)

        # diklik menyorot satu baris penuh
        self.tabel.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.tabel.verticalHeader().setVisible(False)

        layout_utama.addWidget(self.tabel)

        self.tabel.cellClicked.connect(self.klik_tabel)

    def aksi_simpan(self):
        nama = self.input_nama.text()
        idle_rpm = self.input_idle_rpm.text()
        max_torque = self.input_max_torque.text()
        max_rpm = self.input_max_rpm.text()

        # Cek data Kosong atau tidak
        if not nama or not idle_rpm or not max_torque or not max_rpm:
            QMessageBox.warning(self, "Peringatan", "Semua kolom harus diisi.")
            return

        # Cek Angka di isi dengan benar
        try:
            kendaraan_baru = ProfileKendaraan(nama, int(idle_rpm), float(max_torque), int(max_rpm))
            berhasil, pesan = self.db.simpan_data(kendaraan_baru)

            if berhasil:
                QMessageBox.information(self, "Berhasil", pesan)
                self.aksi_batal()
                self.data_tabel()
            else:
                QMessageBox.warning(self, "Gagal", pesan)

        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Harap masukkan angka yang valid.")

    def data_tabel(self):
        daftar_kendaraan = self.db.ambil_data()

        self.tabel.setRowCount(0)

        for baris, kendaraan in enumerate(daftar_kendaraan):
            self.tabel.insertRow(baris)

            self.tabel.setItem(baris, 0, QTableWidgetItem(str(baris + 1)))

            self.tabel.setItem(baris, 1, QTableWidgetItem(kendaraan.nama))
            self.tabel.setItem(baris, 2, QTableWidgetItem(str(kendaraan.idle_rpm)))
            self.tabel.setItem(baris, 3, QTableWidgetItem(str(kendaraan.max_torque)))
            self.tabel.setItem(baris, 4, QTableWidgetItem(str(kendaraan.max_rpm)))

    def klik_tabel(self, baris, kolom):
        nama = self.tabel.item(baris, 1).text()
        idle_rpm = self.tabel.item(baris, 2).text()
        max_torque = self.tabel.item(baris, 3).text()
        max_rpm = self.tabel.item(baris, 4).text()

        # Mengisi form
        self.input_nama.setText(nama)
        self.input_idle_rpm.setText(idle_rpm)
        self.input_max_torque.setText(max_torque)
        self.input_max_rpm.setText(max_rpm)

        # Simpan nama sebagai acuan update/delete
        self.nama_terpilih = nama

        # Ganti mode tombol
        self.tombol_simpan.hide()
        self.tombol_update.show()
        self.tombol_hapus.show()

    def aksi_batal(self):
        self.input_nama.clear()
        self.input_idle_rpm.clear()
        self.input_max_torque.clear()
        self.input_max_rpm.clear()
        self.nama_terpilih = None
        self.tabel.clearSelection()

        # Kembalikan mode tombol ke awal
        self.tombol_simpan.show()
        self.tombol_update.hide()
        self.tombol_hapus.hide()

    def aksi_update(self):
        if not self.nama_terpilih: return

        nama = self.input_nama.text()
        idle_rpm = self.input_idle_rpm.text()
        max_torque = self.input_max_torque.text()
        max_rpm = self.input_max_rpm.text()

        if not nama or not idle_rpm or not max_torque or not max_rpm:
            QMessageBox.warning(self, "Peringatan", "Semua kolom harus diisi.")
            return

        try:
            kendaraan_update = ProfileKendaraan(nama, int(idle_rpm), float(max_torque), int(max_rpm))
            berhasil, pesan = self.db.update_data(self.nama_terpilih, kendaraan_update)

            if berhasil:
                QMessageBox.information(self, "Berhasil", pesan)
                self.aksi_batal()
                self.data_tabel()
            else:
                QMessageBox.warning(self, "Gagal", pesan)
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Harap masukkan angka yang valid.")

    def aksi_hapus(self):
        if not self.nama_terpilih: return

        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus profil {self.nama_terpilih}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if konfirmasi == QMessageBox.Yes:
            berhasil, pesan = self.db.hapus_data(self.nama_terpilih)
            if berhasil:
                QMessageBox.information(self, "Berhasil", pesan)
                self.aksi_batal()
                self.data_tabel()
            else:
                QMessageBox.warning(self, "Gagal", pesan)