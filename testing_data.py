# from database.models import ProfileKendaraan
# from database.db_koneksi import DatabaseKendaraan
#
# print("=== UJI DATABASE TORSI ===")
#
# print("\n1. Menghubungkan Database...")
# db = DatabaseKendaraan()
#
# print("\n2. Menyimpan Data Kendaraan...")
# mobil_test = ProfileKendaraan(nama="Toyota Supra", idle_rpm=850, max_torque=145.0, max_rpm=4600)
#
# berhasil, pesan = db.simpan_data(mobil_test)
# if berhasil:
#     print(f"SUKSES: {pesan}")
# else:
#     print(f"GAGAL: {pesan}")
#
# print("\n3. Mengecek Data Kendaraan...")
# daftar_kendaraan = db.ambil_data()
#
# if len(daftar_kendaraan) == 0:
#     print("Data Kendaraan Kosong")
# else:
#     for kendaraan in daftar_kendaraan:
#         print(f"{kendaraan.nama} - idle_rpm: {kendaraan.idle_rpm} - max_torque: {kendaraan.max_torque} - max_rpm: {kendaraan.max_rpm}")
#
# print("\n=== SELESAI ===")
#
