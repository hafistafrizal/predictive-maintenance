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
    Menyediakan fitur visualisasi status, pencarian dinamis, ekspor CSV, dan pembersihan log.
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

        # Inisialisasi bagian aksi atas dan tabel utama secara modular
        layout_atas = self._init_panel_aksi()
        self.tabel_log = self._init_panel_tabel()

        layout_utama.addLayout(layout_atas)
        layout_utama.addWidget(self.tabel_log)
        
        self.muat_data_log()

    def _init_panel_aksi(self) -> QHBoxLayout:
        """Inisialisasi panel atas: Judul, kolom pencarian, dan tombol aksi."""
        layout_atas = QHBoxLayout()
        lbl_judul = QLabel("Log Riwayat Pemeriksaan Kendaraan")
        lbl_judul.setStyleSheet("font-weight: bold; font-size: 18px; color: #ffffff;")

        # Inisialisasi tombol aksi dengan kursor hand pointing
        self.btn_refresh = QPushButton("⟳  PERBARUI DATA")
        self.btn_refresh.setObjectName("btn_refresh_hist")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.muat_data_log)

        self.btn_ekspor = QPushButton("↓  EKSPOR CSV")
        self.btn_ekspor.setObjectName("btn_ekspor_hist")
        self.btn_ekspor.setCursor(Qt.PointingHandCursor)
        self.btn_ekspor.clicked.connect(self.ekspor_csv)

        self.btn_reset = QPushButton("✕  HAPUS RIWAYAT")
        self.btn_reset.setObjectName("btn_reset_hist")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.hapus_semua_riwayat)

        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("🔍  Cari Riwayat...")
        self.input_cari.setFixedWidth(240)
        self.input_cari.textChanged.connect(self.muat_data_log)

        layout_atas.addWidget(lbl_judul)
        layout_atas.addStretch()
        layout_atas.addWidget(self.input_cari)
        layout_atas.addWidget(self.btn_refresh)
        layout_atas.addWidget(self.btn_ekspor)
        layout_atas.addWidget(self.btn_reset)
        
        return layout_atas

    def _init_panel_tabel(self) -> QTableWidget:
        """Inisialisasi tabel riwayat diagnosa."""
        tabel = QTableWidget()
        tabel.setColumnCount(9)
        tabel.setHorizontalHeaderLabels([
            "Waktu", "Kendaraan", "RPM", "Torsi (Nm)",
            "Beban (%)", "Suhu M (°C)", "Suhu U (°C)", "Risiko (%)", "Status Akhir"
        ])

        # Mengatur responsivitas kolom dan baris
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
        """Memuat seluruh log diagnosa dari database dan menyaringnya berdasarkan kolom pencarian."""
        try:
            daftar_log = self.db.ambil_semua_log()
            
            # Saring data riwayat secara dinamis (Case Insensitive)
            query = self.input_cari.text().strip().lower()
            if query:
                filtered_log = []
                for log_row in daftar_log:
                    teks_gabungan = " ".join([str(val).lower() for val in log_row])
                    if query in teks_gabungan:
                        filtered_log.append(log_row)
                daftar_log = filtered_log

            self.tabel_log.setRowCount(0)

            # Memetakan data ke dalam sel tabel
            for baris_idx, data_baris in enumerate(daftar_log):
                self.tabel_log.insertRow(baris_idx)
                for kolom_idx, data_sel in enumerate(data_baris):
                    teks_sel = str(data_sel)
                    # Merapikan tampilan waktu (ambil jam:menit:detik saja)
                    if kolom_idx == 0 and " " in teks_sel:
                        teks_sel = teks_sel.split(" ")[1]

                    # Mengatur format persen untuk kolom beban dan risiko
                    if kolom_idx in [4, 7]:
                        teks_sel = f"{float(data_sel):.1f}%"

                    item = QTableWidgetItem(teks_sel)
                    item.setTextAlignment(Qt.AlignCenter)

                    # Pewarnaan teks visual khusus kolom status akhir
                    if kolom_idx == 8:
                        item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                        if "NORMAL" in str(data_sel):
                            item.setForeground(QBrush(QColor("#4ade80")))
                        elif "WARNING" in str(data_sel) or "WASPADA" in str(data_sel):
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

        konfirmasi = QMessageBox.question(self, "Konfirmasi Reset",
                                          "Apakah Anda yakin ingin MENGHAPUS SEMUA riwayat diagnosa?",
                                          QMessageBox.Yes | QMessageBox.No)
        if konfirmasi == QMessageBox.Yes:
            berhasil, pesan = self.db.hapus_semua_log()
            if berhasil:
                self.muat_data_log()

    def ekspor_csv(self):
        """Mengekspor data tabel riwayat saat ini ke dalam berkas CSV format eksternal."""
        if self.tabel_log.rowCount() == 0:
            return
        path_file, _ = QFileDialog.getSaveFileName(self, "Simpan Laporan", "Laporan_Diagnosa_Kendaraan.csv",
                                                   "CSV Files (*.csv)")
        if path_file:
            try:
                with open(path_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    header = [self.tabel_log.horizontalHeaderItem(i).text() for i in
                               range(self.tabel_log.columnCount())]
                    writer.writerow(header)
                    for baris in range(self.tabel_log.rowCount()):
                        data_baris = [
                            self.tabel_log.item(baris, kolom).text() if self.tabel_log.item(baris, kolom) else "" for
                            kolom in range(self.tabel_log.columnCount())]
                        writer.writerow(data_baris)
                QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke:\n{path_file}")
            except Exception as e:
                pass