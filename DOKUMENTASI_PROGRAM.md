# DOKUMENTASI PROGRAM: Sistem Predictive Maintenance Kendaraan Berbasis Machine Learning (KNN)

> **Dokumen ini dibuat sebagai bahan referensi laporan ilmiah/akademik.**  
> Berisi gambaran lengkap sistem, metodologi algoritma, alur kerja program, dan interpretasi hasil diagnosa.

---

## 1. GAMBARAN UMUM SISTEM

### 1.1 Deskripsi Program

Program ini adalah **aplikasi desktop berbasis Graphical User Interface (GUI)** yang menerapkan algoritma *Machine Learning* **K-Nearest Neighbors (KNN)** untuk melakukan **diagnosa pemeliharaan prediktif (Predictive Maintenance)** pada mesin kendaraan bermotor. Sistem ini dirancang untuk membantu mekanik atau teknisi otomotif dalam mendeteksi potensi kegagalan mesin secara real-time berdasarkan data telemetri (sensor) yang diinputkan.

### 1.2 Latar Belakang & Masalah yang Diselesaikan

Perawatan kendaraan konvensional bersifat **reaktif** — mekanik baru bertindak setelah kerusakan terjadi. Pendekatan ini menyebabkan kerugian waktu dan biaya yang besar. Sistem ini menerapkan pendekatan **Predictive Maintenance** yang proaktif: menganalisis data kondisi mesin secara real-time dan **memprediksi kemungkinan kegagalan sebelum terjadi** menggunakan pola data historis dari dataset industri.

### 1.3 Tujuan Sistem

| Tujuan | Penjelasan |
|---|---|
| Deteksi dini kegagalan | Mengidentifikasi potensi kerusakan mesin sebelum terjadi |
| Kuantifikasi risiko | Memberikan persentase risiko (0-100%) sebagai dasar keputusan |
| Pencatatan riwayat | Menyimpan setiap hasil diagnosa ke database untuk analisis berkala |
| Transparansi AI | Menampilkan detail teknis konversi data agar dapat diaudit |

### 1.4 Teknologi yang Digunakan

| Komponen | Teknologi |
|---|---|
| Bahasa Pemrograman | Python 3.10 |
| Framework GUI | PySide6 (Qt for Python) |
| Database | MySQL |
| Algoritma ML | K-Nearest Neighbors (KNN) via scikit-learn |
| Penyeimbangan Data | SMOTE (Synthetic Minority Oversampling Technique) via imbalanced-learn |
| Normalisasi Data | MinMaxScaler via scikit-learn |
| Manipulasi Data | Pandas, NumPy |

---

## 2. ARSITEKTUR DAN STRUKTUR PROGRAM

### 2.1 Struktur Folder Proyek

```
predictive-maintenance/
|
+-- main.py                    <- Entry point, inisialisasi window & tab
+-- style.qss                  <- Tema dark mode visual (Qt Style Sheet)
+-- model_terbaik.pkl          <- Model KNN pre-trained + SMOTE (biner)
+-- scaler.pkl                 <- MinMaxScaler pre-trained (biner)
+-- 2020 Predictive Maintenance Dataset.csv  <- Dataset sumber
|
+-- database/
|   +-- db_koneksi.py          <- Koneksi MySQL + CRUD + logging
|   +-- models.py              <- Kelas data ProfileKendaraan
|
+-- core/
|   +-- kalkulator_torsi.py    <- Perhitungan estimasi torsi (interpolasi linear)
|   +-- logika_diagnosa.py     <- Pipeline utama: validasi -> torsi -> domain adaptation -> KNN
|   +-- mesin_ai_base.py       <- Base class: scaling data, predict, hitung_risiko
|   +-- mesin_ai_pickle.py     <- Model AI dari file .pkl (pre-trained)
|   +-- mesin_ai_manual.py     <- Model AI live training dari CSV + SMOTE
|
+-- ui/
    +-- diagnostics_view.py    <- Tab Diagnosa AI (panel utama)
    +-- torque_view.py         <- Tab Database Torsi (CRUD kendaraan)
    +-- history_view.py        <- Tab Log Riwayat (tabel + ekspor CSV)
    +-- styles.py              <- Konstanta gaya tampilan header
```

### 2.2 Pola Arsitektur 3-Layer

Program menggunakan pola **3-Layer Architecture** (Presentasi - Logika - Data):

```
+-------------------------------------------+
|         LAYER PRESENTASI (UI)             |
|  diagnostics_view  torque_view            |
|  history_view  styles                     |
+-------------------------------------------+
|         LAYER LOGIKA BISNIS (Core)        |
|  logika_diagnosa  kalkulator_torsi        |
|  mesin_ai_base  mesin_ai_pickle           |
|  mesin_ai_manual                          |
+-------------------------------------------+
|         LAYER DATA (Database)             |
|  db_koneksi  models                       |
|  MySQL: db_predict_maintenance            |
+-------------------------------------------+
```

---

## 3. DATASET DAN SUMBER DATA

### 3.1 Informasi Dataset

| Atribut | Keterangan |
|---|---|
| **Nama Dataset** | 2020 Predictive Maintenance Dataset |
| **Format** | CSV (Comma Separated Values) |
| **Ukuran** | +/- 10.000 baris data |
| **Domain Asli** | Mesin industri manufaktur (CNC / Computer Numerical Control) |
| **Sumber** | Dataset open-source untuk penelitian Predictive Maintenance |

### 3.2 Fitur (Variabel Input) yang Digunakan

| Kolom Dataset | Satuan | Deskripsi |
|---|---|---|
| `Rotational speed [rpm]` | RPM | Kecepatan rotasi spindle mesin CNC |
| `Process temperature [K]` | Kelvin | Suhu proses/kerja mesin |
| `Air temperature [K]` | Kelvin | Suhu udara lingkungan |
| `Torque [Nm]` | Newton-meter | Torsi yang dihasilkan mesin |

### 3.3 Variabel Target (Label Klasifikasi)

| Nilai | Kelas | Makna |
|---|---|---|
| `0` | Normal | Mesin beroperasi dalam kondisi baik |
| `1` | Machine Failure | Mesin mengalami kegagalan/kerusakan |

### 3.4 Distribusi Kelas (Ketidakseimbangan Data)

Dataset asli memiliki **distribusi kelas yang sangat tidak seimbang**:

| Kelas | Jumlah Baris | Persentase |
|---|---|---|
| Normal (0) | ~9.661 | ~96,6% |
| Failure (1) | ~339 | ~3,4% |

> Ketidakseimbangan ini menjadi alasan utama penggunaan **SMOTE** dalam pipeline training model.

---

## 4. METODOLOGI DAN ALGORITMA

### 4.1 Algoritma Utama: K-Nearest Neighbors (KNN)

**K-Nearest Neighbors (KNN)** adalah algoritma *supervised learning* berbasis instance (*lazy learner*) yang melakukan klasifikasi berdasarkan **kedekatan jarak** suatu data baru terhadap data training yang sudah berlabel.

#### Alur Kerja KNN:

```
DATA INPUT (4 fitur) --> SCALING --> CARI 5 TETANGGA TERDEKAT --> VOTING --> PROBABILITAS RISIKO
```

**Parameter model yang digunakan:**

| Parameter | Nilai | Keterangan |
|---|---|---|
| `n_neighbors` | 5 | 5 tetangga terdekat dipertimbangkan |
| `metric` | Euclidean | Fungsi pengukur jarak antar titik |
| `weights` | uniform | Semua tetangga memiliki bobot yang sama |

**Rumus Jarak Euclidean antar dua titik data:**

```
d(A,B) = akar dari:
  (rpm_A - rpm_B)^2 + (suhu_mesin_A - suhu_mesin_B)^2
  + (suhu_udara_A - suhu_udara_B)^2 + (torsi_A - torsi_B)^2
```

**Formula Persentase Risiko (dari predict_proba):**

```
Risiko (%) = (jumlah tetangga berkelas Failure dari 5 tetangga) / 5 x 100
```

**Ilustrasi voting 5 tetangga:**

| Skenario | Komposisi 5 Tetangga | Risiko |
|---|---|---|
| Semua Normal | 5 Normal, 0 Failure | 0% |
| Mayoritas Normal | 4 Normal, 1 Failure | 20% |
| Campuran seimbang | 3 Normal, 2 Failure | 40% |
| Mayoritas Failure | 2 Normal, 3 Failure | 60% |
| Semua Failure | 0 Normal, 5 Failure | 100% |

### 4.2 Teknik Penyeimbangan Data: SMOTE

**SMOTE (Synthetic Minority Oversampling Technique)** membuat data sintetis baru pada kelas minoritas (Failure) dengan cara **interpolasi antara data minoritas yang sudah ada** — bukan sekadar duplikasi data.

```
SEBELUM SMOTE:  Normal [==========================] 96.6% | Failure [=] 3.4%
SETELAH SMOTE:  Normal [=============] 50.0% | Failure [=============] 50.0%
```

**Mengapa SMOTE penting?**  
Tanpa SMOTE, model KNN akan **bias** memprediksi Normal terus-menerus karena kelas tersebut mendominasi 96.6% data training — membuat model tidak berguna untuk mendeteksi kegagalan yang sebenarnya.

**Parameter SMOTE:**

| Parameter | Nilai | Keterangan |
|---|---|---|
| `random_state` | 42 | Seed untuk reproduktibilitas hasil training |
| `sampling_strategy` | auto | Seimbangkan kelas ke rasio 50:50 |

### 4.3 Normalisasi Data: MinMaxScaler

Sebelum training dan prediksi, semua fitur dinormalisasi ke rentang **[0, 1]** agar fitur dengan skala besar tidak mendominasi perhitungan jarak Euclidean:

**Rumus MinMaxScaler:**
```
x_scaled = (x - x_min) / (x_max - x_min)
```

**Rentang normalisasi berdasarkan data training:**

| Fitur | Rentang Asli | Setelah Scaling |
|---|---|---|
| RPM | 1168 - 2886 RPM | 0.0 - 1.0 |
| Suhu Proses | 295.3 - 313.8 K | 0.0 - 1.0 |
| Suhu Udara | 295.3 - 304.5 K | 0.0 - 1.0 |
| Torsi | 3.8 - 76.6 Nm | 0.0 - 1.0 |

### 4.4 Kalkulator Torsi: Interpolasi Linear

Karena input dari pengguna adalah **RPM kendaraan** (bukan torsi langsung dari sensor), sistem menghitung estimasi torsi secara otomatis menggunakan **interpolasi linear** antara kondisi idle dan kondisi puncak:

**Rumus:**
```
T_idle = T_max x 0.15   (torsi saat stasioner = 15% dari puncak)

Jika RPM_live <= RPM_idle   --> T_estimasi = T_idle
Jika RPM_live >= RPM_puncak --> T_estimasi = T_max

Jika di antara keduanya:
T_estimasi = T_idle + ((RPM_live - RPM_idle) / (RPM_puncak - RPM_idle)) x (T_max - T_idle)
```

**Contoh perhitungan** (Kendaraan: idle_rpm=750, max_rpm=6000, max_torque=140 Nm):

| RPM Input | Perhitungan | Torsi Estimasi |
|---|---|---|
| 500 RPM (di bawah idle) | T_idle = 140 x 0.15 | 21.0 Nm |
| 750 RPM (tepat idle) | T_idle = 140 x 0.15 | 21.0 Nm |
| 3.375 RPM (tengah) | 21 + (2625/5250) x 119 | 80.5 Nm |
| 6.000 RPM (redline) | T_max | 140.0 Nm |
| 7.000 RPM (di atas redline) | T_max (dikap) | 140.0 Nm |

### 4.5 Domain Adaptation: Jembatan Kendaraan ke Dataset CNC

**Masalah inti:** Dataset menggunakan data mesin CNC industri, sedangkan input pengguna adalah data kendaraan bermotor dengan satuan dan rentang nilai yang berbeda.

**Solusi:** Sistem menghitung **persentase beban** kendaraan terlebih dahulu, lalu memetakan persentase tersebut ke rentang nilai yang realistis dalam dataset CNC.

**Langkah-langkah Domain Adaptation:**

```
LANGKAH 1 - Hitung Beban Kendaraan (normalisasi internal):
  persen_rpm   = RPM_live / RPM_max_kendaraan       (0.0 - 1.0)
  persen_torsi = T_estimasi / T_max_kendaraan        (0.0 - 1.0)

LANGKAH 2 - Petakan ke Skala Dataset CNC:
  RPM_AI       = 2500 - (persen_rpm x 1200)          [1300 - 2500 RPM]
  Torsi_AI     = 20 + (persen_torsi x 55)            [20 - 75 Nm]
  SuhuMesin_AI = 300 + (suhu_m / 120 x 14)          [300 - 314 K]
  SuhuUdara_AI = 295 + (suhu_u / 50 x 9)            [295 - 304 K]

LANGKAH 3 - Klamping (batasi ke rentang valid dataset):
  RPM_AI       --> [1200, 3000] RPM
  Torsi_AI     --> [10, 80] Nm
  SuhuMesin_AI --> [295, 315] K
  SuhuUdara_AI --> [290, 305] K
```

**Catatan penting tentang pemetaan RPM (inversi):**  
Pada dataset CNC, RPM **tinggi** = mesin berputar **cepat dan ringan** (tanpa beban). RPM **rendah** = mesin **tertahan/terbebani**. Karena itu pemetaan menggunakan formula inversi: semakin tinggi beban kendaraan → RPM_AI semakin rendah.

---

## 5. ALUR KERJA SISTEM (PIPELINE DIAGNOSA)

### 5.1 Diagram Pipeline Lengkap

```
INPUT MEKANIK
(RPM, Suhu Mesin, Suhu Udara, Pilih Kendaraan)
        |
        v
+-------------------+
|  VALIDASI INPUT   | --> RPM: 0-20000 | Suhu M: -20 s/d 250 C | Suhu U: -20 s/d 70 C
+-------------------+     max_rpm > 0 | max_torque > 0 | RPM > 50% idle
        |
        v (jika invalid --> return ERROR)
+-------------------------------+
|  KALKULASI TORSI ESTIMASI     | --> Interpolasi Linear
|  T = T_idle + fraksi x dT    |     Hasil: Torsi (Nm) & Beban (%)
+-------------------------------+
        |
        v
+-------------------------------+
|  DOMAIN ADAPTATION            | --> Petakan Kendaraan ke Skala Dataset CNC
|  4 parameter -> 4 nilai AI    |     RPM_AI, Torsi_AI, SuhuMesin_AI, SuhuUdara_AI
+-------------------------------+
        |
        v
+-------------------------------+
|  FEATURE SCALING              | --> MinMaxScaler.transform()
|  Normalisasi ke [0, 1]        |     Gunakan scaler yang sama saat training
+-------------------------------+
        |
        v
+-------------------------------+
|  KNN PREDICT_PROBA (k=5)      | --> Cari 5 tetangga terdekat (Euclidean)
|  Output: [P(Normal), P(Fail)] |     Risiko % = P(Failure) x 100
+-------------------------------+
        |
        v
+-------------------------------+
|  PENGAMBILAN KEPUTUSAN        | Risiko < 40%   --> NORMAL
|  Berdasarkan Threshold (%)    | 40% <= R < 75% --> WARNING
+-------------------------------+ Risiko >= 75%  --> MALFUNGSI
        |
        v
+-------------------------------+
|  OUTPUT & PENYIMPANAN LOG     | --> Update UI Dashboard (status, torsi, beban, risiko, insight)
|  Simpan ke MySQL              | --> INSERT ke tabel log_diagnosa
+-------------------------------+
```

### 5.2 Dua Mode Model AI

| Aspek | Mode Pickle (.pkl) | Mode Manual (CSV) |
|---|---|---|
| **Cara kerja** | Memuat model KNN yang sudah jadi dari file biner | Melatih KNN baru dari dataset CSV setiap digunakan |
| **Kecepatan startup** | Instan (< 1 detik) | Lambat (5-15 detik, perlu SMOTE + training) |
| **Data training** | Tetap (snapshot saat model dibuat) | Selalu menggunakan data CSV terbaru |
| **File yang diperlukan** | model_terbaik.pkl + scaler.pkl | 2020 Predictive Maintenance Dataset.csv |
| **Rekomendasi** | Penggunaan sehari-hari | Verifikasi atau eksplorasi ulang model |

---

## 6. ANTARMUKA PENGGUNA (GUI)

### 6.1 Struktur Tab Aplikasi

Aplikasi memiliki **3 tab utama** yang diakses dari panel navigasi atas:

```
+----------------------------------------------------------+
|  [AI] Diagnosa AI  |  [DB] Database Torsi  |  [LOG] Log  |
+----------------------------------------------------------+
|                   Konten Tab Aktif                        |
+----------------------------------------------------------+
```

### 6.2 Tab 1: Diagnosa AI (Panel Utama)

Tab ini dibagi menjadi **4 panel**:

**Panel Kiri — Input Telemetri:**
- Dropdown pilih kendaraan (data dari database)
- Field input: RPM, Suhu Mesin (C), Suhu Udara (C)
- Validator numerik mencegah input non-angka

**Panel Tengah — Konfigurasi Model ML:**
- Radio button pilih mode AI (Pickle pre-trained / Manual CSV live training)
- Tombol PROSES DIAGNOSA — eksekusi pipeline lengkap
- Tombol RESET FORMULIR — bersihkan semua input dan hasil

**Panel Kanan — Dashboard Hasil:**

| Komponen UI | Informasi yang Ditampilkan |
|---|---|
| Label STATUS AI | NORMAL / WARNING / MALFUNGSI (warna berubah) |
| Label Torsi | Estimasi torsi kendaraan hasil interpolasi linear (Nm) |
| Label Beban | Persentase beban mesin 0-100% (merah jika > 85%) |
| Progress Bar | Persentase risiko kerusakan dari KNN 0-100% (warna dinamis) |
| Text Insight | Penjelasan logis dan saran mekanis berdasarkan hasil |
| Label Detail AI | Nilai 4 parameter setelah dipetakan ke skala dataset CNC |

**Panel Bawah — Riwayat Mini:**
- Tabel 5 diagnosa terakhir: Waktu, Kendaraan, Beban, Risiko, Status

### 6.3 Tab 2: Database Torsi (Manajemen Kendaraan)

Tab CRUD untuk mengelola profil spesifikasi kendaraan.

**Data profil kendaraan yang disimpan:**

| Field | Satuan | Contoh Nilai |
|---|---|---|
| Nama Kendaraan | - | Toyota Avanza 2019 |
| RPM Idle | RPM | 750 |
| Torsi Puncak | Nm | 140 |
| RPM Redline | RPM | 6000 |

**Operasi yang tersedia:**
- **SIMPAN PROFIL** — Tambah kendaraan baru ke database
- **PERBARUI** — Edit spesifikasi kendaraan yang dipilih di tabel
- **HAPUS** — Hapus kendaraan terpilih (dengan konfirmasi)
- **BATAL** — Batalkan seleksi dan kosongkan form

### 6.4 Tab 3: Log Riwayat

Menampilkan tabel lengkap semua rekaman hasil diagnosa.

**Kolom tabel riwayat:**
`Waktu | Kendaraan | RPM | Torsi (Nm) | Beban (%) | Suhu M (C) | Suhu U (C) | Risiko (%) | Status`

**Fitur tab ini:**
- **Pencarian dinamis** — filter real-time semua kolom saat mengetik
- **Perbarui Data** — muat ulang data terbaru dari database
- **Ekspor CSV** — simpan data yang tampil ke file CSV eksternal
- **Hapus Riwayat** — TRUNCATE tabel log (permanen, dengan konfirmasi)

---

## 7. DATABASE: STRUKTUR TABEL MySQL

**Nama Database:** `db_predict_maintenance`

### Tabel `torsi_kendaraan` — Profil Spesifikasi Kendaraan

```sql
CREATE TABLE torsi_kendaraan (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nama       VARCHAR(255),  -- Nama/model kendaraan
    idle_rpm   INT,           -- RPM stasioner (idle)
    max_torque INT,           -- Torsi puncak dalam Nm
    max_rpm    INT            -- RPM redline (batas maksimum)
);
```

### Tabel `log_diagnosa` — Riwayat Hasil Diagnosa

```sql
CREATE TABLE log_diagnosa (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    tanggal     VARCHAR(255), -- Timestamp: "YYYY-MM-DD HH:MM:SS"
    nama_mobil  VARCHAR(255), -- Nama kendaraan yang didiagnosa
    rpm         INT,          -- RPM input dari mekanik
    torsi       DOUBLE,       -- Estimasi torsi hasil kalkulasi (Nm)
    beban       DOUBLE,       -- Persentase beban mesin (%)
    suhu_mesin  DOUBLE,       -- Suhu mesin input (derajat C)
    suhu_udara  DOUBLE,       -- Suhu udara input (derajat C)
    risiko      DOUBLE,       -- Risiko dari KNN predict_proba (%)
    status      VARCHAR(255)  -- NORMAL / WARNING / MALFUNGSI
);
```

---

## 8. INTERPRETASI HASIL DIAGNOSA

### 8.1 Tabel Keputusan Sistem

| Status | Warna | Risiko KNN | Interpretasi | Tindakan yang Disarankan |
|---|---|---|---|---|
| NORMAL | Hijau | 0% - 39% | Parameter operasional dalam batas toleransi | Tidak diperlukan tindakan khusus |
| WARNING | Oranye | 40% - 74% | Terdeteksi anomali stres fisik atau suhu | Periksa sistem pendingin, kurangi beban mesin |
| MALFUNGSI | Merah | 75% - 100% | Pola identik dengan kegagalan absolut di dataset | Hentikan operasi, lakukan inspeksi menyeluruh |

### 8.2 Kondisi ERROR Otomatis (Sebelum Proses KNN)

Sistem melakukan validasi berlapis sebelum data masuk ke model KNN:

| Kode Error | Penyebab |
|---|---|
| `ERROR (INPUT INVALID)` | RPM, suhu mesin, atau suhu udara di luar batas fisik yang masuk akal |
| `ERROR (MESIN MATI)` | RPM live < 50% dari RPM idle (indikasi mesin stall/mati) |
| `ERROR (DATA KENDARAAN)` | Spesifikasi kendaraan tidak valid (max_rpm = 0 atau max_torque = 0) |

### 8.3 Insight Kontekstual Tambahan

Selain threshold risiko KNN, sistem menambahkan peringatan spesifik:
- Jika **suhu mesin > 95 C** -> insight peringatan sistem pendingin
- Jika **torsi > 80% dari torsi puncak** -> insight peringatan beban torsi berlebih

---

## 9. PARAMETER TEKNIS DAN BATASAN SISTEM

### 9.1 Batasan Validasi Input

| Parameter | Batas Minimum | Batas Maksimum | Alasan Penetapan Batas |
|---|---|---|---|
| RPM | 0 | 20.000 | Batas fisik umum mesin kendaraan |
| Suhu Mesin | -20 C | 250 C | Batas fisik material logam mesin |
| Suhu Udara | -20 C | 70 C | Kondisi lapangan paling ekstrem |
| RPM Live | > idle x 50% | - | Deteksi kondisi mesin stall/mati |
| max_rpm kendaraan | > 0 | - | Mencegah pembagian nol di kalkulasi beban |

### 9.2 Asumsi yang Digunakan dalam Sistem

| Asumsi | Nilai / Penjelasan |
|---|---|
| Rasio torsi idle | 15% dari torsi puncak (estimasi umum mesin bensin) |
| Kurva torsi | Linear dari idle ke redline (disederhanakan dari kurva non-linear nyata) |
| Pemetaan domain | Heuristik berdasarkan observasi distribusi dataset CNC |
| Jumlah tetangga KNN | k=5 (trade-off antara sensitifitas dan robustness) |

---

## 10. KETERBATASAN SISTEM

| Keterbatasan | Penjelasan |
|---|---|
| **Domain Gap** | Dataset adalah data mesin CNC industri, bukan mesin kendaraan. Domain Adaptation merupakan pendekatan heuristik, belum tervalidasi secara ilmiah untuk semua jenis kendaraan. |
| **Torsi Estimasi** | Torsi dihitung via interpolasi linear, bukan pembacaan sensor langsung. Akurasi bergantung pada kebenaran spesifikasi kendaraan yang diinput pengguna. |
| **Ketergantungan Dataset** | Model hanya dapat mendeteksi pola kegagalan yang pernah ada di dataset. Jenis kegagalan baru yang belum terekam tidak akan terdeteksi. |
| **Jumlah Fitur** | Hanya 4 fitur sensor digunakan. Sistem sensor kendaraan riil memiliki puluhan parameter yang tidak dipertimbangkan dalam model ini. |
| **Asumsi Linear Torsi** | Kurva torsi mesin nyata bersifat non-linear (berubah berbeda di tiap RPM). Penyederhanaan ini mengurangi akurasi estimasi torsi. |

---

## 11. CONTOH SKENARIO PENGGUNAAN LENGKAP

### Skenario A: Kendaraan dalam Kondisi Normal

```
DATA INPUT:
  Kendaraan    : Toyota Avanza (idle_rpm=750, max_torque=140, max_rpm=6000)
  RPM          : 2.000
  Suhu Mesin   : 85 C
  Suhu Udara   : 30 C

PERHITUNGAN KALKULATOR TORSI:
  T_idle       = 140 x 0.15 = 21 Nm
  rentang_rpm  = 6000 - 750 = 5.250
  selisih_rpm  = 2000 - 750 = 1.250
  T_estimasi   = 21 + (1250/5250) x (140-21) = 21 + 0.238 x 119 = 21 + 28.33 = 49.33 Nm

PERHITUNGAN BEBAN:
  persen_rpm   = 2000/6000 = 0.333
  persen_torsi = 49.33/140 = 0.352
  Beban Mesin  = max(0.333, 0.352) x 100 = 35.2%

DOMAIN ADAPTATION:
  RPM_AI       = 2500 - (0.333 x 1200) = 2500 - 400 = 2100 RPM
  Torsi_AI     = 20 + (0.352 x 55) = 20 + 19.4 = 39.4 Nm
  SuhuMesin_AI = 300 + (85/120 x 14) = 300 + 9.9 = 309.9 K
  SuhuUdara_AI = 295 + (30/50 x 9) = 295 + 5.4 = 300.4 K

HASIL KNN:
  Risiko       : ~15% (mayoritas 5 tetangga berkelas Normal)
  STATUS       : NORMAL
  Insight      : Aman - parameter operasional dalam zona toleransi
```

### Skenario B: Mesin Overheat saat RPM Tinggi

```
DATA INPUT:
  Kendaraan    : Toyota Avanza (idle_rpm=750, max_torque=140, max_rpm=6000)
  RPM          : 5.500
  Suhu Mesin   : 110 C
  Suhu Udara   : 38 C

PERHITUNGAN KALKULATOR TORSI:
  selisih_rpm  = 5500 - 750 = 4.750
  T_estimasi   = 21 + (4750/5250) x 119 = 21 + 107.6 = 128.6 Nm

PERHITUNGAN BEBAN:
  persen_rpm   = 5500/6000 = 0.917
  persen_torsi = 128.6/140 = 0.919
  Beban Mesin  = max(0.917, 0.919) x 100 = 91.9%

DOMAIN ADAPTATION:
  RPM_AI       = 2500 - (0.917 x 1200) = 2500 - 1100 = 1400 RPM
  Torsi_AI     = 20 + (0.919 x 55) = 20 + 50.5 = 70.5 Nm
  SuhuMesin_AI = 300 + (110/120 x 14) = 300 + 12.8 = 312.8 K
  SuhuUdara_AI = 295 + (38/50 x 9) = 295 + 6.8 = 301.8 K

HASIL KNN:
  Risiko       : ~78% (mayoritas 5 tetangga berkelas Failure)
  STATUS       : MALFUNGSI
  Insight      : Suhu mesin di atas normal, torsi mendekati batas redline
```

---

## 12. RINGKASAN UNTUK PEMBUATAN LAPORAN

### 12.1 Poin Utama yang Harus Ada di Laporan:

1. **Latar Belakang:** Pentingnya Predictive Maintenance dibanding reactive maintenance untuk efisiensi dan penghematan biaya
2. **Dataset:** 2020 Predictive Maintenance Dataset, ~10.000 baris, 4 fitur sensor, label biner (0=Normal, 1=Failure), ketidakseimbangan kelas 96.6%:3.4%
3. **Preprocessing:** SMOTE untuk oversampling kelas minoritas, MinMaxScaler untuk normalisasi fitur ke [0,1]
4. **Model:** KNN k=5, jarak Euclidean, predict_proba menghasilkan persentase probabilitas risiko
5. **Inovasi:** Domain Adaptation — teknik heuristik untuk memetakan parameter kendaraan ke skala dataset mesin CNC
6. **Kalkulator Torsi:** Interpolasi linear dengan T_idle = 15% x T_max
7. **Keputusan:** 3 level output (Normal < 40%, Warning 40-75%, Malfungsi >= 75%)
8. **Implementasi:** Desktop GUI PySide6, database MySQL, pencatatan log riwayat diagnosa

### 12.2 Kalimat Abstrak yang Dapat Digunakan:

> "Penelitian ini mengembangkan sistem Predictive Maintenance berbasis algoritma K-Nearest Neighbors (KNN) untuk mendeteksi potensi kegagalan mesin kendaraan secara real-time. Dataset yang digunakan adalah 2020 Predictive Maintenance Dataset yang berisi 10.000 data sensor mesin industri CNC dengan empat fitur: kecepatan rotasi, suhu proses, suhu udara, dan torsi. Untuk mengatasi ketidakseimbangan kelas yang ekstrem (96.6% Normal vs 3.4% Failure), diterapkan teknik SMOTE dalam proses pelatihan model. Inovasi utama sistem ini adalah penerapan Domain Adaptation yang memetakan parameter telemetri kendaraan ke dalam skala dataset CNC, memungkinkan model KNN pre-trained dapat diaplikasikan pada domain kendaraan. Sistem menghasilkan persentase risiko kegagalan melalui fungsi predict_proba dengan tiga tingkat keputusan: Normal (risiko < 40%), Warning (40-75%), dan Malfungsi (>= 75%). Aplikasi diimplementasikan sebagai perangkat lunak desktop menggunakan framework PySide6 dengan penyimpanan riwayat diagnosa berbasis MySQL."
