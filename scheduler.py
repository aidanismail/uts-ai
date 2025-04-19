# app/scheduler.py

import pandas as pd

def underutilized(x):
    if x <= 3:
        return 1
    elif 3 < x < 5:
        return (5 - x) / 2
    return 0

def normal(x):
    if 5 < x < 10:
        return (x - 5) / 5
    elif 10 <= x <= 20:
        return (20 - x) / 10
    return 0

def overutilized(x):
    if 20 < x < 25:
        return (x - 20) / 5
    elif x >= 25:
        return 1
    return 0

def jalankan_simulasi(jumlah_peserta_total):
    peserta_df = pd.read_csv("data/Data Dummy Peserta.csv")
    wahana_df = pd.read_csv("data/Data Dummy Wahana.csv")
    pasien_df = pd.read_csv("data/Jumlah Pasien.csv")

    df_long = pasien_df.melt(id_vars="Tanggal", var_name="Nama Wahana", value_name="Jumlah Pasien")
    merged_df = df_long.merge(wahana_df, on="Nama Wahana", how="left")

    data_pasien = {}
    for _, row in merged_df.iterrows():
        tgl = row['Tanggal']
        if tgl not in data_pasien:
            data_pasien[tgl] = {}
        data_pasien[tgl][row['Nama Wahana']] = {
            'jumlah_pasien': row['Jumlah Pasien'],
            'kapasitas_optimal': row['Kapasitas Peserta Optimal'],
            'estimasi_pasien_optimal': row['Estimasi Pasien Optimal']
        }

    data_peserta = dict(zip(peserta_df['ID_Peserta'], peserta_df['Nama Peserta']))
    list_dokter = list(data_peserta.items())

    set_rs = sorted({rs for wahana in data_pasien.values() for rs in wahana})
    jumlah_rs = len(set_rs)

    rs_to_dokter = {rs: [] for rs in set_rs}
    for i, (id_d, nama_d) in enumerate(list_dokter):
        rs = set_rs[i % jumlah_rs]
        rs_to_dokter[rs].append({'ID': id_d, 'Nama': nama_d})

    hasil_per_tanggal = {}

    for tanggal, data_harian in data_pasien.items():
        rumah_sakit_info = []

        # Step 1: Hitung fuzzy untuk semua RS
        for rs in set_rs:
            dokter_list = rs_to_dokter[rs]
            jumlah_dokter = len(dokter_list)
            if rs in data_harian:
                jumlah_pasien = data_harian[rs]['jumlah_pasien']
                rasio = jumlah_pasien / jumlah_dokter if jumlah_dokter > 0 else 0

                u = underutilized(rasio)
                n = normal(rasio)
                o = overutilized(rasio)

                rumah_sakit_info.append({
                    "RS": rs,
                    "Pasien": jumlah_pasien,
                    "Dokter_List": dokter_list.copy(),  # simpan list aslinya
                    "Jumlah Dokter": jumlah_dokter,
                    "Rasio": round(rasio, 2),
                    "Under": round(u, 2),
                    "Normal": round(n, 2),
                    "Over": round(o, 2),
                    "Aksi": "Tetap"
                })

        # Step 2: Redistribusi dari yang under
        surplus_pool = []
        for info in rumah_sakit_info:
            if info['Under'] > max(info['Normal'], info['Over']):
                if info['Jumlah Dokter'] > 1:
                    dokter_diambil = info['Dokter_List'].pop()  # ambil 1 dokter terakhir
                    surplus_pool.append(dokter_diambil)
                    info['Jumlah Dokter'] -= 1
                    info['Aksi'] = "Kurangi dokter"
                else:
                    info['Aksi'] = "Tetap (tidak bisa dikurangi)"

        # Step 3: Tambahkan ke RS yang overutilized
        for info in rumah_sakit_info:
            if info['Over'] > max(info['Normal'], info['Under']) and surplus_pool:
                dokter_diberikan = surplus_pool.pop()
                info['Dokter_List'].append(dokter_diberikan)
                info['Jumlah Dokter'] += 1
                info['Aksi'] = "Tambah dokter (dari surplus)"

        # Step 4: Hitung ulang rasio dan format dokter untuk display
        for info in rumah_sakit_info:
            info['Rasio Baru'] = round(info['Pasien'] / info['Jumlah Dokter'], 2)
            info['Dokter'] = ', '.join([d['Nama'] for d in info['Dokter_List']])

        # Simpan data distribusi akhir dokter (setelah redistribusi)
        dokter_per_rs = {
            info['RS']: [d['Nama'] for d in info['Dokter_List']]
            for info in rumah_sakit_info
        }

        # Hapus Dokter_List agar tidak bocor ke tampilan
        for info in rumah_sakit_info:
            del info['Dokter_List']

        # Simpan hasil ke hasil_per_tanggal
        hasil_per_tanggal[tanggal] = {
            "jadwal": rumah_sakit_info,
            "distribusi_dokter": dokter_per_rs
        }
    return hasil_per_tanggal
