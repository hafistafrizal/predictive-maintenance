# File: tests/test_kalkulator.py
# Deskripsi: Menguji estimasi torsi kendaraan pada berbagai RPM menggunakan logika interpolasi linear.

import sys
import os

# Menambahkan direktori utama ke sys.path agar modul database dan core dapat diimpor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import ProfileKendaraan
from core.kalkulator_torsi import KalkulatorTorsi

print("--- TEST DRIVE MESIN KALKULATOR TORSI ---")

# Membuat profil kendaraan contoh
mobil_test = ProfileKendaraan(nama="Toyota Avanza", idle_rpm=800, max_torque=136, max_rpm=4200)

# Menginisialisasi kalkulator torsi
kalkulator = KalkulatorTorsi()

# Simulasi pembacaan RPM dari sensor
daftar_rpm_live = [700, 800, 2000, 3500, 4200, 5000]

print(f"Spesifikasi Mobil: {mobil_test.nama}")
print(f"RPM Idle: {mobil_test.idle_rpm} | RPM Puncak: {mobil_test.max_rpm} | Torsi Max: {mobil_test.max_torque} Nm\n")
print("Hasil Simulasi Injak Gas:")

# Melakukan pengujian untuk masing-masing RPM
for rpm in daftar_rpm_live:
    hasil_torsi = kalkulator.hitung_estimasi(rpm_live=rpm, kendaraan=mobil_test)
    print(f"Gas di {rpm:4d} RPM  => Estimasi Torsi: {hasil_torsi:6.2f} Nm")
