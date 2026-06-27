# File: core/mesin_ai_pickle.py
# Deskripsi: Subclass dari MesinDiagnosaBase yang memuat model KNN dan Scaler
#            dari file biner (.pkl) yang sudah terlatih sebelumnya (pre-trained).
#
# File yang dimuat:
#   - model_terbaik.pkl  : model KNN yang telah dilatih + SMOTE
#   - scaler.pkl         : MinMaxScaler yang di-fit saat training

import pickle
import warnings
from core.mesin_ai_base import MesinDiagnosaBase

# Abaikan warning bawaan library yang tidak relevan dengan eksekusi
warnings.filterwarnings('ignore')


class MesinDiagnosaPickle(MesinDiagnosaBase):
    """
    Model AI Diagnosa berbasis file .pkl (pre-trained).
    Memuat model KNN dan scaler yang telah dilatih offline
    dengan data SMOTE-balanced untuk menangani ketidakseimbangan kelas.
    """

    def __init__(self):
        # Panggil konstruktor base class untuk inisialisasi self.model dan self.scaler = None
        super().__init__()
        # Langsung muat model dari file .pkl saat kelas diinstansiasi
        self.muat_model()

    def muat_model(self):
        """
        Memuat otak AI (model KNN) dan alat scaling (MinMaxScaler) dari file .pkl.

        File .pkl adalah file biner Python (Pickle) yang menyimpan objek sklearn
        yang sudah sepenuhnya terlatih, sehingga tidak perlu training ulang.

        Raises:
        -------
        FileNotFoundError : jika file .pkl tidak ditemukan di direktori aplikasi
        Exception         : jika file .pkl rusak/corrupt atau tidak kompatibel
        """
        try:
            # Buka dan muat model KNN dari file biner
            with open('model_terbaik.pkl', 'rb') as f:
                self.model = pickle.load(f)

            # Buka dan muat scaler dari file biner
            # Scaler harus sama persis dengan yang digunakan saat training
            with open('scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)

            print("[OK] Mesin AI (Mode Pickle / SMOTE) berhasil dinyalakan.")

        except FileNotFoundError:
            # Salah satu atau kedua file .pkl tidak ditemukan
            print("[ERROR] File model_terbaik.pkl atau scaler.pkl tidak ditemukan!")
            # self.model dan self.scaler tetap None → siapkan_data() akan return None
            # → hitung_risiko() akan return 0.0 (safe fallback)

        except Exception as e:
            # File ada tapi rusak, versi sklearn tidak cocok, atau error lainnya
            print(f"[ERROR] Gagal memuat model dari .pkl: {e}")
            # Pastikan state tetap bersih agar tidak crash di bagian lain
            self.model = None
            self.scaler = None