# File: core/mesin_ai_base.py
# Deskripsi: Kelas dasar (base class / abstract class) untuk semua model AI diagnosa.
#            Menyediakan:
#            - siapkan_data()  → mengubah 4 parameter input menjadi format numpy scaled
#            - prediksi()      → prediksi kelas keras (0=Normal, 1=Malfungsi)
#            - hitung_risiko() → menghitung persentase risiko kerusakan dari probabilitas KNN

import pandas as pd


class MesinDiagnosaBase:
    """
    Kelas dasar (Base Class) untuk model Machine Learning diagnosa mesin.
    Semua model AI (Pickle maupun Manual CSV) harus mewarisi kelas ini.

    Atribut:
    --------
    model  : objek sklearn classifier (KNN atau lainnya), None sampai dimuat/dilatih
    scaler : objek sklearn scaler (MinMaxScaler), None sampai dimuat/dilatih
    """

    def __init__(self):
        # Inisialisasi placeholder model dan scaler.
        # Akan diisi oleh subclass setelah pemuatan/pelatihan selesai.
        self.model = None
        self.scaler = None

    def siapkan_data(self, rpm: float, suhu_m: float, suhu_u: float, torsi: float):
        """
        Mengubah parameter telemetri mentah menjadi format DataFrame ber-skala
        yang dikenali oleh model Machine Learning.

        Parameter:
        ----------
        rpm    : float - RPM mesin dalam domain dataset AI (bukan RPM live kendaraan)
        suhu_m : float - Suhu proses mesin dalam Kelvin (domain dataset AI)
        suhu_u : float - Suhu udara dalam Kelvin (domain dataset AI)
        torsi  : float - Torsi dalam Nm (domain dataset AI)

        Return:
        -------
        numpy.ndarray  - Data yang sudah di-scale siap masuk model predict()
        None           - Jika scaler belum dimuat (model tidak siap)

        Logika:
        -------
        1. Bungkus 4 nilai ke DataFrame dengan nama kolom persis sesuai saat training.
        2. Terapkan scaler.transform() → mengubah ke skala [0,1] MinMax.
        """
        # Jika scaler belum ada (model belum dimuat/dilatih), kembalikan None.
        if self.scaler is None:
            return None

        # Nama kolom HARUS sama persis dengan yang digunakan saat melatih model.
        # Urutan: RPM → Suhu Proses → Suhu Udara → Torsi
        nama_kolom = [
            'Rotational speed [rpm]',
            'Process temperature [K]',
            'Air temperature [K]',
            'Torque [Nm]'
        ]

        # Buat DataFrame 1 baris dari input (format yang dimengerti sklearn)
        df_input = pd.DataFrame([[rpm, suhu_m, suhu_u, torsi]], columns=nama_kolom)

        # Terapkan scaling: setiap fitur dipetakan ke rentang [0, 1]
        # berdasarkan min/max yang dipelajari saat fit pada data training.
        data_scaled = self.scaler.transform(df_input)
        return data_scaled

    def prediksi(self, data_matang) -> str:
        """
        Melakukan prediksi kelas keras (Hard Prediction) terhadap data yang sudah di-scale.

        Return: "MALFUNGSI" jika kelas=1, "NORMAL" jika kelas=0, "ERROR" jika model belum siap.

        Catatan: Fungsi ini adalah fallback. Gunakan hitung_risiko() untuk probabilitas yang lebih
                 informatif dan digunakan oleh LogikaDiagnosa.
        """
        # Jika model belum dimuat atau data tidak tersedia, kembalikan error string.
        if self.model is None or data_matang is None:
            return "ERROR"

        # KNN predict() mengembalikan array kelas prediksi → ambil elemen pertama (1 baris input)
        hasil = self.model.predict(data_matang)
        if hasil[0] == 1:
            return "MALFUNGSI"
        else:
            return "NORMAL"

    def hitung_risiko(self, data_matang) -> float:
        """
        Menghitung persentase risiko kerusakan mesin berdasarkan probabilitas output KNN.

        KNN dengan predict_proba() mengembalikan probabilitas untuk setiap kelas:
          - probabilitas[0] = peluang kelas 0 (NORMAL)
          - probabilitas[1] = peluang kelas 1 (MALFUNGSI / Machine Failure)

        Return:
        -------
        float - nilai risiko dalam rentang [0.0, 100.0] (persen)
                  0.0  → dipastikan normal
                 100.0 → dipastikan malfungsi

        Rumus:
        ------
          risiko (%) = probabilitas[1] * 100

        Fallback:
        ---------
        Jika model tidak mendukung predict_proba() (misalnya model custom non-sklearn),
        maka hasil prediksi keras digunakan sebagai proxy:
          - MALFUNGSI → 85.0%
          - NORMAL    → 10.0%
        """
        # Jika model atau data tidak tersedia, risiko dianggap nol (aman secara default).
        if self.model is None or data_matang is None:
            return 0.0

        try:
            # predict_proba mengembalikan array 2D: shape (n_samples, n_classes)
            # Contoh: [[0.8, 0.2]] → 80% Normal, 20% Malfungsi
            proba_array = self.model.predict_proba(data_matang)

            # Ambil baris pertama (karena hanya 1 data input), lalu ambil probabilitas kelas 1
            probabilitas_kelas = proba_array[0]

            # Pastikan model memiliki minimal 2 kelas sebelum mengakses index [1]
            if len(probabilitas_kelas) < 2:
                # Jika hanya 1 kelas terdeteksi (data tidak seimbang ekstrem),
                # gunakan prediksi keras sebagai fallback.
                return 85.0 if self.prediksi(data_matang) == "MALFUNGSI" else 10.0

            # Konversi probabilitas kelas 1 ke persentase (dikalikan 100)
            return float(probabilitas_kelas[1] * 100.0)

        except AttributeError:
            # Model tidak memiliki metode predict_proba (model non-sklearn standard).
            # Gunakan prediksi keras sebagai proxy persentase risiko.
            hasil_mentah = self.prediksi(data_matang)
            return 85.0 if hasil_mentah == "MALFUNGSI" else 10.0
