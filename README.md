# 🩺 Fuzzy Dokter Scheduler

Aplikasi web berbasis Flask untuk mensimulasikan penjadwalan adaptif dokter di berbagai rumah sakit dan klinik menggunakan logika fuzzy berdasarkan jumlah pasien harian.

## Update Ver 1.0.0
- Ubah tampilan ke streamlit, jadi semua hal yang berhubungan flask diganti
- Searching awal untuk RS diterapkan algoritma Greedy, berbeda dengan sebelumnya yang memakai pembagian Round Robin biasa.

### What to do next?
- Implementasi penyakit setiap peserta.
- Implementasi Planning explisit dalam code.

## Fitur Utama

- Menghitung rasio pasien per dokter di tiap wahana (klinik/rumah sakit).
- Menggunakan logika fuzzy untuk menilai kondisi:
  - **Underutilized** (dokter kurang dimanfaatkan),
  - **Normal** (beban seimbang),
  - **Overutilized** (dokter terlalu dibebani).
- Redistribusi dokter dari wahana yang under ke yang over.
- Tampilan hasil per tanggal: sebelum dan sesudah reposisi dokter.
- Fitur dropdown interaktif untuk memilih tanggal tertentu.

## Struktur Proyek
uts-ai/
├── app.py
├── routes.py
├── scheduler.py
├── README.md
├── data/
│   ├── Data Dummy Peserta.csv
│   ├── Data Dummy Wahana.csv
│   └── Jumlah Pasien.csv
├── templates/
│   └── index.html
└── static/
    └── (opsional file CSS)

## Deskripsi Dataset

- **Data Dummy Peserta.csv**: Daftar dokter beserta ID dan nama.
- **Data Dummy Wahana.csv**: Informasi wahana (klinik/RS) dan kapasitas optimal.
- **Jumlah Pasien.csv**: Data jumlah pasien harian untuk setiap wahana.

## Cara Kerja

1. Dokter dibagikan secara merata ke semua wahana di awal.
2. Sistem menghitung rasio pasien per dokter.
3. Fuzzy logic digunakan untuk menentukan status masing-masing wahana.
4. Dokter dari wahana underutilized dikurangi dan didistribusikan ulang ke wahana yang overutilized atau rasio tertinggi.
5. Tampilkan hasil jadwal sebelum & sesudah redistribusi.

## 🚀 Cara Menjalankan

### 1. Clone & Install Dependency
    ```bash
    git clone https://github.com/namakamu/uts-ai.git
    cd uts-ai
    pip install flask pandas
    ```

### 2. Jalankan Flask
    ```bash
    python app.py
    ```
    Buka browser dan kunjungi: http://127.0.0.1:5000

## Pengembangan Selanjutnya
1. Merapikan template dan tata-letak browser
2. Merubah data CSV secara real-time di HTML
3. Reposisi dokter seusai dengan jenis penyakit yang ingin dipelajari.
4. Penambahan styles simple.