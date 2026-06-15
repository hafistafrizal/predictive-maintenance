# File: uji_kalkulator.py
from database.models import ProfileKendaraan
from core.kalkulator_torsi import KalkulatorTorsi

print("--- TEST DRIVE MESIN KALKULATOR TORSI ---")

# Kita buat data dummy (pura-pura ambil dari database)
mobil_test = ProfileKendaraan(nama="Toyota Avanza", idle_rpm=800, max_torque=136, max_rpm=4200)

# Nyalakan mesin kalkulator
kalkulator = KalkulatorTorsi()

# Kita simulasikan mekanik sedang menginjak gas di berbagai RPM
daftar_rpm_live = [700, 800, 2000, 3500, 4200, 5000]

print(f"Spesifikasi Mobil: {mobil_test.nama}")
print(f"RPM Idle: {mobil_test.idle_rpm} | RPM Puncak: {mobil_test.max_rpm} | Torsi Max: {mobil_test.max_torque} Nm\n")
print("Hasil Simulasi Injak Gas:")

for rpm in daftar_rpm_live:
    hasil_torsi = kalkulator.hitung_estimasi(rpm_live=rpm, kendaraan=mobil_test)
    print(f"Gas di {rpm} RPM  => Estimasi Torsi: {hasil_torsi} Nm")