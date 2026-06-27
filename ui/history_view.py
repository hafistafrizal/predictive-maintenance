# File: ui/history_view.py
# Deskripsi: Mengimplementasikan kelas TampilanRiwayat yang digunakan untuk menampilkan log lengkap
#            riwayat diagnosa mesin, melakukan pencarian dinamis, serta melakukan ekspor ke berkas CSV.

import csv
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont


class TampilanRiwayat(QWidget):
    """
    Kelas widget utama untuk menampilkan dan mengelola catatan log riwayat pemeriksaan kendaraan.
    Menyediakan fitur:
    - Visualisasi status berwarna (Normal/Warning/Malfungsi)
    - Pencarian dinamis (real-time filter saat mengetik)
    - Ekspor CSV seluruh data yang sedang ditampilkan
    - Pembersihan log (TRUNCATE) dengan konfirmasi
    """

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.atur_tampilan()

    def atur_tampilan(self):
        """Menyusun struktur tata letak utama halaman riwayat diagnosa."""
        layout_utama = QVBoxLayout(self)
        layout_utama.setContentsMargins(20, 20, 20, 20)
        layout_utama.setSpacing(15)

        # Inisialisasi panel atas (aksi) dan tabel utama secara modular
        layout_atas    = self._init_panel_aksi()
        self.tabel_log = self._init_panel_tabel()

        layout_utama.addLayout(layout_atas)
        layout_utama.addWidget(self.tabel_log)

        self.muat_data_log()

    def _init_panel_aksi(self) -> QHBoxLayout:
        """Inisialisasi panel atas: Judul, kolom pencarian, dan tombol aksi."""
        layout_atas = QHBoxLayout()
        lbl_judul = QLabel("Log Riwayat Pemeriksaan Kendaraan")
        lbl_judul.setStyleSheet("font-weight: bold; font-size: 18px; color: #ffffff;")

        # Tombol Perbarui: memuat ulang data dari database
        self.btn_refresh = QPushButton("⟳  PERBARUI DATA")
        self.btn_refresh.setObjectName("btn_refresh_hist")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.muat_data_log)

        # Tombol Ekspor: menyimpan data tabel saat ini ke file CSV eksternal
        self.btn_ekspor = QPushButton("↓  EKSPOR CSV")
        self.btn_ekspor.setObjectName("btn_ekspor_hist")
        self.btn_ekspor.setCursor(Qt.PointingHandCursor)
        self.btn_ekspor.clicked.connect(self.ekspor_csv)

        # Tombol Hapus: mengosongkan seluruh riwayat (TRUNCATE) setelah konfirmasi
        self.btn_reset = QPushButton("✕  HAPUS RIWAYAT")
        self.btn_reset.setObjectName("btn_reset_hist")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.hapus_semua_riwayat)

        # Kolom pencarian: filter data riwayat secara real-time (case insensitive)
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("🔍  Cari Riwayat...")
        self.input_cari.setFixedWidth(240)
        # Setiap kali teks berubah, tampilan tabel diperbarui otomatis
        self.input_cari.textChanged.connect(self.muat_data_log)

        layout_atas.addWidget(lbl_judul)
        layout_atas.addStretch()
        layout_atas.addWidget(self.input_cari)
        layout_atas.addWidget(self.btn_refresh)
        layout_atas.addWidget(self.btn_ekspor)
        layout_atas.addWidget(self.btn_reset)

        return layout_atas

    def _init_panel_tabel(self) -> QTableWidget:
        """Inisialisasi tabel riwayat diagnosa dengan 9 kolom."""
        tabel = QTableWidget()
        tabel.setColumnCount(9)
        tabel.setHorizontalHeaderLabels([
            "Waktu", "Kendaraan", "RPM", "Torsi (Nm)",
            "Beban (%)", "Suhu M (°C)", "Suhu U (°C)", "Risiko (%)", "Status Akhir"
        ])

        # Semua kolom stretch rata kecuali kolom Waktu (ResizeToContents)
        tabel.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tabel.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabel.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabel.verticalHeader().setVisible(False)
        tabel.setShowGrid(False)
        tabel.verticalHeader().setDefaultSectionSize(40)

        return tabel

    def showEvent(self, event):
        """Memperbarui tabel secara otomatis saat tab riwayat dipilih."""
        self.muat_data_log()
        super().showEvent(event)

    def muat_data_log(self):
        """
        Memuat seluruh log diagnosa dari database dan menyaringnya
        berdasarkan kata kunci di kolom pencarian.

        Logika Filter:
        - Gabungkan semua nilai kolom per baris menjadi satu string
        - Periksa apakah query (lowercase) ada di string gabungan (case-insensitive)
        - Hanya tampilkan baris yang cocok

        Format Kolom (sesuai urutan query DB):
        [0] tanggal  [1] nama_mobil  [2] rpm  [3] torsi  [4] beban
        [5] suhu_mesin  [6] suhu_udara  [7] risiko  [8] status
        """
        try:
            daftar_log = self.db.ambil_semua_log()

            # --- Filter pencarian dinamis ---
            query = self.input_cari.text().strip().lower()
            if query:
                daftar_log = [
                    log_row for log_row in daftar_log
                    if query in " ".join([str(val).lower() for val in log_row])
                ]

            self.tabel_log.setRowCount(0)

            # --- Isi tabel dengan data hasil filter ---
            for baris_idx, data_baris in enumerate(daftar_log):
                self.tabel_log.insertRow(baris_idx)

                for kolom_idx, data_sel in enumerate(data_baris):
                    teks_sel = str(data_sel)

                    # Kolom 0 (tanggal): hanya tampilkan jam:menit:detik (tanpa tanggal)
                    if kolom_idx == 0 and " " in teks_sel:
                        teks_sel = teks_sel.split(" ")[1]

                    # Kolom 4 (beban %) dan 7 (risiko %): format satu desimal + simbol %
                    if kolom_idx in [4, 7]:
                        try:
                            teks_sel = f"{float(data_sel):.1f}%"
                        except (ValueError, TypeError):
                            teks_sel = "0.0%"

                    item = QTableWidgetItem(teks_sel)
                    item.setTextAlignment(Qt.AlignCenter)

                    # Kolom 8 (Status Akhir): pewarnaan visual berdasarkan nilai status
                    if kolom_idx == 8:
                        item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                        status_str = str(data_sel)
                        if "NORMAL" in status_str:
                            item.setForeground(QBrush(QColor("#4ade80")))
                        elif "WARNING" in status_str or "WASPADA" in status_str:
                            item.setForeground(QBrush(QColor("#fbbf24")))
                        else:
                            item.setForeground(QBrush(QColor("#f87171")))

                    self.tabel_log.setItem(baris_idx, kolom_idx, item)

        except Exception as e:
            print(f"[UI Error]: Gagal memuat tabel riwayat: {e}")

    def hapus_semua_riwayat(self):
        """Menghapus seluruh rekaman log dari database setelah konfirmasi pengguna."""
        if self.tabel_log.rowCount() == 0:
            QMessageBox.information(self, "Info", "Tabel riwayat sudah kosong.")
            return

        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Reset",
            "Apakah Anda yakin ingin MENGHAPUS SEMUA riwayat diagnosa?",
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi == QMessageBox.Yes:
            berhasil, pesan = self.db.hapus_semua_log()
            if berhasil:
                self.muat_data_log()
            else:
                # Tampilkan pesan error jika penghapusan gagal
                QMessageBox.warning(self, "Gagal", pesan)

    def ekspor_csv(self):
        """
        Mengekspor data tabel riwayat yang sedang ditampilkan ke berkas CSV.

        Catatan: Data yang diekspor adalah data yang tampil di tabel (sudah difilter),
                 bukan semua data di database. Ini memungkinkan ekspor selektif.
        """
        if self.tabel_log.rowCount() == 0:
            QMessageBox.information(self, "Info", "Tidak ada data untuk diekspor.")
            return

        # Dialog pemilihan lokasi simpan file
        path_file, _ = QFileDialog.getSaveFileName(
            self, "Simpan Laporan", "Laporan_Diagnosa_Kendaraan.csv",
            "CSV Files (*.csv)"
        )
        if not path_file:
            return  # Pengguna membatalkan dialog

        try:
            with open(path_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Tulis header dari label kolom tabel
                header = [self.tabel_log.horizontalHeaderItem(i).text()
                          for i in range(self.tabel_log.columnCount())]
                writer.writerow(header)

                # Tulis setiap baris data dari tabel (sesuai tampilan saat ini)
                for baris in range(self.tabel_log.rowCount()):
                    data_baris = [
                        self.tabel_log.item(baris, kolom).text()
                        if self.tabel_log.item(baris, kolom) else ""
                        for kolom in range(self.tabel_log.columnCount())
                    ]
                    writer.writerow(data_baris)

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke:\n{path_file}")

        except PermissionError:
            # File sedang dibuka di program lain (misal Excel)
            QMessageBox.warning(self, "Gagal Ekspor",
                                "File sedang digunakan program lain. Tutup file tersebut lalu coba lagi.")
        except Exception as e:
            QMessageBox.warning(self, "Gagal Ekspor", f"Terjadi kesalahan saat menyimpan file:\n{e}")