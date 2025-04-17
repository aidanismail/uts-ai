# app/scheduler.py

import pandas as pd
from fuzzy_logic import fuzzy_relokasi

# Fungsi untuk membaca data dari .csv
def baca_data_wahana():
    df = pd.read_csv('data_dummy.csv')
    return df.to_dict(orient='records')

# Fungsi utama simulasi penjadwalan
def jalankan_simulasi(jumlah_peserta_total):
    data_wahana = baca_data_wahana()
    sisa = jumlah_peserta_total
    hasil = []

    for w in data_wahana:
        kapasitas = w["kapasitas"]
        estimasi_pasien = w["estimasi_pasien"]

        # Penempatan peserta
        penempatan = min(sisa, kapasitas)
        sisa -= penempatan

        # Hitung rasio dan fuzzy relokasi
        if penempatan > 0:
            rasio = estimasi_pasien / penempatan
        else:
            rasio = 999  # avoid division by zero
        
        relokasi = fuzzy_relokasi(rasio)

        hasil.append({
            "nama": w["nama_wahana"],
            "kapasitas": kapasitas,
            "peserta": penempatan,
            "estimasi_pasien": estimasi_pasien,
            "rasio": round(rasio, 2),
            "relokasi": relokasi
        })

    return hasil
