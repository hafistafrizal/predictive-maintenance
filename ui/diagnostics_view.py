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

    Komponen UI:
    - Panel Input   : form RPM, suhu mesin, suhu udara, pilihan kendaraan
    - Panel ML      : pilihan model (Pickle vs Manual CSV) + tombol proses
    - Panel Hasil   : dashboard status, torsi, beban, risiko, insight, detail AI
    - Panel Riwayat : tabel mini 5 diagnosa terakhir
    """

    def __init__(self, database):
        super().__init__()
        self.db = database

        # Inisialisasi LogikaDiagnosa yang mengorkestrasi kalkulator torsi + KNN
        self.logika = LogikaDiagnosa()

        # Model Pickle dimuat saat startup (cepat, dari file .pkl)
        self.ai_pickle = MesinDiagnosaPickle()

        # Model Manual ditunda (lazy loading) agar startup aplikasi tetap instan.
        # Akan diinisialisasi pertama kali saat pengguna memilih mode AI Manual.
        self.ai_manual = None

        self.atur_tampilan()
        self.muat_daftar_mobil()
        self.muat_riwayat_mini()

    def atur_tampilan(self):
        """Menyusun struktur tata letak utama halaman diagnosa dengan scrollbar."""
        # Scroll Area memungkinkan konten tidak terpotong di layar kecil
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        wadah_konten = QWidget()

        layout_utama = QVBoxLayout(wadah_konten)
        layout_utama.setContentsMargins(15, 15, 15, 15)
        layout_utama.setSpacing(15)

        layout_atas = QHBoxLayout()
        layout_atas.setSpacing(15)

        # Inisialisasi masing-masing panel secara modular
        grup_input = self._init_panel_input()
        grup_opsi  = self._init_panel_ml()
        grup_hasil = self._init_panel_hasil()

        # Alokasi lebar panel dengan faktor stretch (3 : 2 : 4)
        layout_atas.addWidget(grup_input, 3)
        layout_atas.addWidget(grup_opsi, 2)
        layout_atas.addWidget(grup_hasil, 4)

        grup_riwayat = self._init_panel_riwayat()

        layout_utama.addLayout(layout_atas, 6)
        layout_utama.addWidget(grup_riwayat, 4)

        scroll_area.setWidget(wadah_konten)

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

        # ComboBox kendaraan: reset form saat pilihan berubah untuk menghindari data stale
        self.combo_mobil = QComboBox()
        self.combo_mobil.currentIndexChanged.connect(self.reset_form)

        self.input_rpm       = QLineEdit()
        self.input_suhu_mesin = QLineEdit()
        self.input_suhu_udara = QLineEdit()

        # Validator input: membatasi rentang yang dapat diketik pengguna di UI.
        # Catatan: validasi logis lebih ketat dilakukan di LogikaDiagnosa.proses().
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

        # Radio button pilihan model AI:
        # - Pickle: model pre-trained dari file .pkl (cepat, sudah ter-SMOTE)
        # - Manual: live training dari CSV saat ini (lebih lambat, data selalu segar)
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

        # Label status utama (WordWrap aktif untuk mencegah layout overflow horizontal)
        self.lbl_status = QLabel("STATUS: MENUNGGU INPUT...")
        self.lbl_status.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setMinimumHeight(40)
        self.lbl_status.setWordWrap(True)

        # Label hasil kalkulasi torsi dan beban mesin
        self.lbl_torsi = QLabel("Kalkulasi Torsi Kendaraan: - Nm")
        self.lbl_torsi.setWordWrap(True)

        self.lbl_beban = QLabel("Persentase Beban Mesin: 0%")
        self.lbl_beban.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_beban.setWordWrap(True)

        # Progress bar visual untuk menampilkan persentase risiko KNN (0–100%)
        self.bar_risiko = QProgressBar()
        self.bar_risiko.setRange(0, 100)
        self.bar_risiko.setValue(0)
        self.bar_risiko.setTextVisible(True)
        self.bar_risiko.setMinimumHeight(28)

        # Area insight: penjelasan logis hasil diagnosa untuk mekanik
        self.teks_insight = QTextEdit()
        self.teks_insight.setReadOnly(True)
        self.teks_insight.setMinimumHeight(100)
        self.teks_insight.setMaximumHeight(150)
        self.teks_insight.setStyleSheet(
            "background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #444444; border-radius: 5px;")

        # Label detail teknis pemetaan domain AI (transparan ke mekanik)
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
        """Inisialisasi panel bawah: Tabel mini 5 riwayat diagnosa terakhir."""
        grup = QGroupBox()
        layout = QVBoxLayout(grup)
        layout.setContentsMargins(15, 15, 15, 15)

        lbl_head = QLabel("Riwayat Diagnosa Terakhir")
        lbl_head.setStyleSheet(STYLE_HEADER_CARD)
        layout.addWidget(lbl_head)

        self.tabel_mini = QTableWidget()
        self.tabel_mini.setColumnCount(5)
        self.tabel_mini.setHorizontalHeaderLabels(["Waktu", "Kendaraan", "Beban", "Risiko", "Status"])

        # Responsivitas kolom: stretch semua kecuali kolom waktu (ResizeToContents)
        self.tabel_mini.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabel_mini.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabel_mini.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel_mini.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabel_mini.verticalHeader().setVisible(False)
        self.tabel_mini.setShowGrid(False)
        self.tabel_mini.setMinimumHeight(180)

        layout.addWidget(self.tabel_mini)
        return grup

    def showEvent(self, event):
        """Memperbarui riwayat mini setiap kali tab Diagnosa AI diakses."""
        self.muat_riwayat_mini()
        super().showEvent(event)

    def muat_riwayat_mini(self):
        """
        Mengambil 5 log diagnosa terakhir dari database dan menampilkannya
        di tabel mini bagian bawah halaman diagnosa.

        Kolom yang ditampilkan: Waktu, Kendaraan, Beban (%), Risiko (%), Status
        Data log diambil dari ambil_semua_log() yang sudah diurutkan DESC (terbaru duluan).
        """
        try:
            # Ambil 5 rekaman terbaru (ORDER BY id DESC sudah dilakukan di DB)
            daftar_log = self.db.ambil_semua_log()[:5]
            self.tabel_mini.setRowCount(0)

            for baris_idx, data in enumerate(daftar_log):
                self.tabel_mini.insertRow(baris_idx)

                # Kolom 0 (tanggal): ambil bagian jam:menit:detik saja
                waktu_singkat = str(data[0]).split(" ")[1] if " " in str(data[0]) else str(data[0])
                item_waktu  = QTableWidgetItem(waktu_singkat)
                item_nama   = QTableWidgetItem(str(data[1]))

                # Kolom 4 = beban (%), Kolom 7 = risiko (%) dari query DB
                beban_bersih  = float(data[4])
                risiko_bersih = float(data[7])

                item_beban  = QTableWidgetItem(f"{beban_bersih:.1f}%")
                item_risiko = QTableWidgetItem(f"{risiko_bersih:.1f}%")

                item_status = QTableWidgetItem(str(data[8]))
                item_status.setFont(QFont("Segoe UI", 9, QFont.Bold))

                # Pewarnaan teks status: hijau=Normal, kuning=Warning, merah=Malfungsi
                status_str = str(data[8])
                if "NORMAL" in status_str:
                    item_status.setForeground(QBrush(QColor("#4ade80")))
                elif "WARNING" in status_str or "WASPADA" in status_str:
                    item_status.setForeground(QBrush(QColor("#fbbf24")))
                else:
                    item_status.setForeground(QBrush(QColor("#f87171")))

                # Rata-tengah semua item
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
        self.combo_mobil.blockSignals(True)   # Cegah trigger reset_form berulang saat reload
        self.combo_mobil.clear()
        for mobil in self.db.ambil_data():
            self.combo_mobil.addItem(mobil.nama)
        self.combo_mobil.blockSignals(False)

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
        """
        Melakukan pemrosesan input telemetri menggunakan model AI terpilih (KNN).

        Alur:
        1. Validasi form tidak kosong
        2. Konversi teks input ke tipe numerik
        3. Ambil profil kendaraan dari DB (single call, disimpan di variabel lokal)
        4. Inisialisasi AI Manual jika belum ada (lazy loading)
        5. Jalankan LogikaDiagnosa.proses() → pipeline lengkap torsi + KNN
        6. Update semua komponen UI dari dictionary hasil
        7. Simpan log ke DB jika bukan ERROR
        """
        nama_mobil = self.combo_mobil.currentText()

        # Pastikan ada kendaraan terpilih
        if not nama_mobil:
            QMessageBox.warning(self, "Peringatan", "Tidak ada kendaraan terdaftar di database!")
            return

        t_rpm    = self.input_rpm.text().strip()
        t_suhu_m = self.input_suhu_mesin.text().strip()
        t_suhu_u = self.input_suhu_udara.text().strip()

        # Validasi: semua kolom telemetri wajib diisi
        if not t_rpm or not t_suhu_m or not t_suhu_u:
            QMessageBox.warning(self, "Peringatan", "Isi semua data telemetri!")
            return

        try:
            # Konversi string input ke tipe numerik yang tepat
            rpm_live = int(t_rpm)
            suhu_m   = float(t_suhu_m)
            suhu_u   = float(t_suhu_u)
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Gunakan angka yang benar!")
            return

        # Ambil profil kendaraan sekali saja (satu pemanggilan DB)
        # Gunakan generator + next() untuk efisiensi tanpa perlu loop penuh
        semua_kendaraan = self.db.ambil_data()
        mobil_target = next((m for m in semua_kendaraan if m.nama == nama_mobil), None)
        if not mobil_target:
            QMessageBox.warning(self, "Peringatan", f"Kendaraan '{nama_mobil}' tidak ditemukan di database!")
            return

        # --- Pilih model AI yang aktif ---
        if self.radio_pickle.isChecked():
            # Model Pickle: sudah dimuat saat startup, siap digunakan langsung
            ai_terpilih = self.ai_pickle
        else:
            # Model Manual: lazy loading → hanya dilatih saat pertama kali dipilih
            if self.ai_manual is None:
                self.lbl_status.setText("STATUS AI: MELATIH MODEL (TUNGGU)...")
                self.lbl_status.setStyleSheet("color: #fbbf24;")
                QApplication.processEvents()  # Paksa UI render pesan loading
                self.ai_manual = MesinDiagnosaManual()
            ai_terpilih = self.ai_manual

        # --- Eksekusi pipeline diagnosa ---
        # Menjalankan: validasi → kalkulasi torsi → domain adaptation → KNN predict_proba
        hasil = self.logika.proses(rpm_live, suhu_m, suhu_u, mobil_target, ai_terpilih)

        # --- Update semua komponen UI dari dictionary hasil ---

        # Status utama
        self.lbl_status.setText(f"STATUS AI: {hasil['status']}")
        # Warna hijau membutuhkan konversi karena 'green' native terlalu gelap di UI dark mode
        warna_tampil = "#4ade80" if hasil['warna'] == "green" else hasil['warna']
        self.lbl_status.setStyleSheet(f"color: {warna_tampil};")

        # Torsi estimasi kendaraan (dari kalkulator interpolasi linear)
        self.lbl_torsi.setText(f"Kalkulasi Torsi Kendaraan: {hasil['torsi']:.1f} Nm")

        # Persentase beban mesin (merah jika >85%)
        beban = hasil['beban']
        self.lbl_beban.setText(f"Persentase Beban Mesin: {beban:.1f}%")
        self.lbl_beban.setStyleSheet(
            "color: #f87171; font-weight: bold;" if beban > 85 else "color: white; font-weight: bold;")

        # Progress bar risiko (nilai int, karena QProgressBar tidak menerima float)
        self.bar_risiko.setValue(int(hasil['risiko']))
        self.bar_risiko.setStyleSheet(f"QProgressBar::chunk {{ background-color: {warna_tampil}; }}")

        # Teks insight dan detail teknis AI
        self.teks_insight.setText(hasil['insight'])
        self.lbl_detail_ai.setText(hasil['data_ai'])

        # --- Simpan log ke database (hanya jika bukan status ERROR) ---
        if "ERROR" not in hasil['status']:
            # Sederhanakan label status sebelum disimpan ke DB
            status_db = hasil['status'].replace("WARNING (WASPADA)", "WARNING")
            try:
                self.db.simpan_log_diagnosa(
                    nama_mobil, rpm_live, hasil['torsi'], hasil['beban'],
                    suhu_m, suhu_u, hasil['risiko'], status_db
                )
                # Perbarui tabel mini riwayat setelah log baru tersimpan
                self.muat_riwayat_mini()
            except Exception as e:
                print(f"[UI Error]: Gagal menyimpan log diagnosa: {e}")