# File: core/mesin_ai_manual.py
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE # Tambahan untuk mencerdaskan AI Manual
import warnings

# Mengabaikan pesan peringatan (warning) dari terminal
warnings.filterwarnings('ignore')

class MesinDiagnosaManual:
    def __init__(self):
        # Menyediakan tempat untuk model dan alat penyesuai skala
        self.model = None
        self.scaler = None

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

    def siapkan_data(self, rpm, suhu_m, suhu_u, torsi):
        """Membungkus data inputan mekanik agar formatnya dikenali AI"""
        if self.scaler is None:
            return None

        nama_kolom = [
            'Rotational speed [rpm]',
            'Process temperature [K]',
            'Air temperature [K]',
            'Torque [Nm]'
        ]

        df_input = pd.DataFrame([[rpm, suhu_m, suhu_u, torsi]], columns=nama_kolom)
        data_scaled = self.scaler.transform(df_input)
        return data_scaled

    def prediksi(self, data_matang):
        """Fungsi fallback (cadangan) untuk menghasilkan tebakan akhir"""
        if self.model is None or data_matang is None:
            return "ERROR"

        hasil = self.model.predict(data_matang)

        if hasil[0] == 1:
            return "MALFUNGSI"
        else:
            return "NORMAL"