# File: core/kalkulator_torsi.py
# Deskripsi: Mengestimasi torsi mesin kendaraan menggunakan interpolasi linear
#            antara RPM idle (stasioner) dan RPM puncak (redline).
#
# RUMUS INTI (Interpolasi Linear):
#   T_estimasi = T_idle + ((RPM_live - RPM_idle) / (RPM_puncak - RPM_idle)) * (T_max - T_idle)
#
#   Dimana:
#   - T_idle  = Torsi saat mesin stasioner = T_max * 15%
#   - RPM_live = RPM aktual yang dimasukkan mekanik
#   - Rumus ini mengasumsikan kenaikan torsi bersifat LINEAR antara idle dan puncak


class KalkulatorTorsi:
    """
    Kelas untuk menghitung estimasi torsi mesin secara otomatis
    berdasarkan RPM live dan spesifikasi profil kendaraan dari database.
    """

    # Rasio torsi saat mesin stasioner (idle) terhadap torsi maksimum.
    # Nilai 0.15 berarti torsi idle = 15% dari torsi puncak.
    # Ini adalah estimasi umum untuk mesin bensin konvensional.
    RASIO_TORSI_IDLE = 0.15

    def __init__(self):
        # Tidak ada state internal yang perlu diinisialisasi;
        # konstanta RASIO_TORSI_IDLE sudah dideklarasi di level kelas.
        pass

    def hitung_estimasi(self, rpm_live: float, kendaraan) -> float:
        """
        Menghitung estimasi torsi (Nm) berdasarkan RPM saat ini (live).

        Parameter:
        ----------
        rpm_live  : float  - RPM mesin aktual yang dibaca/diinput
        kendaraan : ProfileKendaraan - objek spesifikasi kendaraan dari database

        Return:
        -------
        float - estimasi torsi dalam satuan Newton-meter (Nm), dibulatkan 2 desimal.

        Logika:
        -------
        1. Hitung T_idle = T_max * RASIO_TORSI_IDLE
        2. Jika RPM <= RPM_idle  → kembalikan T_idle (mesin belum berakselerasi)
        3. Jika RPM >= RPM_puncak → kembalikan T_max  (mesin sudah di redline)
        4. Selain itu → interpolasi linear antara (RPM_idle, T_idle) dan (RPM_puncak, T_max)
        """

        # --- Ambil data spesifikasi dari profil kendaraan ---
        rpm_idle   = kendaraan.idle_rpm
        rpm_puncak = kendaraan.max_rpm
        torsi_max  = kendaraan.max_torque

        # --- Hitung Torsi Idle (T_idle) ---
        # T_idle adalah torsi minimum saat mesin berputar stasioner.
        torsi_idle = torsi_max * self.RASIO_TORSI_IDLE

        # --- PENGAMAN BATAS BAWAH ---
        # Jika RPM berada di bawah atau sama dengan RPM idle,
        # asumsikan torsi berada di titik terendahnya (torsi idle).
        if rpm_live <= rpm_idle:
            return round(torsi_idle, 2)

        # --- PENGAMAN BATAS ATAS ---
        # Jika RPM melampaui redline, torsi sudah di puncak (T_max).
        if rpm_live >= rpm_puncak:
            return round(float(torsi_max), 2)

        # --- PENGAMAN PEMBAGIAN NOL ---
        # Cegah ZeroDivisionError jika rpm_puncak == rpm_idle (data tidak valid).
        rentang_rpm = rpm_puncak - rpm_idle
        if rentang_rpm <= 0:
            # Jika rentang tidak valid, kembalikan T_max sebagai fallback teraman
            return round(float(torsi_max), 2)

        # --- INTERPOLASI LINEAR ---
        # Seberapa jauh RPM_live dari titik idle menuju titik puncak (0.0 – 1.0)
        selisih_rpm  = rpm_live - rpm_idle
        selisih_torsi = torsi_max - torsi_idle

        # Rumus: T = T_idle + (fraksi_rpm * delta_T)
        torsi_estimasi = torsi_idle + (selisih_rpm / rentang_rpm) * selisih_torsi

        # --- Kembalikan hasil dibulatkan 2 angka di belakang koma ---
        return round(torsi_estimasi, 2)
