# File: ui/diagnostics_view.py
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont, QIntValidator, QDoubleValidator, QBrush, QColor
from PySide6.QtCore import Qt

from core.mesin_ai_pickle import MesinDiagnosaPickle
from core.mesin_ai_manual import MesinDiagnosaManual
from core.logika_diagnosa import LogikaDiagnosa


class TampilanDiagnosa(QWidget):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.logika = LogikaDiagnosa()
        self.ai_pickle = MesinDiagnosaPickle()
        self.ai_manual = MesinDiagnosaManual()
        self.atur_tampilan()
        self.muat_daftar_mobil()
        self.muat_riwayat_mini()

    def atur_tampilan(self):
        layout_utama = QVBoxLayout(self)
        layout_utama.setContentsMargins(15, 15, 15, 15)
        layout_utama.setSpacing(15)

        layout_atas = QHBoxLayout()
        layout_atas.setSpacing(15)

        # STYLE UNTUK HEADER DI DALAM KOTAK (CARD HEADER)
        style_header_card = """
            color: #3b82f6; 
            font-size: 18px; 
            font-weight: bold; 
            border-bottom: 1px solid #333333; 
            padding-bottom: 8px;
            margin-bottom: 5px;
        """

        # ========================================================
        # KOLOM 1: Panel Input
        # ========================================================
        grup_input = QGroupBox()  # Judul default dikosongkan
        layout_form_input = QVBoxLayout(grup_input)
        layout_form_input.setContentsMargins(15, 15, 15, 15)
        layout_form_input.setSpacing(10)

        lbl_head1 = QLabel("Input Telemetri Kendaraan")
        lbl_head1.setStyleSheet(style_header_card)
        layout_form_input.addWidget(lbl_head1)

        self.combo_mobil = QComboBox()
        self.combo_mobil.currentIndexChanged.connect(self.reset_form)
        self.input_rpm = QLineEdit()
        self.input_suhu_mesin = QLineEdit()
        self.input_suhu_udara = QLineEdit()

        self.input_rpm.setValidator(QIntValidator(-10000, 50000))
        self.input_suhu_mesin.setValidator(QDoubleValidator(-100.0, 500.0, 2))
        self.input_suhu_udara.setValidator(QDoubleValidator(-100.0, 500.0, 2))

        layout_form_input.addWidget(QLabel("Pilih Kendaraan:"))
        layout_form_input.addWidget(self.combo_mobil)
        layout_form_input.addWidget(QLabel("RPM Mesin Saat Ini:"))
        layout_form_input.addWidget(self.input_rpm)
        layout_form_input.addWidget(QLabel("Suhu Mesin (°C):"))
        layout_form_input.addWidget(self.input_suhu_mesin)
        layout_form_input.addWidget(QLabel("Suhu Udara (°C):"))
        layout_form_input.addWidget(self.input_suhu_udara)
        layout_form_input.addStretch()

        # ========================================================
        # KOLOM 2: Panel Eksekusi (Ruang kosong dirapikan)
        # ========================================================
        grup_opsi = QGroupBox()
        layout_opsi = QVBoxLayout(grup_opsi)
        layout_opsi.setContentsMargins(15, 15, 15, 15)
        layout_opsi.setSpacing(12)

        lbl_head2 = QLabel("Model Machine Learning")
        lbl_head2.setStyleSheet(style_header_card)
        layout_opsi.addWidget(lbl_head2)

        # Penjelasan singkat agar area tidak melompong
        lbl_desc = QLabel("Pilih algoritma pemrosesan\nuntuk diagnosa telemetri:")
        lbl_desc.setStyleSheet("color: #9ca3af; font-size: 12px;")
        layout_opsi.addWidget(lbl_desc)

        self.radio_pickle = QRadioButton("AI Pickle (Model SMOTE)")
        self.radio_pickle.setChecked(True)
        self.radio_manual = QRadioButton("AI Manual (CSV)")

        self.btn_proses = QPushButton("▶  PROSES DIAGNOSA")
        self.btn_proses.setObjectName("btn_proses")
        self.btn_proses.setCursor(Qt.PointingHandCursor)
        self.btn_proses.clicked.connect(self.aksi_diagnosa)

        self.btn_reset = QPushButton("⟳  RESET FORMULIR")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_form)

        layout_opsi.addWidget(self.radio_pickle)
        layout_opsi.addWidget(self.radio_manual)

        layout_opsi.addStretch()  # Ruang sisa didorong ke TENGAH, tombol turun ke bawah agar sejajar form input

        layout_opsi.addWidget(self.btn_proses)
        layout_opsi.addWidget(self.btn_reset)

        # ========================================================
        # KOLOM 3: Dashboard Hasil
        # ========================================================
        grup_hasil = QGroupBox()
        layout_hasil = QVBoxLayout(grup_hasil)
        layout_hasil.setContentsMargins(15, 15, 15, 15)
        layout_hasil.setSpacing(10)

        lbl_head3 = QLabel("Dashboard Hasil")
        lbl_head3.setStyleSheet(style_header_card)
        layout_hasil.addWidget(lbl_head3)

        self.lbl_status = QLabel("STATUS: MENUNGGU INPUT...")
        self.lbl_status.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setMinimumHeight(40)

        self.lbl_torsi = QLabel("Kalkulasi Torsi Kendaraan: - Nm")
        self.lbl_beban = QLabel("Persentase Beban Mesin: 0%")
        self.lbl_beban.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.bar_risiko = QProgressBar()
        self.bar_risiko.setRange(0, 100)
        self.bar_risiko.setValue(0)
        self.bar_risiko.setTextVisible(True)
        self.bar_risiko.setMinimumHeight(28)

        self.teks_insight = QTextEdit()
        self.teks_insight.setReadOnly(True)
        self.teks_insight.setStyleSheet(
            "background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #444444; border-radius: 5px;")

        self.lbl_detail_ai = QLabel("Data Transparan AI:\n-")
        self.lbl_detail_ai.setStyleSheet("color: #6b7280; font-size: 11px;")

        layout_hasil.addWidget(self.lbl_status)
        layout_hasil.addWidget(self.lbl_torsi)
        layout_hasil.addWidget(self.lbl_beban)
        layout_hasil.addWidget(QLabel("Persentase Risiko Kerusakan:"))
        layout_hasil.addWidget(self.bar_risiko)
        layout_hasil.addWidget(QLabel("Insight & Keterangan Risiko:"))
        layout_hasil.addWidget(self.teks_insight)
        layout_hasil.addWidget(self.lbl_detail_ai)

        layout_atas.addWidget(grup_input, 3)
        layout_atas.addWidget(grup_opsi, 2)
        layout_atas.addWidget(grup_hasil, 4)

        # ========================================================
        # BARIS BAWAH: Riwayat Mini
        # ========================================================
        grup_riwayat = QGroupBox()
        layout_riwayat = QVBoxLayout(grup_riwayat)
        layout_riwayat.setContentsMargins(15, 15, 15, 15)

        lbl_head4 = QLabel("Riwayat Diagnosa Terakhir")
        lbl_head4.setStyleSheet(style_header_card)
        layout_riwayat.addWidget(lbl_head4)

        self.tabel_mini = QTableWidget()
        self.tabel_mini.setColumnCount(5)
        self.tabel_mini.setHorizontalHeaderLabels(["Waktu", "Kendaraan", "Beban", "Risiko", "Status"])

        self.tabel_mini.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel_mini.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabel_mini.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel_mini.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabel_mini.verticalHeader().setVisible(False)
        self.tabel_mini.setShowGrid(False)

        layout_riwayat.addWidget(self.tabel_mini)

        layout_utama.addLayout(layout_atas, 6)
        layout_utama.addWidget(grup_riwayat, 4)

        # Sisa kode (showEvent, muat_riwayat_mini, muat_daftar_mobil, reset_form, aksi_diagnosa)

    # TETAP SAMA PERSIS SEPERTI SEBELUMNYA.
    # (Saya cantumkan agar Anda tinggal Copy Paste)

    def showEvent(self, event):
        self.muat_riwayat_mini()
        super().showEvent(event)

    def muat_riwayat_mini(self):
        try:
            daftar_log = self.db.ambil_semua_log()[:5]
            self.tabel_mini.setRowCount(0)

            for baris_idx, data in enumerate(daftar_log):
                self.tabel_mini.insertRow(baris_idx)

                waktu_singkat = str(data[0]).split(" ")[1] if " " in str(data[0]) else str(data[0])
                item_waktu = QTableWidgetItem(waktu_singkat)
                item_nama = QTableWidgetItem(str(data[1]))

                beban_bersih = float(data[4])
                risiko_bersih = float(data[7])

                item_beban = QTableWidgetItem(f"{beban_bersih:.1f}%")
                item_risiko = QTableWidgetItem(f"{risiko_bersih:.1f}%")

                item_status = QTableWidgetItem(str(data[8]))
                item_status.setFont(QFont("Segoe UI", 9, QFont.Bold))

                if "NORMAL" in str(data[8]):
                    item_status.setForeground(QBrush(QColor("#4ade80")))
                elif "WARNING" in str(data[8]) or "WASPADA" in str(data[8]):
                    item_status.setForeground(QBrush(QColor("#fbbf24")))
                else:
                    item_status.setForeground(QBrush(QColor("#f87171")))

                for item in [item_waktu, item_nama, item_beban, item_risiko, item_status]:
                    item.setTextAlignment(Qt.AlignCenter)

                self.tabel_mini.setItem(baris_idx, 0, item_waktu)
                self.tabel_mini.setItem(baris_idx, 1, item_nama)
                self.tabel_mini.setItem(baris_idx, 2, item_beban)
                self.tabel_mini.setItem(baris_idx, 3, item_risiko)
                self.tabel_mini.setItem(baris_idx, 4, item_status)
        except Exception as e:
            print(f"[UI Error]: Gagal memuat mini riwayat: {e}")

    def muat_daftar_mobil(self):
        self.combo_mobil.clear()
        for mobil in self.db.ambil_data():
            self.combo_mobil.addItem(mobil.nama)

    def reset_form(self):
        self.input_rpm.clear()
        self.input_suhu_mesin.clear()
        self.input_suhu_udara.clear()
        self.lbl_status.setText("STATUS: MENUNGGU INPUT...")
        self.lbl_status.setStyleSheet("color: white;")
        self.lbl_torsi.setText("Kalkulasi Torsi Kendaraan: - Nm")
        self.lbl_beban.setText("Persentase Beban Mesin: 0%")
        self.lbl_beban.setStyleSheet("color: white;")
        self.bar_risiko.setValue(0)
        self.bar_risiko.setStyleSheet("")
        self.teks_insight.clear()
        self.lbl_detail_ai.setText("Data Transparan AI:\n-")

    def aksi_diagnosa(self):
        nama_mobil = self.combo_mobil.currentText()
        t_rpm = self.input_rpm.text()
        t_suhu_m = self.input_suhu_mesin.text()
        t_suhu_u = self.input_suhu_udara.text()

        if not t_rpm or not t_suhu_m or not t_suhu_u:
            QMessageBox.warning(self, "Peringatan", "Isi semua data telemetri!")
            return
        try:
            rpm_live = int(t_rpm)
            suhu_m = float(t_suhu_m)
            suhu_u = float(t_suhu_u)
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Gunakan angka yang benar!")
            return

        mobil_target = next((m for m in self.db.ambil_data() if m.nama == nama_mobil), None)
        if not mobil_target: return

        ai_terpilih = self.ai_pickle if self.radio_pickle.isChecked() else self.ai_manual
        hasil = self.logika.proses(rpm_live, suhu_m, suhu_u, mobil_target, ai_terpilih)

        self.lbl_status.setText(f"STATUS AI: {hasil['status']}")
        warna_tampil = "#4ade80" if hasil['warna'] == "green" else hasil['warna']
        self.lbl_status.setStyleSheet(f"color: {warna_tampil};")
        self.lbl_torsi.setText(f"Kalkulasi Torsi Kendaraan: {hasil['torsi']:.1f} Nm")

        beban = hasil['beban']
        self.lbl_beban.setText(f"Persentase Beban Mesin: {beban:.1f}%")
        self.lbl_beban.setStyleSheet(
            "color: #f87171; font-weight: bold;" if beban > 85 else "color: white; font-weight: bold;")

        self.bar_risiko.setValue(int(hasil['risiko']))
        self.bar_risiko.setStyleSheet(f"QProgressBar::chunk {{ background-color: {warna_tampil}; }}")

        self.teks_insight.setText(hasil['insight'])
        self.lbl_detail_ai.setText(hasil['data_ai'])

        if "ERROR" not in hasil['status']:
            status_db = hasil['status'].replace("WARNING (WASPADA)", "WARNING")
            try:
                self.db.simpan_log_diagnosa(nama_mobil, rpm_live, hasil['torsi'], hasil['beban'], suhu_m, suhu_u,
                                            hasil['risiko'], status_db)
                self.muat_riwayat_mini()
            except Exception as e:
                pass