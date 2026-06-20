# File: ui/history_view.py
import csv
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont


class TampilanRiwayat(QWidget):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.atur_tampilan()

    def atur_tampilan(self):
        layout_utama = QVBoxLayout(self)
        layout_utama.setContentsMargins(20, 20, 20, 20)
        layout_utama.setSpacing(15)

        # ==========================================
        # PANEL ATAS: Judul & Tombol Aksi
        # ==========================================
        layout_atas = QHBoxLayout()
        lbl_judul = QLabel("Log Riwayat Pemeriksaan Kendaraan")
        lbl_judul.setStyleSheet("font-weight: bold; font-size: 18px; color: #ffffff;")

        # Desain Tombol Modern
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

        layout_utama.addLayout(layout_atas)

        # ==========================================
        # TABEL RIWAYAT: Desain Modern & Clean
        # ==========================================
        self.tabel_log = QTableWidget()
        self.tabel_log.setColumnCount(9)
        self.tabel_log.setHorizontalHeaderLabels([
            "Waktu", "Kendaraan", "RPM", "Torsi (Nm)",
            "Beban (%)", "Suhu M (°C)", "Suhu U (°C)", "Risiko (%)", "Status Akhir"
        ])

        self.tabel_log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel_log.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabel_log.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel_log.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabel_log.verticalHeader().setVisible(False)
        self.tabel_log.setShowGrid(False)  # Menghilangkan garis kotak kaku
        self.tabel_log.verticalHeader().setDefaultSectionSize(40)  # Baris lebih lega

        layout_utama.addWidget(self.tabel_log)
        self.muat_data_log()

    def showEvent(self, event):
        self.muat_data_log()
        super().showEvent(event)

    def muat_data_log(self):
        try:
            daftar_log = self.db.ambil_semua_log()
            
            # Saring data riwayat secara dinamis
            query = self.input_cari.text().strip().lower()
            if query:
                filtered_log = []
                for log_row in daftar_log:
                    teks_gabungan = " ".join([str(val).lower() for val in log_row])
                    if query in teks_gabungan:
                        filtered_log.append(log_row)
                daftar_log = filtered_log

            self.tabel_log.setRowCount(0)

            for baris_idx, data_baris in enumerate(daftar_log):
                self.tabel_log.insertRow(baris_idx)
                for kolom_idx, data_sel in enumerate(data_baris):
                    # Khusus kolom waktu, rapikan menjadi jam saja jika formatnya panjang
                    teks_sel = str(data_sel)
                    if kolom_idx == 0 and " " in teks_sel:
                        teks_sel = teks_sel.split(" ")[1]

                    # Jika kolom beban atau risiko (tambah format persentase yang rapi)
                    if kolom_idx in [4, 7]:
                        teks_sel = f"{float(data_sel):.1f}%"

                    item = QTableWidgetItem(teks_sel)
                    item.setTextAlignment(Qt.AlignCenter)

                    # Pewarnaan Status Akhir
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

    # LOGIKA TOMBOL 100% SAMA
    def hapus_semua_riwayat(self):
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