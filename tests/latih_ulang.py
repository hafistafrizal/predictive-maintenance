# File: tests/latih_ulang.py
# Deskripsi: Skrip untuk melatih ulang model Machine Learning (KNN) menggunakan SMOTE untuk mengatasi ketidakseimbangan data,
#            serta menyimpan file scaler dan model biner (.pkl) ke folder utama.

import os
import sys
import pickle
import warnings
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from imblearn.over_sampling import SMOTE

warnings.filterwarnings('ignore')

# Menentukan jalur (path) relatif ke direktori utama proyek
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(root_dir, "2020 Predictive Maintenance Dataset.csv")
scaler_path = os.path.join(root_dir, "scaler.pkl")
model_path = os.path.join(root_dir, "model_terbaik.pkl")

print("1. Membaca Dataset dari:", csv_path)
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"[ERROR] Berkas '{csv_path}' tidak ditemukan!")
    sys.exit(1)

# Menentukan fitur input dan target output
X = df[['Rotational speed [rpm]', 'Process temperature [K]', 'Air temperature [K]', 'Torque [Nm]']]
y = df['Machine failure']

print("2. Menyeimbangkan Data AI (SMOTE)...")
smote = SMOTE(random_state=42)
X_seimbang, y_seimbang = smote.fit_resample(X, y)

# Membagi data menjadi data latih (train) dan data uji (test)
X_train, X_test, y_train, y_test = train_test_split(X_seimbang, y_seimbang, test_size=0.2, random_state=42)

print("3. Membuat Scaler dan Melatih Model KNN...")
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)

model_knn = KNeighborsClassifier(n_neighbors=5)
model_knn.fit(X_train_scaled, y_train)

print("4. Menyimpan Hasil Latihan (.pkl)...")
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
    print(f"- Scaler disimpan di: {scaler_path}")

with open(model_path, 'wb') as f:
    pickle.dump(model_knn, f)
    print(f"- Model disimpan di: {model_path}")

print("✅ SELESAI! Model AI Anda sekarang 100% Cerdas dan Siap Uji.")
