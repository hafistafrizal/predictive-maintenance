# File: core/mesin_ai_pickle.py
# Deskripsi: Mengimplementasikan pemuatan model AI (KNN) dan Scaler yang telah terlatih dari file biner (.pkl).

import pickle
import warnings
from core.mesin_ai_base import MesinDiagnosaBase

# Abaikan warning bawaan yang tidak perlu
warnings.filterwarnings('ignore')

class MesinDiagnosaPickle(MesinDiagnosaBase):
    def __init__(self):
        # Memanggil konstruktor base class
        super().__init__()
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