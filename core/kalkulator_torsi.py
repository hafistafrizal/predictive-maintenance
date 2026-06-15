class KalkulatorTorsi:
    def __init__(self):
        self.rasio_torsi_idle = 0.15

    def hitung_estimasi(self, rpm_live, kendaraan):
        """
        Menghitung estimasi torsi berdasarkan RPM saat ini (live).
        Membutuhkan data spesifikasi kendaraan dari database.
        """

        # Ambil data spesifikasi dasar mobil tersebut
        rpm_idle = kendaraan.idle_rpm
        rpm_puncak = kendaraan.max_rpm
        torsi_max = kendaraan.max_torque

        # Hitung Torsi Idle (T_idle)
        torsi_idle = torsi_max * self.rasio_torsi_idle

        # PENGAMAN (Safety Check)
        # Jika mekanik memasukkan RPM di bawah batas idle, anggap torsinya sebesar torsi idle
        if rpm_live <= rpm_idle:
            return round(torsi_idle, 2)

        # Jika mekanik memasukkan RPM di atas batas puncak, anggap torsinya mentok di torsi maksimal
        elif rpm_live >= rpm_puncak:
            return round(torsi_max, 2)

        # RUMUS INTERPOLASI LINEAR
        selisih_rpm = rpm_live - rpm_idle
        rentang_rpm = rpm_puncak - rpm_idle
        selisih_torsi = torsi_max - torsi_idle

        # Eksekusi rumus utama
        torsi_estimasi = torsi_idle + (selisih_rpm / rentang_rpm) * selisih_torsi

        # Kembalikan hasil dengan 2 angka di belakang koma
        return round(torsi_estimasi, 2)
