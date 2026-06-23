# File: ui/diagnostics_view.py
# Deskripsi: Mengimplementasikan kelas TampilanDiagnosa yang menyediakan panel input telemetri,
#            pilihan model Machine Learning (KNN dari file biner atau CSV),
#            dashboard visualisasi hasil diagnosa, serta riwayat singkat diagnosa terakhir.

from PySide6.QtWidgets import *
from PySide6.QtGui import QFont, QIntValidator, QDoubleValidator, QBrush, QColor
from PySide6.QtCore import Qt

from core.mesin_ai_pickle import MesinDiagnosaPickle
from core.mesin_ai_manual import MesinDiagnosaManual
from core.logika_diagnosa import LogikaDiagnosa
from ui.styles import STYLE_HEADER_CARD


class TampilanDiagnosa(QWidget):
    """
    Kelas widget utama untuk melakukan diagnosa pemeliharaan prediktif kendaraan.
    Menghubungkan data input telemetri pengguna ke model AI (KNN).
    """
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.logika = LogikaDiagnosa()
        self.ai_pickle = MesinDiagnosaPickle()
        self.ai_manual = None  # Ditunda (lazy loaded) agar startup aplikasi instan
        self.atur_tampilan()
        self.muat_daftar_mobil()
        self.muat_riwayat_mini()

    def atur_tampilan(self):
        """Menyusun struktur tata letak utama halaman diagnosa dengan scrollbar."""
        # 1. Membuat area pengguliran (Scroll Area)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # 2. Membuat widget kontainer utama
        wadah_konten = QWidget()

        layout_utama = QVBoxLayout(wadah_konten)
        layout_utama.setContentsMargins(15, 15, 15, 15)
        layout_utama.setSpacing(15)

        layout_atas = QHBoxLayout()
        layout_atas.setSpacing(15)

        # Inisialisasi masing-masing panel secara modular
        grup_input = self._init_panel_input()
        grup_opsi = self._init_panel_ml()
        grup_hasil = self._init_panel_hasil()

        # Menambahkan panel atas ke layout (Form Input, Opsi ML, Dashboard Hasil)
        layout_atas.addWidget(grup_input, 3)
        layout_atas.addWidget(grup_opsi, 2)
        layout_atas.addWidget(grup_hasil, 4)

        # Inisialisasi panel riwayat di bagian bawah
        grup_riwayat = self._init_panel_riwayat()

        layout_utama.addLayout(layout_atas, 6)
        layout_utama.addWidget(grup_riwayat, 4)

        # 3. Menetapkan widget kontainer ke dalam Scroll Area
        scroll_area.setWidget(wadah_konten)

        # 4. Memasang Scroll Area ke layout luar widget utama
        layout_self = QVBoxLayout(self)
        layout_self.setContentsMargins(0, 0, 0, 0)
        layout_self.addWidget(scroll_area)

    def _init_panel_input(self) -> QGroupBox:
        """Inisialisasi panel kiri: Form input telemetri kendaraan."""
        grup = QGroupBox()
        layout = QVBoxLayout(grup)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        lbl_head = QLabel("Input Telemetri Kendaraan")
        lbl_head.setStyleSheet(STYLE_HEADER_CARD)
        layout.addWidget(lbl_head)

        self.combo_mobil = QComboBox()
        self.combo_mobil.currentIndexChanged.connect(self.reset_form)
        self.input_rpm = QLineEdit()
        self.input_suhu_mesin = QLineEdit()
        self.input_suhu_udara = QLineEdit()

        # Validasi input numerik
        self.input_rpm.setValidator(QIntValidator(-10000, 50000))
        self.input_suhu_mesin.setValidator(QDoubleValidator(-100.0, 500.0, 2))
        self.input_suhu_udara.setValidator(QDoubleValidator(-100.0, 500.0, 2))

        layout.addWidget(QLabel("Pilih Kendaraan:"))
        layout.addWidget(self.combo_mobil)
        layout.addWidget(QLabel("RPM Mesin Saat Ini:"))
        layout.addWidget(self.input_rpm)
        layout.addWidget(QLabel("Suhu Mesin (°C):"))
        layout.addWidget(self.input_suhu_mesin)
        layout.addWidget(QLabel("Suhu Udara (°C):"))
        layout.addWidget(self.input_suhu_udara)
        layout.addStretch()
        
        return grup

    def _init_panel_ml(self) -> QGroupBox:
        """Inisialisasi panel tengah: Memilih model machine learning & tombol eksekusi."""
        grup = QGroupBox()
        layout = QVBoxLayout(grup)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        lbl_head = QLabel("Model Machine Learning")
        lbl_head.setStyleSheet(STYLE_HEADER_CARD)
        layout.addWidget(lbl_head)

        lbl_desc = QLabel("Pilih algoritma pemrosesan\nuntuk diagnosa telemetri:")
        lbl_desc.setStyleSheet("color: #9ca3af; font-size: 12px;")
        layout.addWidget(lbl_desc)

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

        layout.addWidget(self.radio_pickle)
        layout.addWidget(self.radio_manual)
        layout.addStretch()
        layout.addWidget(self.btn_proses)
        layout.addWidget(self.btn_reset)
        
        return grup

    def _init_panel_hasil(self) -> QGroupBox:
        """Inisialisasi panel kanan: Dashboard hasil visualisasi diagnosa AI."""
        grup = QGroupBox()
        layout = QVBoxLayout(grup)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        lbl_head = QLabel("Dashboard Hasil")
        lbl_head.setStyleSheet(STYLE_HEADER_CARD)
        layout.addWidget(lbl_head)

        # Label status (WordWrap aktif untuk mencegah layout shifting/melebar ke samping)
        self.lbl_status = QLabel("STATUS: MENUNGGU INPUT...")
        self.lbl_status.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setMinimumHeight(40)
        self.lbl_status.setWordWrap(True)

        self.lbl_torsi = QLabel("Kalkulasi Torsi Kendaraan: - Nm")
        self.lbl_torsi.setWordWrap(True)
        
        self.lbl_beban = QLabel("Persentase Beban Mesin: 0%")
        self.lbl_beban.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_beban.setWordWrap(True)

        # Progress bar risiko kerusakan
        self.bar_risiko = QProgressBar()
        self.bar_risiko.setRange(0, 100)
        self.bar_risiko.setValue(0)
        self.bar_risiko.setTextVisible(True)
        self.bar_risiko.setMinimumHeight(28)

        # Area insight penjelasan logis dari AI (Batas tinggi diatur agar proporsional)
        self.teks_insight = QTextEdit()
        self.teks_insight.setReadOnly(True)
        self.teks_insight.setMinimumHeight(100)
        self.teks_insight.setMaximumHeight(150)
        self.teks_insight.setStyleSheet(
            "background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #444444; border-radius: 5px;")

        # Label detail teknis AI (WordWrap aktif agar teks multi-line dari core tertata rapi)
        self.lbl_detail_ai = QLabel("Data Transparan AI:\n-")
        self.lbl_detail_ai.setStyleSheet("color: #6b7280; font-size: 11px;")
        self.lbl_detail_ai.setWordWrap(True)

        layout.addWidget(self.lbl_status)
        layout.addWidget(self.lbl_torsi)
        layout.addWidget(self.lbl_beban)
        layout.addWidget(QLabel("Persentase Risiko Kerusakan:"))
        layout.addWidget(self.bar_risiko)
        layout.addWidget(QLabel("Insight & Keterangan Risiko:"))
        layout.addWidget(self.teks_insight)
        layout.addWidget(self.lbl_detail_ai)
        
        return grup

    def _init_panel_riwayat(self) -> QGroupBox:
        """Inisialisasi panel bawah: Tabel mini riwayat diagnosa."""
        grup = QGroupBox()
        layout = QVBoxLayout(grup)
        layout.setContentsMargins(15, 15, 15, 15)

        lbl_head = QLabel("Riwayat Diagnosa Terakhir")
        lbl_head.setStyleSheet(STYLE_HEADER_CARD)
        layout.addWidget(lbl_head)

        self.tabel_mini = QTableWidget()
        self.tabel_mini.setColumnCount(5)
        self.tabel_mini.setHorizontalHeaderLabels(["Waktu", "Kendaraan", "Beban", "Risiko", "Status"])

        # Menyesuaikan lebar kolom secara otomatis
        self.tabel_mini.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel_mini.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabel_mini.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel_mini.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabel_mini.verticalHeader().setVisible(False)
        self.tabel_mini.setShowGrid(False)
        # Menetapkan tinggi minimum agar tabel riwayat selalu terlihat proporsional
        self.tabel_mini.setMinimumHeight(180)

        layout.addWidget(self.tabel_mini)
        return grup

    def showEvent(self, event):
        """Memperbarui riwayat mini setiap kali tab ini diakses."""
        self.muat_riwayat_mini()
        super().showEvent(event)

    def muat_riwayat_mini(self):
        """Mengambil data 5 log diagnosa terakhir dari database untuk tabel mini."""
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

                # Pewarnaan teks status secara visual
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
        """Memuat daftar kendaraan terdaftar dari basis data ke ComboBox pilihan."""
        self.combo_mobil.clear()
        for mobil in self.db.ambil_data():
            self.combo_mobil.addItem(mobil.nama)

    def reset_form(self):
        """Mengosongkan form input dan mengembalikan dashboard hasil ke kondisi semula."""
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
        """Melakukan pemrosesan input telemetri menggunakan model AI terpilih."""
        nama_mobil = self.combo_mobil.currentText()
        t_rpm = self.input_rpm.text()
        t_suhu_m = self.input_suhu_mesin.text()
        t_suhu_u = self.input_suhu_udara.text()

        # Validasi kolom wajib diisi
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
        if not mobil_target: 
            return

        # Penanganan lazy loading untuk AI Manual (agar startup aplikasi tetap instan)
        if self.radio_pickle.isChecked():
            ai_terpilih = self.ai_pickle
        else:
            if self.ai_manual is None:
                self.lbl_status.setText("STATUS AI: MELATIH MODEL (TUNGGU)...")
                self.lbl_status.setStyleSheet("color: #fbbf24;")
                QApplication.processEvents()  # Memaksa UI memperbarui tulisan
                self.ai_manual = MesinDiagnosaManual()
            ai_terpilih = self.ai_manual

        # Memproses perhitungan kalkulator torsi dan model machine learning
        hasil = self.logika.proses(rpm_live, suhu_m, suhu_u, mobil_target, ai_terpilih)

        # Mengupdate visualisasi dashboard hasil
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

        # Menyimpan catatan diagnosa ke dalam basis data
        if "ERROR" not in hasil['status']:
            status_db = hasil['status'].replace("WARNING (WASPADA)", "WARNING")
            try:
                self.db.simpan_log_diagnosa(nama_mobil, rpm_live, hasil['torsi'], hasil['beban'], suhu_m, suhu_u,
                                             hasil['risiko'], status_db)
                self.muat_riwayat_mini()
            except Exception as e:
                pass