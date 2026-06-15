import mysql.connector
from database.models import ProfileKendaraan

class DatabaseKendaraan:
    def __init__(self):
        self.koneksi = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_kendaraan_torsi"
        )

    def buat_tabel(self):
        cursor = self.koneksi.cursor()
        tabel = """CREATE TABLE IF NOT EXISTS torsi_kendaraan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama VARCHAR(255),
                    idle_rpm INT,
                    max_torque INT,
                    max_rpm INT
                    )"""
        cursor.execute(tabel)
        self.koneksi.commit()

    def simpan_data(self, kendaraan):
        cursor = self.koneksi.cursor()
        try:
            cursor.execute("INSERT INTO torsi_kendaraan (nama, idle_rpm, max_torque, max_rpm) VALUES (%s, %s, %s, %s)",
                           (kendaraan.nama, kendaraan.idle_rpm, kendaraan.max_torque, kendaraan.max_rpm))
            self.koneksi.commit()
            return True, "Data Berhasil Disimpan"
        except mysql.connector.IntegrityError:
            return False, f"Data dengan nama {kendaraan.nama} sudah ada"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"

    def ambil_data(self):
        cursor = self.koneksi.cursor()
        cursor.execute("SELECT * FROM torsi_kendaraan")
        baris_data = cursor.fetchall()

        daftar_kendaraan = []
        for baris in baris_data:
            kendaraan = ProfileKendaraan(nama=baris[1], idle_rpm=baris[2], max_torque=baris[3], max_rpm=baris[4])
            daftar_kendaraan.append(kendaraan)

        return daftar_kendaraan

    def update_data(self, nama_lama, kendaraan):
        cursor = self.koneksi.cursor()
        try:
            cursor.execute(
                "UPDATE torsi_kendaraan SET nama=%s, idle_rpm=%s, max_torque=%s, max_rpm=%s WHERE nama=%s",
                (kendaraan.nama, kendaraan.idle_rpm, kendaraan.max_torque, kendaraan.max_rpm, nama_lama)
            )
            self.koneksi.commit()
            return True, "Data Berhasil Diupdate"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"

    def hapus_data(self, nama_kendaraan):
        cursor = self.koneksi.cursor()
        try:
            cursor.execute("DELETE FROM torsi_kendaraan WHERE nama=%s", (nama_kendaraan,))
            self.koneksi.commit()
            return True, "Data Berhasil Dihapus"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"



