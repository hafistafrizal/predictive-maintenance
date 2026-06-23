# File: core/logika_diagnosa.py
# Deskripsi: Kelas ini mengatur seluruh alur logika diagnosa mulai dari validasi telemetri,
#            perhitungan estimasi torsi kendaraan, pemetaan ke skala dataset AI,
#            hingga eksekusi prediksi model Machine Learning.

from core.kalkulator_torsi import KalkulatorTorsi


class LogikaDiagnosa:
    def __init__(self):
        self.kalkulator = KalkulatorTorsi()

    def proses(self, rpm_live, suhu_m, suhu_u, mobil_target, ai_terpilih):
        """Memproses seluruh hitungan ML dan mengembalikan hasil dalam bentuk Dictionary"""

        # =====================================================================
        # 1. VALIDASI LAPANGAN (Mencegah input asal / tidak masuk akal)
        # =====================================================================
        if rpm_live < 0 or rpm_live > 20000:
            return self._format_hasil("ERROR (INPUT INVALID)", "red", 0, 0,
                                      "❌ RPM di luar nalar mekanis (Harus 0 - 20.000).", "-", 0)
        if suhu_m < -20 or suhu_m > 250:
            return self._format_hasil("ERROR (INPUT INVALID)", "red", 0, 0,
                                      "❌ Suhu mesin tidak masuk akal (Harus -20°C s/d 250°C).", "-", 0)
        if suhu_u < -20 or suhu_u > 70:
            return self._format_hasil("ERROR (INPUT INVALID)", "red", 0, 0,
                                      "❌ Suhu udara tidak masuk akal (Harus -20°C s/d 70°C).", "-", 0)

        # =====================================================================
        # 2. KALKULASI TORSI UNIVERSAL (Berlaku untuk SEMUA kendaraan)
        # =====================================================================
        # Mengambil torsi riil berdasarkan kurva interpolasi kalkulator Anda
        torsi_asli = self.kalkulator.hitung_estimasi(rpm_live, mobil_target)

        # Menghitung seberapa keras mesin disiksa (Rasio 0.0 - 1.0)
        persen_rpm = rpm_live / mobil_target.max_rpm
        persen_torsi = torsi_asli / mobil_target.max_torque

        # Beban akhir adalah yang paling memberatkan mesin
        beban_persen = round(min(100.0, max(persen_rpm, persen_torsi) * 100.0), 1)
        # Cegatan Logis Mesin Mati
        if rpm_live < (mobil_target.idle_rpm * 0.5):
            return self._format_hasil("ERROR (MESIN MATI)", "red", 0, torsi_asli,
                                      "❌ RPM di bawah batas idle kritis. Mesin stall/mati.", "-", beban_persen)

        # =====================================================================
        # 3. DOMAIN ADAPTATION (Mentranslasikan Mobil ke Bahasa Dataset AI)
        # =====================================================================
        # Karena Dataset (2020 Predictive Maintenance) menggunakan data mesin pabrik (CNC),
        # kita petakan persentase beban mobil ini ke dalam rentang rasio dataset.
        # Ini memastikan model KNN bekerja berdasarkan DATA HISTORIS, bukan sekadar If-Else.

        # Torsi Dataset CNC: Normal ~20 Nm | Overload ~70+ Nm
        torsi_ai = 20.0 + (persen_torsi * 55.0)

        # RPM Dataset CNC: Rileks ~2500 RPM | Berat/Tertahan ~1300 RPM
        # (Semakin mobil digeber dengan beban, RPM di mata AI semakin berat)
        rpm_ai = 2500.0 - (persen_rpm * 1200.0)

        # Suhu Mesin Dataset CNC (Kelvin): Normal ~300 K | Overheat ~313+ K
        # Pemetaan: Suhu mobil 80°C -> 305 K (Aman), 120°C -> 314 K (Bahaya)
        suhu_m_ai = 300.0 + ((suhu_m / 120.0) * 14.0)

        # Suhu Udara Dataset CNC (Kelvin): Normal ~296 K | Panas ~303+ K
        suhu_u_ai = 295.0 + ((suhu_u / 50.0) * 9.0)

        # Mengunci batas maksimal agar data tidak "Out of Bounds" di mata KNN
        torsi_ai = min(80.0, max(10.0, torsi_ai))
        rpm_ai = min(3000.0, max(1200.0, rpm_ai))
        suhu_m_ai = min(315.0, max(295.0, suhu_m_ai))
        suhu_u_ai = min(305.0, max(290.0, suhu_u_ai))

        # =====================================================================
        # 4. EKSEKUSI MACHINE LEARNING (K-Nearest Neighbors)
        # =====================================================================
        data_matang = ai_terpilih.siapkan_data(rpm_ai, suhu_m_ai, suhu_u_ai, torsi_ai)
        risiko = 0.0

        if data_matang is not None:
            # Menggunakan method hitung_risiko yang terenkapsulasi di dalam kelas model
            risiko = ai_terpilih.hitung_risiko(data_matang)

        # =====================================================================
        # 5. PEMBENTUKAN KEPUTUSAN & INSIGHT BERDASARKAN HASIL ML
        # =====================================================================
        insight = []
        if risiko < 40.0:
            status_teks = "NORMAL"
            warna = "green"
            insight.append(
                "✅ AMAN: Model Machine Learning mendeteksi parameter operasional kendaraan dalam zona batas toleransi.")
        elif risiko < 75.0:
            status_teks = "WARNING (WASPADA)"
            warna = "orange"
            insight.append("⚠️ WARNING: Algoritma KNN mendeteksi anomali (Peningkatan Stres Fisik/Suhu).")
            if suhu_m > 95: insight.append("-> Suhu mesin di atas rata-rata normal. Awasi sistem pendingin.")
            if persen_torsi > 0.8: insight.append(
                "-> Tarikan torsi mendekati batas redline spesifikasi profil kendaraan.")
        else:
            status_teks = "MALFUNGSI"
            warna = "red"
            insight.append(
                "🚨 MALFUNGSI TERDETEKSI: Model AI menemukan pola telemetri yang identik dengan kegagalan mesin absolut (Power/Heat Failure) pada dataset.")

        # Format data konversi transparan AI agar tersusun rapi secara vertikal (multi-line)
        data_ai_teks = (
            "Data Transparan AI (Hasil Pemetaan Dataset ML):\n"
            f"  • RPM AI: {rpm_ai:.0f} RPM\n"
            f"  • Torsi AI: {torsi_ai:.1f} Nm\n"
            f"  • Suhu Mesin AI: {suhu_m_ai:.1f} K\n"
            f"  • Suhu Udara AI: {suhu_u_ai:.1f} K"
        )

        return self._format_hasil(status_teks, warna, risiko, torsi_asli, "\n".join(insight), data_ai_teks,
                                  beban_persen)

    def _format_hasil(self, status, warna, risiko, torsi, insight, data_ai, beban):
        """Fungsi pembantu untuk membungkus hasil menjadi rapi"""
        return {
            "status": status,
            "warna": warna,
            "risiko": risiko,
            "torsi": torsi,
            "insight": insight,
            "data_ai": data_ai,
            "beban": beban
        }