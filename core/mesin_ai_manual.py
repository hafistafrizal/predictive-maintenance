# File: core/mesin_ai_manual.py
# Deskripsi: Mengimplementasikan model AI manual yang dilatih secara langsung (Live Training) dari berkas dataset CSV
#            menggunakan algoritma KNN dan penyeimbangan data SMOTE.

import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE # Tambahan untuk mencerdaskan AI Manual
import warnings
from core.mesin_ai_base import MesinDiagnosaBase

# Mengabaikan pesan peringatan (warning) dari terminal
warnings.filterwarnings('ignore')

class MesinDiagnosaManual(MesinDiagnosaBase):
    def __init__(self):
        # Memanggil konstruktor base class
        super().__init__()
        # Langsung melatih model saat kelas ini dipanggil
        self.muat_dan_latih_dari_csv()

    def muat_dan_latih_dari_csv(self):
        """Membaca file CSV dan melatih model KNN secara langsung (Live Training)"""
        try:
            print("[INFO] Memulai Mode AI Manual... Sedang membaca dataset CSV...")
            # 1. Baca data asli
            df = pd.read_csv("2020 Predictive Maintenance Dataset.csv")

            # 2. Tentukan Kolom Input (X) dan Target (y)
            X = df[['Rotational speed [rpm]', 'Process temperature [K]', 'Air temperature [K]', 'Torque [Nm]']]
            y = df['Machine failure']

            # ==========================================================
            # KUNCI PERBAIKAN: Menyuntikkan SMOTE agar AI Manual Cerdas
            # ==========================================================
            print("[INFO] Sedang menyeimbangkan data (SMOTE)...")
            smote = SMOTE(random_state=42)
            X_seimbang, y_seimbang = smote.fit_resample(X, y)

            # 3. Lakukan Scaling (Penyesuaian Skala Angka) dari data seimbang
            self.scaler = MinMaxScaler()
            X_scaled = self.scaler.fit_transform(X_seimbang)

            # 4. Latih Otak AI dengan Algoritma KNN
            self.model = KNeighborsClassifier(n_neighbors=5)
            self.model.fit(X_scaled, y_seimbang)

            print("[OK] Mesin AI Manual (Live CSV + SMOTE) berhasil dilatih dan siap!")

        except FileNotFoundError:
            print("[ERROR] File '2020 Predictive Maintenance Dataset.csv' tidak ditemukan di folder!")
        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan saat melatih AI Manual: {e}")