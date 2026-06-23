# File: tests/testing_data.py
# Deskripsi: Menguji fungsi konektivitas basis data dan penyimpanan profil kendaraan.

import sys
import os

# Menambahkan direktori utama ke sys.path agar modul database dan core dapat diimpor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import ProfileKendaraan
from database.db_koneksi import DatabaseKendaraan

print("=== UJI DATABASE TORSI ===")

print("\n1. Menghubungkan Database...")
db = DatabaseKendaraan()

print("\n2. Menyimpan Data Kendaraan...")
# Membuat data uji coba profil kendaraan
mobil_test = ProfileKendaraan(nama="Toyota Supra", idle_rpm=850, max_torque=145.0, max_rpm=4600)

berhasil, pesan = db.simpan_data(mobil_test)
if berhasil:
    print(f"SUKSES: {pesan}")
else:
    print(f"GAGAL: {pesan}")

print("\n3. Mengecek Data Kendaraan...")
# Mengambil seluruh data kendaraan terdaftar
daftar_kendaraan = db.ambil_data()

if len(daftar_kendaraan) == 0:
    print("Data Kendaraan Kosong")
else:
    for kendaraan in daftar_kendaraan:
        print(f"- {kendaraan.nama} | Idle: {kendaraan.idle_rpm} RPM | Max Torque: {kendaraan.max_torque} Nm | Max RPM: {kendaraan.max_rpm} RPM")

print("\n=== SELESAI ===")
