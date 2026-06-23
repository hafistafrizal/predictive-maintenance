# File: core/mesin_ai_base.py
# Deskripsi: Kelas dasar (base class) untuk model AI diagnosa. Menyediakan fungsi scaling data input,
#            serta hitung risiko kegagalan mesin berbasis probabilitas.

import pandas as pd

class MesinDiagnosaBase:
    def __init__(self):
        self.model = None
        self.scaler = None

    def siapkan_data(self, rpm, suhu_m, suhu_u, torsi):
        """Membungkus data dari UI menjadi format yang dikenali oleh AI"""
        if self.scaler is None:
            return None

        # Nama kolom harus sama dengan yang digunakan saat melatih model
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
        """Fungsi fallback jika UI meminta tebakan mentah (Bukan Probabilitas)"""
        if self.model is None or data_matang is None:
            return "ERROR"

        hasil = self.model.predict(data_matang)
        if hasil[0] == 1:
            return "MALFUNGSI"
        else:
            return "NORMAL"

    def hitung_risiko(self, data_matang):
        """Menghitung persentase risiko kerusakan berdasarkan probabilitas kegagalan KNN"""
        if self.model is None or data_matang is None:
            return 0.0
        try:
            # Mengambil probabilitas kelas 1 (Machine failure)
            probabilitas = self.model.predict_proba(data_matang)[0]
            return float(probabilitas[1] * 100.0)
        except AttributeError:
            # Fallback jika model tidak mendukung predict_proba (misal bukan scikit-learn standard)
            hasil_mentah = self.prediksi(data_matang)
            return 85.0 if hasil_mentah == "MALFUNGSI" else 10.0
