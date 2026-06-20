# File: core/mesin_ai_pickle.py
import pickle
import pandas as pd
import warnings

# Abaikan warning bawaan yang tidak perlu
warnings.filterwarnings('ignore')


class MesinDiagnosaPickle:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.muat_model()

    def muat_model(self):
        """Memuat otak AI dan alat ukur skala (Scaler) dari file .pkl"""
        try:
            with open('model_terbaik.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open('scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            print("[OK] Mesin AI (Mode Pickle / SMOTE) berhasil dinyalakan.")
        except FileNotFoundError:
            print("[ERROR] File model_terbaik.pkl atau scaler.pkl tidak ditemukan!")

    def siapkan_data(self, rpm, suhu_m, suhu_u, torsi):
        """Membungkus data dari UI menjadi format yang dikenali oleh AI"""
        if self.scaler is None:
            return None

        # 1. Tuliskan nama kolom PERSIS seperti saat file latih_ulang.py dijalankan
        nama_kolom = [
            'Rotational speed [rpm]',
            'Process temperature [K]',
            'Air temperature [K]',
            'Torque [Nm]'
        ]

        # 2. Bungkus angka mentah menjadi Pandas DataFrame agar scikit-learn tidak cerewet
        df_input = pd.DataFrame([[rpm, suhu_m, suhu_u, torsi]], columns=nama_kolom)

        # 3. Sesuaikan skala angkanya
        data_scaled = self.scaler.transform(df_input)
        return data_scaled

    def prediksi(self, data_matang):
        """Fungsi fallback jika UI meminta tebakan mentah (Bukan Probabilitas)"""
        if self.model is None or data_matang is None:
            return "ERROR"

        hasil = self.model.predict(data_matang)
        if hasil[0] == 1:
            return "MALFUNGSI"
        else:
            return "NORMAL"