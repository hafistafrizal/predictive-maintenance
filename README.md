# Sistem Manajemen Torsi (Predictive Maintenance)

Aplikasi berbasis GUI (PySide6) untuk mengelola data spesifikasi kendaraan dan melakukan estimasi torsi berdasarkan RPM menggunakan database MySQL.

---

## Prasyarat (Prerequisites)

Sebelum menjalankan aplikasi, pastikan Anda telah menginstal komponen berikut di sistem Anda:
1. **Python 3.8+**
2. **MySQL Server** (bisa menggunakan XAMPP, Laragon, WAMP, atau MySQL Installer mandiri)

---

## 1. Instalasi Library (Dependensi)

Ikuti langkah-langkah di bawah ini untuk menyiapkan *virtual environment* dan menginstal pustaka Python yang diperlukan.

### A. Mengaktifkan Virtual Environment (Direkomendasikan)
Masuk ke terminal atau Command Prompt pada direktori proyek Anda (`predict-maintenence`), lalu jalankan perintah berikut:

**Windows (PowerShell):**
```powershell
# Jika folder .venv belum ada, buat terlebih dahulu:
python -m venv .venv

# Aktifkan virtual environment:
.venv\Scripts\activate
```

**Windows (CMD):**
```cmd
# Aktifkan virtual environment:
.venv\Scripts\activate.bat
```

### B. Menginstal Pustaka Python
Setelah virtual environment aktif, instal dependensi utama menggunakan perintah berikut:
```bash
pip install PySide6 mysql-connector-python
```

*Catatan opsional: Jika Anda berencana menggunakan model machine learning (`model_terbaik.pkl`) dan dataset CSV yang ada di dalam proyek ini di masa depan, silakan instal juga pustaka pendukung data science:*
```bash
pip install pandas scikit-learn joblib
```

---

## 2. Konfigurasi Database MySQL

Aplikasi terhubung ke MySQL lokal dengan konfigurasi sebagai berikut (dapat dilihat pada `database/db_koneksi.py`):
- **Host:** `localhost`
- **User:** `root`
- **Password:** `""` (kosong/default)
- **Database:** `db_kendaraan_torsi`

### Langkah Pembuatan Database & Tabel:

1. **Jalankan MySQL Server** melalui aplikasi control panel Anda (contoh: buka **XAMPP Control Panel** dan klik **Start** pada modul **MySQL**).
2. Buka alat pengelola database Anda, misalnya **phpMyAdmin** di browser melalui alamat: `http://localhost/phpmyadmin/`.
3. Buat database baru dengan nama **`db_kendaraan_torsi`**. Anda dapat menggunakan tab SQL di phpMyAdmin dan menjalankan perintah:
   ```sql
   CREATE DATABASE db_kendaraan_torsi;
   ```
4. Masuk ke database tersebut dan buat tabel bernama **`torsi_kendaraan`** menggunakan perintah SQL berikut:
   ```sql
   USE db_kendaraan_torsi;

   CREATE TABLE IF NOT EXISTS torsi_kendaraan (
       id INT AUTO_INCREMENT PRIMARY KEY,
       nama VARCHAR(255),
       idle_rpm INT,
       max_torque INT,
       max_rpm INT
   );
   ```

---

## 3. Cara Menjalankan Aplikasi

Ada dua file utama yang bisa Anda jalankan untuk mencoba proyek ini:

### A. Menjalankan Aplikasi GUI Utama
Jalankan file `main.py` untuk membuka tampilan antarmuka visual (GUI):
```bash
python main.py
```
**Fitur di dalam GUI:**
- **Input Data:** Tambahkan nama kendaraan, RPM Idle, Torsi Maksimal, dan RPM Maksimal.
- **CRUD Operations:** Tombol Simpan, Update, dan Delete untuk mengelola data langsung ke database.
- **Tabel Interaktif:** Klik baris pada tabel untuk memilih data yang ingin diubah atau dihapus.

### B. Menjalankan Simulasi Uji Coba Kalkulator (CLI)
Jalankan file `test_kalkulator.py` untuk melihat simulasi perhitungan torsi di berbagai rentang RPM melalui terminal (Command Line Interface):
```bash
python test_kalkulator.py
```

---

## Struktur Folder Proyek
- `main.py` - Titik masuk (*entry point*) utama aplikasi GUI.
- `test_kalkulator.py` - Skrip uji coba logika kalkulator torsi via terminal.
- `testing_data.py` - Skrip uji coba koneksi database (CRUD test).
- `core/`
  - `kalkulator_torsi.py` - Logika interpolasi linear untuk mengestimasi torsi berdasarkan RPM input.
  - `mesin_ai_manual.py` & `mesin_ai_pickle.py` - Modul kosong (placeholder) untuk pengembangan AI lebih lanjut.
- `database/`
  - `db_koneksi.py` - Modul untuk mengelola koneksi dan query SQL ke database MySQL.
  - `models.py` - Kelas `ProfileKendaraan` sebagai representasi objek data kendaraan.
- `ui/`
  - `torque_view.py` - Tata letak dan event handling dari komponen GUI (PySide6).
- `2020 Predictive Maintenance Dataset.csv` - Dataset pendukung.
- `model_terbaik.pkl` & `scaler.pkl` - Model machine learning yang siap diintegrasikan untuk estimasi tingkat lanjut.
