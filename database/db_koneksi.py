import mysql.connector
from datetime import datetime
from database.models import ProfileKendaraan


class DatabaseKendaraan:
    def __init__(self):
        self.koneksi = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_predict_maintenance"
        )
        self.buat_tabel()

    def buat_tabel(self):
        cursor = self.koneksi.cursor()

        # 1. Tabel Spesifikasi Kendaraan
        tabel_kendaraan = """CREATE TABLE IF NOT EXISTS torsi_kendaraan (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            nama VARCHAR(255),
                            idle_rpm INT,
                            max_torque INT,
                            max_rpm INT
                            )"""
        cursor.execute(tabel_kendaraan)

        # 2. Tabel Log Riwayat Diagnosa (Disempurnakan)
        tabel_log = """CREATE TABLE IF NOT EXISTS log_diagnosa (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        tanggal VARCHAR(255),
                        nama_mobil VARCHAR(255),
                        rpm INT,
                        torsi DOUBLE,
                        beban DOUBLE,
                        suhu_mesin DOUBLE,
                        suhu_udara DOUBLE,
                        risiko DOUBLE,
                        status VARCHAR(255)
                        )"""
        cursor.execute(tabel_log)

        # Trik Cerdas: Menambahkan kolom 'beban' ke tabel lama secara otomatis jika belum ada
        try:
            cursor.execute("ALTER TABLE log_diagnosa ADD COLUMN beban DOUBLE AFTER torsi")
        except Exception:
            pass  # Kolom sudah ada, abaikan error

        self.koneksi.commit()

    # =========================================================================
    # FITUR KELOLA DATABASE TORSI MOBIL
    # =========================================================================
    def simpan_data(self, kendaraan: ProfileKendaraan):
        cursor = self.koneksi.cursor()
        try:
            query = "INSERT INTO torsi_kendaraan (nama, idle_rpm, max_torque, max_rpm) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (kendaraan.nama, kendaraan.idle_rpm, kendaraan.max_torque, kendaraan.max_rpm))
            self.koneksi.commit()
            return True, "Data berhasil disimpan!"
        except Exception as e:
            return False, f"Error: {e}"

    def ambil_data(self):
        cursor = self.koneksi.cursor()
        cursor.execute("SELECT nama, idle_rpm, max_torque, max_rpm FROM torsi_kendaraan")
        hasil = cursor.fetchall()
        return [ProfileKendaraan(baris[0], baris[1], baris[2], baris[3]) for baris in hasil]

    def update_data(self, nama_lama, kendaraan_baru: ProfileKendaraan):
        cursor = self.koneksi.cursor()
        try:
            query = "UPDATE torsi_kendaraan SET nama=%s, idle_rpm=%s, max_torque=%s, max_rpm=%s WHERE nama=%s"
            cursor.execute(query, (kendaraan_baru.nama, kendaraan_baru.idle_rpm, kendaraan_baru.max_torque,
                                   kendaraan_baru.max_rpm, nama_lama))
            self.koneksi.commit()
            return True, "Data berhasil diupdate!"
        except Exception as e:
            return False, f"Error: {e}"

    def hapus_data(self, nama):
        cursor = self.koneksi.cursor()
        try:
            query = "DELETE FROM torsi_kendaraan WHERE nama=%s"
            cursor.execute(query, (nama,))
            self.koneksi.commit()
            return True, "Data berhasil dihapus!"
        except Exception as e:
            return False, f"Error: {e}"

    # =========================================================================
    # FITUR MANAJEMEN LOG RIWAYAT (TIME-SERIES LOGGING)
    # =========================================================================
    def simpan_log_diagnosa(self, nama, rpm, torsi, beban, suhu_m, suhu_u, risiko, status):
        """Menyimpan hasil rekaman termasuk beban"""
        cursor = self.koneksi.cursor()
        try:
            tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """INSERT INTO log_diagnosa
                       (tanggal, nama_mobil, rpm, torsi, beban, suhu_mesin, suhu_udara, risiko, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (tanggal_sekarang, nama, rpm, torsi, beban, suhu_m, suhu_u, round(risiko, 1), status))
            self.koneksi.commit()
            return True
        except Exception as e:
            print(f"[Database Error]: Gagal menyimpan log: {e}")
            return False

    def ambil_semua_log(self):
        """Mengambil semua riwayat pencatatan (Urut dari yang terbaru)"""
        cursor = self.koneksi.cursor()
        try:
            query = """SELECT tanggal, nama_mobil, rpm, torsi, beban, suhu_mesin, suhu_udara, risiko, status
                       FROM log_diagnosa ORDER BY id DESC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"[Database Error]: Gagal mengambil log: {e}")
            return []

    def hapus_semua_log(self):
        """Mengosongkan semua data riwayat dari tabel"""
        cursor = self.koneksi.cursor()
        try:
            cursor.execute("TRUNCATE TABLE log_diagnosa")
            self.koneksi.commit()
            return True, "Riwayat log berhasil dikosongkan secara permanen."
        except Exception as e:
            return False, f"Gagal menghapus log riwayat: {e}"