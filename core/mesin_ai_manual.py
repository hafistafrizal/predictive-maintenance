# File: core/mesin_ai_manual.py
# Deskripsi: Subclass dari MesinDiagnosaBase yang melatih model KNN secara langsung (Live Training)
#            dari berkas dataset CSV menggunakan algoritma KNN dan penyeimbangan data SMOTE.
#
# Alur kerja:
#   1. Baca CSV → ambil 4 fitur + label
#   2. SMOTE    → seimbangkan kelas 0 (Normal) dan 1 (Failure) yang tidak seimbang
#   3. Scaling  → normalisasi fitur ke [0, 1] dengan MinMaxScaler
#   4. Training → latih KNeighborsClassifier(k=5) pada data seimbang

import os
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE
import warnings
from core.mesin_ai_base import MesinDiagnosaBase

# Abaikan pesan peringatan (warning) dari terminal yang tidak relevan
warnings.filterwarnings('ignore')

# Nama file dataset relatif terhadap direktori kerja (root project)
NAMA_FILE_CSV = "2020 Predictive Maintenance Dataset.csv"

# Kolom fitur yang digunakan untuk pelatihan (harus sama dengan saat prediksi)
KOLOM_FITUR = [
    'Rotational speed [rpm]',
    'Process temperature [K]',
    'Air temperature [K]',
    'Torque [Nm]'
]

# Kolom target/label
KOLOM_TARGET = 'Machine failure'


class MesinDiagnosaManual(MesinDiagnosaBase):
    """
    Model AI Diagnosa yang dilatih secara langsung (on-the-fly) saat aplikasi berjalan.
    Menggunakan dataset CSV asli dengan penyeimbangan SMOTE dan algoritma KNN.

    Pendekatan ini berguna ketika model .pkl tidak tersedia atau perlu diverifikasi
    langsung dari data mentah.
    """

    def __init__(self):
        # Panggil konstruktor base class untuk inisialisasi self.model dan self.scaler = None
        super().__init__()
        # Langsung latih model saat kelas ini diinstansiasi (proses beberapa detik)
        self.muat_dan_latih_dari_csv()

    def muat_dan_latih_dari_csv(self):
        """
        Membaca file CSV dan melatih model KNN secara langsung (Live Training).

        Tahapan:
        --------
        1. Verifikasi keberadaan file CSV
        2. Baca DataFrame dan validasi kolom yang diperlukan
        3. Terapkan SMOTE untuk mengatasi ketidakseimbangan kelas
           (dataset asli: ~97% Normal vs ~3% Failure)
        4. Normalisasi fitur dengan MinMaxScaler (fit pada data SMOTE)
        5. Latih KNN (k=5) pada data seimbang dan ter-scale

        SMOTE (Synthetic Minority Oversampling Technique):
        --------------------------------------------------
        Membuat sampel sintetis dari kelas minoritas (Failure) agar jumlah
        kedua kelas seimbang. Ini mencegah model bias ke kelas mayoritas (Normal).

        KNN k=5:
        ---------
        Saat prediksi, model mencari 5 tetangga terdekat (Euclidean distance)
        di ruang fitur ber-skala, lalu voting mayoritas menentukan kelas prediksi.
        predict_proba() = proporsi kelas dari 5 tetangga (mis. 3/5 Failure → 60% risiko).
        """
        try:
            # --- LANGKAH 0: Verifikasi keberadaan file ---
            if not os.path.isfile(NAMA_FILE_CSV):
                print(f"[ERROR] File '{NAMA_FILE_CSV}' tidak ditemukan di folder!")
                return  # self.model tetap None → safe fallback aktif

            print("[INFO] Memulai Mode AI Manual... Sedang membaca dataset CSV...")

            # --- LANGKAH 1: Baca data dari CSV ---
            df = pd.read_csv(NAMA_FILE_CSV)

            # Validasi: pastikan semua kolom yang dibutuhkan ada di CSV
            kolom_dibutuhkan = KOLOM_FITUR + [KOLOM_TARGET]
            kolom_hilang = [k for k in kolom_dibutuhkan if k not in df.columns]
            if kolom_hilang:
                print(f"[ERROR] Kolom berikut tidak ditemukan di CSV: {kolom_hilang}")
                return

            # --- LANGKAH 2: Pisahkan Fitur (X) dan Target (y) ---
            # X: 4 kolom sensor sebagai fitur input untuk KNN
            # y: label kelas (0 = Normal, 1 = Machine Failure)
            X = df[KOLOM_FITUR]
            y = df[KOLOM_TARGET]

            # --- LANGKAH 3: Terapkan SMOTE (Penyeimbangan Data) ---
            # Dataset asli sangat tidak seimbang → SMOTE membuat sampel sintetis
            # pada kelas minoritas (Failure) agar jumlah kelas seimbang.
            # random_state=42 memastikan hasil reproducible.
            print("[INFO] Sedang menyeimbangkan data (SMOTE)...")
            smote = SMOTE(random_state=42)
            X_seimbang, y_seimbang = smote.fit_resample(X, y)

            # --- LANGKAH 4: Normalisasi Fitur (Feature Scaling) ---
            # MinMaxScaler mengubah setiap fitur ke rentang [0, 1]:
            #   x_scaled = (x - x_min) / (x_max - x_min)
            # Scaler di-FIT pada X_seimbang (bukan X asli) agar konsisten dengan SMOTE.
            self.scaler = MinMaxScaler()
            X_scaled = self.scaler.fit_transform(X_seimbang)

            # --- LANGKAH 5: Latih Model KNN ---
            # n_neighbors=5 → 5 tetangga terdekat digunakan untuk voting prediksi.
            # Pemilihan k=5 adalah trade-off umum: cukup robust tapi tidak terlalu smooth.
            self.model = KNeighborsClassifier(n_neighbors=5)
            self.model.fit(X_scaled, y_seimbang)

            print("[OK] Mesin AI Manual (Live CSV + SMOTE) berhasil dilatih dan siap!")

        except FileNotFoundError:
            # Antisipasi race condition: file ada saat cek os.path tapi hilang saat dibaca
            print(f"[ERROR] File '{NAMA_FILE_CSV}' tidak ditemukan!")

        except Exception as e:
            # Tangkap error apapun selama training (misal: data corrupt, memory error)
            print(f"[ERROR] Terjadi kesalahan saat melatih AI Manual: {e}")
            # Pastikan state bersih agar tidak crash di hilir
            self.model = None
            self.scaler = None