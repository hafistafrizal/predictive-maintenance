# File: database/models.py
# Deskripsi: Mendefinisikan kelas model data ProfileKendaraan sebagai representasi
#            satu baris data spesifikasi kendaraan dari tabel 'torsi_kendaraan' di MySQL.
#
# Digunakan oleh:
#   - DatabaseKendaraan.ambil_data()  → membuat objek dari query SELECT
#   - DatabaseKendaraan.simpan_data() → menerima objek untuk query INSERT
#   - LogikaDiagnosa.proses()         → mengakses atribut idle_rpm, max_rpm, max_torque


class ProfileKendaraan:
    """
    Model data (Data Transfer Object) untuk satu profil spesifikasi kendaraan.

    Atribut:
    --------
    id         : int   - Primary key dari database (opsional, None jika belum disimpan)
    nama       : str   - Nama/identifikasi kendaraan (mis. "Toyota Avanza 2019")
    idle_rpm   : int   - RPM mesin saat kondisi stasioner/idle (mis. 750)
    max_torque : float - Torsi puncak kendaraan dalam Newton-meter (mis. 140.0)
    max_rpm    : int   - Batas RPM mesin maksimum / redline (mis. 6000)
    """

    def __init__(self, nama: str, idle_rpm: int, max_torque: float, max_rpm: int, id: int = None):
        self.id         = id         # Primary key DB (None jika objek belum disimpan)
        self.nama       = nama       # Nama kendaraan
        self.idle_rpm   = idle_rpm   # RPM stasioner
        self.max_torque = max_torque # Torsi puncak (Nm)
        self.max_rpm    = max_rpm    # RPM redline
