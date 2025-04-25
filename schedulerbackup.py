# app/scheduler.py

import pandas as pd
from fuzzy_logic import fuzzifikasi

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

    ### Revisi 1
    # Simpan spesialisasi yang pernah dihandle dokter
    dokter_to_spesialisasi = {id_d: set() for id_d, _ in list_dokter}
    rs_to_spesialisasi = dict(zip(wahana_df['Nama Wahana'], wahana_df['Jenis Penyakit']))

    set_rs = sorted({rs for wahana in data_pasien.values() for rs in wahana})
    jumlah_rs = len(set_rs)

    ### SEARCHING FOR RS ###
    # Hitung total pasien per RS untuk semua tanggal
    total_pasien = {rs: 0 for rs in set_rs}
    for data_harian in data_pasien.values():
        for rs in data_harian:
            total_pasien[rs] += data_harian[rs]['jumlah_pasien']

    # Urutkan RS berdasarkan total pasien (desc)
    rs_sorted_by_pasien = sorted(set_rs, key=lambda rs: total_pasien[rs], reverse=True)

    # Distribusikan dokter berdasarkan urutan RS yang paling sibuk
    rs_to_dokter = {rs: [] for rs in set_rs}
    # dilakukan ulang di setiap hari (di dalam loop for tanggal)
    for i, (id_d, nama_d) in enumerate(list_dokter):
        rs = rs_sorted_by_pasien[i % jumlah_rs]        
        rs_to_dokter[rs].append({'ID': id_d, 'Nama': nama_d})

        # Tambahkan ke log spesialisasi dokter
        dokter_to_spesialisasi[id_d].add(rs_to_spesialisasi[rs])

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

            μ = fuzzifikasi(rasio)

            rumah_sakit_info.append({
                "RS": rs,
                "Pasien": jumlah_pasien,
                "Dokter_List": dokter_list.copy(),
                "Jumlah Dokter Awal": jumlah_dokter, 
                "Jumlah Dokter": jumlah_dokter,
                "Rasio": round(rasio, 2),

                # New fuzzy values
                "Under Berat": round(μ["Underutilized Berat"], 2),
                "Under Ringan": round(μ["Underutilized Ringan"], 2),
                "Optimal": round(μ["Optimal"], 2),
                "Over Ringan": round(μ["Overload Ringan"], 2),
                "Over Berat": round(μ["Overload Berat"], 2),

                "Aksi": "Tetap"
            })

        # Step 2: Redistribusi dokter dari RS underutilized
        surplus_pool = []
        rs_underutilized = []
        rs_overutilized = sorted(
            [info for info in rumah_sakit_info if (info['Over Berat'] + info['Over Ringan']) > max(info['Optimal'], info['Under Berat'], info['Under Ringan'])],
            key=lambda x: x['Over Berat'] + x['Over Ringan'],
            reverse=True
        )

        for info in rumah_sakit_info:
            if (info['Under Berat'] + info['Under Ringan']) > max(info['Optimal'], info['Over Ringan'], info['Over Berat']):
                if info['Jumlah Dokter'] > 1:
                    dokter_diambil = info['Dokter_List'].pop()
                    surplus_pool.append(dokter_diambil)
                    info['Jumlah Dokter'] -= 1
                    info['Aksi'] = "Kurangi dokter"
                    rs_underutilized.append(info['RS'])
                else:
                    info['Aksi'] = "Tetap (tidak bisa dikurangi)"
            elif (info['Over Ringan'] + info['Over Berat']) > max(info['Optimal'], info['Under Berat'], info['Under Ringan']):
                rs_overutilized.append(info['RS'])

        # Step 3: Distribusi ke RS overutilized (jika ada dokter sisa)
        for info in rumah_sakit_info:
            if info['RS'] in rs_overutilized and surplus_pool:
                dokter_diberikan = surplus_pool.pop(0)
                info['Dokter_List'].append(dokter_diberikan)
                dokter_to_spesialisasi[dokter_diberikan['ID']].add(rs_to_spesialisasi[info['RS']])
                info['Jumlah Dokter'] += 1
                info['Aksi'] = "Tambah dokter (dari surplus)"

        # Step 3.5: Jika masih ada surplus, berikan ke RS dengan rasio tertinggi
        if surplus_pool:
            # Urutkan berdasarkan rasio tertinggi (yang belum menerima dokter tambahan)
            calon_rs = sorted(
                [info for info in rumah_sakit_info if info['Aksi'] == "Tetap"],
                key=lambda x: x['Rasio'],
                reverse=True
            )

            for info in calon_rs:
                if surplus_pool:
                    dokter_diberikan = surplus_pool.pop(0)
                    info['Dokter_List'].append(dokter_diberikan)
                    dokter_to_spesialisasi[dokter_diberikan['ID']].add(rs_to_spesialisasi[info['RS']])
                    info['Jumlah Dokter'] += 1
                    info['Aksi'] = "Tambah dokter (rasio tertinggi)"

        # === Step 3.8: Reassignment berdasarkan kebutuhan spesialisasi ===
        # Jika RS punya spesialisasi tapi tidak ada dokter yang pernah tangani spesialisasi itu
        for info in rumah_sakit_info:
            spesialisasi_rs = rs_to_spesialisasi[info['RS']]
            assigned_dokter = info['Dokter_List']

            # Cek apakah RS ini butuh spesialisasi tapi belum punya dokter yang handle itu
            if not any(spesialisasi_rs in dokter_to_spesialisasi[d['ID']] for d in assigned_dokter):
                # Cari dokter dari RS lain yang pernah handle spesialisasi itu
                for donor_info in rumah_sakit_info:
                    if donor_info['RS'] == info['RS'] or donor_info['Jumlah Dokter'] <= 1:
                        continue

                    for idx, donor in enumerate(donor_info['Dokter_List']):
                        if spesialisasi_rs in dokter_to_spesialisasi[donor['ID']]:
                            # Pindahkan dokter dari donor ke RS ini
                            info['Dokter_List'].append(donor)
                            dokter_to_spesialisasi[donor['ID']].add(spesialisasi_rs)
                            donor_info['Dokter_List'].pop(idx)
                            info['Aksi'] = f"Reassign spesialisasi {spesialisasi_rs}"
                            donor_info['Jumlah Dokter'] -= 1
                            info['Jumlah Dokter'] += 1
                            break
                    else:
                        continue  # next donor_info
                    break  # stop if reassign berhasil


        # Step 4: Hitung ulang rasio dan format dokter untuk display
        for info in rumah_sakit_info:
            info['Rasio Baru'] = round(info['Pasien'] / info['Jumlah Dokter'], 2)
            info['Dokter'] = ', '.join([d['Nama'] for d in info['Dokter_List']])

        # Step 4.1: Tambahkan ke log spesialisasi dokter (harian)
        for info in rumah_sakit_info:
            spesialisasi_rs = rs_to_spesialisasi[info['RS']]
            for d in info['Dokter_List']:
                dokter_to_spesialisasi[d['ID']].add(spesialisasi_rs)

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
        # Ambil semua jenis spesialisasi dari RS
        semua_spesialisasi = set(rs_to_spesialisasi.values())

        # Buat tabel berdasarkan data asli
        tabel_data = []
        for id_d, sudah_dikerjakan in dokter_to_spesialisasi.items():
            belum_dikerjakan = semua_spesialisasi - sudah_dikerjakan
            tabel_data.append({
                "ID Dokter": id_d,
                "Nama": data_peserta[id_d],
                "Spesialisasi Dikerjakan": ', '.join(sorted(sudah_dikerjakan)),
                "Belum Dikerjakan": ', '.join(sorted(belum_dikerjakan))
            })

        df_spesialisasi = pd.DataFrame(tabel_data)

    return hasil_per_tanggal, dokter_to_spesialisasi, rs_to_spesialisasi, data_peserta


