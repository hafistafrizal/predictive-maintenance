# File: database/db_koneksi.py
# Deskripsi: Mengatur koneksi ke MySQL, inisialisasi tabel torsi dan log diagnosa,
#            serta menyediakan fungsi CRUD data kendaraan dan pencatatan log diagnosa.
#
# Struktur tabel:
#   - torsi_kendaraan : menyimpan profil spesifikasi kendaraan (idle_rpm, max_rpm, max_torque)
#   - log_diagnosa    : menyimpan riwayat hasil diagnosa setiap sesi pemeriksaan

import mysql.connector
from datetime import datetime
from database.models import ProfileKendaraan


class DatabaseKendaraan:
    """
    Kelas pengelola koneksi dan operasi database MySQL.
    Menyediakan antarmuka CRUD untuk profil kendaraan dan pencatatan log diagnosa.
    """

    def __init__(self):
        # Buat koneksi ke MySQL database lokal
        # Sesuaikan host/user/password/database dengan konfigurasi server MySQL Anda
        self.koneksi = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_predict_maintenance"
        )
        # Inisialisasi struktur tabel jika belum ada
        self.buat_tabel()

    def _get_cursor(self):
        """
        Fungsi pembantu internal: mengembalikan cursor baru.
        Cursor selalu dibuat baru untuk setiap operasi agar tidak ada
        konflik state antar pemanggilan berurutan.
        """
        return self.koneksi.cursor()

    def buat_tabel(self):
        """
        Membuat tabel database jika belum ada (CREATE TABLE IF NOT EXISTS).
        Dipanggil sekali saat aplikasi pertama kali dijalankan.

        Tabel yang dibuat:
        1. torsi_kendaraan : profil spesifikasi kendaraan
        2. log_diagnosa    : log riwayat hasil diagnosa
        """
        cursor = self._get_cursor()

        # --- Tabel 1: Spesifikasi Kendaraan ---
        # Menyimpan profil torsi/RPM setiap model kendaraan yang terdaftar
        tabel_kendaraan = """CREATE TABLE IF NOT EXISTS torsi_kendaraan (
                            id         INT AUTO_INCREMENT PRIMARY KEY,
                            nama       VARCHAR(255),
                            idle_rpm   INT,
                            max_torque INT,
                            max_rpm    INT
                            )"""
        cursor.execute(tabel_kendaraan)

        # --- Tabel 2: Log Riwayat Diagnosa ---
        # Menyimpan semua rekaman hasil diagnosa secara kronologis
        tabel_log = """CREATE TABLE IF NOT EXISTS log_diagnosa (
                        id          INT AUTO_INCREMENT PRIMARY KEY,
                        tanggal     VARCHAR(255),
                        nama_mobil  VARCHAR(255),
                        rpm         INT,
                        torsi       DOUBLE,
                        beban       DOUBLE,
                        suhu_mesin  DOUBLE,
                        suhu_udara  DOUBLE,
                        risiko      DOUBLE,
                        status      VARCHAR(255)
                        )"""
        cursor.execute(tabel_log)

        # --- Migrasi Otomatis: Tambahkan kolom 'beban' jika tabel lama belum memilikinya ---
        # Ini memastikan kompatibilitas mundur (backward compatibility) dengan instalasi lama.
        # Error diabaikan karena berarti kolom sudah ada.
        try:
            cursor.execute("ALTER TABLE log_diagnosa ADD COLUMN beban DOUBLE AFTER torsi")
        except Exception:
            pass  # Kolom sudah ada → abaikan error ALTER TABLE

        self.koneksi.commit()
        cursor.close()

    # =========================================================================
    # CRUD: PENGELOLAAN DATABASE SPESIFIKASI KENDARAAN
    # =========================================================================

    def simpan_data(self, kendaraan: ProfileKendaraan):
        """
        Menyimpan profil kendaraan baru ke tabel torsi_kendaraan.

        Return: (True, pesan_sukses) atau (False, pesan_error)
        """
        cursor = self._get_cursor()
        try:
            query = "INSERT INTO torsi_kendaraan (nama, idle_rpm, max_torque, max_rpm) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (kendaraan.nama, kendaraan.idle_rpm, kendaraan.max_torque, kendaraan.max_rpm))
            self.koneksi.commit()
            return True, "Data berhasil disimpan!"
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            cursor.close()  # Selalu tutup cursor setelah operasi selesai

    def ambil_data(self) -> list:
        """
        Mengambil semua profil kendaraan dari database.

        Return: list of ProfileKendaraan objects, atau list kosong jika tidak ada data.
        """
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT nama, idle_rpm, max_torque, max_rpm FROM torsi_kendaraan")
            hasil = cursor.fetchall()
            # Konversi setiap baris tuple menjadi objek ProfileKendaraan
            return [ProfileKendaraan(baris[0], baris[1], baris[2], baris[3]) for baris in hasil]
        except Exception as e:
            print(f"[Database Error]: Gagal mengambil data kendaraan: {e}")
            return []
        finally:
            cursor.close()

    def update_data(self, nama_lama: str, kendaraan_baru: ProfileKendaraan):
        """
        Memperbarui profil kendaraan yang ada berdasarkan nama lama.

        Return: (True, pesan_sukses) atau (False, pesan_error)
        """
        cursor = self._get_cursor()
        try:
            query = "UPDATE torsi_kendaraan SET nama=%s, idle_rpm=%s, max_torque=%s, max_rpm=%s WHERE nama=%s"
            cursor.execute(query, (
                kendaraan_baru.nama, kendaraan_baru.idle_rpm,
                kendaraan_baru.max_torque, kendaraan_baru.max_rpm,
                nama_lama
            ))
            self.koneksi.commit()
            return True, "Data berhasil diupdate!"
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            cursor.close()

    def hapus_data(self, nama: str):
        """
        Menghapus profil kendaraan dari database berdasarkan nama.

        Return: (True, pesan_sukses) atau (False, pesan_error)
        """
        cursor = self._get_cursor()
        try:
            query = "DELETE FROM torsi_kendaraan WHERE nama=%s"
            cursor.execute(query, (nama,))
            self.koneksi.commit()
            return True, "Data berhasil dihapus!"
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            cursor.close()

    # =========================================================================
    # MANAJEMEN LOG RIWAYAT (TIME-SERIES LOGGING)
    # =========================================================================

    def simpan_log_diagnosa(self, nama: str, rpm: int, torsi: float, beban: float,
                            suhu_m: float, suhu_u: float, risiko: float, status: str) -> bool:
        """
        Menyimpan satu rekaman hasil diagnosa ke tabel log_diagnosa.

        Parameter:
        ----------
        nama   : nama kendaraan yang didiagnosa
        rpm    : RPM mesin aktual saat diagnosa
        torsi  : estimasi torsi kendaraan (Nm)
        beban  : persentase beban mesin (0–100%)
        suhu_m : suhu mesin aktual (°C)
        suhu_u : suhu udara aktual (°C)
        risiko : persentase risiko dari model KNN (0–100%)
        status : label status akhir (NORMAL / WARNING / MALFUNGSI)

        Return: True jika berhasil, False jika gagal.
        """
        cursor = self._get_cursor()
        try:
            # Ambil timestamp saat diagnosa dilakukan
            tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            query = """INSERT INTO log_diagnosa
                       (tanggal, nama_mobil, rpm, torsi, beban, suhu_mesin, suhu_udara, risiko, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            # Bulatkan risiko ke 1 desimal untuk konsistensi tampilan
            cursor.execute(query, (
                tanggal_sekarang, nama, rpm, torsi, beban,
                suhu_m, suhu_u, round(risiko, 1), status
            ))
            self.koneksi.commit()
            return True
        except Exception as e:
            print(f"[Database Error]: Gagal menyimpan log: {e}")
            return False
        finally:
            cursor.close()

    def ambil_semua_log(self) -> list:
        """
        Mengambil semua riwayat pencatatan diagnosa, diurutkan dari yang paling baru.

        Return: list of tuples (tanggal, nama_mobil, rpm, torsi, beban,
                                suhu_mesin, suhu_udara, risiko, status)
                atau list kosong jika tidak ada data.
        """
        cursor = self._get_cursor()
        try:
            query = """SELECT tanggal, nama_mobil, rpm, torsi, beban,
                              suhu_mesin, suhu_udara, risiko, status
                       FROM log_diagnosa ORDER BY id DESC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"[Database Error]: Gagal mengambil log: {e}")
            return []
        finally:
            cursor.close()

    def hapus_semua_log(self):
        """
        Mengosongkan semua data riwayat dari tabel log_diagnosa (TRUNCATE).
        Operasi TRUNCATE lebih cepat dari DELETE karena tidak mencatat baris per baris.

        Return: (True, pesan_sukses) atau (False, pesan_error)
        """
        cursor = self._get_cursor()
        try:
            cursor.execute("TRUNCATE TABLE log_diagnosa")
            self.koneksi.commit()
            return True, "Riwayat log berhasil dikosongkan secara permanen."
        except Exception as e:
            return False, f"Gagal menghapus log riwayat: {e}"
        finally:
            cursor.close()