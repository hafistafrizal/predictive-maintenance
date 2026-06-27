# File: core/logika_diagnosa.py
# Deskripsi: Kelas ini mengatur seluruh alur logika diagnosa mulai dari validasi telemetri,
#            perhitungan estimasi torsi kendaraan, pemetaan (Domain Adaptation) ke skala dataset AI,
#            hingga eksekusi prediksi model Machine Learning (KNN) dan pembentukan keputusan akhir.
#
# ============================================================
# ALUR PROSES (Pipeline):
#   1. Validasi input mekanik (RPM, suhu mesin, suhu udara)
#   2. Kalkulasi torsi estimasi via KalkulatorTorsi (interpolasi linear)
#   3. Hitung beban mesin (persentase RPM dan torsi terhadap maksimum)
#   4. Domain Adaptation: petakan parameter mobil → skala dataset CNC AI
#   5. Eksekusi KNN predict_proba → dapatkan persentase risiko
#   6. Terjemahkan risiko → keputusan (Normal / Warning / Malfungsi) + insight
# ============================================================

from core.kalkulator_torsi import KalkulatorTorsi


class LogikaDiagnosa:
    """
    Pusat kendali alur diagnosa prediktif kendaraan.
    Mengorkestrasi kalkulasi torsi, pemetaan domain, dan inferensi model KNN.
    """

    def __init__(self):
        # Inisialisasi kalkulator torsi yang akan digunakan di setiap siklus diagnosa
        self.kalkulator = KalkulatorTorsi()

    def proses(self, rpm_live: float, suhu_m: float, suhu_u: float,
               mobil_target, ai_terpilih) -> dict:
        """
        Memproses seluruh hitungan diagnosa ML dan mengembalikan hasil dalam bentuk Dictionary.

        Parameter:
        ----------
        rpm_live     : float  - RPM mesin aktual dari input mekanik
        suhu_m       : float  - Suhu mesin aktual dalam derajat Celsius
        suhu_u       : float  - Suhu udara aktual dalam derajat Celsius
        mobil_target : ProfileKendaraan - spesifikasi kendaraan yang dipilih
        ai_terpilih  : MesinDiagnosaBase subclass - model AI yang aktif

        Return:
        -------
        dict dengan kunci: status, warna, risiko, torsi, insight, data_ai, beban
        """

        # =====================================================================
        # 1. VALIDASI LAPANGAN (Guard Clause)
        #    Mencegah input yang tidak masuk akal secara mekanis memasuki pipeline.
        # =====================================================================

        # RPM tidak boleh negatif atau melebihi 20.000 RPM (batas fisik umum)
        if rpm_live < 0 or rpm_live > 20000:
            return self._format_hasil("ERROR (INPUT INVALID)", "red", 0, 0,
                                      "❌ RPM di luar nalar mekanis (Harus 0 - 20.000).", "-", 0)

        # Suhu mesin: -20°C (kondisi beku ekstrem) s/d 250°C (batas fisik metal)
        if suhu_m < -20 or suhu_m > 250:
            return self._format_hasil("ERROR (INPUT INVALID)", "red", 0, 0,
                                      "❌ Suhu mesin tidak masuk akal (Harus -20°C s/d 250°C).", "-", 0)

        # Suhu udara: -20°C s/d 70°C (kondisi lapangan ekstrem di dunia nyata)
        if suhu_u < -20 or suhu_u > 70:
            return self._format_hasil("ERROR (INPUT INVALID)", "red", 0, 0,
                                      "❌ Suhu udara tidak masuk akal (Harus -20°C s/d 70°C).", "-", 0)

        # Validasi spesifikasi kendaraan: pastikan max_rpm > 0 agar tidak terjadi pembagian nol
        if mobil_target.max_rpm <= 0 or mobil_target.max_torque <= 0:
            return self._format_hasil("ERROR (DATA KENDARAAN)", "red", 0, 0,
                                      "❌ Spesifikasi kendaraan tidak valid (RPM/Torsi maks harus > 0).", "-", 0)

        # =====================================================================
        # 2. KALKULASI TORSI & BEBAN MESIN
        #    Menghitung torsi estimasi via interpolasi linear, lalu menormalkan
        #    ke persentase beban berdasarkan spesifikasi kendaraan.
        # =====================================================================

        # Hitung torsi estimasi (Nm) berdasarkan RPM live menggunakan interpolasi linear
        torsi_asli = self.kalkulator.hitung_estimasi(rpm_live, mobil_target)

        # Hitung fraksi beban RPM: seberapa dekat RPM live terhadap RPM maksimum (0.0–1.0+)
        persen_rpm = rpm_live / mobil_target.max_rpm

        # Hitung fraksi beban torsi: seberapa besar torsi terhadap torsi maksimum (0.0–1.0)
        persen_torsi = torsi_asli / mobil_target.max_torque

        # Beban akhir = faktor pemberat terbesar antara RPM dan torsi, dikap 100%
        # Logika: mesin dianggap "seberat" faktor yang paling membebaninya
        beban_persen = round(min(100.0, max(persen_rpm, persen_torsi) * 100.0), 1)

        # PENGAMAN MESIN MATI:
        # Jika RPM live < 50% dari RPM idle (mis. mesin stall/tersendat), hentikan proses
        if rpm_live < (mobil_target.idle_rpm * 0.5):
            return self._format_hasil("ERROR (MESIN MATI)", "red", 0, torsi_asli,
                                      "❌ RPM di bawah batas idle kritis. Mesin stall/mati.", "-", beban_persen)

        # =====================================================================
        # 3. DOMAIN ADAPTATION (Pemetaan Konteks Kendaraan → Dataset AI)
        #    Dataset "2020 Predictive Maintenance" menggunakan data mesin industri CNC,
        #    bukan mesin kendaraan. Kita petakan persentase beban kendaraan ke dalam
        #    rentang nilai yang REALISTIS di dataset CNC agar KNN membandingkan
        #    dengan tetangga yang tepat secara kontekstual.
        # =====================================================================

        # --- Pemetaan Torsi (Nm) ---
        # Dataset CNC: torsi normal ~20 Nm, overload ~75 Nm
        # Formula: torsi_ai = 20 + (fraksi_torsi * 55)
        # Contoh: persen_torsi=0.5 → torsi_ai = 20 + (0.5*55) = 47.5 Nm (beban sedang)
        torsi_ai = 20.0 + (persen_torsi * 55.0)

        # --- Pemetaan RPM (putaran/menit) ---
        # Dataset CNC: mesin rileks ~2500 RPM, mesin tertahan ~1300 RPM (inversi)
        # Semakin tinggi beban RPM kendaraan → semakin "berat/tertahan" di mata AI CNC
        # Formula: rpm_ai = 2500 - (fraksi_rpm * 1200)
        # Contoh: persen_rpm=1.0 → rpm_ai = 2500 - 1200 = 1300 RPM (beban penuh)
        rpm_ai = 2500.0 - (persen_rpm * 1200.0)

        # --- Pemetaan Suhu Mesin ke Kelvin ---
        # Dataset CNC: suhu proses normal ~300 K, overheat ~314 K
        # Referensi mobil: 80°C = suhu normal → 305 K; 120°C = bahaya → ~314 K
        # Formula: suhu_m_ai = 300 + ((suhu_m / 120) * 14)
        # CATATAN: suhu_m yang divalidasi maksimal 250°C → hasil maksimum:
        #   300 + (250/120 * 14) = 300 + 29.17 = 329.17 K → akan dikap di 315 K
        suhu_m_ai = 300.0 + ((suhu_m / 120.0) * 14.0)

        # --- Pemetaan Suhu Udara ke Kelvin ---
        # Dataset CNC: suhu udara normal ~296 K, panas ~304 K
        # Referensi lapangan: suhu udara normal 25°C → sekitar 298 K
        # Formula: suhu_u_ai = 295 + ((suhu_u / 50) * 9)
        # CATATAN: suhu_u divalidasi s/d 70°C → hasil maksimum:
        #   295 + (70/50 * 9) = 295 + 12.6 = 307.6 K → akan dikap di 305 K
        suhu_u_ai = 295.0 + ((suhu_u / 50.0) * 9.0)

        # --- KLAMPING (Clamping) ke batas valid dataset CNC ---
        # Memastikan semua nilai AI tidak keluar dari rentang distribusi data training KNN.
        # Ini penting agar KNN tidak mencari tetangga di ruang ekstrapolasi (di luar data training).
        torsi_ai  = min(80.0, max(10.0, torsi_ai))     # [10, 80] Nm
        rpm_ai    = min(3000.0, max(1200.0, rpm_ai))   # [1200, 3000] RPM
        suhu_m_ai = min(315.0, max(295.0, suhu_m_ai))  # [295, 315] Kelvin
        suhu_u_ai = min(305.0, max(290.0, suhu_u_ai))  # [290, 305] Kelvin

        # =====================================================================
        # 4. EKSEKUSI MODEL MACHINE LEARNING (K-Nearest Neighbors)
        #    Data yang sudah dipetakan disiapkan (di-scale) lalu dimasukkan ke KNN.
        # =====================================================================

        # Siapkan data: wrap ke DataFrame → terapkan scaler → return numpy array ter-scale
        # Urutan parameter: rpm, suhu_proses, suhu_udara, torsi
        data_matang = ai_terpilih.siapkan_data(rpm_ai, suhu_m_ai, suhu_u_ai, torsi_ai)
        risiko = 0.0

        if data_matang is not None:
            # hitung_risiko menggunakan KNN predict_proba:
            # → cari 5 tetangga terdekat di ruang fitur ber-skala
            # → hitung proporsi tetangga berkelas "Failure" (kelas 1)
            # → kalikan 100 → persentase risiko (0–100%)
            risiko = ai_terpilih.hitung_risiko(data_matang)

        # =====================================================================
        # 5. PEMBENTUKAN KEPUTUSAN & INSIGHT BERDASARKAN AMBANG RISIKO KNN
        #    Ambang batas ditetapkan berdasarkan distribusi probabilitas KNN:
        #    - < 40%  : zona aman (mayoritas 5 tetangga adalah Normal)
        #    - 40–75% : zona waspada (campuran tetangga Normal & Failure)
        #    - >= 75% : zona bahaya (mayoritas tetangga adalah Failure)
        # =====================================================================
        insight = []

        if risiko < 40.0:
            # Zona NORMAL: sebagian besar tetangga KNN berkelas Normal
            status_teks = "NORMAL"
            warna = "green"
            insight.append(
                "✅ AMAN: Model Machine Learning mendeteksi parameter operasional kendaraan dalam zona batas toleransi.")

        elif risiko < 75.0:
            # Zona WARNING: campuran tetangga Normal dan Failure terdeteksi
            status_teks = "WARNING (WASPADA)"
            warna = "orange"
            insight.append("⚠️ WARNING: Algoritma KNN mendeteksi anomali (Peningkatan Stres Fisik/Suhu).")

            # Tambahkan insight spesifik berdasarkan parameter yang paling ekstrem
            if suhu_m > 95:
                insight.append("-> Suhu mesin di atas rata-rata normal. Awasi sistem pendingin.")
            if persen_torsi > 0.8:
                insight.append("-> Tarikan torsi mendekati batas redline spesifikasi profil kendaraan.")

        else:
            # Zona MALFUNGSI: mayoritas 5 tetangga KNN berkelas Failure
            status_teks = "MALFUNGSI"
            warna = "red"
            insight.append(
                "🚨 MALFUNGSI TERDETEKSI: Model AI menemukan pola telemetri yang identik dengan "
                "kegagalan mesin absolut (Power/Heat Failure) pada dataset.")

        # Susun teks detail transparan AI agar mudah dibaca di UI (multi-line)
        data_ai_teks = (
            "Data Transparan AI (Hasil Pemetaan Dataset ML):\n"
            f"  • RPM AI: {rpm_ai:.0f} RPM\n"
            f"  • Torsi AI: {torsi_ai:.1f} Nm\n"
            f"  • Suhu Mesin AI: {suhu_m_ai:.1f} K\n"
            f"  • Suhu Udara AI: {suhu_u_ai:.1f} K"
        )

        # Kembalikan hasil lengkap sebagai dictionary
        return self._format_hasil(
            status_teks, warna, risiko, torsi_asli,
            "\n".join(insight), data_ai_teks, beban_persen
        )

    def _format_hasil(self, status: str, warna: str, risiko: float, torsi: float,
                      insight: str, data_ai: str, beban: float) -> dict:
        """
        Fungsi pembantu internal untuk membungkus semua hasil diagnosa
        menjadi dictionary berstruktur seragam yang dipakai oleh UI.

        Kunci dictionary:
        -----------------
        status  : teks status akhir (NORMAL / WARNING / MALFUNGSI / ERROR ...)
        warna   : kode warna teks UI ('green', 'orange', 'red')
        risiko  : persentase risiko kerusakan 0.0–100.0 (dari KNN)
        torsi   : estimasi torsi aktual kendaraan (Nm)
        insight : pesan penjelasan untuk mekanik
        data_ai : detail teknis pemetaan domain AI
        beban   : persentase beban mesin 0.0–100.0
        """
        return {
            "status":  status,
            "warna":   warna,
            "risiko":  risiko,
            "torsi":   torsi,
            "insight": insight,
            "data_ai": data_ai,
            "beban":   beban
        }