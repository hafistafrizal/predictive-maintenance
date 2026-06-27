# Changelog

Semua perubahan penting pada proyek ini akan didokumentasikan di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-06-27

### ✨ Added
- Logika KNN yang dioptimasi dengan perbaikan domain adaptation yang lebih akurat
- Komentar kode yang lebih detail pada seluruh modul
- File `.gitignore` yang lengkap untuk proyek Python + Qt

### 🔧 Fixed
- Perbaikan logika perhitungan risiko KNN agar lebih konsisten
- Bug pada estimasi torsi saat nilai RPM input melebihi RPM maksimum kendaraan
- Perbaikan validasi input pada semua field form

### 📝 Changed
- Refaktor `logika_diagnosa.py` untuk memisahkan tanggung jawab lebih jelas
- Update dokumentasi README dengan diagram alur sistem yang lebih lengkap

---

## [1.0.0] - 2026-06-20

### 🎉 Initial Release

#### ✨ Added
- **Aplikasi GUI Desktop** berbasis PySide6 dengan tema dark mode
- **3 Tab Utama:**
  - `Diagnosa AI` — Pipeline prediksi risiko kegagalan mesin via KNN
  - `Database Torsi` — CRUD profil spesifikasi kendaraan (MySQL)
  - `Log Riwayat` — Tabel riwayat diagnosa + pencarian + ekspor CSV
- **Model Machine Learning:**
  - KNN (K-Nearest Neighbors, k=5) dengan SMOTE untuk balancing data
  - Dua mode: AI Pickle (pre-trained `.pkl`) dan AI Manual (live training dari CSV)
- **Pipeline Domain Adaptation:** Pemetaan parameter kendaraan ke skala dataset CNC industri
- **Estimasi Torsi** via interpolasi linear berdasarkan profil RPM kendaraan
- **Database MySQL** dengan auto-create tabel saat pertama dijalankan
- **Export CSV** untuk laporan riwayat diagnosa
- Pre-trained model `model_terbaik.pkl` + `scaler.pkl` (KNN + SMOTE)
- Dataset `2020 Predictive Maintenance Dataset.csv` (AI4I 2020)
- Tema dark mode via `style.qss` (Qt Style Sheet)

#### 🧠 ML Features
- SMOTE untuk menyeimbangkan dataset (97% Normal vs 3% Failure → 50:50)
- MinMaxScaler normalisasi fitur ke rentang `[0, 1]`
- `predict_proba()` untuk mendapatkan probabilitas risiko kontinyu
- 3 level status: NORMAL (<40%) / WARNING (40-74%) / MALFUNGSI (≥75%)

---

[1.1.0]: https://github.com/hafistafrizal/predictive-maintenance/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/hafistafrizal/predictive-maintenance/releases/tag/v1.0.0
